"""Ollama LLM Inference Service"""
from typing import List, Dict, Any, AsyncIterator, Optional
import httpx
import json
import structlog

from app.core.config import settings
from app.core.exceptions import ServiceUnavailableException

logger = structlog.get_logger()


class OllamaService:
    """Ollama inference service"""
    
    def __init__(self):
        self.base_url = settings.OLLAMA_BASE_URL
        self.embedding_base_url = settings.OLLAMA_BASE_URL
        self.model = settings.OLLAMA_MODEL
        self.embedding_model = settings.OLLAMA_EMBEDDING_MODEL
        self.use_vllm = settings.VLLM_ENABLED or settings.EMBEDDING_MODEL_TYPE in (
            "vllm",
            "openai-compatible",
        )
        if self.use_vllm and settings.VLLM_BASE_URL:
            self.base_url = settings.VLLM_BASE_URL
            self.embedding_base_url = settings.VLLM_EMBEDDING_BASE_URL or settings.VLLM_BASE_URL
            if settings.VLLM_MODEL:
                self.model = settings.VLLM_MODEL
            if settings.EMBEDDING_MODEL_NAME:
                self.embedding_model = settings.EMBEDDING_MODEL_NAME
        self.timeout = settings.OLLAMA_TIMEOUT

    def _auth_headers(self) -> Dict[str, str]:
        if self.use_vllm and settings.VLLM_API_KEY:
            return {"Authorization": f"Bearer {settings.VLLM_API_KEY}"}
        return {}

    def _iter_openai_stream(self, lines: List[str]) -> List[str]:
        tokens: List[str] = []
        for line in lines:
            if not line.startswith("data:"):
                continue
            payload = line[len("data:"):].strip()
            if payload == "[DONE]":
                continue
            try:
                chunk = json.loads(payload)
                choices = chunk.get("choices", [])
                if choices:
                    delta = choices[0].get("delta", {})
                    content = delta.get("content")
                    if content:
                        tokens.append(content)
            except json.JSONDecodeError:
                continue
        return tokens
    
    async def generate_completion(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
    ) -> str:
        """Generate completion (non-streaming)"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                options = {"temperature": temperature}
                if max_tokens:
                    options["num_predict"] = max_tokens

                generate_payload = {
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "options": options,
                }

                if system_prompt:
                    generate_payload["system"] = system_prompt

                last_error: Optional[httpx.Response] = None
                response = await client.post(
                    f"{self.base_url}/api/generate",
                    json=generate_payload,
                    headers=self._auth_headers(),
                )
                if response.status_code == 404:
                    last_error = response
                    chat_messages = []
                    if system_prompt:
                        chat_messages.append({"role": "system", "content": system_prompt})
                    chat_messages.append({"role": "user", "content": prompt})
                    chat_payload = {
                        "model": self.model,
                        "messages": chat_messages,
                        "stream": False,
                        "options": options,
                    }
                    response = await client.post(
                        f"{self.base_url}/api/chat",
                        json=chat_payload,
                        headers=self._auth_headers(),
                    )
                    if response.status_code == 404:
                        last_error = response
                        oa_payload = {
                            "model": self.model,
                            "messages": chat_messages,
                            "temperature": temperature,
                        }
                        response = await client.post(
                            f"{self.base_url}/v1/chat/completions",
                            json=oa_payload,
                            headers=self._auth_headers(),
                        )
                        if response.status_code == 404 and last_error is not None:
                            last_error.raise_for_status()
                response.raise_for_status()

                result = response.json()
                if "response" in result:
                    return result.get("response", "")
                if "message" in result and "content" in result["message"]:
                    return result["message"]["content"]
                if "choices" in result and result["choices"]:
                    return result["choices"][0]["message"].get("content", "")
                return ""
                
        except httpx.HTTPError as e:
            logger.error(f"Ollama generation failed: {e}")
            raise ServiceUnavailableException(f"LLM inference failed: {e}")
    
    async def generate_completion_stream(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
    ) -> AsyncIterator[str]:
        """Generate completion (streaming)"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                options = {"temperature": temperature}
                if max_tokens:
                    options["num_predict"] = max_tokens

                generate_payload = {
                    "model": self.model,
                    "prompt": prompt,
                    "stream": True,
                    "options": options,
                }

                if system_prompt:
                    generate_payload["system"] = system_prompt

                async with client.stream(
                    "POST",
                    f"{self.base_url}/api/generate",
                    json=generate_payload,
                    headers=self._auth_headers(),
                ) as response:
                    if response.status_code == 404:
                        chat_messages = []
                        if system_prompt:
                            chat_messages.append({"role": "system", "content": system_prompt})
                        chat_messages.append({"role": "user", "content": prompt})
                        chat_payload = {
                            "model": self.model,
                            "messages": chat_messages,
                            "stream": True,
                            "options": options,
                        }
                        async with client.stream(
                            "POST",
                            f"{self.base_url}/api/chat",
                            json=chat_payload,
                            headers=self._auth_headers(),
                        ) as chat_response:
                            if chat_response.status_code == 404:
                                oa_payload = {
                                    "model": self.model,
                                    "messages": chat_messages,
                                    "stream": True,
                                }
                                async with client.stream(
                                    "POST",
                                    f"{self.base_url}/v1/chat/completions",
                                    json=oa_payload,
                                    headers=self._auth_headers(),
                                ) as oa_response:
                                    oa_response.raise_for_status()
                                    async for line in oa_response.aiter_lines():
                                        if line.strip():
                                            for token in self._iter_openai_stream([line]):
                                                yield token
                                return

                            chat_response.raise_for_status()
                            async for line in chat_response.aiter_lines():
                                if line.strip():
                                    try:
                                        chunk = json.loads(line)
                                        if "message" in chunk and "content" in chunk["message"]:
                                            yield chunk["message"]["content"]
                                    except json.JSONDecodeError:
                                        continue
                        return

                    response.raise_for_status()
                    async for line in response.aiter_lines():
                        if line.strip():
                            try:
                                chunk = json.loads(line)
                                if "response" in chunk:
                                    yield chunk["response"]
                            except json.JSONDecodeError:
                                continue
                                
        except httpx.HTTPError as e:
            logger.error(f"Ollama streaming failed: {e}")
            raise ServiceUnavailableException(f"LLM streaming failed: {e}")
    
    async def generate_chat_completion_stream(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
    ) -> AsyncIterator[str]:
        """Generate chat completion (streaming)"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                payload = {
                    "model": self.model,
                    "messages": messages,
                    "stream": True,
                    "options": {
                        "temperature": temperature,
                    }
                }
                
                async with client.stream(
                    "POST",
                    f"{self.base_url}/api/chat",
                    json=payload,
                ) as response:
                    response.raise_for_status()
                    
                    async for line in response.aiter_lines():
                        if line.strip():
                            try:
                                chunk = json.loads(line)
                                if "message" in chunk and "content" in chunk["message"]:
                                    yield chunk["message"]["content"]
                            except json.JSONDecodeError:
                                continue
                                
        except httpx.HTTPError as e:
            logger.error(f"Ollama chat streaming failed: {e}")
            raise ServiceUnavailableException(f"Chat streaming failed: {e}")
    
    async def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for text"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                last_error: Optional[httpx.Response] = None
                endpoints = (
                    ("/api/embeddings", {"model": self.embedding_model, "prompt": text}),
                    ("/api/embed", {"model": self.embedding_model, "input": text}),
                    ("/v1/embeddings", {"model": self.embedding_model, "input": text}),
                )
                for endpoint, payload in endpoints:
                    response = await client.post(
                        f"{self.embedding_base_url}{endpoint}",
                        json=payload,
                        headers=self._auth_headers(),
                    )
                    if response.status_code == 404:
                        last_error = response
                        continue
                    response.raise_for_status()
                    result = response.json()
                    if "embedding" in result:
                        return result.get("embedding") or []
                    if result.get("embeddings"):
                        return result.get("embeddings", [[]])[0]
                    if "data" in result and result["data"]:
                        return result["data"][0].get("embedding") or []
                    return []
                if last_error is not None:
                    last_error.raise_for_status()
                
        except httpx.HTTPError as e:
            logger.error(f"Ollama embedding failed: {e}")
            raise ServiceUnavailableException(f"Embedding generation failed: {e}")
    
    async def generate_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts"""
        embeddings = []
        
        for text in texts:
            embedding = await self.generate_embedding(text)
            embeddings.append(embedding)
        
        return embeddings
    
    async def health_check(self) -> bool:
        """Check if Ollama is available"""
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.get(f"{self.base_url}/api/tags")
                response.raise_for_status()
                return True
        except httpx.HTTPError:
            return False

