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

    import websockets

except ImportError:

    websockets = None



class WebSocketsClientHandler(SimpleWebSocket):

    def __init__(self):

        if websockets is None: raise RuntimeError("Requires websockets library")

        self._websocket = None



    async def connect(self, uri: str, **connect_kwargs):

        self._websocket = await websockets.connect(uri, **connect_kwargs)



    async def send(self, msg):

        await self._websocket.send(msg)



    async def recv(self):

        try:

            return await self._websocket.recv()

        except websockets.exceptions.ConnectionClosed:

            return None



    async def close(self, code: int = 1000):

        if self._websocket: await self._websocket.close(code)



def isNotForbidden(value) -> bool:

    value = getattr(value, "response", value)

    return not (hasattr(value, "status_code") and value.status_code in (401, 403))



class WebSocketRpcClient:

    def logerror(retry_state: RetryCallState):

        logger.exception(retry_state.outcome.exception())



    DEFAULT_RETRY_CONFIG = {

        'wait': wait.wait_random_exponential(min=0.1, max=120),

        'retry': retry_if_exception(isNotForbidden),

        'reraise': True,

        "retry_error_callback": logerror

    }



    def __init__(self, uri: str, methods: RpcMethodsBase = None,

                 retry_config=None, default_response_timeout: float = None,

                 on_connect: List[OnConnectCallback] = None,

                 on_disconnect: List[OnDisconnectCallback] = None,

                 keep_alive: float = 0,

                 websocket_client_handler_cls: Type[SimpleWebSocket] = None,

                 **kwargs):

        self.methods = methods or RpcMethodsBase()

        self.connect_kwargs = kwargs

        self.ws = None

        self.uri = uri

        self._read_task = None

        self._keep_alive_task = None

        self._keep_alive_interval = keep_alive

        self.default_response_timeout = default_response_timeout

        self.channel = None

        self.retry_config = retry_config if retry_config is not None else self.DEFAULT_RETRY_CONFIG

        self._on_disconnect = on_disconnect

        self._on_connect = on_connect

        self._websocket_client_handler_cls = websocket_client_handler_cls or WebSocketsClientHandler



    async def __connect__(self):

        raw_ws = self._websocket_client_handler_cls()

        self.ws = JsonSerializingWebSocket(raw_ws)

        await self.ws.connect(self.uri, **self.connect_kwargs)

        self.channel = RpcChannel(self.methods, self.ws, default_response_timeout=self.default_response_timeout)

        self.channel.register_connect_handler(self._on_connect)

        self.channel.register_disconnect_handler(self._on_disconnect)

        self._read_task = asyncio.create_task(self.reader())

        if self._keep_alive_interval > 0:

            self._keep_alive_task = asyncio.create_task(self._keep_alive())

        await self.channel.on_connect()

        return self



    async def __aenter__(self):

        if self.retry_config is False: return await self.__connect__()

        else: return await retry(**self.retry_config)(self.__connect__)()



    async def __aexit__(self, *args, **kwargs):

        await self.close()



    async def close(self):

        if self.ws: await self.ws.close()

        if self.channel and not self.channel.isClosed():

            await self.channel.on_disconnect()

            await self.channel.close()

        if self._read_task: self._read_task.cancel()

        if self._keep_alive_task: self._keep_alive_task.cancel()



    async def reader(self):

        try:

            while True:

                raw_message = await self.ws.recv()

                if raw_message is None:

                    await self.close()

                    break

                await self.channel.on_message(raw_message)

        except asyncio.CancelledError: pass



    async def _keep_alive(self):

        try:

            while True:

                await asyncio.sleep(self._keep_alive_interval)

                answer = await self.channel.other._ping_()

                assert answer.result == PING_RESPONSE

        except asyncio.CancelledError: pass



    @property

    def other(self):

        return self.channel.other
