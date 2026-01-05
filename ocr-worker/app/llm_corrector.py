"""LLM-based OCR Correction"""
import os
import json
from typing import Dict, Any, List
import httpx
import structlog

logger = structlog.get_logger()


class LLMCorrector:
    """LLM-based OCR text correction"""
    
    def __init__(self):
        self.ollama_base_url = os.getenv("OLLAMA_BASE_URL", "http://ollama:11434")
        self.model = os.getenv("OLLAMA_MODEL", "jais:13b")
        self.enabled = os.getenv("OCR_LLM_CORRECTION_ENABLED", "true").lower() == "true"
        
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
        Correct OCR text using LLM
        
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
            # Build prompt
            prompt = self._build_correction_prompt(page_number, ocr_text, block_id)
            
            # Call Ollama
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{self.ollama_base_url}/api/generate",
                    json={
                        "model": self.model,
                        "prompt": prompt,
                        "stream": False,
                        "options": {
                            "temperature": 0.1,  # Low temperature for consistency
                        }
                    },
                )
                response.raise_for_status()
                
                result = response.json()
                llm_output = result.get("response", "")
            
            # Parse LLM output (expecting JSON)
            try:
                parsed = json.loads(llm_output)
                corrected_text = parsed.get("corrected_text", ocr_text)
                corrections = parsed.get("corrections", [])
            except json.JSONDecodeError:
                # Fallback if LLM doesn't return valid JSON
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
            # Return original text on error
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
        """Build prompt for LLM correction"""
        
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

