import asyncio

import uvicorn

from fastapi import FastAPI

from fasterpc import RpcMethodsBase, WebsocketRPCEndpoint



class BaseAgentMethods(RpcMethodsBase):

