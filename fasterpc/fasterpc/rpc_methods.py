import asyncio

import os

import sys

import typing

import copy

from pydantic import BaseModel

from .utils import gen_uid



PING_RESPONSE = "pong"

EXPOSED_BUILT_IN_METHODS = ['_ping_', '_get_channel_id_']



class NoResponse:

    pass



class RpcMethodsBase:

    def __init__(self):

        self._channel = None



    def _set_channel_(self, channel):

        self._channel = channel



    @property

    def channel(self):

        return self._channel



    def _copy_(self):

        return copy.copy(self)



    async def _ping_(self) -> str:

        return PING_RESPONSE



    async def _get_channel_id_(self) -> str:

        return self._channel.id



class ProcessDetails(BaseModel):

    pid: int = os.getpid()

    cmd: typing.List[str] = sys.argv

    workingdir: str = os.getcwd()



class RpcUtilityMethods(RpcMethodsBase):

    async def get_process_details(self) -> ProcessDetails:

        return ProcessDetails()



    async def echo(self, text: str) -> str:

        return text

