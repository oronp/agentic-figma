import asyncio
import json
import pytest
import websockets
from figma_mcp.socket_server import start_relay


@pytest.mark.asyncio
async def test_relay_starts_and_accepts_connections():
    """Verify that a relay started via start_relay() accepts WebSocket connections."""
    server = await start_relay(port=13056)
    try:
        async with websockets.connect("ws://localhost:13056") as ws:
            msg = await asyncio.wait_for(ws.recv(), timeout=2)
            data = json.loads(msg)
            assert data["type"] == "system"
    finally:
        server.close()
        await server.wait_closed()
