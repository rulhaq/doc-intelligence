"""Conversation Endpoints"""
from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
import json
import time
import structlog

from app.core.database import get_db
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

logger = structlog.get_logger()
router = APIRouter()


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
    
    # If the message is empty, return a prompt message
    if not request.text or not request.text.strip():
        prompt_text = "It looks like you didn't ask a question. How can I help you? Please ask a question about the available documents."

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
        limit=10,  # Get more results for better context
        score_threshold=0.3,  # Lower threshold to include more relevant docs
        filters=search_filters,
    )
    
    logger.info(f"RAG Search: Found {len(search_results)} results for query: '{request.text[:50]}...'")
    
    # 2. Build context from search results
    context_docs = []
    cards = []
    sources = []
    
    for result in search_results:
        payload = result["payload"]
        context_docs.append(payload.get("text", ""))
        
        # Create card
        card = Card(
            type="document_snippet",
            doc_id=payload.get("doc_id"),
            title=payload.get("title", "Document"),
            snippet=payload.get("text", "")[:200],
            score=result["score"],
            metadata=payload,
        )
        cards.append(card)
        
        # Add to sources
        sources.append({
            "document_id": payload.get("doc_id"),
            "document_title": payload.get("title", "Document"),
            "chunk_id": payload.get("chunk_id"),
            "page_number": payload.get("page_number"),
            "similarity": result["score"],
        })
    
    # 3. Generate LLM response with multi-language support
    if not context_docs:
        # No relevant documents found
        logger.warning(f"No relevant documents found for query: '{request.text[:50]}...'")
        context_text = "No relevant documents found in the database."
        no_context_message = "I don't have any relevant documents to answer your question. Please upload documents first or ask a different question."
    else:
        # Number each context document for better reference
        numbered_context = []
        for i, doc in enumerate(context_docs, 1):
            numbered_context.append(f"[Document {i}]:\n{doc}")
        context_text = "\n\n".join(numbered_context)
        no_context_message = None
    
    # Detect if query is in Arabic or other RTL language
    is_arabic = any('\u0600' <= char <= '\u06FF' for char in request.text)
    
    if no_context_message:
        # No context available
        if is_arabic:
            assistant_text = "عذراً، لم أجد أي مستندات ذات صلة للإجابة على سؤالك. يرجى تحميل المستندات أولاً أو طرح سؤال مختلف."
        else:
            assistant_text = no_context_message
    elif is_arabic:
        system_prompt = """أنت مساعد ذكي متخصص في تحليل المستندات. قدم إجابات دقيقة ومفيدة باللغة العربية بناءً على المستندات المقدمة فقط.

**مهم جداً**: يجب أن تجيب دائماً باللغة العربية فقط، بغض النظر عن لغة المستندات. جميع إجاباتك يجب أن تكون باللغة العربية."""
        prompt = f"""المستندات المرجعية:
{context_text}

سؤال المستخدم: {request.text}

التعليمات:
1. أجب بناءً على المعلومات الموجودة في المستندات المرجعية فقط
2. إذا كانت المعلومات غير كافية، قل ذلك بوضوح
3. اذكر رقم المستند عند الإشارة إلى معلومات محددة
4. كن دقيقاً ومباشراً في إجابتك
5. **يجب أن تكون الإجابة باللغة العربية فقط**

الإجابة:"""
        assistant_text = await ollama_service.generate_completion(
            prompt=prompt,
            system_prompt=system_prompt
        )
    else:
        system_prompt = """You are an AI assistant specialized in document analysis. Provide accurate, helpful answers based ONLY on the provided context documents.

**IMPORTANT**: Always respond in the SAME LANGUAGE as the user's question. If the question is in English, respond in English. If in another language, respond in that language."""
        prompt = f"""Context documents:
{context_text}

User question: {request.text}

Instructions:
1. Answer based ONLY on information in the context documents above
2. If the context doesn't contain enough information, state that clearly
3. Reference document numbers when citing specific information (e.g., "According to Document 1...")
4. Be precise and direct in your answer
5. If multiple documents are relevant, synthesize the information
6. **Respond in the SAME LANGUAGE as the user's question (English)**

Answer:"""
        assistant_text = await ollama_service.generate_completion(
            prompt=prompt,
            system_prompt=system_prompt
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
            
            # Generate streaming response
            qdrant_service = QdrantService()
            ollama_service = OllamaService()
            
            # Search for context
            query_embedding = await ollama_service.generate_embedding(message_data["text"])
            search_results = await qdrant_service.search(
                query_vector=query_embedding,
                limit=5,
                score_threshold=0.5,
            )
            
            # Send cards first
            for result in search_results:
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
            
            # Build context and prompt with language detection
            context_docs = [r["payload"].get("text", "") for r in search_results]
            context_text = "\n\n".join(context_docs)
            
            # Detect if query is in Arabic
            user_text = message_data["text"]
            is_arabic = any('\u0600' <= char <= '\u06FF' for char in user_text)
            
            if is_arabic:
                system_prompt = """أنت مساعد ذكي متخصص في تحليل المستندات. قدم إجابات دقيقة ومفيدة باللغة العربية بناءً على المستندات المقدمة فقط.

**مهم جداً**: يجب أن تجيب دائماً باللغة العربية فقط، بغض النظر عن لغة المستندات. جميع إجاباتك يجب أن تكون باللغة العربية."""
                prompt = f"""المستندات المرجعية:
{context_text}

سؤال المستخدم: {user_text}

التعليمات:
1. أجب بناءً على المعلومات الموجودة في المستندات المرجعية فقط
2. إذا كانت المعلومات غير كافية، قل ذلك بوضوح
3. كن دقيقاً ومباشراً في إجابتك
4. **يجب أن تكون الإجابة باللغة العربية فقط**

الإجابة:"""
            else:
                system_prompt = """You are an AI assistant specialized in document analysis. Provide accurate, helpful answers based ONLY on the provided context documents.

**IMPORTANT**: Always respond in the SAME LANGUAGE as the user's question. If the question is in English, respond in English."""
                prompt = f"""Context documents:
{context_text}

User question: {user_text}

Instructions:
1. Answer based ONLY on information in the context documents above
2. If the context doesn't contain enough information, state that clearly
3. Be precise and direct in your answer
4. **Respond in the SAME LANGUAGE as the user's question (English)**

Answer:"""
            
            # Stream tokens with system prompt
            full_response = ""
            async for token in ollama_service.generate_completion_stream(prompt, system_prompt=system_prompt):
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

