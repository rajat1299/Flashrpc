import asyncio

from .base_agent import BaseAgentMethods, run_agent_server



class AnalysisAgent(BaseAgentMethods):

    def __init__(self):

        super().__init__("Analysis Agent")



    async def analyze(self, data: list) -> dict:

        print(f"📊 [Analysis] Analyzing {len(data)} items")

        await asyncio.sleep(1)

        return {

            "summary": "Data indicates positive trend",

            "confidence": 0.95,

            "key_points": [d.upper() for d in data]

        }



if __name__ == "__main__":

    run_agent_server(AnalysisAgent(), 9002)

