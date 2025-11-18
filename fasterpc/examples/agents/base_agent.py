import asyncio

import uvicorn

from fastapi import FastAPI

from fasterpc import RpcMethodsBase, WebsocketRPCEndpoint



class BaseAgentMethods(RpcMethodsBase):

    def __init__(self, agent_name):

        super().__init__()

        self.agent_name = agent_name



    async def get_info(self):

        return {"name": self.agent_name, "status": "active"}



def run_agent_server(agent_methods, port):

