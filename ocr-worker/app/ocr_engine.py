"""OCR Engine using PaddleOCR and LayoutParser"""
import os
from typing import List, Dict, Any
from pathlib import Path
from pdf2image import convert_from_path
from paddleocr import PaddleOCR
import structlog
import tempfile

logger = structlog.get_logger()


class OCREngine:
    """OCR engine with PaddleOCR and layout detection"""
    
    def __init__(self):
        # Initialize PaddleOCR
        lang = os.getenv("PADDLEOCR_LANG", "en").split(",")
        use_gpu = os.getenv("PADDLEOCR_USE_GPU", "false").lower() == "true"
        
        self.ocr = PaddleOCR(
            lang=lang[0],  # Primary language
            use_angle_cls=True,
            use_gpu=use_gpu,
            show_log=False,
        )
        
        self.confidence_threshold = float(os.getenv("OCR_CONFIDENCE_THRESHOLD", "0.5"))
        storage_path = os.getenv("FILE_STORAGE_PATH")
        if not storage_path:
            raise RuntimeError("FILE_STORAGE_PATH is required")
        self.storage_path = Path(storage_path)
        self.images_dir = self.storage_path / "ocr_images"
        self.images_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(
            "OCR engine initialized",
            lang=lang,
            use_gpu=use_gpu,
            threshold=self.confidence_threshold,
        )
    
    async def process_document(self, document_id: str, file_path: str) -> Dict[str, Any]:
        """
        Process document with OCR
        
        Args:
            document_id: Document ID
            file_path: Path to PDF file in PVC storage
            
        Returns:
            OCR results with pages
        """
        logger.info("Processing document", file_path=file_path)
        
        pdf_path = Path(file_path).resolve()
        base_path = self.storage_path.resolve()
        if not str(pdf_path).startswith(str(base_path)):
            raise ValueError("Invalid file path")
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF not found: {pdf_path}")
        
        # Convert PDF to images
        temp_dir = Path(tempfile.mkdtemp())
        output_dir = self.images_dir / document_id
        output_dir.mkdir(parents=True, exist_ok=True)
        
        try:
            pages_data = []
            images = convert_from_path(str(pdf_path), fmt="png", output_folder=str(temp_dir))

            for index, image in enumerate(images, start=1):
                image_path = output_dir / f"page_{index}.png"
                image.save(image_path, "PNG")

                ocr_result = await self.process_image(str(image_path))
                pages_data.append({
                    "page_number": index,
                    "image_path": str(image_path),
                    "ocr_text": ocr_result.get("text", ""),
                    "ocr_blocks": ocr_result.get("blocks", []),
                    "ocr_confidence": ocr_result.get("confidence", 0.0),
                    "corrected_text": None,
                    "corrections": None,
                })

            logger.info("Document processing completed", pages=len(pages_data))
            
            return {
                "pages": pages_data,
                "total_pages": len(pages_data),
            }
            
        except Exception as e:
            logger.error("Document processing failed", error=str(e))
            raise
        finally:
            # Cleanup temp files
            import shutil
            if temp_dir.exists():
                shutil.rmtree(temp_dir)
    
    async def process_image(self, image_path: str) -> Dict[str, Any]:
        """
        Process single image with OCR
        
        Args:
            image_path: Path to image file
            
        Returns:
            OCR results with blocks
        """
        try:
            # Run PaddleOCR
            result = self.ocr.ocr(image_path, cls=True)
            
            if not result or not result[0]:
                return {
                    "text": "",
                    "blocks": [],
                    "confidence": 0.0,
                }
            
            # Parse results
            blocks = []
            all_text = []
            confidences = []
            
            for idx, line in enumerate(result[0]):
                bbox, (text, confidence) = line
                
                if confidence >= self.confidence_threshold:
                    blocks.append({
                        "block_id": f"b-{idx}",
                        "text": text,
                        "bbox": bbox,
                        "confidence": float(confidence),
                        "block_type": "text",  # Simplified, use layoutparser for actual type
                    })
                    all_text.append(text)
                    confidences.append(confidence)
            
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0
            full_text = "\n".join(all_text)
            
            return {
                "text": full_text,
                "blocks": blocks,
                "confidence": float(avg_confidence),
            }
            
        except Exception as e:
            logger.error("Image OCR failed", error=str(e))
            return {
                "text": "",
                "blocks": [],
                "confidence": 0.0,
            }
    
    def detect_layout(self, image_path: str) -> List[Dict[str, Any]]:
        """
        Detect layout blocks (title, paragraph, table, etc.)
        
        Note: This is a placeholder. In production, use layoutparser
        """
        # TODO: Implement layoutparser integration
        # For now, return empty list
        return []

