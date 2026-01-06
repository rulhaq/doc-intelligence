"""Conversation Endpoints"""
from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
import json
import time
import structlog

from app.core.database import get_db
from app.core.config import settings
from app.core.guardrails import (
    detect_explicit_language,
    detect_language,
    is_ambiguous_language,
    is_greeting,
    is_illegal_request,
    greeting_response,
    illegal_request_response,
    insufficient_info_response,
    ambiguous_language_response,
    empty_message_response,
)
from app.core.security import get_current_active_user
from app.core.exceptions import NotFoundException, AuthorizationException
from app.models.user import User
from app.models.conversation import Conversation, Message
from app.schemas.conversation import (
    CreateConversationRequest,
    ConversationResponse,
    ConversationDetailResponse,
    MessageRequest,
    MessageResponse,
    Card,
)
from app.services.vector.qdrant_service import QdrantService
from app.services.inference.ollama_service import OllamaService
from app.core.prompts import SYSTEM_PROMPT

logger = structlog.get_logger()
router = APIRouter()


def _build_context(results: List[dict]) -> list[str]:
    context_docs = []
    for result in results:
        payload = result.get("payload") or {}
        text = payload.get("text", "")
        if not text:
            continue
        context_docs.append(text)
    return context_docs



@router.post("", response_model=ConversationResponse)
async def create_conversation(
    request: CreateConversationRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Create new conversation"""
    conversation = Conversation(
        user_id=current_user.id,
        title=request.title,
    )
    
    db.add(conversation)
    db.commit()
    db.refresh(conversation)
    
    logger.info("Conversation created", conversation_id=str(conversation.id))
    
    response = ConversationResponse.model_validate(conversation)
    response.message_count = 0
    return response


@router.get("", response_model=List[ConversationResponse])
async def list_conversations(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """List user's conversations"""
    conversations = db.query(Conversation).filter(
        Conversation.user_id == current_user.id
    ).order_by(Conversation.updated_at.desc()).all()
    
    result = []
    for conv in conversations:
        response = ConversationResponse.model_validate(conv)
        response.message_count = len(conv.messages)
        result.append(response)
    
    return result


@router.get("/{conversation_id}", response_model=ConversationDetailResponse)
async def get_conversation(
    conversation_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Get conversation with messages"""
    conversation = db.query(Conversation).filter(
        Conversation.id == conversation_id
    ).first()
    
    if not conversation:
        raise NotFoundException("Conversation not found")
    
    if conversation.user_id != current_user.id:
        raise AuthorizationException("Not authorized to access this conversation")
    
    # Build response
    response = ConversationDetailResponse.model_validate(conversation)
    response.message_count = len(conversation.messages)
    response.messages = [MessageResponse.model_validate(msg) for msg in conversation.messages]
    
    return response


@router.post("/{conversation_id}/message", response_model=MessageResponse)
async def send_message(
    conversation_id: UUID,
    request: MessageRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Send message in conversation (non-streaming)
    For streaming, use WebSocket endpoint
    """
    conversation = db.query(Conversation).filter(
        Conversation.id == conversation_id
    ).first()
    
    if not conversation:
        raise NotFoundException("Conversation not found")
    
    if conversation.user_id != current_user.id:
        raise AuthorizationException("Not authorized")
    
    # Save user message
    user_message = Message(
        conversation_id=conversation.id,
        role=request.role,
        text=request.text,
        context_filters=request.context_filters.model_dump() if request.context_filters else None,
    )
    db.add(user_message)
    db.commit()
    
    user_text = request.text or ""
    if not user_text.strip():
        response_lang = detect_language(user_text) or "en"
        prompt_text = empty_message_response(response_lang)

        assistant_message = Message(
            conversation_id=conversation.id,
            role="assistant",
            text=prompt_text,
            cards=[],
            sources=[],
            inference_time_ms=0,
        )
        db.add(assistant_message)
        db.commit()
        db.refresh(assistant_message)

        response = MessageResponse.model_validate(assistant_message)
        response.cards = []
        response.sources = []
        return response

    explicit_lang = detect_explicit_language(user_text)
    if not explicit_lang and is_ambiguous_language(user_text):
        prompt_text = ambiguous_language_response()
        assistant_message = Message(
            conversation_id=conversation.id,
            role="assistant",
            text=prompt_text,
            cards=[],
            sources=[],
            inference_time_ms=0,
        )
        db.add(assistant_message)
        db.commit()
        db.refresh(assistant_message)

        response = MessageResponse.model_validate(assistant_message)
        response.cards = []
        response.sources = []
        return response

    response_lang = explicit_lang or detect_language(user_text) or "en"

    if is_greeting(user_text):
        prompt_text = greeting_response(response_lang)
        assistant_message = Message(
            conversation_id=conversation.id,
            role="assistant",
            text=prompt_text,
            cards=[],
            sources=[],
            inference_time_ms=0,
        )
        db.add(assistant_message)
        db.commit()
        db.refresh(assistant_message)

        response = MessageResponse.model_validate(assistant_message)
        response.cards = []
        response.sources = []
        return response

    if is_illegal_request(user_text):
        prompt_text = illegal_request_response(response_lang)
        assistant_message = Message(
            conversation_id=conversation.id,
            role="assistant",
            text=prompt_text,
            cards=[],
            sources=[],
            inference_time_ms=0,
        )
        db.add(assistant_message)
        db.commit()
        db.refresh(assistant_message)

        response = MessageResponse.model_validate(assistant_message)
        response.cards = []
        response.sources = []
        return response

    # Generate response
    start_time = time.time()
    
    # 1. Search for relevant documents
    qdrant_service = QdrantService()
    ollama_service = OllamaService()
    
    # Generate query embedding
    query_embedding = await ollama_service.generate_embedding(request.text)
    
    # Search Qdrant with better parameters
    search_filters = {}
    if request.context_filters:
        if request.context_filters.source:
            search_filters["source"] = request.context_filters.source[0]  # First source

    search_results = await qdrant_service.search(
        query_vector=query_embedding,
        limit=10,
        score_threshold=None,
        filters=search_filters,
    )

    logger.info(f"RAG Search: Found {len(search_results)} results for query: '{request.text[:50]}...'")

    relevant_results = [
        result for result in search_results if result["score"] >= settings.MIN_SIMILARITY
    ]

    if not relevant_results:
        prompt_text = insufficient_info_response(response_lang)
        assistant_message = Message(
            conversation_id=conversation.id,
            role="assistant",
            text=prompt_text,
            cards=[],
            sources=[],
            inference_time_ms=0,
        )
        db.add(assistant_message)
        db.commit()
        db.refresh(assistant_message)

        response = MessageResponse.model_validate(assistant_message)
        response.cards = []
        response.sources = []
        return response

    context_docs = _build_context(relevant_results)
    if not context_docs:
        prompt_text = insufficient_info_response(response_lang)
        assistant_message = Message(
            conversation_id=conversation.id,
            role="assistant",
            text=prompt_text,
            cards=[],
            sources=[],
            inference_time_ms=0,
        )
        db.add(assistant_message)
        db.commit()
        db.refresh(assistant_message)

        response = MessageResponse.model_validate(assistant_message)
        response.cards = []
        response.sources = []
        return response

    cards = []
    sources = []
    for result in relevant_results:
        payload = result["payload"]
        card = Card(
            type="document_snippet",
            doc_id=payload.get("doc_id"),
            title=payload.get("title", "Document"),
            snippet=payload.get("text", "")[:200],
            score=result["score"],
            metadata=payload,
        )
        cards.append(card)

        sources.append({
            "document_id": payload.get("doc_id"),
            "document_title": payload.get("title", "Document"),
            "chunk_id": payload.get("chunk_id"),
            "page_number": payload.get("page_number") or payload.get("page"),
            "similarity": result["score"],
        })

    context_text = "\n\n".join(context_docs)
    language_instruction = "Respond in Arabic." if response_lang == "ar" else "Respond in English."

    prompt = f"""Context passages:
{context_text}

User question: {request.text}

Instructions:
- {language_instruction}
- Use only the provided context passages.
- If information is missing, say so and ask a precise follow-up question.

Answer:"""

    assistant_text = await ollama_service.generate_completion(
        prompt=prompt,
        system_prompt=SYSTEM_PROMPT,
    )

    inference_time = int((time.time() - start_time) * 1000)
    
    # Save assistant message
    assistant_message = Message(
        conversation_id=conversation.id,
        role="assistant",
        text=assistant_text,
        cards=[card.model_dump() for card in cards],
        sources=sources,
        inference_time_ms=inference_time,
    )
    db.add(assistant_message)
    db.commit()
    db.refresh(assistant_message)
    
    logger.info(
        "Message generated",
        conversation_id=str(conversation.id),
        inference_time_ms=inference_time,
    )
    
    response = MessageResponse.model_validate(assistant_message)
    response.cards = cards
    response.sources = sources
    return response


@router.delete("/{conversation_id}")
async def delete_conversation(
    conversation_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Delete conversation"""
    conversation = db.query(Conversation).filter(
        Conversation.id == conversation_id
    ).first()
    
    if not conversation:
        raise NotFoundException("Conversation not found")
    
    if conversation.user_id != current_user.id:
        raise AuthorizationException("Not authorized")
    
    db.delete(conversation)
    db.commit()
    
    logger.info("Conversation deleted", conversation_id=str(conversation_id))
    
    return {"message": "Conversation deleted"}


@router.websocket("/{conversation_id}/ws")
async def websocket_chat(
    websocket: WebSocket,
    conversation_id: UUID,
    token: str,
    db: Session = Depends(get_db),
):
    """
    WebSocket endpoint for streaming chat
    Usage: ws://host/api/v1/conversations/{id}/ws?token=<jwt_token>
    """
    await websocket.accept()
    
    try:
        # Verify token and get user
        from app.core.security import decode_token
        payload = decode_token(token)
        user_id = payload.get("sub")
        
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            await websocket.send_json({"error": "Unauthorized"})
            await websocket.close()
            return
        
        # Verify conversation access
        conversation = db.query(Conversation).filter(
            Conversation.id == conversation_id
        ).first()
        
        if not conversation or conversation.user_id != user.id:
            await websocket.send_json({"error": "Conversation not found"})
            await websocket.close()
            return
        
        logger.info("WebSocket connected", conversation_id=str(conversation_id))
        
        # Listen for messages
        while True:
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            # Save user message
            user_message = Message(
                conversation_id=conversation.id,
                role="user",
                text=message_data["text"],
            )
            db.add(user_message)
            db.commit()
            
            user_text = message_data.get("text", "")
            if not user_text.strip():
                response_lang = detect_language(user_text) or "en"
                prompt_text = empty_message_response(response_lang)
                await websocket.send_json({"type": "token", "content": prompt_text})
                await websocket.send_json({"type": "done"})
                continue

            explicit_lang = detect_explicit_language(user_text)
            if not explicit_lang and is_ambiguous_language(user_text):
                prompt_text = ambiguous_language_response()
                await websocket.send_json({"type": "token", "content": prompt_text})
                await websocket.send_json({"type": "done"})
                continue

            response_lang = explicit_lang or detect_language(user_text) or "en"

            if is_greeting(user_text):
                prompt_text = greeting_response(response_lang)
                await websocket.send_json({"type": "token", "content": prompt_text})
                await websocket.send_json({"type": "done"})
                continue

            if is_illegal_request(user_text):
                prompt_text = illegal_request_response(response_lang)
                await websocket.send_json({"type": "token", "content": prompt_text})
                await websocket.send_json({"type": "done"})
                continue

            # Generate streaming response
            qdrant_service = QdrantService()
            ollama_service = OllamaService()

            query_embedding = await ollama_service.generate_embedding(user_text)
            search_results = await qdrant_service.search(
                query_vector=query_embedding,
                limit=5,
                score_threshold=None,
            )

            relevant_results = [
                result for result in search_results if result["score"] >= settings.MIN_SIMILARITY
            ]

            if not relevant_results:
                prompt_text = insufficient_info_response(response_lang)
                await websocket.send_json({"type": "token", "content": prompt_text})
                await websocket.send_json({"type": "done"})
                continue

            context_docs = _build_context(relevant_results)
            if not context_docs:
                prompt_text = insufficient_info_response(response_lang)
                await websocket.send_json({"type": "token", "content": prompt_text})
                await websocket.send_json({"type": "done"})
                continue

            for result in relevant_results:
                payload = result["payload"]
                card = {
                    "type": "card",
                    "card": {
                        "type": "document_snippet",
                        "doc_id": payload.get("doc_id"),
                        "title": payload.get("title", "Document"),
                        "snippet": payload.get("text", "")[:200],
                        "score": result["score"],
                    }
                }
                await websocket.send_json(card)

            context_text = "\n\n".join(context_docs)
            language_instruction = "Respond in Arabic." if response_lang == "ar" else "Respond in English."

            prompt = f"""Context passages:
{context_text}

User question: {user_text}

Instructions:
- {language_instruction}
- Use only the provided context passages.
- If information is missing, say so and ask a precise follow-up question.

Answer:"""

            full_response = ""
            async for token in ollama_service.generate_completion_stream(prompt, system_prompt=SYSTEM_PROMPT):
                await websocket.send_json({"type": "token", "content": token})
                full_response += token

            # Send done signal
            await websocket.send_json({"type": "done"})
            # Save assistant message
            assistant_message = Message(
                conversation_id=conversation.id,
                role="assistant",
                text=full_response,
            )
            db.add(assistant_message)
            db.commit()
            
    except WebSocketDisconnect:
        logger.info("WebSocket disconnected", conversation_id=str(conversation_id))
    except Exception as e:
        logger.error("WebSocket error", error=str(e))
        await websocket.send_json({"error": str(e)})
    finally:
        await websocket.close()

