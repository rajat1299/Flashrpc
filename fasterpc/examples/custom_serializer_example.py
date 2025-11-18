import json



import datetime

from fasterpc.simplewebsocket import JsonSerializingWebSocket

from fasterpc.utils import pydantic_serialize

# 1. Define Custom Serializer

class DateTimeEncoder(json.JSONEncoder):

    def default(self, obj):

        if isinstance(obj, datetime.datetime):

            return {"__datetime__": obj.isoformat()}

        return super().default(obj)

def datetime_decoder(dct):

    if "__datetime__" in dct:

        return datetime.datetime.fromisoformat(dct["__datetime__"])

    return dct

class CustomJsonSocket(JsonSerializingWebSocket):

    def _serialize(self, msg):

        # Use custom encoder

        return json.dumps(msg.dict(), cls=DateTimeEncoder)

    def _deserialize(self, buffer):

        # Use custom decoder

        return json.loads(buffer, object_hook=datetime_decoder)

# This class can now be passed to WebsocketRPCEndpoint or WebSocketRpcClient

# via the serializing_socket_cls parameter.

