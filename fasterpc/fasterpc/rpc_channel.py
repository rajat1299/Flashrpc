import asyncio

from inspect import _empty, getmembers, ismethod, signature

from typing import Any, Callable, Dict, List

from pydantic import ValidationError



from .logger import get_logger

from .rpc_methods import EXPOSED_BUILT_IN_METHODS, NoResponse, RpcMethodsBase

from .schemas import RpcMessage, RpcRequest, RpcResponse

from .utils import gen_uid, pydantic_parse



logger = get_logger("RPC_CHANNEL")



OnConnectCallback = Callable[['RpcChannel'], Any]

OnDisconnectCallback = Callable[['RpcChannel'], Any]



class DEFAULT_TIMEOUT:

    pass



class RemoteValueError(ValueError):

    pass



class RpcChannelClosedException(Exception):

    pass



class RpcPromise:

    def __init__(self, request: RpcRequest):

        self._request = request

        self._id = request.call_id

        self._event = asyncio.Event()



    @property

    def request(self):

        return self._request



    @property

    def call_id(self):

        return self._id



    def set(self):

        self._event.set()



    def wait(self):

        return self._event.wait()



class RpcProxy:

    def __init__(self, channel, method_name) -> None:

        self.method_name = method_name

        self.channel = channel



    def __call__(self, **kwds: Any) -> Any:

        return self.channel.call(self.method_name, args=kwds)



class RpcCaller:

    def __init__(self, channel, methods=None) -> None:

        self._channel = channel

        self._method_names = (

            [method[0] for method in getmembers(methods, lambda i: ismethod(i))]

            if methods is not None

            else None

        )



    def __getattribute__(self, name: str):

        if (not name.startswith("_") or name in EXPOSED_BUILT_IN_METHODS) and (

            self._method_names is None or name in self._method_names

        ):

            return RpcProxy(self._channel, name)

        else:

            return super().__getattribute__(name)



class RpcChannel:

    def __init__(self, methods: RpcMethodsBase, socket, channel_id=None, default_response_timeout=None, sync_channel_id=False, **kwargs):

        self.methods = methods._copy_()

        self.methods._set_channel_(self)

        self.requests: Dict[str, asyncio.Event] = {}

        self.responses = {}

        self.socket = socket

        self.default_response_timeout = default_response_timeout

        self.id = channel_id if channel_id is not None else gen_uid()

        self._sync_channel_id = sync_channel_id

        self._other_channel_id = None

        self._channel_id_synced = asyncio.Event()

        self.other = RpcCaller(self)

        self._connect_handlers = []

        self._disconnect_handlers = []

        self._error_handlers = []

        self._closed = asyncio.Event()

        self._context = kwargs or {}



    @property

    def context(self) -> Dict[str, Any]:

        return self._context



    def get_return_type(self, method):

        method_signature = signature(method)

        return method_signature.return_annotation if method_signature.return_annotation is not _empty else str



    async def send(self, data):

        await self.socket.send(data)



    async def close(self):

        res = await self.socket.close()

        self._closed.set()

        return res



    def isClosed(self):

        return self._closed.is_set()



    async def on_message(self, data):

        try:

            message = pydantic_parse(RpcMessage, data)

            if message.request is not None:

                await self.on_request(message.request)

            if message.response is not None:

                await self.on_response(message.response)

        except Exception as e:

            await self.on_error(e)

            raise



    def register_connect_handler(self, coros=None):

        if coros is not None: self._connect_handlers.extend(coros)



    def register_disconnect_handler(self, coros=None):

        if coros is not None: self._disconnect_handlers.extend(coros)



    async def on_handler_event(self, handlers, *args, **kwargs):

        await asyncio.gather(*(callback(*args, **kwargs) for callback in handlers))



    async def on_connect(self):

        if self._sync_channel_id:

            asyncio.create_task(self._get_other_channel_id())

        await self.on_handler_event(self._connect_handlers, self)



    async def _get_other_channel_id(self):

        if self._other_channel_id is None:

            other_channel_id = await self.other._get_channel_id_()

            self._other_channel_id = other_channel_id.result if other_channel_id else None

            self._channel_id_synced.set()

            return self._other_channel_id

        return self._other_channel_id



    async def on_disconnect(self):

        self._closed.set()

        await self.on_handler_event(self._disconnect_handlers, self)



    async def on_error(self, error: Exception):

        await self.on_handler_event(self._error_handlers, self, error)



    async def on_request(self, message: RpcRequest):

        method_name = message.method

        if isinstance(method_name, str) and (not method_name.startswith("_") or method_name in EXPOSED_BUILT_IN_METHODS):

            method = getattr(self.methods, method_name)

            if callable(method):

                result = await method(**message.arguments)

                if result is not NoResponse:

                    result_type = self.get_return_type(method)

                    response = RpcMessage(response=RpcResponse[result_type](

                            call_id=message.call_id,

                            result=result,

                            result_type=getattr(result_type, "__name__", "unknown-type"),

                        ))

                    await self.send(response)



    async def on_response(self, response: RpcResponse):

        if response.call_id is not None and response.call_id in self.requests:

            self.responses[response.call_id] = response

            self.requests[response.call_id].set()



    async def wait_for_response(self, promise, timeout=DEFAULT_TIMEOUT) -> RpcResponse:

        if timeout is DEFAULT_TIMEOUT:

            timeout = self.default_response_timeout

        _, pending = await asyncio.wait(

            [asyncio.ensure_future(promise.wait()), asyncio.ensure_future(self._closed.wait())],

            timeout=timeout,

            return_when=asyncio.FIRST_COMPLETED,

        )

        for fut in pending: fut.cancel()

        response = self.responses.get(promise.call_id, NoResponse)

        if response is NoResponse:

            raise RpcChannelClosedException(f"Channel Closed before RPC response for {promise.call_id} received")

        del self.requests[promise.call_id]

        del self.responses[promise.call_id]

        return response



    async def async_call(self, name, args={}, call_id=None) -> RpcPromise:

        call_id = call_id or gen_uid()

        msg = RpcMessage(request=RpcRequest(method=name, arguments=args, call_id=call_id))

        await self.send(msg)

        promise = self.requests[msg.request.call_id] = RpcPromise(msg.request)

        return promise



    async def call(self, name, args={}, timeout=DEFAULT_TIMEOUT):

        promise = await self.async_call(name, args)

        return await self.wait_for_response(promise, timeout=timeout)

