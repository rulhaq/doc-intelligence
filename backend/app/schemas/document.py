"""Document Schemas"""
from pydantic import BaseModel, Field, field_serializer
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID
from uuid import UUID


class DocumentUploadResponse(BaseModel):
    """Document upload response"""
    document_id: str
    filename: str
    file_size: int
    status: str


class OCRBlock(BaseModel):
    """OCR block with layout information"""
    block_id: str
    text: str
    bbox: List[float]  # [x1, y1, x2, y2]
    confidence: float
    block_type: str  # paragraph, title, table, etc.


class OCRCorrection(BaseModel):
    """LLM OCR correction"""
    from_text: str = Field(..., alias="from")
    to: str
    confidence: float
    explain: str
    
    class Config:
        populate_by_name = True


class PagePreview(BaseModel):
    """Page preview with OCR results"""
    page_number: int
    image_url: str
    ocr_text: Optional[str]
    ocr_blocks: Optional[List[OCRBlock]]
    ocr_confidence: Optional[float]
    corrected_text: Optional[str]
    corrections: Optional[List[OCRCorrection]]
    edited_text: Optional[str]
    is_edited: bool = False


class DocumentPreviewResponse(BaseModel):
    """Document preview response"""
    document_id: str
    filename: str
    total_pages: int
    status: str
    pages: List[PagePreview]


class PageEditRequest(BaseModel):
    """Page edit request"""
    page_number: int
    edited_text: str


class DocumentStatusResponse(BaseModel):
    """Document processing status"""
    document_id: str
    filename: str
    status: str
    total_pages: Optional[int]
    processing_started_at: Optional[datetime]
    processing_completed_at: Optional[datetime]
    error_message: Optional[str]
    audit_log: Optional[List[Dict[str, Any]]] = []
    
    class Config:
        from_attributes = True


class DocumentResponse(BaseModel):
    """Document response"""
    id: UUID
    filename: str
    original_filename: str
    file_size: int
    mime_type: str
    status: str
    title: Optional[str]
    source: Optional[str]
    tags: Optional[List[str]]
    total_pages: Optional[int]
    created_at: datetime
    updated_at: datetime
    
    @field_serializer('id')
    def serialize_id(self, value: UUID) -> str:
        return str(value)
    
    class Config:
        from_attributes = True


class DocumentListResponse(BaseModel):
    """Document list response"""
    documents: List[DocumentResponse]
    total: int
    page: int
    page_size: int

