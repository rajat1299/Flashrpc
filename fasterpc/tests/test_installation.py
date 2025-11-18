import asyncio



import uvicorn

from fastapi import FastAPI

from multiprocessing import Process

from fasterpc import RpcMethodsBase, WebsocketRPCEndpoint, WebSocketRpcClient

# 1. Define Server Methods

class ServerMethods(RpcMethodsBase):

    async def hello(self, name: str) -> str:

        return f"Hello {name} from Server!"

