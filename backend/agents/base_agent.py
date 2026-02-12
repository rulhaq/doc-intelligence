from services.llm_service import llm_service
from services.vector_store import vector_store
import re

class BaseAgent:
    def __init__(self, system_prompt: str):
        self.system_prompt = system_prompt
        self.llm = llm_service
        self.vector_store = vector_store

    async def get_context(self, query: str, limit: int = 5) -> str:
        results = self.vector_store.search(query, limit=limit)
        context = "\n\n".join([f"Source: {res['metadata']['source']}\nContent: {res['content']}" for res in results])
        return context

    def language_instruction(self, *texts: str) -> str:
        combined = " ".join([text for text in texts if text])
        has_arabic = bool(re.search(r"[\u0600-\u06FF]", combined))
        if has_arabic:
            return "Respond in Arabic. Keep legal terminology accurate and include citations from the provided sources."
        return "Respond in English unless the user asked in another language. Include citations from the provided sources."

    async def run(self, prompt: str) -> str:
        return await self.llm.generate_response(prompt, self.system_prompt)
