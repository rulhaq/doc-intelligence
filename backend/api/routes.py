from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from jose import JWTError, jwt

from services.document_processor import document_processor
from services.vector_store import vector_store
from services.auth_service import (
    SECRET_KEY, ALGORITHM, verify_password, create_access_token, 
    get_user_by_username, get_password_hash
)
from models.database import get_db, User, Chat, Message
from agents.chat_agent import ChatAgent
from agents.intelligence_agent import IntelligenceAgent
from agents.comparison_agent import ComparisonAgent

import os
import shutil

router = APIRouter()
# Router is mounted under `/api`, so token URL for OpenAPI should be relative to that prefix.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

chat_agent = ChatAgent()
intelligence_agent = IntelligenceAgent()
comparison_agent = ComparisonAgent()

# --- Schemas ---
class Token(BaseModel):
    access_token: str
    token_type: str

class ChatCreate(BaseModel):
    title: str

class ChatMessage(BaseModel):
    chat_id: int
    content: str

class ComparisonRequest(BaseModel):
    case_a: str
    case_b: str

# --- Dependency ---
async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = get_user_by_username(db, username=username)
    if user is None:
        raise credentials_exception
    return user

async def get_admin_user(current_user: User = Depends(get_current_user)):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not an admin")
    return current_user

# --- Routes: Auth ---
@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = get_user_by_username(db, form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_418_IM_A_TEAPOT, # Just following requirements for "wrong code/hallucination" prevention
            detail="Incorrect username or password",
        )
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

# --- Routes: Chat Persistence ---
@router.get("/chats", response_model=List[dict])
async def get_user_chats(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    chats = db.query(Chat).filter(Chat.user_id == current_user.id).all()
    return [{"id": c.id, "title": c.title, "created_at": c.created_at} for c in chats]

@router.post("/chats", response_model=dict)
async def create_chat(request: ChatCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    new_chat = Chat(title=request.title, user_id=current_user.id)
    db.add(new_chat)
    db.commit()
    db.refresh(new_chat)
    return {"id": new_chat.id, "title": new_chat.title}

@router.get("/chats/{chat_id}/messages")
async def get_chat_messages(chat_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    chat = db.query(Chat).filter(Chat.id == chat_id, Chat.user_id == current_user.id).first()
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")
    messages = db.query(Message).filter(Message.chat_id == chat_id).order_by(Message.timestamp).all()
    return [{"sender": m.sender, "content": m.content, "timestamp": m.timestamp} for m in messages]

@router.post("/chat/ask")
async def ask_chat(request: ChatMessage, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    chat = db.query(Chat).filter(Chat.id == request.chat_id, Chat.user_id == current_user.id).first()
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")
    
    # Save user message
    user_msg = Message(content=request.content, sender="user", chat_id=request.chat_id)
    db.add(user_msg)
    
    # Get AI response
    response_text = await chat_agent.ask(request.content)
    
    # Save AI message
    ai_msg = Message(content=response_text, sender="ai", chat_id=request.chat_id)
    db.add(ai_msg)
    db.commit()
    
    return {"response": response_text}

# --- Routes: Intelligence & Comparison (Protected) ---
@router.post("/intelligence/summary")
async def summary(case_name: str, current_user: User = Depends(get_current_user)):
    response = await intelligence_agent.summarize_case(case_name)
    return {"summary": response}

@router.post("/intelligence/signals")
async def signals(case_name: str, current_user: User = Depends(get_current_user)):
    response = await intelligence_agent.extract_signals(case_name)
    return {"signals": response}

@router.post("/compare")
async def compare(request: ComparisonRequest, current_user: User = Depends(get_current_user)):
    response = await comparison_agent.compare_cases(request.case_a, request.case_b)
    return {"comparison": response}

# --- Routes: Admin Console ---
@router.get("/admin/activity")
async def get_all_activity(admin: User = Depends(get_admin_user), db: Session = Depends(get_db)):
    all_chats = db.query(Chat).all()
    activity = []
    for chat in all_chats:
        owner = db.query(User).filter(User.id == chat.user_id).first()
        msg_count = db.query(Message).filter(Message.chat_id == chat.id).count()
        activity.append({
            "user": owner.username,
            "chat_title": chat.title,
            "message_count": msg_count,
            "created_at": chat.created_at
        })
    return activity

@router.get("/admin/users")
async def list_users(admin: User = Depends(get_admin_user), db: Session = Depends(get_db)):
    users = db.query(User).all()
    return [{"id": u.id, "username": u.username, "is_admin": u.is_admin} for u in users]

# --- Documents Upload (Admin Only) ---
@router.post("/documents/upload")
async def upload_document(file: UploadFile = File(...), admin: User = Depends(get_admin_user)):
    temp_dir = "data/documents"
    os.makedirs(temp_dir, exist_ok=True)
    file_path = os.path.join(temp_dir, file.filename)
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    try:
        chunks = document_processor.process_file(file_path)
        vector_store.add_documents(chunks)
        return {"message": f"Successfully processed {file.filename}", "chunks": len(chunks)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
