#!/usr/bin/env python3
"""
WebSocket relay server for talk-to-figma-mcp.

Port of src/socket.ts — implements a channel-based pub/sub relay so the MCP
server and the Figma plugin can communicate without a direct connection.

Usage:
    python socket_server.py          # listens on port 3055
    PORT=4000 python socket_server.py
"""

import asyncio
import json
import logging
import os
import sys
from typing import Dict, Set

import websockets
from websockets.server import ServerConnection

logging.basicConfig(
    level=logging.DEBUG,
    format="[%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stderr)],
)
logger = logging.getLogger("figma_relay")

# channel_name -> set of connected ServerConnection objects
channels: Dict[str, Set[ServerConnection]] = {}


async def handler(ws: ServerConnection) -> None:
    """Handle a single WebSocket client connection."""
    logger.info("New client connected")

    # Send welcome message
    await ws.send(json.dumps({
        "type": "system",
        "message": "Please join a channel to start chatting",
    }))

    try:
        async for raw_message in ws:
            try:
                logger.debug("Received message from client: %s", raw_message)
                data = json.loads(raw_message)

                # ── JOIN ──────────────────────────────────────────────────────
                if data.get("type") == "join":
                    channel_name = data.get("channel")
                    if not channel_name or not isinstance(channel_name, str):
                        await ws.send(json.dumps({
                            "type": "error",
                            "message": "Channel name is required",
                        }))
                        continue

                    channels.setdefault(channel_name, set()).add(ws)
                    channel_clients = channels[channel_name]

                    # Confirmation 1: plain join confirmation
                    await ws.send(json.dumps({
                        "type": "system",
                        "message": f"Joined channel: {channel_name}",
                        "channel": channel_name,
                    }))

                    # Confirmation 2: result keyed by request id
                    logger.debug("Sending join confirmation for request: %s", data.get("id"))
                    await ws.send(json.dumps({
                        "type": "system",
                        "message": {
                            "id": data.get("id"),
                            "result": f"Connected to channel: {channel_name}",
                        },
                        "channel": channel_name,
                    }))

                    # Notify other members of the channel
                    for client in list(channel_clients):
                        if client is not ws:
                            try:
                                await client.send(json.dumps({
                                    "type": "system",
                                    "message": "A new user has joined the channel",
                                    "channel": channel_name,
                                }))
                            except Exception:
                                channel_clients.discard(client)

                # ── MESSAGE ───────────────────────────────────────────────────
                elif data.get("type") == "message":
                    channel_name = data.get("channel")
                    if not channel_name or not isinstance(channel_name, str):
                        await ws.send(json.dumps({
                            "type": "error",
                            "message": "Channel name is required",
                        }))
                        continue

                    channel_clients = channels.get(channel_name)
                    if channel_clients is None or ws not in channel_clients:
                        await ws.send(json.dumps({
                            "type": "error",
                            "message": "You must join the channel first",
                        }))
                        continue

                    # Broadcast to every member of the channel (including sender)
                    for client in list(channel_clients):
                        try:
                            logger.debug("Broadcasting message to client: %s", data.get("message"))
                            await client.send(json.dumps({
                                "type": "broadcast",
                                "message": data.get("message"),
                                "sender": "You" if client is ws else "User",
                                "channel": channel_name,
                            }))
                        except Exception:
                            channel_clients.discard(client)

            except json.JSONDecodeError as exc:
                logger.error("Error parsing message: %s", exc)
            except Exception as exc:
                logger.error("Error handling message: %s", exc)

    except websockets.exceptions.ConnectionClosedError:
        pass
    except websockets.exceptions.ConnectionClosedOK:
        pass
    finally:
        logger.info("Client disconnected")
        for channel_name, clients in list(channels.items()):
            if ws in clients:
                clients.discard(ws)
                for client in list(clients):
                    try:
                        await client.send(json.dumps({
                            "type": "system",
                            "message": "A user has left the channel",
                            "channel": channel_name,
                        }))
                    except Exception:
                        clients.discard(client)


async def start_relay(port: int = 3055):
    """Start the WebSocket relay server and return the server object (non-blocking)."""
    server = await websockets.serve(handler, "0.0.0.0", port)
    logger.info("WebSocket relay started on port %d", port)
    return server


async def main() -> None:
    port = int(os.environ.get("PORT", 3055))

    async with websockets.serve(handler, "0.0.0.0", port):
        logger.info("WebSocket server running on port %d", port)
        await asyncio.get_running_loop().create_future()


if __name__ == "__main__":
    asyncio.run(main())
