import asyncio

from .base_agent import BaseAgentMethods, run_agent_server



class ResearchAgent(BaseAgentMethods):

    def __init__(self):

        super().__init__("Research Agent")



    async def search(self, query: str) -> list:

        print(f"🔍 [Research] Searching for: {query}")

        await asyncio.sleep(1)  # Simulate work

        return [

