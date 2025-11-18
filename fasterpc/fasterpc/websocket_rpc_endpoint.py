import asyncio

from typing import Coroutine, List, Type

from fastapi import WebSocket, WebSocketDisconnect

from .connection_manager import ConnectionManager

from .rpc_channel import RpcChannel

from .rpc_methods import RpcMethodsBase

from .logger import get_logger

from .schemas import WebSocketFrameType

from .simplewebsocket import SimpleWebSocket, JsonSerializingWebSocket



logger = get_logger("RPC_ENDPOINT")



class WebSocketSimplifier(SimpleWebSocket):

    def __init__(self, websocket: WebSocket, frame_type: WebSocketFrameType = WebSocketFrameType.Text):

        self.websocket = websocket

        self.frame_type = frame_type



    async def connect(self, uri: str, **connect_kwargs): pass



    @property

    def send(self):

        return self.websocket.send_bytes if self.frame_type == WebSocketFrameType.Binary else self.websocket.send_text



    @property

    def recv(self):

        return self.websocket.receive_bytes if self.frame_type == WebSocketFrameType.Binary else self.websocket.receive_text



    async def close(self, code: int = 1000):

        return await self.websocket.close(code)



class WebsocketRPCEndpoint:

    def __init__(self, methods: RpcMethodsBase = None,

                 manager: ConnectionManager = None,

                 on_disconnect: List[Coroutine] = None,

                 on_connect: List[Coroutine] = None,

                 on_channel_created: List[Coroutine] = None,

                 frame_type: WebSocketFrameType = WebSocketFrameType.Text,

                 serializing_socket_cls: Type[SimpleWebSocket] = JsonSerializingWebSocket,

                 rpc_channel_get_remote_id: bool = False):

        self.manager = manager if manager is not None else ConnectionManager()

        self.methods = methods if methods is not None else RpcMethodsBase()

        self._on_disconnect = on_disconnect

        self._on_connect = on_connect

        self._on_channel_created = on_channel_created

        self._frame_type = frame_type

        self._serializing_socket_cls = serializing_socket_cls

        self._rpc_channel_get_remote_id = rpc_channel_get_remote_id



    async def main_loop(self, websocket: WebSocket, client_id: str = None, **kwargs):

        try:

            await self.manager.connect(websocket)

            logger.info(f"Client connected")

            simple_websocket = self._serializing_socket_cls(WebSocketSimplifier(websocket, frame_type=self._frame_type))

            channel = RpcChannel(self.methods, simple_websocket, sync_channel_id=self._rpc_channel_get_remote_id, **kwargs)

            # Call on_channel_created callback if provided

            if self._on_channel_created:

                await asyncio.gather(*(callback(channel) for callback in self._on_channel_created))

            channel.register_connect_handler(self._on_connect)

            channel.register_disconnect_handler(self._on_disconnect)

            await channel.on_connect()

            try:

                while True:

                    data = await simple_websocket.recv()

                    await channel.on_message(data)

            except WebSocketDisconnect:

                await self.handle_disconnect(websocket, channel)

            except Exception:

                await self.handle_disconnect(websocket, channel)

        except:

            self.manager.disconnect(websocket)



    async def handle_disconnect(self, websocket, channel):

        self.manager.disconnect(websocket)

        await channel.on_disconnect()



    def register_route(self, router, path="/ws", dependencies=None):

        @router.websocket(path, dependencies=dependencies)

        async def websocket_endpoint(websocket: WebSocket):

            await self.main_loop(websocket)

