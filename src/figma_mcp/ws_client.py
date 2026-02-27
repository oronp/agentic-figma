"""WebSocket client for communicating with the Figma relay server."""

import asyncio
import json
import logging
import uuid
from typing import Any, Dict, Optional

logger = logging.getLogger("talk_to_figma_mcp")


class FigmaClient:
    """Manages a single WebSocket connection to the Figma relay server."""

    def __init__(self, ws_base: str) -> None:
        self.ws_base = ws_base
        self._ws_conn: Optional[Any] = None
        self._pending: Dict[str, asyncio.Future] = {}
        self._channel: Optional[str] = None
        self._listen_task: Optional[asyncio.Task] = None

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    @property
    def current_channel(self) -> Optional[str]:
        return self._channel

    async def connect(self, port: int = 3055) -> None:
        """Connect to the WebSocket relay server and start the listener."""
        import websockets

        if self._ws_conn is not None:
            logger.info("Already connected to Figma")
            return

        ws_url = f"{self.ws_base}:{port}" if "localhost" in self.ws_base else self.ws_base
        logger.info("Connecting to Figma socket server at %s...", ws_url)

        try:
            self._ws_conn = await websockets.connect(ws_url)
            logger.info("Connected to Figma socket server")
            self._listen_task = asyncio.get_running_loop().create_task(self._listen())
        except Exception as exc:
            logger.error("Failed to connect to Figma: %s", exc)
            self._ws_conn = None

    async def join_channel(self, channel_name: str) -> Any:
        """Send a join message and wait for the relay to confirm."""
        if self._ws_conn is None:
            raise RuntimeError("Not connected to Figma")

        result = await self.send_command("join", {"channel": channel_name}, timeout_ms=30000)
        self._channel = channel_name
        logger.info("Joined channel: %s", channel_name)
        return result

    async def send_command(
        self,
        command: str,
        params: Optional[Dict] = None,
        timeout_ms: int = 30000,
    ) -> Any:
        """Send a command to Figma via the relay and await the response."""
        if self._ws_conn is None:
            await self.connect()
        if self._ws_conn is None:
            raise RuntimeError("Not connected to Figma. Is the relay server running?")

        is_join = command == "join"
        if not is_join and self._channel is None:
            raise RuntimeError("Must join a channel before sending commands")

        if params is None:
            params = {}

        req_id = str(uuid.uuid4())
        loop = asyncio.get_running_loop()
        future: asyncio.Future = loop.create_future()
        self._pending[req_id] = future

        request = {
            "id": req_id,
            "type": "join" if is_join else "message",
            "channel": params.get("channel") if is_join else self._channel,
            "message": {
                "id": req_id,
                "command": command,
                "params": {**params, "commandId": req_id},
            },
        }

        logger.info("Sending command to Figma: %s", command)
        logger.debug("Request details: %s", json.dumps(request))
        await self._ws_conn.send(json.dumps(request))

        timeout_sec = timeout_ms / 1000.0
        try:
            return await asyncio.wait_for(future, timeout=timeout_sec)
        except asyncio.TimeoutError:
            self._pending.pop(req_id, None)
            raise RuntimeError(f"Request to Figma timed out after {timeout_ms // 1000}s")

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    async def _listen(self) -> None:
        """Background task: read WS messages and resolve/reject pending futures."""
        try:
            async for raw in self._ws_conn:
                try:
                    json_data = json.loads(raw)

                    if json_data.get("type") == "progress_update":
                        msg = json_data.get("message", {})
                        progress_data = msg.get("data", {}) if isinstance(msg, dict) else {}
                        cmd_type = progress_data.get("commandType", "unknown")
                        progress = progress_data.get("progress", 0)
                        message = progress_data.get("message", "")
                        logger.info(
                            "Progress update for %s: %s%% - %s",
                            cmd_type, progress, message,
                        )
                        if (
                            progress_data.get("status") == "completed"
                            and progress_data.get("progress") == 100
                        ):
                            logger.info(
                                "Operation %s completed, waiting for final result", cmd_type
                            )
                        continue

                    my_response = json_data.get("message")
                    logger.debug("Received message: %s", json.dumps(my_response))

                    req_id = my_response.get("id") if isinstance(my_response, dict) else None
                    if req_id and req_id in self._pending:
                        future = self._pending.pop(req_id)
                        if not future.done():
                            if my_response.get("error"):
                                logger.error("Error from Figma: %s", my_response["error"])
                                future.set_exception(RuntimeError(my_response["error"]))
                            elif my_response.get("result") is not None:
                                future.set_result(my_response["result"])
                    else:
                        logger.info(
                            "Received broadcast message: %s", json.dumps(my_response)
                        )

                except json.JSONDecodeError as exc:
                    logger.error("Error parsing message: %s", exc)
                except Exception as exc:
                    logger.error("Error handling message: %s", exc)

        except Exception as exc:
            logger.info("WebSocket listen loop ended: %s", exc)

        finally:
            logger.info("Disconnected from Figma socket server")
            for future in self._pending.values():
                if not future.done():
                    future.set_exception(RuntimeError("Connection closed"))
            self._pending.clear()
            self._ws_conn = None
