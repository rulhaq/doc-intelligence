"""Search Endpoints"""
from fastapi import APIRouter, Depends
import time
import structlog

from app.core.security import get_current_active_user
from app.models.user import User
from app.schemas.search import SearchRequest, SearchResponse, SearchResult
from app.services.vector.qdrant_service import QdrantService
from app.services.inference.ollama_service import OllamaService

logger = structlog.get_logger()
router = APIRouter()


@router.post("", response_model=SearchResponse)
async def semantic_search(
    request: SearchRequest,
    current_user: User = Depends(get_current_active_user),
):
    """Semantic search across documents"""
    start_time = time.time()
    
    # Generate query embedding
    ollama_service = OllamaService()
    query_embedding = await ollama_service.generate_embedding(request.query)
    
    # Search Qdrant
    qdrant_service = QdrantService()
    results = await qdrant_service.search(
        query_vector=query_embedding,
        limit=request.limit,
        score_threshold=request.score_threshold,
        filters=request.filters,
    )
    
    search_time = int((time.time() - start_time) * 1000)
    
    # Format results
    search_results = [
        SearchResult(
            doc_id=result["payload"].get("doc_id", ""),
            chunk_id=result["id"],
            score=result["score"],
            text=result["payload"].get("text", ""),
            page=result["payload"].get("page"),
            source=result["payload"].get("source"),
            metadata=result["payload"],
        )
        for result in results
    ]
    
    logger.info(
        "Search completed",
        query=request.query,
        results_count=len(search_results),
        search_time_ms=search_time,
    )
    
    return SearchResponse(
        query=request.query,
        results=search_results,
        total=len(search_results),
        search_time_ms=search_time,
    )

