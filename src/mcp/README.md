# talk-to-figma-mcp

MCP server and WebSocket relay for AI agent ↔ Figma communication.

## Setup

Run all commands from the **repo root** directory.

```bash
pip3 install -r src/mcp/requirements.txt
```

## Run the WebSocket relay

```bash
# From repo root:
python3 src/mcp/socket_server.py
# Runs on port 3055 by default. Override with PORT env var.
```

## Run the MCP server

```bash
# From repo root:
python3 src/mcp/server.py
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
