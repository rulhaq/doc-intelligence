"""Search Schemas"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any


class SearchRequest(BaseModel):
    """Semantic search request"""
    query: str = Field(..., description="Search query")
    limit: int = Field(10, ge=1, le=100, description="Max results")
    score_threshold: Optional[float] = Field(None, ge=0.0, le=1.0)
    filters: Optional[Dict[str, Any]] = None


class SearchResult(BaseModel):
    """Search result"""
    doc_id: str
    chunk_id: str
    score: float
    text: str
    page: Optional[int]
    source: Optional[str]
    metadata: Optional[Dict[str, Any]]


class SearchResponse(BaseModel):
    """Search response"""
    query: str
    results: List[SearchResult]
    total: int
    search_time_ms: int

