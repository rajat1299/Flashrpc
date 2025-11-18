import asyncio



import logging

from .simplewebsocket import SimpleWebSocket

from .logger import get_logger

logger = get_logger("PROXY_HANDLER")

try:

    import websocket

except ImportError:

    websocket = None



class ProxyEnabledWebSocketClientHandler(SimpleWebSocket):

    def __init__(self):

        if websocket is None:

            raise RuntimeError("Proxy handler requires websocket-client library")

        self._websocket = None

    async def connect(self, uri: str, **connect_kwargs):

        # websocket-client is synchronous, so we run it in an executor

        try:

            self._websocket = await asyncio.get_event_loop().run_in_executor(

                None, 

                lambda: websocket.create_connection(uri, **connect_kwargs)

            )

        except Exception as e:

            logger.error(f"Proxy connection failed: {e}")

            raise

    async def send(self, msg):

        if self._websocket:

            await asyncio.get_event_loop().run_in_executor(None, self._websocket.send, msg)

    async def recv(self):

        if not self._websocket:

            return None

        try:

            return await asyncio.get_event_loop().run_in_executor(None, self._websocket.recv)

        except (websocket.WebSocketConnectionClosedException, BrokenPipeError):

            return None

    async def close(self, code: int = 1000):

        if self._websocket:

            await asyncio.get_event_loop().run_in_executor(None, self._websocket.close, code=code)
