"""LLM-based OCR Correction."""
import os
import json
from typing import Dict, Any, List
import httpx
import structlog

logger = structlog.get_logger()


def _normalize_base_url(base_url: str) -> str:
    url = base_url.rstrip("/")
    if url.endswith("/v1"):
        url = url[:-3]
    return f"{url}/v1"


class LLMCorrector:
    """LLM-based OCR text correction."""

    def __init__(self):
        self.enabled = os.getenv("OCR_LLM_CORRECTION_ENABLED", "true").lower() == "true"
        self.base_url = os.getenv("VLLM_BASE_URL")
        self.model = os.getenv("VLLM_MODEL")
        self.token = os.getenv("VLLM_API_TOKEN")
        self.timeout = float(os.getenv("VLLM_TIMEOUT", "60"))

        if self.enabled:
            if not self.base_url or not self.model or not self.token:
                raise RuntimeError("VLLM_BASE_URL, VLLM_MODEL, and VLLM_API_TOKEN are required for OCR LLM correction")
            self.base_url = _normalize_base_url(self.base_url)
            self.headers = {"Authorization": f"Bearer {self.token}"}

        logger.info(
            "LLM corrector initialized",
            enabled=self.enabled,
            model=self.model,
        )

    async def correct_text(
        self,
        page_number: int,
        ocr_text: str,
        block_id: str = None,
    ) -> Dict[str, Any]:
        """
        Correct OCR text using LLM.

        Args:
            page_number: Page number
            ocr_text: Raw OCR text
            block_id: Optional block ID

        Returns:
            Corrected text and corrections list
        """
        if not self.enabled:
            return {
                "corrected_text": ocr_text,
                "corrections": [],
            }

        if not ocr_text or len(ocr_text.strip()) == 0:
            return {
                "corrected_text": "",
                "corrections": [],
            }

        try:
            prompt = self._build_correction_prompt(page_number, ocr_text, block_id)
            payload = {
                "model": self.model,
                "messages": [
                    {
                        "role": "system",
                        "content": "You are a precise OCR correction assistant for legal documents.",
                    },
                    {"role": "user", "content": prompt},
                ],
                "temperature": 0.1,
                "stream": False,
            }

            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    json=payload,
                    headers=self.headers,
                )
                response.raise_for_status()
                result = response.json()
                choices = result.get("choices") or []
                llm_output = choices[0].get("message", {}).get("content", "") if choices else ""

            try:
                parsed = json.loads(llm_output)
                corrected_text = parsed.get("corrected_text", ocr_text)
                corrections = parsed.get("corrections", [])
            except json.JSONDecodeError:
                logger.warning("LLM output is not valid JSON, using original text")
                corrected_text = ocr_text
                corrections = []

            logger.info(
                "Text corrected",
                page=page_number,
                corrections_count=len(corrections),
            )

            return {
                "corrected_text": corrected_text,
                "corrections": corrections,
            }

        except Exception as e:
            logger.error("LLM correction failed", error=str(e))
            return {
                "corrected_text": ocr_text,
                "corrections": [],
            }

    def _build_correction_prompt(
        self,
        page_number: int,
        ocr_text: str,
        block_id: str = None,
    ) -> str:
        """Build prompt for LLM correction."""
        prompt = f"""You are CustomerLLM specialized in legal and contract documents. Your task is to correct OCR errors in text.

Input OCR text (from page {page_number}):
{ocr_text}

Instructions:
- Fix obvious spelling errors and OCR mistakes (e.g., '0' vs 'O', 'I' vs 'l', 'rn' vs 'm')
- Preserve legal tokens and defined terms (especially ALL-CAPS terms)
- Fix broken words caused by poor OCR
- Maintain original formatting and line breaks where possible
- Be conservative - only fix clear errors

Output your response as valid JSON with this exact structure:
{{
  "corrected_text": "The corrected text here...",
  "corrections": [
    {{"from": "Th1s", "to": "This", "confidence": 0.98, "explain": "digit 1 -> letter i"}},
    {{"from": "Jannary", "to": "January", "confidence": 0.95, "explain": "double n -> single n"}}
  ]
}}

Your JSON response:"""
        return prompt
