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
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
    ) -> str:
        """Generate a non-streaming chat completion."""
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        payload: Dict[str, Any] = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "stream": False,
        }
        if max_tokens:
            payload["max_tokens"] = max_tokens

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    json=payload,
                    headers=self.headers,
                )
                response.raise_for_status()
                result = response.json()
                choices = result.get("choices") or []
                if choices:
                    return choices[0].get("message", {}).get("content", "") or ""
                return ""
        except httpx.HTTPError as exc:
            logger.error("vLLM generation failed", error=str(exc))
            raise ServiceUnavailableException(f"LLM inference failed: {exc}")

    async def generate_completion_stream(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
    ) -> AsyncIterator[str]:
        """Generate a streaming chat completion."""
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        payload: Dict[str, Any] = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "stream": True,
        }
        if max_tokens:
            payload["max_tokens"] = max_tokens

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                async with client.stream(
                    "POST",
                    f"{self.base_url}/chat/completions",
                    json=payload,
                    headers=self.headers,
                ) as response:
                    response.raise_for_status()
                    async for line in response.aiter_lines():
                        if not line:
                            continue
                        if not line.startswith("data:"):
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
                        delta = choices[0].get("delta", {})
                        token = delta.get("content")
                        if token:
                            yield token
        except httpx.HTTPError as exc:
            logger.error("vLLM streaming failed", error=str(exc))
            raise ServiceUnavailableException(f"LLM streaming failed: {exc}")

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
                response.raise_for_status()
                return True
        except httpx.HTTPError:
            return False
