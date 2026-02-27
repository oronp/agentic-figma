#!/usr/bin/env python3
"""
MCP server for talk-to-figma-mcp — Python port of src/talk_to_figma_mcp/server.ts.

Infrastructure is fully implemented; individual tool handlers are stubs that
will be filled in by later tasks.

Usage:
    python server.py [--server=<hostname>]
"""

import argparse
import asyncio
import json
import logging
import sys
import uuid
from typing import Any, Dict, List, Optional

import mcp.types as types
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import ImageContent, TextContent, Tool

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
# Global WebSocket state
# ---------------------------------------------------------------------------
ws_conn: Optional[Any] = None  # websockets.ClientConnection once connected
pending_requests: Dict[str, asyncio.Future] = {}
current_channel: Optional[str] = None
_listen_task: Optional[asyncio.Task] = None

# ---------------------------------------------------------------------------
# MCP server instance
# ---------------------------------------------------------------------------
server = Server("TalkToFigmaMCP")

# ---------------------------------------------------------------------------
# Utility helpers
# ---------------------------------------------------------------------------

def rgba_to_hex(color: Any) -> str:
    """Convert an RGBA dict (0-1 float values) to a CSS hex string.

    If *color* is already a hex string it is returned unchanged.
    """
    if isinstance(color, str):
        if color.startswith("#"):
            return color
        # unexpected string — return as-is
        return color

    r = round(color.get("r", 0) * 255)
    g = round(color.get("g", 0) * 255)
    b = round(color.get("b", 0) * 255)
    a = round(color.get("a", 1) * 255)

    hex_color = f"#{r:02x}{g:02x}{b:02x}"
    if a != 255:
        hex_color += f"{a:02x}"
    return hex_color


def filter_figma_node(node: Any) -> Optional[Dict]:
    """Strip VECTOR nodes and clean up fills/strokes before returning to the AI."""
    if not isinstance(node, dict):
        return node

    if node.get("type") == "VECTOR":
        return None

    filtered: Dict[str, Any] = {
        "id": node.get("id"),
        "name": node.get("name"),
        "type": node.get("type"),
    }

    # Fills
    fills = node.get("fills")
    if fills and len(fills) > 0:
        processed_fills = []
        for fill in fills:
            pf = dict(fill)
            pf.pop("boundVariables", None)
            pf.pop("imageRef", None)

            if "gradientStops" in pf:
                new_stops = []
                for stop in pf["gradientStops"]:
                    ps = dict(stop)
                    if "color" in ps:
                        ps["color"] = rgba_to_hex(ps["color"])
                    ps.pop("boundVariables", None)
                    new_stops.append(ps)
                pf["gradientStops"] = new_stops

            if "color" in pf:
                pf["color"] = rgba_to_hex(pf["color"])

            processed_fills.append(pf)
        filtered["fills"] = processed_fills

    # Strokes
    strokes = node.get("strokes")
    if strokes and len(strokes) > 0:
        processed_strokes = []
        for stroke in strokes:
            ps = dict(stroke)
            ps.pop("boundVariables", None)
            if "color" in ps:
                ps["color"] = rgba_to_hex(ps["color"])
            processed_strokes.append(ps)
        filtered["strokes"] = processed_strokes

    if "cornerRadius" in node:
        filtered["cornerRadius"] = node["cornerRadius"]

    if "absoluteBoundingBox" in node:
        filtered["absoluteBoundingBox"] = node["absoluteBoundingBox"]

    if "characters" in node:
        filtered["characters"] = node["characters"]

    if "style" in node:
        s = node["style"]
        filtered["style"] = {
            "fontFamily": s.get("fontFamily"),
            "fontStyle": s.get("fontStyle"),
            "fontWeight": s.get("fontWeight"),
            "fontSize": s.get("fontSize"),
            "textAlignHorizontal": s.get("textAlignHorizontal"),
            "letterSpacing": s.get("letterSpacing"),
            "lineHeightPx": s.get("lineHeightPx"),
        }

    if "children" in node:
        children = [filter_figma_node(child) for child in node["children"]]
        filtered["children"] = [c for c in children if c is not None]

    return filtered


def process_figma_node_response(result: Any) -> Any:
    """Log node details to stderr and return *result* unchanged."""
    if not isinstance(result, dict):
        return result

    if "id" in result and isinstance(result["id"], str):
        logger.info(
            "Processed Figma node: %s (ID: %s)",
            result.get("name", "Unknown"),
            result["id"],
        )
        if "x" in result and "y" in result:
            logger.debug("Node position: (%s, %s)", result["x"], result["y"])
        if "width" in result and "height" in result:
            logger.debug(
                "Node dimensions: %sx%s", result["width"], result["height"]
            )

    return result


# ---------------------------------------------------------------------------
# WebSocket connection helpers
# ---------------------------------------------------------------------------

async def _listen() -> None:
    """Background task: read WS messages and resolve/reject pending futures."""
    import websockets  # imported here to keep top-level imports clean

    global ws_conn, pending_requests, current_channel

    try:
        async for raw in ws_conn:
            try:
                json_data = json.loads(raw)

                # Progress update — log and extend implicit timeout (asyncio
                # futures have no built-in timer, so we just log here).
                if json_data.get("type") == "progress_update":
                    msg = json_data.get("message", {})
                    progress_data = msg.get("data", {}) if isinstance(msg, dict) else {}
                    cmd_type = progress_data.get("commandType", "unknown")
                    progress = progress_data.get("progress", 0)
                    message = progress_data.get("message", "")
                    logger.info(
                        "Progress update for %s: %s%% - %s",
                        cmd_type,
                        progress,
                        message,
                    )
                    if (
                        progress_data.get("status") == "completed"
                        and progress_data.get("progress") == 100
                    ):
                        logger.info(
                            "Operation %s completed, waiting for final result",
                            cmd_type,
                        )
                    continue

                # Regular response
                my_response = json_data.get("message")
                logger.debug("Received message: %s", json.dumps(my_response))

                req_id = my_response.get("id") if isinstance(my_response, dict) else None
                if req_id and req_id in pending_requests:
                    future = pending_requests.pop(req_id)
                    if not future.done():
                        if my_response.get("error"):
                            logger.error(
                                "Error from Figma: %s", my_response["error"]
                            )
                            future.set_exception(
                                RuntimeError(my_response["error"])
                            )
                        elif my_response.get("result") is not None:
                            future.set_result(my_response["result"])
                        # else: no result and no error — ignore (shouldn't happen)
                else:
                    logger.info(
                        "Received broadcast message: %s",
                        json.dumps(my_response),
                    )

            except json.JSONDecodeError as exc:
                logger.error("Error parsing message: %s", exc)
            except Exception as exc:
                logger.error("Error handling message: %s", exc)

    except Exception as exc:
        logger.info("WebSocket listen loop ended: %s", exc)

    finally:
        # Connection dropped — reject all outstanding futures
        logger.info("Disconnected from Figma socket server")
        for req_id, future in list(pending_requests.items()):
            if not future.done():
                future.set_exception(RuntimeError("Connection closed"))
        pending_requests.clear()
        ws_conn = None


async def connect_to_figma(port: int = 3055) -> None:
    """Connect to the WebSocket relay server and start the background listener."""
    import websockets  # imported here to avoid circular issues at module load

    global ws_conn, _listen_task

    if ws_conn is not None:
        logger.info("Already connected to Figma")
        return

    ws_url = f"{WS_BASE}:{port}" if SERVER_URL == "localhost" else WS_BASE
    logger.info("Connecting to Figma socket server at %s...", ws_url)

    try:
        ws_conn = await websockets.connect(ws_url)
        logger.info("Connected to Figma socket server")
        _listen_task = asyncio.get_running_loop().create_task(_listen())
    except Exception as exc:
        logger.error("Failed to connect to Figma: %s", exc)
        ws_conn = None


async def join_channel(channel_name: str) -> None:
    """Send a join message and wait for the relay to confirm."""
    global current_channel

    if ws_conn is None:
        raise RuntimeError("Not connected to Figma")

    result = await send_command("join", {"channel": channel_name}, timeout_ms=30000)
    current_channel = channel_name
    logger.info("Joined channel: %s", channel_name)
    return result


async def send_command(
    command: str,
    params: Optional[Dict] = None,
    timeout_ms: int = 30000,
) -> Any:
    """Send a command to Figma via the relay and await the response."""
    if ws_conn is None:
        await connect_to_figma()
    if ws_conn is None:
        raise RuntimeError("Not connected to Figma. Is the relay server running?")

    is_join = command == "join"
    if not is_join and current_channel is None:
        raise RuntimeError("Must join a channel before sending commands")

    if params is None:
        params = {}

    req_id = str(uuid.uuid4())
    loop = asyncio.get_running_loop()
    future: asyncio.Future = loop.create_future()
    pending_requests[req_id] = future

    request = {
        "id": req_id,
        "type": "join" if is_join else "message",
        "channel": params.get("channel") if is_join else current_channel,
        "message": {
            "id": req_id,
            "command": command,
            "params": {**params, "commandId": req_id},
        },
    }

    logger.info("Sending command to Figma: %s", command)
    logger.debug("Request details: %s", json.dumps(request))
    await ws_conn.send(json.dumps(request))

    # Await with timeout
    timeout_sec = timeout_ms / 1000.0
    try:
        result = await asyncio.wait_for(future, timeout=timeout_sec)
        return result
    except asyncio.TimeoutError:
        pending_requests.pop(req_id, None)
        raise RuntimeError(f"Request to Figma timed out after {timeout_ms // 1000}s")


# ---------------------------------------------------------------------------
# MCP response helpers
# ---------------------------------------------------------------------------

def ok(result: Any) -> List[TextContent]:
    """Wrap a successful result in an MCP TextContent list."""
    return [TextContent(type="text", text=json.dumps(result))]


def err(msg: str) -> List[TextContent]:
    """Wrap an error message in an MCP TextContent list."""
    return [TextContent(type="text", text=msg)]


def _stub(name: str) -> List[TextContent]:
    """Placeholder for tools that are not yet implemented."""
    return err(f"Tool '{name}' not yet implemented")


# ---------------------------------------------------------------------------
# Tool registry and handlers — imported after the above are defined so that
# handlers.py can safely do `from server import send_command, ...` without
# hitting a circular-import problem.
# ---------------------------------------------------------------------------

from tools import ALL_TOOLS          # noqa: E402
from handlers import handle_tool     # noqa: E402


@server.list_tools()
async def list_tools() -> List[Tool]:
    return ALL_TOOLS


@server.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent | ImageContent]:
    return await handle_tool(name, arguments)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

async def main() -> None:
    await connect_to_figma()

    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options(),
        )


if __name__ == "__main__":
    asyncio.run(main())
