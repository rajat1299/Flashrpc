import asyncio

from fasterpc import WebSocketRpcClient, RpcMethodsBase



async def run_workflow():

    print("🚀 Starting Multi-Agent Workflow")

    

    # Connect to agents

    # In a real app, you might use a connection pool or service discovery

    async with                WebSocketRpcClient("ws://localhost:9001/ws", RpcMethodsBase()) as researcher, \

               WebSocketRpcClient("ws://localhost:9002/ws", RpcMethodsBase()) as analyst:

        

        # 1. Task Researcher

        topic = "Quantum Computing"

        print(f"\n1️⃣ Asking Researcher about '{topic}'...")

        search_results = await researcher.other.search(query=topic)

        print(f"   Received: {search_results.result}")



        # 2. Task Analyst with Researcher's output

        print(f"\n2️⃣ Sending data to Analyst...")

        analysis = await analyst.other.analyze(data=search_results.result)

        print(f"   Analysis: {analysis.result}")



    print("\n✅ Workflow Complete")



if __name__ == "__main__":

    try:

        asyncio.run(run_workflow())

    except OSError:

        print("❌ Could not connect to agents. Make sure research_agent.py and analysis_agent.py are running!")

