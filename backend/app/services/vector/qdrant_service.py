"""Qdrant Vector Database Service"""
from typing import List, Dict, Any, Optional
from qdrant_client import QdrantClient
from qdrant_client.http.exceptions import UnexpectedResponse
from qdrant_client.models import (
    Distance,
    VectorParams,
    PointStruct,
    Filter,
    FieldCondition,
    MatchValue,
    Range,
)
import structlog

from app.core.config import settings
from app.core.exceptions import ServiceUnavailableException

logger = structlog.get_logger()


class QdrantService:
    """Qdrant vector database service"""
    
    def __init__(self):
        self.client = QdrantClient(
            url=settings.QDRANT_URL,
            api_key=settings.QDRANT_API_KEY,
            timeout=settings.QDRANT_TIMEOUT,
        )
        self.collection_name = settings.QDRANT_COLLECTION_NAME
    
    async def initialize_collections(self):
        """Initialize Qdrant collections"""
        try:
            # Check if collection exists
            collections = self.client.get_collections().collections
            collection_names = [c.name for c in collections]
            
            if self.collection_name not in collection_names:
                logger.info(f"Creating Qdrant collection: {self.collection_name}")
                
                try:
                    self.client.create_collection(
                        collection_name=self.collection_name,
                        vectors_config=VectorParams(
                            size=settings.EMBEDDING_DIMENSION,
                            distance=Distance.COSINE,
                        ),
                    )
                except UnexpectedResponse as exc:
                    if exc.status_code == 409:
                        logger.info(
                            f"Qdrant collection already exists (race): {self.collection_name}"
                        )
                    else:
                        raise
                
                # Create indexes for faster filtering
                for field_name, field_schema in (
                    ("doc_id", "keyword"),
                    ("source", "keyword"),
                    ("page", "integer"),
                ):
                    try:
                        self.client.create_payload_index(
                            collection_name=self.collection_name,
                            field_name=field_name,
                            field_schema=field_schema,
                        )
                    except UnexpectedResponse as exc:
                        if exc.status_code == 409:
                            logger.info(
                                f"Qdrant index already exists (race): {field_name}"
                            )
                        else:
                            raise
                
                logger.info(f"Qdrant collection created: {self.collection_name}")
            else:
                logger.info(f"Qdrant collection already exists: {self.collection_name}")
                
        except Exception as e:
            logger.error(f"Failed to initialize Qdrant collections: {e}")
            raise ServiceUnavailableException(f"Qdrant initialization failed: {e}")
    
    async def upsert_vectors(
        self,
        points: List[Dict[str, Any]],
    ) -> bool:
        """
        Upsert vectors to Qdrant
        
        Args:
            points: List of points with id, vector, payload
        """
        try:
            qdrant_points = [
                PointStruct(
                    id=point["id"],
                    vector=point["vector"],
                    payload=point["payload"],
                )
                for point in points
            ]
            
            self.client.upsert(
                collection_name=self.collection_name,
                points=qdrant_points,
            )
            
            logger.info(f"Upserted {len(points)} vectors to Qdrant")
            return True
            
        except Exception as e:
            logger.error(f"Failed to upsert vectors: {e}")
            raise ServiceUnavailableException(f"Vector upsert failed: {e}")
    
    async def search(
        self,
        query_vector: List[float],
        limit: int = 10,
        score_threshold: Optional[float] = None,
        filters: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Semantic search
        
        Args:
            query_vector: Query embedding vector
            limit: Maximum number of results
            score_threshold: Minimum similarity score
            filters: Metadata filters
        """
        try:
            # Build filter
            qdrant_filter = None
            if filters:
                conditions = []
                
                if "source" in filters and filters["source"]:
                    conditions.append(
                        FieldCondition(
                            key="source",
                            match=MatchValue(value=filters["source"]),
                        )
                    )
                
                if "doc_id" in filters and filters["doc_id"]:
                    conditions.append(
                        FieldCondition(
                            key="doc_id",
                            match=MatchValue(value=filters["doc_id"]),
                        )
                    )
                
                if "page" in filters and filters["page"] is not None:
                    conditions.append(
                        FieldCondition(
                            key="page",
                            match=MatchValue(value=filters["page"]),
                        )
                    )
                
                if conditions:
                    qdrant_filter = Filter(must=conditions)
            
            # Search
            results = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_vector,
                limit=limit,
                score_threshold=score_threshold,
                query_filter=qdrant_filter,
            )
            
            # Format results
            formatted_results = [
                {
                    "id": str(result.id),
                    "score": result.score,
                    "payload": result.payload,
                }
                for result in results
            ]
            
            logger.info(f"Found {len(formatted_results)} results from Qdrant search")
            return formatted_results
            
        except Exception as e:
            logger.error(f"Qdrant search failed: {e}")
            raise ServiceUnavailableException(f"Vector search failed: {e}")
    
    async def delete_by_doc_id(self, doc_id: str) -> bool:
        """Delete all vectors for a document"""
        try:
            self.client.delete(
                collection_name=self.collection_name,
                points_selector=Filter(
                    must=[
                        FieldCondition(
                            key="doc_id",
                            match=MatchValue(value=doc_id),
                        )
                    ]
                ),
            )
            logger.info(f"Deleted vectors for document: {doc_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete vectors: {e}")
            return False
    
    async def get_collection_info(self) -> Dict[str, Any]:
        """Get collection information"""
        try:
            info = self.client.get_collection(self.collection_name)
            return {
                "name": info.config.name if hasattr(info.config, 'name') else self.collection_name,
                "vectors_count": info.vectors_count,
                "points_count": info.points_count,
                "status": info.status,
            }
        except Exception as e:
            logger.error(f"Failed to get collection info: {e}")
            return {}

