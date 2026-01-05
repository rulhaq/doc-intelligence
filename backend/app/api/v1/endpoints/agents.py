"""Agent Management Endpoints"""
from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, BackgroundTasks
from sqlalchemy.orm import Session
import structlog

from app.core.database import get_db
from app.core.security import get_current_active_user, require_role
from app.core.exceptions import NotFoundException
from app.models.user import User
from app.models.agent import Agent, AgentTask, AgentStatus, TaskStatus
from app.schemas.agent import (
    CreateAgentRequest,
    AgentResponse,
    RunAgentTaskRequest,
    AgentTaskResponse,
    AgentStatusResponse,
)

logger = structlog.get_logger()
router = APIRouter()


@router.post("", response_model=AgentResponse)
async def create_agent(
    request: CreateAgentRequest,
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db),
):
    """Register new agent"""
    agent = Agent(
        name=request.name,
        agent_type=request.agent_type,
        description=request.description,
        config=request.config,
        mcp_server_url=request.mcp_server_url,
        mcp_enabled=request.mcp_enabled,
        execution_timeout=request.execution_timeout,
        max_concurrent_tasks=request.max_concurrent_tasks,
        created_by=current_user.id,
    )
    
    db.add(agent)
    db.commit()
    db.refresh(agent)
    
    logger.info("Agent created", agent_id=str(agent.id), name=agent.name)
    
    return AgentResponse.model_validate(agent)


@router.get("", response_model=List[AgentResponse])
async def list_agents(
    current_user: User = Depends(require_role("viewer")),
    db: Session = Depends(get_db),
):
    """List agents"""
    agents = db.query(Agent).filter(Agent.status == AgentStatus.ACTIVE).all()
    return [AgentResponse.model_validate(agent) for agent in agents]


@router.get("/{agent_id}", response_model=AgentResponse)
async def get_agent(
    agent_id: UUID,
    current_user: User = Depends(require_role("viewer")),
    db: Session = Depends(get_db),
):
    """Get agent details"""
    agent = db.query(Agent).filter(Agent.id == agent_id).first()
    
    if not agent:
        raise NotFoundException("Agent not found")
    
    return AgentResponse.model_validate(agent)


@router.post("/{agent_id}/run", response_model=AgentTaskResponse)
async def run_agent_task(
    agent_id: UUID,
    request: RunAgentTaskRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(require_role("editor")),
    db: Session = Depends(get_db),
):
    """Run agent task"""
    agent = db.query(Agent).filter(Agent.id == agent_id).first()
    
    if not agent:
        raise NotFoundException("Agent not found")
    
    if agent.status != AgentStatus.ACTIVE:
        raise Exception("Agent is not active")
    
    # Create task
    task = AgentTask(
        agent_id=agent.id,
        task_type=request.task_type,
        parameters=request.parameters,
        created_by=current_user.id,
    )
    
    db.add(task)
    db.commit()
    db.refresh(task)
    
    # Execute task in background
    async def execute_task():
        from datetime import datetime
        import time
        
        try:
            task_db = db.query(AgentTask).filter(AgentTask.id == task.id).first()
            task_db.status = TaskStatus.RUNNING
            task_db.started_at = datetime.utcnow()
            db.commit()
            
            start_time = time.time()
            
            # Execute agent task (placeholder - implement actual agent logic)
            from app.services.agents.agent_executor import AgentExecutor
            executor = AgentExecutor()
            result = await executor.execute(agent, request.task_type, request.parameters)
            
            execution_time = int((time.time() - start_time) * 1000)
            
            task_db.status = TaskStatus.COMPLETED
            task_db.result = result
            task_db.completed_at = datetime.utcnow()
            task_db.execution_time_ms = execution_time
            db.commit()
            
            logger.info("Agent task completed", task_id=str(task.id))
            
        except Exception as e:
            logger.error("Agent task failed", task_id=str(task.id), error=str(e))
            
            task_db = db.query(AgentTask).filter(AgentTask.id == task.id).first()
            task_db.status = TaskStatus.FAILED
            task_db.error_message = str(e)
            task_db.completed_at = datetime.utcnow()
            db.commit()
    
    background_tasks.add_task(execute_task)
    
    return AgentTaskResponse.model_validate(task)


@router.get("/{agent_id}/status", response_model=AgentStatusResponse)
async def get_agent_status(
    agent_id: UUID,
    current_user: User = Depends(require_role("viewer")),
    db: Session = Depends(get_db),
):
    """Get agent status"""
    agent = db.query(Agent).filter(Agent.id == agent_id).first()
    
    if not agent:
        raise NotFoundException("Agent not found")
    
    # Count tasks
    active_tasks = db.query(AgentTask).filter(
        AgentTask.agent_id == agent_id,
        AgentTask.status == TaskStatus.RUNNING,
    ).count()
    
    completed_tasks = db.query(AgentTask).filter(
        AgentTask.agent_id == agent_id,
        AgentTask.status == TaskStatus.COMPLETED,
    ).count()
    
    failed_tasks = db.query(AgentTask).filter(
        AgentTask.agent_id == agent_id,
        AgentTask.status == TaskStatus.FAILED,
    ).count()
    
    return AgentStatusResponse(
        agent_id=str(agent_id),
        status=agent.status.value,
        active_tasks=active_tasks,
        completed_tasks=completed_tasks,
        failed_tasks=failed_tasks,
    )


@router.get("/{agent_id}/tasks", response_model=List[AgentTaskResponse])
async def list_agent_tasks(
    agent_id: UUID,
    status: str = None,
    limit: int = 50,
    current_user: User = Depends(require_role("viewer")),
    db: Session = Depends(get_db),
):
    """List agent tasks"""
    query = db.query(AgentTask).filter(AgentTask.agent_id == agent_id)
    
    if status:
        query = query.filter(AgentTask.status == status)
    
    tasks = query.order_by(AgentTask.created_at.desc()).limit(limit).all()
    
    return [AgentTaskResponse.model_validate(task) for task in tasks]


@router.delete("/{agent_id}")
async def delete_agent(
    agent_id: UUID,
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db),
):
    """Delete agent"""
    agent = db.query(Agent).filter(Agent.id == agent_id).first()
    
    if not agent:
        raise NotFoundException("Agent not found")
    
    db.delete(agent)
    db.commit()
    
    logger.info("Agent deleted", agent_id=str(agent_id))
    
    return {"message": "Agent deleted"}

