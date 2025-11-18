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

