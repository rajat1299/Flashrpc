# ⚡ flashrpc

A high-performance, production-ready JSON-RPC library for Python, built on top of FastAPI and WebSockets.

flashrpc provides a robust, bidirectional communication channel between clients and servers, making it incredibly easy to execute remote functions as if they were local.

## 🚀 Why flashrpc?

Building real-time, bidirectional systems usually involves a lot of boilerplate: handling WebSocket connections, defining message formats, managing reconnects, and routing requests.

flashrpc abstracts all of that away. It gives you a clean, "vibe coding" experience where you just define functions and call them.

- **Simple RPC**: Call remote methods using standard Python syntax: `await client.other.my_method()`.
- **Bidirectional**: The server can call methods on the client, and the client can call methods on the server.
- **Resilient**: Automatic reconnection handling with exponential backoff (powered by tenacity).
- **Modern Stack**: Built on asyncio and FastAPI for high throughput and low latency.
- **Type Safe**: Full Pydantic support for request/response validation.

## 📦 Installation

```bash
pip install flashrpc
```

## 🛠️ Quick Start

Here is a complete example showing a server and a client talking to each other.

### 1. The Server

Create a file named `server.py`. This server exposes an `add` method and an `echo` method.

```python
import uvicorn
from fastapi import FastAPI
from flashrpc import RpcMethodsBase, WebsocketRPCEndpoint

# 1. Define the methods you want to expose
class ServerMethods(RpcMethodsBase):
    async def add(self, a: int, b: int) -> int:
        return a + b

    async def echo(self, message: str) -> str:
        return f"Server says: {message}"

# 2. Setup FastAPI app
app = FastAPI()
endpoint = WebsocketRPCEndpoint(ServerMethods())
endpoint.register_route(app, "/ws")

if __name__ == "__main__":
    # Run the server
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

### 2. The Client

Create a file named `client.py`. This client connects to the server and calls the methods we defined above.

```python
import asyncio
from flashrpc import WebSocketRpcClient, RpcMethodsBase

async def main():
    # Connect to the server
    async with WebSocketRpcClient("ws://localhost:8000/ws", RpcMethodsBase()) as client:
        
        # Call the 'add' method
        result = await client.other.add(a=5, b=10)
        print(f"5 + 10 = {result.result}")  # Output: 5 + 10 = 15

        # Call the 'echo' method
        response = await client.other.echo(message="Hello!")
        print(response.result)              # Output: Server says: Hello!

if __name__ == "__main__":
    asyncio.run(main())
```

## 🤖 Multi-Agent Frameworks

flashrpc excels at building distributed multi-agent systems where agents need to communicate in real-time.

Because it uses WebSockets, your agents maintain persistent connections. This allows for **Orchestration patterns** where a central "Brain" can dispatch tasks to specialized "Worker" agents instantly, without the latency of opening new HTTP connections for every request.

### Agent-to-Agent Example

Imagine a `ResearchAgent` running on port 9001 and an `AnalysisAgent` running on port 9002.

```python
# Orchestrator
async def run_workflow():
    async with WebSocketRpcClient("ws://localhost:9001/ws", RpcMethodsBase()) as researcher, \
               WebSocketRpcClient("ws://localhost:9002/ws", RpcMethodsBase()) as analyst:
        
        # 1. Ask Researcher to find data
        data = await researcher.other.search(query="Quantum Computing")
        
        # 2. Immediately pass that data to Analyst
        insight = await analyst.other.analyze(data=data.result)
        
        print(insight.result)
```

See `examples/agents/` for a complete working implementation of this pattern.

## 🔄 Bidirectional Communication (Server calls Client)

flashrpc allows the server to invoke methods on the client. This is perfect for notifications, background tasks, or interactive apps.

**Server Side:**

```python
# In your server setup...
async def on_connect(channel):
    # When a client connects, call a method on them!
    # channel.other provides access to the client's exposed methods
    await channel.other.notify_client(text="Welcome!")

endpoint = WebsocketRPCEndpoint(ServerMethods(), on_connect=[on_connect])
```

**Client Side:**

```python
class ClientMethods(RpcMethodsBase):
    async def notify_client(self, text: str):
        print(f"Received notification from server: {text}")

async with WebSocketRpcClient(uri, ClientMethods()) as client:
    # The client is now listening for calls from the server
    # Keep the connection alive to receive notifications
    await asyncio.Future() 
```

## 🔐 Authentication & Dependencies

You can secure your WebSocket endpoints using standard FastAPI dependencies.

```python
from fastapi import Depends, Header, HTTPException

async def verify_token(x_token: str = Header(...)):
    if x_token != "super-secret":
        raise HTTPException(status_code=403, detail="Unauthorized")

# Register route with dependency
endpoint.register_route(app, "/ws", dependencies=[Depends(verify_token)])
```

## 🌐 HTTP Proxy Support

Need to connect through a corporate proxy? We've got you covered.

```python
from flashrpc import ProxyEnabledWebSocketClientHandler

# Note: Requires `websocket-client` library (pip install websocket-client)
async with WebSocketRpcClient(
    "ws://example.com/ws",
    RpcMethodsBase(),
    websocket_client_handler_cls=ProxyEnabledWebSocketClientHandler
) as client:
    # This connection will respect HTTP_PROXY/HTTPS_PROXY env vars
    pass
```

## 🧩 Advanced Usage

### Custom Serialization

You can use your own JSON encoder/decoder by extending `JsonSerializingWebSocket` and passing it to the client/server via `serializing_socket_cls`. See `examples/custom_serializer_example.py` for details.

### Binary Data

flashrpc supports binary frames for high-performance data transfer. Configure `frame_type=WebSocketFrameType.Binary` in your endpoint.

## 🤝 Contributing

Contributions are welcome! Please submit a PR or open an issue if you find a bug or have a feature request.

## 📄 License

MIT License

