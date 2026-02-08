import os
import time
from urllib.parse import quote_plus
from sqlalchemy import create_engine, Column, Integer, String, Text, ForeignKey, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.exc import OperationalError
from datetime import datetime
from passlib.context import CryptContext

def _env_bool(name: str, default: bool) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "y", "on"}


def _build_database_url() -> str:
    explicit = os.getenv("DATABASE_URL")
    if explicit and explicit.strip():
        return explicit.strip()

    # Standard Postgres envs used by postgres images / OpenShift templates.
    host = os.getenv("POSTGRES_HOST") or os.getenv("PGHOST") or "postgres"
    port = os.getenv("POSTGRES_PORT") or os.getenv("PGPORT") or "5432"
    db = os.getenv("POSTGRES_DB") or os.getenv("PGDATABASE") or "qpp"
    user = os.getenv("POSTGRES_USER") or os.getenv("PGUSER") or "user"
    password = os.getenv("POSTGRES_PASSWORD") or os.getenv("PGPASSWORD") or "password"

    return f"postgresql://{user}:{quote_plus(password)}@{host}:{port}/{db}"


DATABASE_URL = _build_database_url()
engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_admin = Column(Boolean, default=False)
    chats = relationship("Chat", back_populates="owner")

class Chat(Base):
    __tablename__ = "chats"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    user_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("User", back_populates="chats")
    messages = relationship("Message", back_populates="chat")

class Message(Base):
    __tablename__ = "messages"
    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text)
    sender = Column(String) # 'user' or 'ai'
    timestamp = Column(DateTime, default=datetime.utcnow)
    chat_id = Column(Integer, ForeignKey("chats.id"))
    chat = relationship("Chat", back_populates="messages")

def init_db():
    max_retries = int(os.getenv("DB_INIT_MAX_RETRIES", "30"))
    sleep_seconds = float(os.getenv("DB_INIT_RETRY_SECONDS", "2"))

    last_error = None
    for attempt in range(1, max_retries + 1):
        try:
            Base.metadata.create_all(bind=engine)
            last_error = None
            break
        except OperationalError as e:
            last_error = e
            time.sleep(sleep_seconds)

    if last_error is not None:
        raise last_error

    db = SessionLocal()
    # Optional seed user (use the dedicated seeding job/script in OpenShift instead).
    if _env_bool("SEED_DEFAULT_ADMIN", False):
        username = (os.getenv("SEED_DEFAULT_ADMIN_USERNAME") or "judge1").strip()
        password = (os.getenv("SEED_DEFAULT_ADMIN_PASSWORD") or "judge1234").strip()
        if username and not db.query(User).filter(User.username == username).first():
            hashed_pw = pwd_context.hash(password)
            admin_user = User(username=username, hashed_password=hashed_pw, is_admin=True)
            db.add(admin_user)
            db.commit()
    db.close()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
