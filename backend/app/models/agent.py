"""Agent Models"""
from datetime import datetime
from sqlalchemy import Column, String, Text, DateTime, ForeignKey, JSON, Integer, Enum, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
import enum

from app.core.database import Base


class AgentType(str, enum.Enum):
    """Agent types"""
    WEB_SCRAPER = "web_scraper"
    FILE_CONNECTOR = "file_connector"
    API_CONNECTOR = "api_connector"
    DATABASE_CONNECTOR = "database_connector"
    CUSTOM = "custom"


class AgentStatus(str, enum.Enum):
    """Agent status"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    ERROR = "error"


class TaskStatus(str, enum.Enum):
    """Task status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class Agent(Base):
    """Agent model"""
    __tablename__ = "agents"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    name = Column(String, nullable=False)
    agent_type = Column(Enum(AgentType), nullable=False)
    description = Column(Text, nullable=True)
    
    # Configuration
    config = Column(JSON, nullable=False)  # Agent-specific configuration
    
    # MCP settings
    mcp_server_url = Column(String, nullable=True)
    mcp_enabled = Column(Boolean, default=False)
    
    # Status
    status = Column(Enum(AgentStatus), default=AgentStatus.ACTIVE, nullable=False)
    
    # Execution limits
    execution_timeout = Column(Integer, default=300)
    max_concurrent_tasks = Column(Integer, default=1)
    
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    tasks = relationship("AgentTask", back_populates="agent", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Agent {self.name} ({self.agent_type})>"


class AgentTask(Base):
    """Agent task execution"""
    __tablename__ = "agent_tasks"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    agent_id = Column(UUID(as_uuid=True), ForeignKey("agents.id"), nullable=False)
    
    # Task details
    task_type = Column(String, nullable=False)
    parameters = Column(JSON, nullable=False)
    
    # Status
    status = Column(Enum(TaskStatus), default=TaskStatus.PENDING, nullable=False)
    
    # Results
    result = Column(JSON, nullable=True)
    error_message = Column(Text, nullable=True)
    
    # Timing
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    execution_time_ms = Column(Integer, nullable=True)
    
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    agent = relationship("Agent", back_populates="tasks")
    
    def __repr__(self):
        return f"<AgentTask {self.id}: {self.task_type} ({self.status})>"

