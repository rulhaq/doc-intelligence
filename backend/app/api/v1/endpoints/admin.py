"""Admin Management Endpoints"""
from typing import List, Dict, Any
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import structlog
import httpx

from app.core.database import get_db
from app.core.security import get_current_active_user, require_role, hash_password
from app.core.config import settings
from app.core.exceptions import NotFoundException, ConflictException
from app.models.user import User, UserRole
from app.schemas.auth import UserResponse
from pydantic import BaseModel, EmailStr

logger = structlog.get_logger()
router = APIRouter()


# Schemas
class CreateUserRequest(BaseModel):
    username: str
    email: EmailStr
    password: str
    role: str = "VIEWER"
    is_active: bool = True


class UpdateUserRequest(BaseModel):
    role: str
    is_active: bool


class SystemStatsResponse(BaseModel):
    total_users: int
    total_documents: int
    total_conversations: int
    total_vectors: int
    storage_used_bytes: int
    ollama_status: str
    qdrant_status: str
    available_models: List[str]


# User Management
@router.get("/users", response_model=List[UserResponse])
async def list_users(
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db),
):
    """List all users (admin only)"""
    users = db.query(User).all()
    return [UserResponse.model_validate(user) for user in users]


@router.post("/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    request: CreateUserRequest,
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db),
):
    """Create a new user (admin only)"""
    # Check if user exists
    existing_user = db.query(User).filter(
        (User.username == request.username) | (User.email == request.email)
    ).first()
    
    if existing_user:
        raise ConflictException("User with this username or email already exists")
    
    # Validate role
    try:
        role = UserRole[request.role.upper()]
    except KeyError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid role. Must be one of: {', '.join([r.name for r in UserRole])}"
        )
    
    # Create user
    user = User(
        email=request.email,
        username=request.username,
        hashed_password=hash_password(request.password),
        role=role,
        auth_provider="local",
        is_active=request.is_active,
        is_verified=True,  # Admin-created users are pre-verified
    )
    
    db.add(user)
    db.commit()
    db.refresh(user)
    
    logger.info("User created by admin", user_id=str(user.id), username=user.username, created_by=str(current_user.id))
    
    return UserResponse.model_validate(user)


@router.put("/users/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: UUID,
    request: UpdateUserRequest,
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db),
):
    """Update user (admin only)"""
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise NotFoundException("User not found")
    
    # Prevent self-demotion
    if user.id == current_user.id and request.role != "ADMIN":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot change your own admin role"
        )
    
    # Validate and update role
    try:
        user.role = UserRole[request.role.upper()]
    except KeyError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid role. Must be one of: {', '.join([r.name for r in UserRole])}"
        )
    
    user.is_active = request.is_active
    
    db.commit()
    db.refresh(user)
    
    logger.info("User updated by admin", user_id=str(user.id), updated_by=str(current_user.id))
    
    return UserResponse.model_validate(user)


@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: UUID,
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db),
):
    """Delete user (admin only)"""
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise NotFoundException("User not found")
    
    # Prevent self-deletion
    if user.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete your own account"
        )
    
    db.delete(user)
    db.commit()
    
    logger.info("User deleted by admin", user_id=str(user_id), deleted_by=str(current_user.id))
    
    return None


# System Statistics
@router.get("/stats", response_model=SystemStatsResponse)
async def get_system_stats(
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db),
):
    """Get real-time system statistics"""
    from app.models.document import Document
    from app.models.conversation import Conversation
    
    # Count users
    total_users = db.query(User).count()
    
    # Count documents
    total_documents = db.query(Document).count()
    
    # Count conversations
    total_conversations = db.query(Conversation).count()
    
    # Get Qdrant stats
    total_vectors = 0
    qdrant_status = "unknown"
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{settings.QDRANT_URL}/collections/{settings.QDRANT_COLLECTION_NAME}")
            if response.status_code == 200:
                data = response.json()
                total_vectors = data.get("result", {}).get("points_count", 0)
                qdrant_status = "healthy"
            else:
                qdrant_status = "error"
    except Exception as e:
        logger.error("Failed to get Qdrant stats", error=str(e))
        qdrant_status = "unreachable"
    
    # Get Ollama models
    available_models = []
    ollama_status = "unknown"
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{settings.OLLAMA_BASE_URL}/api/tags")
            if response.status_code == 200:
                data = response.json()
                available_models = [model["name"] for model in data.get("models", [])]
                ollama_status = "healthy"
            else:
                ollama_status = "error"
    except Exception as e:
        logger.error("Failed to get Ollama models", error=str(e))
        ollama_status = "unreachable"
    
    # Get storage stats (simplified - you'd integrate with MinIO properly)
    storage_used_bytes = 0  # Placeholder - implement MinIO stats if needed
    
    return SystemStatsResponse(
        total_users=total_users,
        total_documents=total_documents,
        total_conversations=total_conversations,
        total_vectors=total_vectors,
        storage_used_bytes=storage_used_bytes,
        ollama_status=ollama_status,
        qdrant_status=qdrant_status,
        available_models=available_models,
    )


# Available LLM Models
@router.get("/ollama/models")
async def get_ollama_models(
    current_user: User = Depends(require_role("admin")),
):
    """Get list of available Ollama models"""
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(f"{settings.OLLAMA_BASE_URL}/api/tags")
            if response.status_code == 200:
                data = response.json()
                models = []
                for model in data.get("models", []):
                    models.append({
                        "name": model["name"],
                        "size": model.get("size", 0),
                        "modified_at": model.get("modified_at", ""),
                        "details": model.get("details", {}),
                    })
                return {"models": models, "status": "healthy"}
            else:
                return {"models": [], "status": "error", "message": "Failed to fetch models"}
    except Exception as e:
        logger.error("Failed to get Ollama models", error=str(e))
        return {"models": [], "status": "unreachable", "message": str(e)}


# System Health
@router.get("/health")
async def get_system_health(
    current_user: User = Depends(require_role("admin")),
):
    """Check health of all services"""
    services = {}
    
    # Check Ollama
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{settings.OLLAMA_BASE_URL}/api/tags")
            services["ollama"] = "healthy" if response.status_code == 200 else "error"
    except:
        services["ollama"] = "unreachable"
    
    # Check Qdrant
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{settings.QDRANT_URL}/collections")
            services["qdrant"] = "healthy" if response.status_code == 200 else "error"
    except:
        services["qdrant"] = "unreachable"
    
    # Check Redis
    try:
        from redis import Redis
        r = Redis.from_url(settings.REDIS_URL, socket_connect_timeout=5)
        r.ping()
        services["redis"] = "healthy"
    except:
        services["redis"] = "unreachable"
    
    # Database is already healthy if we got here
    services["database"] = "healthy"
    
    return {"services": services, "overall": "healthy" if all(s in ["healthy", "error"] for s in services.values()) else "degraded"}


