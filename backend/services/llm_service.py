import os
from typing import Optional, Sequence, Union
from urllib.parse import urlparse

import httpx

class LLMService:
    def __init__(
        self,
        base_urls: Sequence[str],
        api_path: str = "/v1/chat/completions",
        model: Optional[str] = None,
        timeout_seconds: float = 60.0,
        api_key: Optional[str] = None,
        tls_verify: bool = True,
        ca_bundle: Optional[str] = None,
    ):
        self.base_urls = [u.rstrip("/") for u in base_urls if u and u.strip()]
        self.api_path = api_path if api_path.startswith("/") else f"/{api_path}"
        self.model = model
        self.timeout_seconds = timeout_seconds
        self.api_key = api_key.strip() if api_key else None
        self.tls_verify = tls_verify
        self.ca_bundle = ca_bundle.strip() if ca_bundle else None

        if not self.base_urls:
            raise ValueError("LLMService requires at least one base URL")

        for base_url in self.base_urls:
            parsed = urlparse(base_url)
            if parsed.scheme not in {"http", "https"}:
                raise ValueError(f"Invalid VLLM base URL scheme: {base_url}")

    def _build_api_url(self, base_url: str) -> str:
        return f"{base_url}{self.api_path}"

    def _build_headers(self) -> dict:
        if not self.api_key:
            return {}
        return {"Authorization": f"Bearer {self.api_key}"}

    async def generate_response(self, prompt: str, system_prompt: str = "You are a legal intelligence AI assistant.") -> str:
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ]
        
        payload = {
            "messages": messages,
            "temperature": 0.2,
            "max_tokens": 1024
        }
        if self.model:
            payload["model"] = self.model
        
        verify: Union[bool, str] = self.tls_verify
        if self.ca_bundle:
            verify = self.ca_bundle

        async with httpx.AsyncClient(timeout=self.timeout_seconds, verify=verify) as client:
            last_error: Optional[Exception] = None
            for base_url in self.base_urls:
                api_url = self._build_api_url(base_url)
                try:
                    response = await client.post(api_url, json=payload, headers=self._build_headers())
                    response.raise_for_status()
                    data = response.json()
                    return data["choices"][0]["message"]["content"]
                except Exception as e:
                    last_error = e
                    continue

            return (
                f"Error connecting to vLLM endpoints ({', '.join(self.base_urls)}): "
                f"{str(last_error) if last_error else 'unknown error'}"
            )

# Global instance
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


def _load_base_urls() -> list[str]:
    # Prefer explicit list (comma-separated). Otherwise use primary + fallback.
    base_urls_raw = os.getenv("VLLM_BASE_URLS", "").strip()
    if base_urls_raw:
        return [u.strip() for u in base_urls_raw.split(",") if u.strip()]

    primary = os.getenv("VLLM_BASE_URL", "http://localhost:8000").strip()
    fallback = os.getenv("VLLM_BASE_URL_FALLBACK", "").strip()
    return [u for u in [primary, fallback] if u]


llm_service = LLMService(
    base_urls=_load_base_urls(),
    api_path=os.getenv("VLLM_API_PATH", "/v1/chat/completions"),
    model=os.getenv("VLLM_MODEL") or "meta-llama/Llama-3.2-1B-Instruct",
    timeout_seconds=_env_float("VLLM_TIMEOUT_SECONDS", 60.0),
    api_key=os.getenv("VLLM_API_KEY"),
    tls_verify=_env_bool("VLLM_TLS_VERIFY", True),
    ca_bundle=os.getenv("VLLM_CA_BUNDLE"),
)
