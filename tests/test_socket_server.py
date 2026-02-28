import pytest
from figma_mcp.socket_server import start_relay


@pytest.mark.asyncio
async def test_start_relay_returns_server():
    server = await start_relay(port=13055)
    try:
        assert server is not None
        assert server.sockets  # server is actually listening
    finally:
        server.close()
        await server.wait_closed()
