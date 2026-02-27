# talk-to-figma-mcp

MCP server and WebSocket relay for AI agent ↔ Figma communication.

## Setup

Run all commands from the **repo root** directory.

```bash
pip install -e .
```

## Run the WebSocket relay

```bash
# From repo root:
python src/mcp/socket_server.py
# Runs on port 3055 by default. Override with PORT env var.
```

## Run the MCP server

```bash
# From repo root:
python src/mcp/server.py
# Connects to localhost:3055 by default.
# Use --server=<hostname> to connect to a remote relay (uses wss://).
```

## AI Agent config

Use the full path to your Python 3 interpreter (find it with `which python3`):

```json
{
  "mcpServers": {
    "TalkToFigma": {
      "command": "python3",
      "args": ["/path-to-repo/src/mcp/server.py"]
    }
  }
}
```

## Module layout

| File | Purpose |
|------|---------|
| `server.py` | MCP server entry point; wires up MCP SDK, parses `--server` arg |
| `tools.py` | All `Tool` definitions (`ALL_TOOLS` list) |
| `handlers.py` | Tool handler implementations, dispatch dict |
| `utils.py` | Shared helpers: `ok`, `err`, `filter_figma_node`, `rgba_to_hex` |
| `ws_client.py` | `FigmaClient` — WebSocket connection, channel management, command correlation |
| `socket_server.py` | Standalone WebSocket relay (channel-based pub/sub) |
