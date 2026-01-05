"""Admin Document Management Endpoints"""
from typing import List
from uuid import UUID
import uuid
import hashlib
from pathlib import Path
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
import structlog

from app.core.database import get_db
from app.core.security import get_current_active_user, require_role
from app.core.config import settings
from app.core.exceptions import NotFoundException, ValidationException
from app.models.user import User
from app.models.document import Document, DocumentPage, DocumentChunk, DocumentStatus
from app.schemas.document import (
    DocumentUploadResponse,
    DocumentPreviewResponse,
    PagePreview,
    PageEditRequest,
    DocumentStatusResponse,
    DocumentResponse,
    DocumentListResponse,
)
from app.services.storage.minio_service import MinIOService

logger = structlog.get_logger()
router = APIRouter()


async def process_document_simple(document_id: str, file_content: bytes, db: Session):
    """Background task to process document with simple PDF extraction"""
    try:
        from app.services.document.simple_processor import SimpleDocumentProcessor
        from datetime import datetime
        
        document = db.query(Document).filter(Document.id == document_id).first()
        if not document:
            return
        
        document.status = DocumentStatus.OCR_PROCESSING
        document.processing_started_at = datetime.utcnow()
        db.commit()
        
        # Process document (PDF, DOCX, or TXT)
        processor = SimpleDocumentProcessor()
        result = await processor.process_document(file_content, document.original_filename)
        
        if result["success"]:
            # Update document
            document.status = DocumentStatus.OCR_COMPLETED
            document.total_pages = result["total_pages"]
            document.processing_completed_at = datetime.utcnow()
            
            # Store extracted text in metadata
            if not document.doc_metadata:
                document.doc_metadata = {}
            document.doc_metadata['extracted_text'] = result['full_text']
            document.doc_metadata['extraction_method'] = 'simple_pdf'
            
            # Save pages
            for page_data in result["pages"]:
                page = DocumentPage(
                    document_id=document.id,
                    page_number=page_data["page"],
                    ocr_text=page_data["raw_text"],
                    corrected_text=page_data["cleaned_text"],
                    ocr_confidence=1.0,  # PDF extraction is reliable
                )
                db.add(page)
            
            db.commit()
            logger.info("Document processing completed", document_id=str(document_id))
        else:
            raise Exception(result.get("error", "Processing failed"))
            
    except Exception as e:
        logger.error("Document processing failed", document_id=str(document_id), error=str(e))
        
        document = db.query(Document).filter(Document.id == document_id).first()
        if document:
            document.status = DocumentStatus.OCR_FAILED
            document.error_message = str(e)
            db.commit()


async def process_document_ocr(document_id: str, db: Session):
    """Background task to process document OCR"""
    try:
        import httpx
        
        document = db.query(Document).filter(Document.id == document_id).first()
        if not document:
            return
        
        document.status = DocumentStatus.OCR_PROCESSING
        from datetime import datetime
        document.processing_started_at = datetime.utcnow()
        db.commit()
        
        # Call OCR worker
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{settings.OCR_WORKER_URL}/process",
                json={
                    "document_id": str(document_id),
                    "file_path": document.file_path,
                },
                timeout=300,
            )
            response.raise_for_status()
            ocr_result = response.json()
        
        # Update document
        document.status = DocumentStatus.OCR_COMPLETED
        document.total_pages = ocr_result.get("total_pages", 0)
        document.processing_completed_at = datetime.utcnow()
        
        # Save pages
        for page_data in ocr_result.get("pages", []):
            page = DocumentPage(
                document_id=document.id,
                page_number=page_data["page_number"],
                image_path=page_data.get("image_path"),
                ocr_text=page_data.get("ocr_text"),
                ocr_blocks=page_data.get("ocr_blocks"),
                ocr_confidence=page_data.get("ocr_confidence"),
                corrected_text=page_data.get("corrected_text"),
                corrections=page_data.get("corrections"),
            )
            db.add(page)
        
        db.commit()
        
        logger.info("OCR processing completed", document_id=str(document_id))
        
    except Exception as e:
        logger.error("OCR processing failed", document_id=str(document_id), error=str(e))
        
        document = db.query(Document).filter(Document.id == document_id).first()
        if document:
            document.status = DocumentStatus.OCR_FAILED
            document.error_message = str(e)
            db.commit()


@router.post("/upload", response_model=DocumentUploadResponse)
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db),
):
    """Upload document (PDF) - Simple processing without OCR"""
    # Validate file
    if not file.filename:
        raise ValidationException("No filename provided")
    
    file_ext = Path(file.filename).suffix.lower().replace(".", "")
    if file_ext not in settings.get_allowed_extensions_list():
        raise ValidationException(f"File type .{file_ext} not allowed")
    
    # Read file content
    content = await file.read()
    file_size = len(content)
    
    if file_size > settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024:
        raise ValidationException(f"File too large (max {settings.MAX_UPLOAD_SIZE_MB}MB)")
    
    # Generate unique filename
    file_hash = hashlib.sha256(content).hexdigest()[:16]
    unique_filename = f"{uuid.uuid4()}_{file_hash}.{file_ext}"
    object_path = f"documents/{unique_filename}"
    
    # Upload to MinIO
    minio_service = MinIOService()
    from io import BytesIO
    await minio_service.upload_file(
        file=BytesIO(content),
        object_name=object_path,
        content_type=file.content_type,
    )
    
    # Create document record
    document = Document(
        user_id=current_user.id,
        filename=unique_filename,
        original_filename=file.filename,
        file_path=object_path,
        file_size=file_size,
        mime_type=file.content_type or "application/pdf",
        status=DocumentStatus.UPLOADED,
    )
    
    db.add(document)
    db.commit()
    db.refresh(document)
    
    logger.info(
        "Document uploaded",
        document_id=str(document.id),
        filename=file.filename,
    )
    
    # Process document in background
    background_tasks.add_task(process_document_simple, str(document.id), content, db)
    
    return DocumentUploadResponse(
        document_id=str(document.id),
        filename=file.filename,
        file_size=file_size,
        status=document.status.value,
    )


@router.post("/{document_id}/process-ocr")
async def process_ocr(
    document_id: UUID,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db),
):
    """Trigger OCR processing"""
    document = db.query(Document).filter(Document.id == document_id).first()
    
    if not document:
        raise NotFoundException("Document not found")
    
    if document.status != DocumentStatus.UPLOADED:
        raise ValidationException("Document must be in 'uploaded' status")
    
    # Add background task
    background_tasks.add_task(process_document_ocr, str(document_id), db)
    
    logger.info("OCR processing queued", document_id=str(document_id))
    
    return {"message": "OCR processing started", "document_id": str(document_id)}


@router.get("/{document_id}/preview", response_model=DocumentPreviewResponse)
async def get_document_preview(
    document_id: UUID,
    current_user: User = Depends(require_role("editor")),
    db: Session = Depends(get_db),
):
    """Get document preview with OCR results"""
    document = db.query(Document).filter(Document.id == document_id).first()
    
    if not document:
        raise NotFoundException("Document not found")
    
    if document.status not in [DocumentStatus.OCR_COMPLETED, DocumentStatus.PREVIEW, DocumentStatus.COMMITTED]:
        raise ValidationException("Document OCR not completed")
    
    # Get pages
    pages = db.query(DocumentPage).filter(
        DocumentPage.document_id == document_id
    ).order_by(DocumentPage.page_number).all()
    
    # Generate presigned URLs for images
    minio_service = MinIOService()
    page_previews = []
    
    for page in pages:
        image_url = ""
        if page.image_path:
            image_url = await minio_service.get_file_url(page.image_path)
        
        page_preview = PagePreview(
            page_number=page.page_number,
            image_url=image_url,
            ocr_text=page.ocr_text,
            ocr_blocks=page.ocr_blocks,
            ocr_confidence=page.ocr_confidence,
            corrected_text=page.corrected_text,
            corrections=page.corrections,
            edited_text=page.edited_text,
            is_edited=page.is_edited,
        )
        page_previews.append(page_preview)
    
    return DocumentPreviewResponse(
        document_id=str(document.id),
        filename=document.original_filename,
        total_pages=document.total_pages or 0,
        status=document.status.value,
        pages=page_previews,
    )


@router.put("/{document_id}/preview")
async def update_document_preview(
    document_id: UUID,
    edits: List[PageEditRequest],
    current_user: User = Depends(require_role("editor")),
    db: Session = Depends(get_db),
):
    """Update document preview with manual edits"""
    document = db.query(Document).filter(Document.id == document_id).first()
    
    if not document:
        raise NotFoundException("Document not found")
    
    from datetime import datetime
    
    for edit in edits:
        page = db.query(DocumentPage).filter(
            DocumentPage.document_id == document_id,
            DocumentPage.page_number == edit.page_number,
        ).first()
        
        if page:
            page.edited_text = edit.edited_text
            page.is_edited = True
            page.edited_by = current_user.id
            page.edited_at = datetime.utcnow()
    
    document.status = DocumentStatus.PREVIEW
    db.commit()
    
    logger.info("Document preview updated", document_id=str(document_id))
    
    return {"message": "Preview updated", "document_id": str(document_id)}


@router.post("/{document_id}/commit")
async def commit_document(
    document_id: UUID,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db),
):
    """Commit document (embed and upsert to Qdrant)"""
    document = db.query(Document).filter(Document.id == document_id).first()
    
    if not document:
        raise NotFoundException("Document not found")
    
    if document.status not in [DocumentStatus.OCR_COMPLETED, DocumentStatus.PREVIEW]:
        raise ValidationException("Document not ready to commit")
    
    # Background task to chunk, embed, and upsert
    async def commit_task():
        from app.services.vector.qdrant_service import QdrantService
        from app.services.inference.ollama_service import OllamaService
        from app.core.database import SessionLocal
        import hashlib
        
        # Create new DB session for background task
        db_task = SessionLocal()
        
        try:
            # Get document in this session
            doc = db_task.query(Document).filter(Document.id == document_id).first()
            if not doc:
                return
            
            # Check if admin has saved corrected text
            corrected_full_text = None
            if doc.doc_metadata and 'corrected_text' in doc.doc_metadata:
                corrected_full_text = doc.doc_metadata['corrected_text']
            
            pages = db_task.query(DocumentPage).filter(
                DocumentPage.document_id == document_id
            ).all()
            
            # Chunk and embed
            ollama_service = OllamaService()
            qdrant_service = QdrantService()
            
            points = []
            chunk_index = 0
            
            # If we have corrected full text, use that instead of page-by-page
            if corrected_full_text:
                # Simple chunking of the corrected text
                chunks = [corrected_full_text[i:i+settings.CHUNK_SIZE] for i in range(0, len(corrected_full_text), settings.CHUNK_SIZE - settings.CHUNK_OVERLAP)]
                
                for chunk_text in chunks:
                    # Generate embedding
                    embedding = await ollama_service.generate_embedding(chunk_text)
                    
                    # Create chunk record
                    chunk_hash = hashlib.sha256(chunk_text.encode()).hexdigest()
                    chunk = DocumentChunk(
                        document_id=doc.id,
                        page_number=1,  # Not page-specific for corrected text
                        chunk_index=chunk_index,
                        text=chunk_text,
                        chunk_hash=chunk_hash,
                        vector_id=f"{doc.id}_{chunk_index}",
                    )
                    db_task.add(chunk)
                    db_task.flush()  # Get chunk ID
                    
                    # Prepare point for Qdrant (use chunk ID as point ID for Qdrant)
                    points.append({
                        "id": str(chunk.id),  # Use UUID directly
                        "vector": embedding,
                        "payload": {
                            "doc_id": str(doc.id),
                            "chunk_id": str(chunk.id),
                            "chunk_index": chunk_index,
                            "text": chunk_text,
                            "title": doc.title or doc.original_filename,
                            "source": doc.source,
                            "language": doc.doc_metadata.get('language', 'auto') if doc.doc_metadata else 'auto',
                        }
                    })
                    
                    chunk_index += 1
            else:
                # Use page-by-page text
                for page in pages:
                    # Use edited text if available, otherwise corrected or OCR text
                    text = page.edited_text or page.corrected_text or page.ocr_text
                    
                    if not text:
                        continue
                
                    # Simple chunking (in production, use semantic chunking)
                    chunks = [text[i:i+settings.CHUNK_SIZE] for i in range(0, len(text), settings.CHUNK_SIZE - settings.CHUNK_OVERLAP)]
                    
                    for chunk_text in chunks:
                        # Generate embedding
                        embedding = await ollama_service.generate_embedding(chunk_text)
                        
                        # Create chunk record
                        chunk_hash = hashlib.sha256(chunk_text.encode()).hexdigest()
                        chunk = DocumentChunk(
                            document_id=doc.id,
                            page_number=page.page_number,
                            chunk_index=chunk_index,
                            text=chunk_text,
                            chunk_hash=chunk_hash,
                            vector_id=f"{doc.id}_{chunk_index}",
                        )
                        db_task.add(chunk)
                        db_task.flush()  # Get chunk ID
                        
                        # Prepare point for Qdrant (use chunk ID as point ID)
                        points.append({
                            "id": str(chunk.id),  # Use UUID directly
                            "vector": embedding,
                            "payload": {
                                "doc_id": str(doc.id),
                                "chunk_id": str(chunk.id),
                                "chunk_index": chunk_index,
                                "page_number": page.page_number,
                                "text": chunk_text,
                                "title": doc.title or doc.original_filename,
                                "source": doc.source,
                            }
                        })
                        
                        chunk_index += 1
            
            # Upsert to Qdrant
            if points:
                await qdrant_service.upsert_vectors(points)
                logger.info("Upserted to Qdrant", document_id=str(document_id), chunks=len(points))
            
            # Update document status
            doc.status = DocumentStatus.COMMITTED
            db_task.commit()
            
            logger.info("Document committed", document_id=str(document_id), chunks=len(points))
            
        except Exception as e:
            logger.error("Document commit failed", document_id=str(document_id), error=str(e))
            d = db_task.query(Document).filter(Document.id == document_id).first()
            if d:
                d.status = DocumentStatus.FAILED
                d.error_message = str(e)
                db_task.commit()
        finally:
            db_task.close()
    
    background_tasks.add_task(commit_task)
    
    return {"message": "Document commit started", "document_id": str(document_id)}


@router.get("/{document_id}/status", response_model=DocumentStatusResponse)
async def get_document_status(
    document_id: UUID,
    current_user: User = Depends(require_role("viewer")),
    db: Session = Depends(get_db),
):
    """Get document processing status"""
    document = db.query(Document).filter(Document.id == document_id).first()
    
    if not document:
        raise NotFoundException("Document not found")
    
    return DocumentStatusResponse.model_validate(document)


@router.get("", response_model=DocumentListResponse)
async def list_documents(
    page: int = 1,
    page_size: int = 50,
    status: str = None,
    current_user: User = Depends(require_role("viewer")),
    db: Session = Depends(get_db),
):
    """List documents"""
    query = db.query(Document)
    
    if status:
        query = query.filter(Document.status == status)
    
    total = query.count()
    
    documents = query.order_by(Document.created_at.desc()).offset(
        (page - 1) * page_size
    ).limit(page_size).all()
    
    return DocumentListResponse(
        documents=[DocumentResponse.model_validate(doc) for doc in documents],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.post("/{document_id}/corrected-text")
async def save_corrected_text(
    document_id: UUID,
    corrected_text: dict,
    current_user: User = Depends(require_role("editor")),
    db: Session = Depends(get_db),
):
    """Save admin-corrected text for document"""
    document = db.query(Document).filter(Document.id == document_id).first()
    
    if not document:
        raise NotFoundException("Document not found")
    
    # Save corrected text to document metadata
    if not document.doc_metadata:
        document.doc_metadata = {}
    
    document.doc_metadata['corrected_text'] = corrected_text.get('corrected_text', '')
    document.doc_metadata['language'] = corrected_text.get('language', 'auto')
    document.doc_metadata['corrected_by'] = str(current_user.id)
    
    from datetime import datetime
    document.doc_metadata['corrected_at'] = datetime.utcnow().isoformat()
    
    # Update status to indicate manual review
    if document.status == DocumentStatus.OCR_COMPLETED:
        document.status = DocumentStatus.PREVIEW
    
    db.commit()
    
    logger.info("Corrected text saved", document_id=str(document_id))
    
    return {
        "message": "Corrected text saved successfully",
        "document_id": str(document_id)
    }


@router.delete("/{document_id}")
async def delete_document(
    document_id: UUID,
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db),
):
    """Delete document"""
    document = db.query(Document).filter(Document.id == document_id).first()
    
    if not document:
        raise NotFoundException("Document not found")
    
    # Delete from Qdrant
    from app.services.vector.qdrant_service import QdrantService
    qdrant_service = QdrantService()
    await qdrant_service.delete_by_doc_id(str(document_id))
    
    # Delete from MinIO
    from app.services.storage.minio_service import MinIOService
    minio_service = MinIOService()
    await minio_service.delete_file(document.file_path)
    
    # Delete from database
    db.delete(document)
    db.commit()
    
    logger.info("Document deleted", document_id=str(document_id))
    
    return {"message": "Document deleted"}

