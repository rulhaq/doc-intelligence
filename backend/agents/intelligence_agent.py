from agents.base_agent import BaseAgent

class IntelligenceAgent(BaseAgent):
    def __init__(self):
        super().__init__("You are an executive legal analyst. Extract key risks, trends, and summaries from legal documents.")

    async def summarize_case(self, case_name: str) -> str:
        context = await self.get_context(f"Summarize case {case_name}")
        prompt = (
            f"Context:\n{context}\n\n"
            f"{self.language_instruction(case_name, context)}\n"
            f"Provide a high-level executive summary of {case_name}. "
            "Include key alignment with precedents, critical anomalies, and foundational liability risks."
        )
        return await self.run(prompt)

    async def extract_signals(self, case_name: str) -> str:
        context = await self.get_context(f"Extract risks and signals for {case_name}")
        prompt = (
            f"Context:\n{context}\n\n"
            f"{self.language_instruction(case_name, context)}\n"
            f"Identify and extract critical legal signals (e.g., contractual breaches, hidden assets) "
            f"from the documents related to {case_name}."
        )
        return await self.run(prompt)
