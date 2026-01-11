"""Embeddings provider abstraction (vLLM or TEI)."""
from __future__ import annotations

from functools import lru_cache
from typing import List, Optional, Dict, Any
import httpx
import structlog

from app.core.config import settings
from app.core.exceptions import ServiceUnavailableException

logger = structlog.get_logger()


def _normalize_base_url(base_url: str) -> str:
    return base_url.rstrip("/")


class EmbeddingsService:
    """Route embeddings to the configured provider."""

    def __init__(self) -> None:
        self.provider = settings.EMBEDDINGS_PROVIDER
        self.vllm_base_url = settings.VLLM_EMBEDDING_BASE_URL
        self.vllm_model = settings.VLLM_EMBEDDING_MODEL
        self.vllm_token = settings.VLLM_API_TOKEN
        self.tei_base_url = settings.TEI_BASE_URL
        self.tei_token = settings.TEI_API_TOKEN
        self.tei_timeout = settings.TEI_TIMEOUT
        self.vllm_timeout = settings.VLLM_TIMEOUT

        if self.provider == "tei" and not self.tei_base_url:
            raise ServiceUnavailableException("TEI_BASE_URL is required for embeddings provider 'tei'")
        if self.provider == "vllm" and (not self.vllm_base_url or not self.vllm_model):
            raise ServiceUnavailableException("VLLM_EMBEDDING_BASE_URL and VLLM_EMBEDDING_MODEL are required for embeddings provider 'vllm'")

    async def embed_query(self, text: str) -> List[float]:
        vectors = await self.embed_texts([text])
        return vectors[0] if vectors else []

    async def embed_texts(self, texts: List[str]) -> List[List[float]]:
        if self.provider == "tei":
            return await self._embed_with_tei(texts)
        return await self._embed_with_vllm(texts)

    async def _embed_with_vllm(self, texts: List[str]) -> List[List[float]]:
        base_url = _normalize_base_url(self.vllm_base_url)
        payload: Dict[str, Any] = {
            "model": self.vllm_model,
            "input": texts,
        }
        headers = {}
        if self.vllm_token:
            headers = {"Authorization": f"Bearer {self.vllm_token}"}

        try:
            async with httpx.AsyncClient(timeout=self.vllm_timeout) as client:
                response = await client.post(
                    f"{base_url}/v1/embeddings",
                    json=payload,
                    headers=headers,
                )
                response.raise_for_status()
                data = response.json().get("data") or []
                return [item.get("embedding") or [] for item in data]
        except httpx.HTTPError as exc:
            logger.error("vLLM embeddings failed", error=str(exc))
            raise ServiceUnavailableException(f"Embedding generation failed: {exc}")

    async def _embed_with_tei(self, texts: List[str]) -> List[List[float]]:
        base_url = _normalize_base_url(self.tei_base_url)
        payload = {"inputs": texts}
        headers: Dict[str, str] = {}
        if self.tei_token:
            headers["Authorization"] = f"Bearer {self.tei_token}"

        attempts = 0
        last_error: Optional[Exception] = None

        while attempts < 2:
            attempts += 1
            try:
                async with httpx.AsyncClient(timeout=self.tei_timeout) as client:
                    response = await client.post(
                        f"{base_url}/embed",
                        json=payload,
                        headers=headers,
                    )
                    if response.status_code >= 500 and attempts < 2:
                        last_error = httpx.HTTPError(f"TEI server error: {response.status_code}")
                        continue
                    response.raise_for_status()
                    return self._parse_tei_response(response)
            except httpx.HTTPError as exc:
                last_error = exc
                if attempts >= 2:
                    logger.error("TEI embeddings failed", error=str(exc))
                    raise ServiceUnavailableException(f"Embedding generation failed: {exc}")

        raise ServiceUnavailableException(f"Embedding generation failed: {last_error}")

    def _parse_tei_response(self, response: httpx.Response) -> List[List[float]]:
        try:
            data = response.json()
        except ValueError:
            snippet = response.text[:200]
            logger.error("TEI returned non-JSON response", snippet=snippet)
            raise ServiceUnavailableException("TEI returned non-JSON response")

        if isinstance(data, list):
            return data
        if isinstance(data, dict):
            if "embeddings" in data and isinstance(data["embeddings"], list):
                return data["embeddings"]
            if "data" in data and isinstance(data["data"], list):
                return [item.get("embedding") or [] for item in data["data"]]

        snippet = str(data)[:200]
        logger.error("Unexpected TEI response shape", snippet=snippet)
        raise ServiceUnavailableException("Unexpected TEI response shape")


@lru_cache
def get_embeddings_service() -> EmbeddingsService:
    return EmbeddingsService()


async def embed_texts(texts: List[str]) -> List[List[float]]:
    return await get_embeddings_service().embed_texts(texts)


async def embed_query(text: str) -> List[float]:
    return await get_embeddings_service().embed_query(text)
