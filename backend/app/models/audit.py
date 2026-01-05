"""Audit Log Model"""
from datetime import datetime
from sqlalchemy import Column, String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
import uuid

from app.core.database import Base


class AuditLog(Base):
    """Audit log for compliance"""
    __tablename__ = "audit_logs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Who
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    username = Column(String, nullable=True)
    
    # What
    action = Column(String, nullable=False)  # e.g., document.upload, document.commit, message.send
    resource_type = Column(String, nullable=True)  # e.g., document, conversation, agent
    resource_id = Column(String, nullable=True)
    
    # Details
    details = Column(JSON, nullable=True)
    
    # When & Where
    ip_address = Column(String, nullable=True)
    user_agent = Column(String, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    def __repr__(self):
        return f"<AuditLog {self.action} by {self.username} at {self.created_at}>"

