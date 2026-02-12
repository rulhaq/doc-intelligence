from agents.base_agent import BaseAgent

class ChatAgent(BaseAgent):
    def __init__(self):
        super().__init__("You are a specialized legal AI assistant. Provide accurate, citation-based answers from the provided context.")

    async def ask(self, question: str) -> str:
        context = await self.get_context(question)
        prompt = (
            f"Context:\n{context}\n\n"
            f"Question: {question}\n\n"
            f"{self.language_instruction(question, context)}\n"
            "Answer the question using ONLY the provided context. Cite your sources clearly."
        )
        return await self.run(prompt)
