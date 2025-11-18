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

