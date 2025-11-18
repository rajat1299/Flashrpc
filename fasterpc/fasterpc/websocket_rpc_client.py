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

            while True:

                await asyncio.sleep(self._keep_alive_interval)

                answer = await self.channel.other._ping_()

                assert answer.result == PING_RESPONSE

            return await self._websocket.recv()

        except websockets.exceptions.ConnectionClosed:

            return None



    async def close(self, code: int = 1000):

        if self._websocket: await self._websocket.close(code)



def isNotForbidden(value) -> bool:

    value = getattr(value, "response", value)

    return not (hasattr(value, "status_code") and value.status_code in (401, 403))

    import websockets

except ImportError:

    websockets = None
