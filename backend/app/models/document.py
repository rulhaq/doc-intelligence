"""Document Models"""
from datetime import datetime
from sqlalchemy import Column, String, Text, DateTime, ForeignKey, JSON, Integer, Float, Boolean, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
import enum

from app.core.database import Base


class DocumentStatus(str, enum.Enum):
    """Document processing status"""
    UPLOADED = "uploaded"
    OCR_PROCESSING = "ocr_processing"
    OCR_COMPLETED = "ocr_completed"
    OCR_FAILED = "ocr_failed"
    PREVIEW = "preview"
    COMMITTED = "committed"
    FAILED = "failed"


class Document(Base):
    """Document model"""
    __tablename__ = "documents"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    filename = Column(String, nullable=False)
    original_filename = Column(String, nullable=False)
    file_path = Column(String, nullable=False)  # Path in object storage
    file_size = Column(Integer, nullable=False)
    mime_type = Column(String, nullable=False)
    
    status = Column(Enum(DocumentStatus), default=DocumentStatus.UPLOADED, nullable=False)
    
    # Metadata
    title = Column(String, nullable=True)
    source = Column(String, nullable=True)  # contracts, policies, etc.
    tags = Column(JSON, nullable=True)
    doc_metadata = Column("metadata", JSON, nullable=True)
    
    # Processing info
    total_pages = Column(Integer, nullable=True)
    processing_started_at = Column(DateTime, nullable=True)
    processing_completed_at = Column(DateTime, nullable=True)
    error_message = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    pages = relationship("DocumentPage", back_populates="document", cascade="all, delete-orphan")
    chunks = relationship("DocumentChunk", back_populates="document", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Document {self.id}: {self.original_filename} ({self.status})>"


class DocumentPage(Base):
    """Document page with OCR results"""
    __tablename__ = "document_pages"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id = Column(UUID(as_uuid=True), ForeignKey("documents.id"), nullable=False)
    
    page_number = Column(Integer, nullable=False)
    
    # Images
    image_path = Column(String, nullable=True)  # Rendered page image
    
    # OCR results
    ocr_text = Column(Text, nullable=True)  # Raw OCR text
    ocr_blocks = Column(JSON, nullable=True)  # Layout blocks with bbox, text, confidence
    ocr_confidence = Column(Float, nullable=True)  # Average confidence
    
    # LLM corrected text
    corrected_text = Column(Text, nullable=True)
    corrections = Column(JSON, nullable=True)  # List of corrections made
    
    # Admin edited text
    edited_text = Column(Text, nullable=True)
    is_edited = Column(Boolean, default=False)
    edited_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    edited_at = Column(DateTime, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    document = relationship("Document", back_populates="pages")
    
    def __repr__(self):
        return f"<DocumentPage {self.document_id} page {self.page_number}>"


class DocumentChunk(Base):
    """Document chunk (embedded in Qdrant)"""
    __tablename__ = "document_chunks"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id = Column(UUID(as_uuid=True), ForeignKey("documents.id"), nullable=False)
    
    page_number = Column(Integer, nullable=True)
    chunk_index = Column(Integer, nullable=False)
    
    text = Column(Text, nullable=False)
    chunk_hash = Column(String, nullable=False)  # Hash for deduplication
    
    # Qdrant reference
    vector_id = Column(String, nullable=True)  # Qdrant point ID
    
    # Metadata
    token_count = Column(Integer, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    document = relationship("Document", back_populates="chunks")
    
    def __repr__(self):
        return f"<DocumentChunk {self.id} from doc {self.document_id}>"

