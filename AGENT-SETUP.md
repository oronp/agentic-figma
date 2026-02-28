# MCP Setup Guide — Talk to Figma

> **For AI agents:** Parse and execute the steps below in order on behalf of the user. Each step includes the command to run and its expected result.

---

## Step 1 — Check Python

```bash
python3 --version
```

- **Pass:** `Python 3.10.x` or higher → continue to Step 2
- **Fail:** Below 3.10 or not found → install Python via Homebrew (see below)

> On Windows use `python` instead of `python3` throughout this guide.

### Installing Python via Homebrew (macOS / Linux)

**1. Check if Homebrew is installed:**

```bash
brew --version
```

**If Homebrew is not found**, install it:

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

After installation, follow any shell setup instructions Homebrew prints (e.g. adding it to `PATH`). Then verify:

```bash
brew --version
```

**2. Install Python 3:**

```bash
brew install python3
```

**3. Confirm the version:**

```bash
python3 --version
```

Expected: `Python 3.10.x` or higher. If the shell still reports the old version, open a new terminal tab and retry.

---

## Step 2 — Install Dependencies

From the repo root:

```bash
pip3 install -e .
```

Expected: output ends with `Successfully installed ...`

Verify:
```bash
python3 -c "import figma_mcp; print('ok')"
```

> On Windows use `pip` instead of `pip3`.

---

## Step 3 — Configure the AI Client

Find the `figma-mcp` binary installed in the previous step:

```bash
python3 -c "import shutil, sys, pathlib; p=shutil.which('figma-mcp'); print(p if p else pathlib.Path(sys.executable).parent / 'figma-mcp')"
```

Use the path it prints as `<figma-mcp-path>` in the config below.

### Claude Desktop

| OS      | Config file location |
|---------|----------------------|
| macOS   | `~/Library/Application Support/Claude/claude_desktop_config.json` |
| Windows | `%APPDATA%\Claude\claude_desktop_config.json` |

```json
{
  "mcpServers": {
    "TalkToFigma": {
      "command": "<figma-mcp-path>"
    }
  }
}
```

If the file already has content, merge the `"TalkToFigma"` block into the existing `"mcpServers"` object.

### Cursor

Create or update `.cursor/mcp.json` in the project root with the same JSON above.

After saving the config, ask the user to **fully restart** their AI client.

---

## Step 4 — Start the WebSocket Relay

Tell the user to open a terminal in the project folder and run:

```bash
# macOS / Linux
python3 start.py

# Windows
python start.py
```

`start.py` handles first-time venv setup automatically and then starts the relay on port 3055. **The terminal must stay open** while the plugin is in use.

Verify the relay is up:

```bash
python3 -c "import socket; s=socket.socket(); s.settimeout(2); ok=s.connect_ex(('localhost',3055))==0; s.close(); print('relay running' if ok else 'relay NOT running')"
```

---

## Step 5 — Install and Connect the Figma Plugin

Tell the user to:

1. Install the plugin from https://www.figma.com/community/plugin/1485687494525374295
2. Open any Figma file
3. Go to **Plugins → Talk to Figma MCP Plugin**
4. Set the WebSocket URL to `ws://localhost:3055`
5. Click **Connect** — the status should change to **Connected**

---

## Step 6 — Verify

With the relay running and the Figma plugin connected, ask the AI client:

1. `join_channel` → expect a success message
2. `get_document_info` → expect JSON describing the open Figma file

If both return results, setup is complete.

---

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| `pip3 install` permission error | Re-run with `pip3 install --user -e .` |
| Port 3055 already in use | Stop the existing relay (`Ctrl+C` in its terminal), then re-run `start.py` |
| Plugin won't connect | Confirm relay is running (Step 4 verify command), then click Disconnect → Connect in the plugin |
| MCP not detected in AI client | Double-check the config file path and JSON validity; fully restart the client |
| `figma-mcp` path not found | Use the full venv path: `<repo>/.venv/bin/figma-mcp` (macOS/Linux) or `<repo>\.venv\Scripts\figma-mcp.exe` (Windows) |
