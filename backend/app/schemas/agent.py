"""Agent Schemas"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class CreateAgentRequest(BaseModel):
    """Create agent request"""
    name: str = Field(..., description="Agent name")
    agent_type: str = Field(..., description="Agent type")
    description: Optional[str] = None
    config: Dict[str, Any] = Field(..., description="Agent configuration")
    mcp_server_url: Optional[str] = None
    mcp_enabled: bool = False
    execution_timeout: int = 300
    max_concurrent_tasks: int = 1


class AgentResponse(BaseModel):
    """Agent response"""
    id: str
    name: str
    agent_type: str
    description: Optional[str]
    status: str
    mcp_enabled: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class RunAgentTaskRequest(BaseModel):
    """Run agent task request"""
    task_type: str = Field(..., description="Task type")
    parameters: Dict[str, Any] = Field(..., description="Task parameters")


class AgentTaskResponse(BaseModel):
    """Agent task response"""
    id: str
    agent_id: str
    task_type: str
    status: str
    result: Optional[Dict[str, Any]]
    error_message: Optional[str]
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    execution_time_ms: Optional[int]
    created_at: datetime
    
    class Config:
        from_attributes = True


class AgentStatusResponse(BaseModel):
    """Agent status response"""
    agent_id: str
    status: str
    active_tasks: int
    completed_tasks: int
    failed_tasks: int

