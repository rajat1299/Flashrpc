import asyncio

import uvicorn

from fastapi import FastAPI

from fasterpc import RpcMethodsBase, WebsocketRPCEndpoint



class BaseAgentMethods(RpcMethodsBase):

    def __init__(self, agent_name):

        super().__init__()

