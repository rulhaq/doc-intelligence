from agents.base_agent import BaseAgent

class ComparisonAgent(BaseAgent):
    def __init__(self):
        super().__init__("You are a legal comparison specialist. Compare cases across jurisdictions, arguments, and financial impacts.")

    async def compare_cases(self, case_a: str, case_b: str) -> str:
        context_a = await self.get_context(case_a)
        context_b = await self.get_context(case_b)
        
        prompt = f"""
        Case A Context:
        {context_a}
        
        Case B Context:
        {context_b}
        
        Compare these two cases across:
        1. Jurisdiction
        2. Core Argument
        3. Financial Impact
        4. Thematic Similarities
        5. Shared Patterns
        
        Format the response in a structured way that can be easily parsed.
        """
        return await self.run(prompt)
