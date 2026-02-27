# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

MCP integration between AI assistants (Cursor, Claude, etc.) and Figma. Enables reading and programmatically modifying Figma designs through a 3-component architecture.

## Commands

```bash
# Install Python dependencies (from repo root)
pip install -e .

# Start the WebSocket relay server
python -m figma_mcp.socket_server
# or: python src/figma_mcp/socket_server.py

# Start the MCP server
python -m figma_mcp.server [--server=<hostname>]
# or: python src/figma_mcp/server.py [--server=<hostname>]
```

No test suite is present in this repository.

## Architecture

```
AI Assistant (MCP Client)
    ↕ stdio (MCP protocol)
src/mcp/server.py         ← MCP server entry point
    ↕ WebSocket (port 3055)
src/mcp/socket_server.py  ← WebSocket relay server
    ↕ WebSocket (port 3055)
src/figma_plugin/           ← Figma plugin (code.js + ui.html)
    ↕ Figma Plugin API
Figma Document
```

**`src/mcp/server.py`** — MCP server entry point. Parses `--server=<hostname>` CLI arg; `localhost` uses `ws://`, anything else uses `wss://`. Wires up the MCP SDK and delegates to `tools.py` and `handlers.py`. All logging goes to stderr.

**`src/mcp/tools.py`** — All MCP tool definitions (`Tool` objects with names, descriptions, and JSON schemas). `ALL_TOOLS` list is imported by `server.py`.

**`src/mcp/handlers.py`** — Tool handler implementations. Each tool maps to an async function; `handle_tool()` dispatches via a dict.

**`src/mcp/utils.py`** — Shared helpers: `ok()`, `err()`, `filter_figma_node()`, `rgba_to_hex()`.

**`src/mcp/ws_client.py`** — `FigmaClient` class managing the WebSocket connection to the relay, channel joining, command dispatch, and response correlation.

**`src/mcp/socket_server.py`** — Python WebSocket relay server using `websockets` library. Listens on port 3055 by default; set `PORT` env var to override.

**`src/figma_plugin/`** — Plain JS, no build step. `code.js` = Figma plugin sandbox (all Figma API calls), `ui.html` = holds the WebSocket connection to the relay.

## Dependencies

Managed via `pyproject.toml` (replaces `requirements.txt`). Install with:

```bash
pip install -e .
```

Entry points defined in `pyproject.toml`:
- `figma-mcp` → `mcp.server:main`
- `figma-relay` → `mcp.socket_server:main`

## Dev Setup

Point MCP config to the Python server directly:
```json
{
  "mcpServers": {
    "TalkToFigma": {
      "command": "python",
      "args": ["/path-to-repo/src/mcp/server.py"]
    }
  }
}
```

**`AGENT-SETUP.md`**: End-user AI setup guide — not codebase documentation, ignore when working on the project.

## Gotchas

- **Tool name contract**: MCP tool names in `tools.py` must exactly match command names expected by `code.js` — they share a string contract.
- **`join_channel` first**: Must be called before any other tool; `FigmaClient` enforces this with `_channel` state.
- **Relay is separate**: The relay server (`socket_server.py`) does not run as part of the MCP server — start it independently.
- **Manifest network lock**: `src/figma_plugin/manifest.json` only permits `ws://localhost:3055`. Update it for remote/WSS deployments.
