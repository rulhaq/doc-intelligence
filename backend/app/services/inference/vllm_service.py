"""vLLM OpenAI-compatible inference service."""
from typing import List, Dict, Any, AsyncIterator, Optional
import json
import httpx
import structlog

from app.core.config import settings
from app.core.exceptions import ServiceUnavailableException

logger = structlog.get_logger()


def _normalize_base_url(base_url: str) -> str:
    url = base_url.rstrip("/")
    if url.endswith("/v1"):
        url = url[:-3]
    return f"{url}/v1"


class VLLMService:
    """OpenAI-compatible client for vLLM."""

    def __init__(self) -> None:
        self.base_url = _normalize_base_url(settings.VLLM_BASE_URL)
        self.model = settings.VLLM_MODEL
        self.embedding_base_url = None
        self.embedding_model = None
        if settings.VLLM_EMBEDDING_BASE_URL:
            self.embedding_base_url = _normalize_base_url(settings.VLLM_EMBEDDING_BASE_URL)
            self.embedding_model = settings.VLLM_EMBEDDING_MODEL
        self.timeout = settings.VLLM_TIMEOUT
        self.headers = {}
        if settings.VLLM_API_TOKEN:
            self.headers = {"Authorization": f"Bearer {settings.VLLM_API_TOKEN}"}

    async def generate_completion(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = settings.VLLM_TEMPERATURE,
        max_tokens: Optional[int] = None,
    ) -> str:
        """Generate a non-streaming completion.

        Prefers the OpenAI Chat Completions API (`/v1/chat/completions`), but falls back
        to the legacy Completions API (`/v1/completions`) if the server doesn't support chat.
        """

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        chat_payload: Dict[str, Any] = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "stream": False,
        }
        if max_tokens:
            chat_payload["max_tokens"] = max_tokens

        # Legacy completions payload (prompt-based)
        completion_prompt = prompt if not system_prompt else f"{system_prompt}\n\n{prompt}"
        completion_payload: Dict[str, Any] = {
            "model": self.model,
            "prompt": completion_prompt,
            "temperature": temperature,
            "stream": False,
        }
        if max_tokens:
            completion_payload["max_tokens"] = max_tokens

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    json=chat_payload,
                    headers=self.headers,
                )
                if response.status_code in (404, 405):
                    response = await client.post(
                        f"{self.base_url}/completions",
                        json=completion_payload,
                        headers=self.headers,
                    )

                response.raise_for_status()
                result = response.json()
                choices = result.get("choices") or []
                if not choices:
                    return ""

                # Chat format
                message = choices[0].get("message")
                if isinstance(message, dict):
                    return message.get("content", "") or ""

                # Completions format
                return choices[0].get("text", "") or ""
        except httpx.HTTPError as exc:
            logger.error("vLLM generation failed", error=str(exc))
            raise ServiceUnavailableException(f"LLM inference failed: {exc}")

    async def generate_completion_stream(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = settings.VLLM_TEMPERATURE,
        max_tokens: Optional[int] = None,
    ) -> AsyncIterator[str]:
        """Generate a streaming completion.

        Prefers the OpenAI Chat Completions streaming API, but falls back to legacy
        completions streaming if chat is unsupported.
        """
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        chat_payload: Dict[str, Any] = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "stream": True,
        }
        if max_tokens:
            chat_payload["max_tokens"] = max_tokens

        completion_prompt = prompt if not system_prompt else f"{system_prompt}\n\n{prompt}"
        completion_payload: Dict[str, Any] = {
            "model": self.model,
            "prompt": completion_prompt,
            "temperature": temperature,
            "stream": True,
        }
        if max_tokens:
            completion_payload["max_tokens"] = max_tokens

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                # First attempt: chat completions
                async with client.stream(
                    "POST",
                    f"{self.base_url}/chat/completions",
                    json=chat_payload,
                    headers=self.headers,
                ) as response:
                    if response.status_code in (404, 405):
                        # Fallback: legacy completions
                        async with client.stream(
                            "POST",
                            f"{self.base_url}/completions",
                            json=completion_payload,
                            headers=self.headers,
                        ) as fallback_response:
                            fallback_response.raise_for_status()
                            async for token in self._iter_sse_tokens(fallback_response, mode="completions"):
                                yield token
                            return

                    response.raise_for_status()
                    async for token in self._iter_sse_tokens(response, mode="chat"):
                        yield token
        except httpx.HTTPError as exc:
            logger.error("vLLM streaming failed", error=str(exc))
            raise ServiceUnavailableException(f"LLM streaming failed: {exc}")

    async def _iter_sse_tokens(self, response: httpx.Response, *, mode: str) -> AsyncIterator[str]:
        async for line in response.aiter_lines():
            if not line or not line.startswith("data:"):
                continue
            payload_text = line[len("data:"):].strip()
            if payload_text == "[DONE]":
                continue
            try:
                chunk = json.loads(payload_text)
            except json.JSONDecodeError:
                continue

            choices = chunk.get("choices") or []
            if not choices:
                continue

            if mode == "chat":
                delta = choices[0].get("delta", {})
                token = delta.get("content")
                if token:
                    yield token
            else:
                token = choices[0].get("text")
                if token:
                    yield token

    async def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for text."""
        payload = {"model": self.embedding_model, "input": text}
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.embedding_base_url}/embeddings",
                    json=payload,
                    headers=self.headers,
                )
                response.raise_for_status()
                result = response.json()
                data = result.get("data") or []
                if data:
                    return data[0].get("embedding") or []
                return []
        except httpx.HTTPError as exc:
            logger.error("vLLM embedding failed", error=str(exc))
            raise ServiceUnavailableException(f"Embedding generation failed: {exc}")

    async def generate_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts."""
        payload = {"model": self.embedding_model, "input": texts}
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.embedding_base_url}/embeddings",
                    json=payload,
                    headers=self.headers,
                )
                response.raise_for_status()
                result = response.json()
                data = result.get("data") or []
                return [item.get("embedding") or [] for item in data]
        except httpx.HTTPError as exc:
            logger.error("vLLM embeddings batch failed", error=str(exc))
            raise ServiceUnavailableException(f"Embedding generation failed: {exc}")

    async def health_check(self) -> bool:
        """Check if vLLM is reachable."""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    f"{self.base_url}/models",
                    headers=self.headers,
                )
                # When no token is configured, some deployments return 401/403 for protected routes.
                # Treat that as "reachable" so the rest of the app can start, while still surfacing
                # that authentication is required to actually use the LLM.
                if response.status_code in (401, 403) and not settings.VLLM_API_TOKEN:
                    logger.warning(
                        "vLLM reachable but requires authentication (no token configured)",
                        status_code=response.status_code,
                    )
                    return True

                response.raise_for_status()
                return True
        except httpx.HTTPError:
            return False
