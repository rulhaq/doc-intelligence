from services.llm_service import llm_service
from services.vector_store import vector_store
from typing import List, Dict, Any

class BaseAgent:
    def __init__(self, system_prompt: str):
        self.system_prompt = system_prompt
        self.llm = llm_service
        self.vector_store = vector_store

    async def get_context(self, query: str, limit: int = 5) -> str:
        results = self.vector_store.search(query, limit=limit)
        context = "\n\n".join([f"Source: {res['metadata']['source']}\nContent: {res['content']}" for res in results])
        return context

    async def run(self, prompt: str) -> str:
        return await self.llm.generate_response(prompt, self.system_prompt)
