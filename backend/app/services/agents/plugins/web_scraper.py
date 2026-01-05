"""Web Scraper Agent Plugin"""
from typing import Dict, Any
import httpx
from bs4 import BeautifulSoup
import structlog

from app.services.agents.plugins.base import BaseAgentPlugin

logger = structlog.get_logger()


class WebScraperPlugin(BaseAgentPlugin):
    """Web scraper agent plugin"""
    
    async def execute(
        self,
        task_type: str,
        parameters: Dict[str, Any],
        config: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Execute web scraping task"""
        
        if task_type == "scrape_url":
            return await self._scrape_url(parameters, config)
        elif task_type == "scrape_multiple":
            return await self._scrape_multiple(parameters, config)
        else:
            raise ValueError(f"Unknown task type: {task_type}")
    
    async def _scrape_url(
        self,
        parameters: Dict[str, Any],
        config: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Scrape single URL"""
        url = parameters.get("url")
        if not url:
            raise ValueError("URL required")
        
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.get(url)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Extract text
                text = soup.get_text(separator='\n', strip=True)
                
                # Extract links if requested
                links = []
                if parameters.get("extract_links", False):
                    links = [a.get('href') for a in soup.find_all('a', href=True)]
                
                logger.info("URL scraped", url=url, text_length=len(text))
                
                return {
                    "success": True,
                    "url": url,
                    "text": text,
                    "links": links,
                    "status_code": response.status_code,
                }
                
        except Exception as e:
            logger.error("Scraping failed", url=url, error=str(e))
            return {
                "success": False,
                "url": url,
                "error": str(e),
            }
    
    async def _scrape_multiple(
        self,
        parameters: Dict[str, Any],
        config: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Scrape multiple URLs"""
        urls = parameters.get("urls", [])
        results = []
        
        for url in urls:
            result = await self._scrape_url({"url": url}, config)
            results.append(result)
        
        return {
            "success": True,
            "results": results,
            "total": len(results),
        }

