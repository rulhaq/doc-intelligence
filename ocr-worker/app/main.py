"""OCR Worker FastAPI Application"""
from fastapi import FastAPI, Response
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import structlog
import os
from prometheus_client import Counter, Gauge, generate_latest, CONTENT_TYPE_LATEST

from app.ocr_engine import OCREngine
from app.llm_corrector import LLMCorrector

# Setup logging
structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.PrintLoggerFactory(),
)

logger = structlog.get_logger()

app = FastAPI(title="OCR Worker", version="1.0.0")

# Initialize OCR engine
ocr_engine = OCREngine()
llm_corrector = LLMCorrector()

OCR_DOCS_PROCESSED = Counter(
    "ocr_documents_processed_total",
    "Total number of documents processed by the OCR worker",
    ["status"],
)
OCR_QUEUE_SIZE = Gauge(
    "ocr_queue_size",
    "Number of documents waiting in the OCR queue",
)
OCR_QUEUE_SIZE.set(0)


class ProcessRequest(BaseModel):
    """OCR processing request"""
    document_id: str
    file_path: str


class OCRBlock(BaseModel):
    """OCR block"""
    block_id: str
    text: str
    bbox: List[float]
    confidence: float
    block_type: str


class OCRCorrection(BaseModel):
    """OCR correction"""
    from_text: str
    to: str
    confidence: float
    explain: str


class PageResult(BaseModel):
    """Page OCR result"""
    page_number: int
    image_path: Optional[str]
    ocr_text: str
    ocr_blocks: List[Dict[str, Any]]
    ocr_confidence: float
    corrected_text: Optional[str]
    corrections: Optional[List[Dict[str, Any]]]


class ProcessResponse(BaseModel):
    """OCR processing response"""
    document_id: str
    total_pages: int
    pages: List[PageResult]


@app.get("/health")
async def health():
    """Health check"""
    return {"status": "healthy", "service": "ocr-worker"}


@app.on_event("startup")
async def validate_storage():
    storage_path = os.getenv("FILE_STORAGE_PATH")
    if not storage_path:
        raise RuntimeError("FILE_STORAGE_PATH is required")


@app.get("/ready")
async def readiness():
    """Readiness check"""
    return {"ready": True}


@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint"""
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.post("/process", response_model=ProcessResponse)
async def process_document(request: ProcessRequest):
    """Process document with OCR"""
    logger.info("Processing document", document_id=request.document_id)
    
    try:
        # Process with OCR engine
        ocr_results = await ocr_engine.process_document(
            document_id=request.document_id,
            file_path=request.file_path,
        )
        
        # Correct with LLM if enabled
        pages = []
        for page_result in ocr_results["pages"]:
            corrected_text = None
            corrections = None
            
            if page_result["ocr_text"]:
                # Apply LLM correction
                correction_result = await llm_corrector.correct_text(
                    page_number=page_result["page_number"],
                    ocr_text=page_result["ocr_text"],
                )
                
                corrected_text = correction_result.get("corrected_text")
                corrections = correction_result.get("corrections")
            
            pages.append(PageResult(
                page_number=page_result["page_number"],
                image_path=page_result.get("image_path"),
                ocr_text=page_result["ocr_text"],
                ocr_blocks=page_result["ocr_blocks"],
                ocr_confidence=page_result["ocr_confidence"],
                corrected_text=corrected_text,
                corrections=corrections,
            ))
        
        logger.info(
            "Document processed",
            document_id=request.document_id,
            pages=len(pages),
        )
        OCR_DOCS_PROCESSED.labels(status="success").inc()
        
        return ProcessResponse(
            document_id=request.document_id,
            total_pages=len(pages),
            pages=pages,
        )
        
    except Exception as e:
        OCR_DOCS_PROCESSED.labels(status="failed").inc()
        logger.error("OCR processing failed", error=str(e))
        raise


if __name__ == "__main__":
    import uvicorn
    import os
    port_str = os.getenv("OCR_WORKER_PORT")
    if not port_str:
        raise RuntimeError("OCR_WORKER_PORT is required")
    port = int(port_str)
    uvicorn.run(app, host="0.0.0.0", port=port)

