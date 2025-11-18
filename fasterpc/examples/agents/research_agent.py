import asyncio

from .base_agent import BaseAgentMethods, run_agent_server



class ResearchAgent(BaseAgentMethods):

    def __init__(self):

        super().__init__("Research Agent")



    async def search(self, query: str) -> list:

        print(f"🔍 [Research] Searching for: {query}")

        await asyncio.sleep(1)  # Simulate work

        return [

            f"Source 1 about {query}",

            f"Source 2 about {query}",

            f"Source 3 about {query}"

        ]



if __name__ == "__main__":

    run_agent_server(ResearchAgent(), 9001)

