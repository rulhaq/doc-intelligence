"""Conversation Schemas"""
from pydantic import BaseModel, Field, field_serializer
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID


class ContextFilters(BaseModel):
    """Context filters for search"""
    source: Optional[List[str]] = None
    date_range: Optional[Dict[str, str]] = None
    tags: Optional[List[str]] = None
    confidence_min: Optional[float] = None


class MessageRequest(BaseModel):
    """Message request"""
    role: str = Field(..., description="Message role (user/assistant/system)")
    text: str = Field(..., description="Message text")
    context_filters: Optional[ContextFilters] = None


class Card(BaseModel):
    """Contextual card"""
    type: str = Field(..., description="Card type (document_snippet, action, etc.)")
    doc_id: Optional[str] = None
    title: Optional[str] = None
    snippet: Optional[str] = None
    cursor: Optional[int] = None
    score: Optional[float] = None
    action: Optional[str] = None
    label: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class MessageResponse(BaseModel):
    """Message response"""
    id: UUID
    conversation_id: UUID
    role: str
    text: str
    cards: Optional[List[Card]] = None
    sources: Optional[List[Dict[str, Any]]] = None
    tokens_used: Optional[int] = None
    inference_time_ms: Optional[int] = None
    created_at: datetime
    
    @field_serializer('id', 'conversation_id')
    def serialize_uuid(self, value: UUID) -> str:
        return str(value)
    
    class Config:
        from_attributes = True


class CreateConversationRequest(BaseModel):
    """Create conversation request"""
    title: str = Field(..., description="Conversation title")


class ConversationResponse(BaseModel):
    """Conversation response"""
    id: UUID
    user_id: UUID
    title: str
    created_at: datetime
    updated_at: datetime
    message_count: Optional[int] = 0
    
    @field_serializer('id', 'user_id')
    def serialize_uuid(self, value: UUID) -> str:
        return str(value)
    
    class Config:
        from_attributes = True


class ConversationDetailResponse(ConversationResponse):
    """Conversation with messages"""
    messages: List[MessageResponse] = []


class StreamChunk(BaseModel):
    """Streaming response chunk"""
    type: str = Field(..., description="Chunk type (token, card, metadata, done)")
    content: Optional[str] = None
    card: Optional[Card] = None
    metadata: Optional[Dict[str, Any]] = None

