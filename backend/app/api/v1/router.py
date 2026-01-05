"""API v1 Router"""
from fastapi import APIRouter

from app.api.v1.endpoints import (
    auth,
    conversations,
    documents,
    agents,
    search,
    admin,
)

api_router = APIRouter()

# Include routers
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(conversations.router, prefix="/conversations", tags=["conversations"])
api_router.include_router(documents.router, prefix="/admin/documents", tags=["admin"])
api_router.include_router(admin.router, prefix="/admin", tags=["admin"])
api_router.include_router(agents.router, prefix="/agents", tags=["agents"])
api_router.include_router(search.router, prefix="/search", tags=["search"])

