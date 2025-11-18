import asyncio



import uvicorn

from fastapi import FastAPI

from multiprocessing import Process

from fasterpc import RpcMethodsBase, WebsocketRPCEndpoint, WebSocketRpcClient

# 1. Define Server Methods

class ServerMethods(RpcMethodsBase):

    async def hello(self, name: str) -> str:

        return f"Hello {name} from Server!"

# 2. Setup Server

def run_server():

    app = FastAPI()

    endpoint = WebsocketRPCEndpoint(ServerMethods())

    endpoint.register_route(app, "/ws")

    uvicorn.run(app, port=9999, log_level="error")

# 3. Client Logic

async def run_client():

    # Give server a moment to start

    await asyncio.sleep(1)

    async with WebSocketRpcClient("ws://localhost:9999/ws", RpcMethodsBase()) as client:

        response = await client.other.hello(name="Agent")

        print(f"RESPONSE: {response.result}")

        assert response.result == "Hello Agent from Server!"

if __name__ == "__main__":

    # Start server process

    p = Process(target=run_server)

    p.start()

    

