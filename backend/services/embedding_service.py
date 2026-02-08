import os
from typing import List, Optional, Sequence, Union
from urllib.parse import urlparse

import httpx


class EmbeddingService:
    def __init__(
        self,
        base_url: str,
        embed_path: str = "/embed",
        timeout_seconds: float = 30.0,
        api_key: Optional[str] = None,
        tls_verify: bool = True,
        ca_bundle: Optional[str] = None,
    ):
        self.base_url = base_url.rstrip("/")
        self.embed_path = embed_path if embed_path.startswith("/") else f"/{embed_path}"
        self.timeout_seconds = timeout_seconds
        self.api_key = api_key.strip() if api_key else None
        self.tls_verify = tls_verify
        self.ca_bundle = ca_bundle.strip() if ca_bundle else None

        parsed = urlparse(self.base_url)
        if parsed.scheme not in {"http", "https"}:
            raise ValueError(f"Invalid TEI base URL scheme: {self.base_url}")

    def _api_url(self) -> str:
        return f"{self.base_url}{self.embed_path}"

    def _headers(self) -> dict:
        if not self.api_key:
            return {}
        return {"Authorization": f"Bearer {self.api_key}"}

    def embed(self, inputs: Sequence[str]) -> List[List[float]]:
        payload = {"inputs": list(inputs)}

        verify: Union[bool, str] = self.tls_verify
        if self.ca_bundle:
            verify = self.ca_bundle

        with httpx.Client(timeout=self.timeout_seconds, verify=verify) as client:
            response = client.post(self._api_url(), json=payload, headers=self._headers())
            response.raise_for_status()
            data = response.json()

        # TEI typically returns either:
        # - [[...], [...]] for batch inputs
        # - [...] for a single input
        if isinstance(data, list) and data and isinstance(data[0], (int, float)):
            return [data]  # single vector
        if isinstance(data, list):
            return data

        raise ValueError(f"Unexpected TEI /embed response format: {type(data)}")


def _env_bool(name: str, default: bool) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "y", "on"}


def _env_float(name: str, default: float) -> float:
    raw = os.getenv(name)
    if raw is None or not raw.strip():
        return default
    try:
        return float(raw)
    except ValueError:
        return default


embedding_service = EmbeddingService(
    base_url=os.getenv("TEI_BASE_URL", "http://tei:8080"),
    embed_path=os.getenv("TEI_EMBED_PATH", "/embed"),
    timeout_seconds=_env_float("TEI_TIMEOUT_SECONDS", 30.0),
    api_key=os.getenv("TEI_API_KEY"),
    tls_verify=_env_bool("TEI_TLS_VERIFY", True),
    ca_bundle=os.getenv("TEI_CA_BUNDLE"),
)

