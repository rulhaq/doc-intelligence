"""Base Agent Plugin"""
from abc import ABC, abstractmethod
from typing import Dict, Any


class BaseAgentPlugin(ABC):
    """Base class for agent plugins"""
    
    @abstractmethod
    async def execute(
        self,
        task_type: str,
        parameters: Dict[str, Any],
        config: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Execute agent task"""
        pass

