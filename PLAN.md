# Plan: Remove JS Server and All Related Files

## Goal
Remove all JavaScript/TypeScript server infrastructure, keeping only:
- `src/cursor_mcp_plugin/` — Figma plugin (still needed; talks to relay over WebSocket regardless of language)
- `src/python_mcp/` — Python MCP server + relay (the replacement)
- `DRAGME-PYTHON.md` — Python setup guide
- `LICENSE`, `.gitignore`, `readme.md` (updated), `CLAUDE.md` (updated)

---

## Files to DELETE

### JS/TS Source
| Path | Reason |
|------|--------|
| `src/talk_to_figma_mcp/` (entire dir) | TypeScript MCP server — replaced by `src/python_mcp/server.py` |
| `src/socket.ts` | Bun WebSocket relay — replaced by `src/python_mcp/socket_server.py` |

### Build Infrastructure
| Path | Reason |
|------|--------|
| `package.json` | Root npm/bun package config — no JS to build |
| `bun.lock` | Bun lock file |
| `tsconfig.json` | TypeScript root config |
| `tsup.config.ts` | tsup bundler config |
| `dist/` (entire dir) | Compiled JS output |
| `scripts/setup.sh` | Creates `.cursor/mcp.json` pointing to npm package |
| `scripts/` (dir, if empty) | Empty after removing setup.sh |

### Deployment / Docs
| Path | Reason |
|------|--------|
| `smithery.yaml` | Deploys JS server via `bunx cursor-talk-to-figma-mcp` |
| `Dockerfile` | Builds and runs Bun/JS MCP server |
| `DRAGME.md` | End-user setup guide for JS/Bun path |

---

## Files to UPDATE

### `CLAUDE.md`
- Replace JS architecture diagram with Python equivalent
- Replace bun commands with python commands
- Remove gotchas that are JS-specific (nested package.json, bun socket, etc.)

### `readme.md`
- Remove JS/Bun quick-start and dev-setup sections
- Point users to Python path and `DRAGME-PYTHON.md`
- Remove references to npm publish workflow

### `.gitignore`
- Remove JS-specific entries: `node_modules/`, `dist/`
- Keep Python entry: `src/python_mcp/.venv/`

---

## Files to KEEP AS-IS

| Path | Reason |
|------|--------|
| `src/cursor_mcp_plugin/` | Figma plugin runs inside Figma; connects to relay on port 3055 over WebSocket — language-agnostic |
| `src/python_mcp/server.py` | Python MCP server (the new primary) |
| `src/python_mcp/socket_server.py` | Python WebSocket relay |
| `src/python_mcp/requirements.txt` | Python deps |
| `src/python_mcp/README.md` | Python docs |
| `DRAGME-PYTHON.md` | End-user Python setup guide |
| `LICENSE` | Unchanged |

---

## Execution Order

1. Delete JS/TS source dirs and files
2. Delete build infrastructure files
3. Delete deployment/doc files
4. Update `CLAUDE.md`
5. Update `readme.md`
6. Update `.gitignore`
7. Commit and push to `claude/plan-remove-js-server-JeMbU`
