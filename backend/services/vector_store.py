import os
import uuid
from qdrant_client import QdrantClient
from qdrant_client.http import models
from typing import List, Dict, Any

from services.embedding_service import embedding_service

class VectorStoreService:
    def __init__(self, host: str = "localhost", port: int = 6333):
        self.client = QdrantClient(host=host, port=port)
        self.collection_name = "legal_docs"
        self.embedding_dim = None  # type: int | None

    def _ensure_collection(self, vector_size: int):
        collections = self.client.get_collections().collections
        exists = any(c.name == self.collection_name for c in collections)
        
        if not exists:
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=models.VectorParams(
                    size=vector_size,
                    distance=models.Distance.COSINE
                )
            )

    def add_documents(self, documents: List[Dict[str, Any]]):
        if not documents:
            return

        embeddings = embedding_service.embed([doc["content"] for doc in documents])
        if not embeddings:
            return

        if self.embedding_dim is None:
            self.embedding_dim = len(embeddings[0])
            self._ensure_collection(self.embedding_dim)

        points = []
        for doc, embedding in zip(documents, embeddings):
            points.append(
                models.PointStruct(
                    id=str(uuid.uuid4()),
                    vector=embedding,
                    payload=doc
                )
            )
        
        self.client.upsert(
            collection_name=self.collection_name,
            points=points
        )

    def search(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        embeddings = embedding_service.embed([query])
        if not embeddings:
            return []

        query_vector = embeddings[0]
        if self.embedding_dim is None:
            self.embedding_dim = len(query_vector)
            self._ensure_collection(self.embedding_dim)
        
        results = self.client.search(
            collection_name=self.collection_name,
            query_vector=query_vector,
            limit=limit
        )
        
        return [res.payload for res in results]

# Global instance
vector_store = VectorStoreService(
    host=os.getenv("QDRANT_HOST", "localhost"),
    port=int(os.getenv("QDRANT_PORT", 6333))
)
