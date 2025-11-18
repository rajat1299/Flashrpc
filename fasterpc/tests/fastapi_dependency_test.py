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

# 1. Define Dependency

async def verify_token(x_token: str = Header(...)):

    if x_token != SECRET:

        raise HTTPException(status_code=403, detail="Invalid Token")

# 2. Setup Server

def setup_server():

    app = FastAPI()

    endpoint = WebsocketRPCEndpoint(RpcUtilityMethods())

    # Register route WITH dependencies

    endpoint.register_route(app, "/ws", dependencies=[Depends(verify_token)])

    uvicorn.run(app, port=PORT, log_level="error")

@pytest.fixture(scope="module")

def server():

    proc = Process(target=setup_server, args=(), daemon=True)

    proc.start()

    # Wait for server to start

    import time

    time.sleep(1) 

    yield proc

    proc.kill()

@pytest.mark.asyncio

async def test_dependency_success(server):

    """Test connection with correct token"""

    async with WebSocketRpcClient(

        uri, 

        RpcUtilityMethods(),

        extra_headers={"x-token": SECRET}

    ) as client:

        response = await client.other.echo(text="test")

        assert response.result == "test"

@pytest.mark.asyncio

async def test_dependency_failure(server):

    """Test connection with incorrect token"""

    try:

        async with WebSocketRpcClient(

            uri, 

            RpcUtilityMethods(),

            extra_headers={"x-token": "wrong-token"}

        ) as client:

            assert False, "Should have failed connection"

    except InvalidStatus as e:

        # FastAPI returns 403 Forbidden

        assert e.response.status_code == 403

if __name__ == "__main__":

    # Manual run for the agent if pytest isn't invoked directly

    p = Process(target=setup_server, args=(), daemon=True)

    p.start()

    try:

        import time

        time.sleep(1)

        

        # Run success test

        print("Running success test...")

        asyncio.run(test_dependency_success(p))

        print("✅ Success test passed")

        

        # Run failure test

        print("Running failure test...")

        asyncio.run(test_dependency_failure(p))

        print("✅ Failure test passed")

        

    except Exception as e:

        print(f"❌ Test failed: {e}")

    finally:

        p.kill()
