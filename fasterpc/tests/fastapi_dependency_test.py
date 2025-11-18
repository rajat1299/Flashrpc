import os



import pytest

import asyncio

from multiprocessing import Process

import uvicorn

from fastapi import FastAPI, WebSocket, Header, HTTPException, Depends

from websockets.exceptions import InvalidStatus

from fasterpc.rpc_methods import RpcUtilityMethods

from fasterpc.websocket_rpc_client import WebSocketRpcClient

from fasterpc.websocket_rpc_endpoint import WebsocketRPCEndpoint

from fasterpc.utils import gen_uid

PORT = 9998

SECRET = "my-secret-key"

uri = f"ws://localhost:{PORT}/ws"

