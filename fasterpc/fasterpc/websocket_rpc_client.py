import asyncio



import logging

from typing import List, Type

from tenacity import retry, RetryCallState, wait, retry_if_exception



from .rpc_methods import PING_RESPONSE, RpcMethodsBase

from .rpc_channel import RpcChannel, OnConnectCallback, OnDisconnectCallback

from .logger import get_logger

from .simplewebsocket import SimpleWebSocket, JsonSerializingWebSocket



logger = get_logger("RPC_CLIENT")



        try:

            return await self._websocket.recv()

        except websockets.exceptions.ConnectionClosed:

            return None



    async def close(self, code: int = 1000):

        if self._websocket: await self._websocket.close(code)



def isNotForbidden(value) -> bool:

    import websockets

except ImportError:

    websockets = None
