#!/usr/bin/env python3
"""
MCP server for talk-to-figma-mcp — Python port of src/talk_to_figma_mcp/server.ts.

Usage:
    python -m figma_mcp.server [--server=<hostname>]
"""

import argparse
import asyncio
import logging
import os
import sys
from typing import Any, Dict, List

# Allow running directly: python3 src/figma_mcp/server.py
if __name__ == "__main__" and __package__ is None:
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
    __package__ = "figma_mcp"

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import ImageContent, TextContent, Tool

from .tools import ALL_TOOLS
from .handlers import handle_tool
from .utils import ok, err, filter_figma_node, rgba_to_hex
from .ws_client import FigmaClient
from .socket_server import start_relay

# ---------------------------------------------------------------------------
# Logging — ALL output goes to stderr to avoid polluting the MCP stdio transport
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.DEBUG,
    format="[%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stderr)],
)
logger = logging.getLogger("talk_to_figma_mcp")

# ---------------------------------------------------------------------------
# Argument parsing
# ---------------------------------------------------------------------------
_arg_parser = argparse.ArgumentParser(description="Talk-to-Figma MCP server")
_arg_parser.add_argument(
    "--server",
    default="localhost",
    help="Hostname of the WebSocket relay server (default: localhost)",
)
# parse_known_args so that the MCP SDK's own argv parsing doesn't cause errors
_args, _unknown = _arg_parser.parse_known_args()

SERVER_URL: str = _args.server
WS_BASE: str = f"ws://{SERVER_URL}" if SERVER_URL == "localhost" else f"wss://{SERVER_URL}"

# ---------------------------------------------------------------------------
# Shared client instance + MCP server
# ---------------------------------------------------------------------------
figma_client = FigmaClient(WS_BASE)
server = Server("TalkToFigmaMCP")


# ---------------------------------------------------------------------------
# MCP handlers
# ---------------------------------------------------------------------------

@server.list_tools()
async def list_tools() -> List[Tool]:
    return ALL_TOOLS


@server.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent | ImageContent]:
    return await handle_tool(name, arguments, figma_client)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

async def main() -> None:
    port = int(os.environ.get("PORT", 3055))
    relay = await start_relay(port=port)

    async with relay:
        await figma_client.connect(port=port)

        async with stdio_server() as (read_stream, write_stream):
            await server.run(
                read_stream,
                write_stream,
                server.create_initialization_options(),
            )


if __name__ == "__main__":
    asyncio.run(main())
