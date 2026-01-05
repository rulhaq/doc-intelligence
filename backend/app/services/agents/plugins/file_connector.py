"""File Connector Agent Plugin"""
from typing import Dict, Any
import structlog
from pathlib import Path

from app.services.agents.plugins.base import BaseAgentPlugin

logger = structlog.get_logger()


class FileConnectorPlugin(BaseAgentPlugin):
    """File connector agent plugin"""
    
    async def execute(
        self,
        task_type: str,
        parameters: Dict[str, Any],
        config: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Execute file connector task"""
        
        if task_type == "list_files":
            return await self._list_files(parameters, config)
        elif task_type == "read_file":
            return await self._read_file(parameters, config)
        else:
            raise ValueError(f"Unknown task type: {task_type}")
    
    async def _list_files(
        self,
        parameters: Dict[str, Any],
        config: Dict[str, Any],
    ) -> Dict[str, Any]:
        """List files in directory"""
        directory = parameters.get("directory")
        pattern = parameters.get("pattern", "*")
        
        if not directory:
            raise ValueError("Directory required")
        
        try:
            path = Path(directory)
            files = list(path.glob(pattern))
            
            file_list = [
                {
                    "name": f.name,
                    "path": str(f),
                    "size": f.stat().st_size,
                    "is_file": f.is_file(),
                }
                for f in files
            ]
            
            logger.info("Files listed", directory=directory, count=len(file_list))
            
            return {
                "success": True,
                "directory": directory,
                "files": file_list,
                "count": len(file_list),
            }
            
        except Exception as e:
            logger.error("List files failed", directory=directory, error=str(e))
            return {
                "success": False,
                "error": str(e),
            }
    
    async def _read_file(
        self,
        parameters: Dict[str, Any],
        config: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Read file content"""
        file_path = parameters.get("file_path")
        
        if not file_path:
            raise ValueError("File path required")
        
        try:
            path = Path(file_path)
            content = path.read_text()
            
            logger.info("File read", file_path=file_path, size=len(content))
            
            return {
                "success": True,
                "file_path": file_path,
                "content": content,
                "size": len(content),
            }
            
        except Exception as e:
            logger.error("Read file failed", file_path=file_path, error=str(e))
            return {
                "success": False,
                "error": str(e),
            }

