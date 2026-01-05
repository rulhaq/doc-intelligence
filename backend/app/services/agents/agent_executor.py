"""Agent Executor - Plugin Architecture"""
from typing import Dict, Any
import structlog
from app.models.agent import Agent, AgentType

logger = structlog.get_logger()


class AgentExecutor:
    """Execute agent tasks with plugin architecture"""
    
    def __init__(self):
        self.plugins = {}
        self._register_plugins()
    
    def _register_plugins(self):
        """Register agent plugins"""
        from app.services.agents.plugins.web_scraper import WebScraperPlugin
        from app.services.agents.plugins.file_connector import FileConnectorPlugin
        
        self.plugins[AgentType.WEB_SCRAPER.value] = WebScraperPlugin()
        self.plugins[AgentType.FILE_CONNECTOR.value] = FileConnectorPlugin()
        # Add more plugins as needed
    
    async def execute(
        self,
        agent: Agent,
        task_type: str,
        parameters: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Execute agent task"""
        plugin = self.plugins.get(agent.agent_type.value)
        
        if not plugin:
            raise ValueError(f"No plugin found for agent type: {agent.agent_type}")
        
        logger.info(
            "Executing agent task",
            agent_id=str(agent.id),
            agent_type=agent.agent_type.value,
            task_type=task_type,
        )
        
        result = await plugin.execute(task_type, parameters, agent.config)
        
        return result

