"""Celery Background Tasks"""
from app.workers.celery_app import celery_app
import structlog

logger = structlog.get_logger()


@celery_app.task(name="tasks.process_document")
def process_document_task(document_id: str):
    """Process document OCR in background"""
    logger.info("Processing document", document_id=document_id)
    
    # Import here to avoid circular dependencies
    from app.core.database import SessionLocal
    from app.models.document import Document, DocumentStatus
    from datetime import datetime
    
    db = SessionLocal()
    
    try:
        document = db.query(Document).filter(Document.id == document_id).first()
        if not document:
            logger.error("Document not found", document_id=document_id)
            return
        
        document.status = DocumentStatus.OCR_PROCESSING
        document.processing_started_at = datetime.utcnow()
        db.commit()
        
        # Call OCR worker
        import httpx
        from app.core.config import settings
        
        response = httpx.post(
            f"{settings.OCR_WORKER_URL}/process",
            json={
                "document_id": str(document_id),
                "file_path": document.file_path,
            },
            timeout=300,
        )
        response.raise_for_status()
        
        logger.info("Document processed", document_id=document_id)
        
    except Exception as e:
        logger.error("Document processing failed", document_id=document_id, error=str(e))
        
        if document:
            document.status = DocumentStatus.OCR_FAILED
            document.error_message = str(e)
            db.commit()
    
    finally:
        db.close()


@celery_app.task(name="tasks.embed_document")
def embed_document_task(document_id: str):
    """Embed document chunks and upsert to Qdrant"""
    logger.info("Embedding document", document_id=document_id)
    
    from app.core.database import SessionLocal
    from app.models.document import Document, DocumentPage, DocumentChunk, DocumentStatus
    from app.services.vector.qdrant_service import QdrantService
    from app.services.inference.ollama_service import OllamaService
    import hashlib
    from app.core.config import settings
    
    db = SessionLocal()
    
    try:
        document = db.query(Document).filter(Document.id == document_id).first()
        if not document:
            return
        
        pages = db.query(DocumentPage).filter(
            DocumentPage.document_id == document_id
        ).all()
        
        ollama_service = OllamaService()
        qdrant_service = QdrantService()
        
        points = []
        chunk_index = 0
        
        for page in pages:
            text = page.edited_text or page.corrected_text or page.ocr_text
            
            if not text:
                continue
            
            # Simple chunking
            chunks = [text[i:i+settings.CHUNK_SIZE] for i in range(0, len(text), settings.CHUNK_SIZE - settings.CHUNK_OVERLAP)]
            
            for chunk_text in chunks:
                # Generate embedding (synchronous version for Celery)
                import asyncio
                loop = asyncio.get_event_loop()
                embedding = loop.run_until_complete(ollama_service.generate_embedding(chunk_text))
                
                chunk_hash = hashlib.sha256(chunk_text.encode()).hexdigest()
                chunk = DocumentChunk(
                    document_id=document.id,
                    page_number=page.page_number,
                    chunk_index=chunk_index,
                    text=chunk_text,
                    chunk_hash=chunk_hash,
                    vector_id=f"{document.id}_{chunk_index}",
                )
                db.add(chunk)
                
                points.append({
                    "id": f"{document.id}_{chunk_index}",
                    "vector": embedding,
                    "payload": {
                        "doc_id": str(document.id),
                        "chunk_id": str(chunk.id),
                        "page": page.page_number,
                        "text": chunk_text,
                        "title": document.title or document.original_filename,
                        "source": document.source,
                    }
                })
                
                chunk_index += 1
        
        # Upsert to Qdrant
        if points:
            loop = asyncio.get_event_loop()
            loop.run_until_complete(qdrant_service.upsert_vectors(points))
        
        document.status = DocumentStatus.COMMITTED
        db.commit()
        
        logger.info("Document embedded", document_id=document_id, chunks=len(points))
        
    except Exception as e:
        logger.error("Document embedding failed", document_id=document_id, error=str(e))
        
        if document:
            document.status = DocumentStatus.FAILED
            document.error_message = str(e)
            db.commit()
    
    finally:
        db.close()

