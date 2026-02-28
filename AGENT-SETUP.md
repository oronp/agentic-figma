# Talk to Figma — Setup Guide

Connect **Claude Desktop** to your Figma designs. Once set up, you can ask Claude to read, inspect, and edit your Figma files in plain English — no coding required.

---

## What You Need

- [Claude Desktop](https://claude.ai/download) installed on your computer
- [Python 3.10 or higher](https://www.python.org/downloads/) installed
- A Figma account with at least one file open

---

## One-Time Setup

### Step 1 — Get the project files

On this page, click the green **Code** button → **Download ZIP**. Unzip the folder somewhere easy to find (Desktop or Documents works great).

### Step 2 — Install Python 3.10+

**Already have Python?** Skip this step if `python3 --version` (Mac) or `python --version` (Windows) shows 3.10 or higher.

**Mac:**
1. Go to [python.org/downloads](https://www.python.org/downloads/) and download the latest installer
2. Run it and accept the defaults
3. Open a new Terminal window and confirm: `python3 --version`

**Windows:**
1. Go to [python.org/downloads](https://www.python.org/downloads/) and download the latest installer
2. Run it — **on the first screen, check "Add Python to PATH"** before clicking Install
3. Open a new PowerShell window and confirm: `python --version`

### Step 3 — Run the start script

Open a terminal in the project folder and run:

**Mac / Linux:**
```bash
python3 start.py
```

**Windows:**
```
python start.py
```

> **How to open a terminal in the project folder:**
> - **Mac:** Open Terminal, then drag the project folder into the Terminal window and press Enter
> - **Windows:** Hold **Shift** and right-click the project folder → **Open PowerShell window here**

The first run installs everything automatically (takes about a minute). After that it prints the configuration you need for the next step, then starts the relay server.

### Step 4 — Configure Claude Desktop

After running `start.py`, you'll see something like this in the terminal:

```
============================================================
  CLAUDE DESKTOP CONFIGURATION
============================================================

  1. Open this file (create it if it doesn't exist):
     /Users/yourname/Library/Application Support/Claude/claude_desktop_config.json

  2. Paste the following into the file:

     {
       "mcpServers": {
         "TalkToFigma": {
           "command": "/Users/yourname/projects/talk-to-figma-mcp/.venv/bin/figma-mcp"
         }
       }
     }
```

Follow those instructions:

1. Open the config file shown (use a plain text editor like TextEdit on Mac or Notepad on Windows)
2. Paste in the JSON block exactly as shown
3. If the file already has content, add the `"TalkToFigma"` block inside the existing `"mcpServers"` section
4. Save the file
5. **Fully quit and reopen Claude Desktop** (on Mac: ⌘Q, on Windows: right-click the tray icon → Quit)

**Finding the config file if you can't locate it:**
- **Mac:** In Finder, press `Cmd + Shift + G`, paste `~/Library/Application Support/Claude/` and press Enter
- **Windows:** Press `Win + R`, type `%APPDATA%\Claude\` and press Enter

### Step 5 — Install the Figma plugin

1. Open the [Talk to Figma MCP plugin page](https://www.figma.com/community/plugin/1485687494525374295)
2. Click **Install**
3. Open any Figma file
4. Click the **Plugins** menu → **Talk to Figma MCP Plugin**
5. Set the WebSocket URL to: `ws://localhost:3055`
6. Click **Connect** — the status should change to **Connected**

---

## Daily Use

Each time you want to use Talk to Figma:

1. **Start the relay** — open a terminal in the project folder and run `python3 start.py` (Mac) or `python start.py` (Windows). Keep this window open.
2. **Open Figma** — open the plugin (Plugins → Talk to Figma MCP Plugin) and click **Connect**
3. **Open Claude Desktop** — it connects to the MCP server automatically

Then in Claude, start by saying:
> "Join the channel"

After that, try:
- *"What's in my Figma document?"*
- *"List all the text layers"*
- *"Change the button background to blue"*

---

## Troubleshooting

**Python not found after installing**
Close your terminal, open a new one, and try again. On Mac use `python3`; on Windows use `python`.

**First-time setup fails**
Make sure you have an internet connection. If you see a permissions error on Mac/Linux, try:
```bash
python3 -m venv .venv && .venv/bin/pip install -e . -q
```

**"Port 3055 is already in use"**
Another copy of the relay is already running. Find the terminal window where `start.py` is running and press **Ctrl+C** to stop it, then run `start.py` again.

**Claude Desktop doesn't show TalkToFigma as connected**
- Confirm the config file is saved and contains valid JSON (no missing commas or brackets)
- Fully quit Claude Desktop (not just close the window) and reopen it
- Make sure the path in the config points to your actual project folder

**Figma plugin won't connect**
- Make sure `start.py` is still running in the terminal
- Check that the URL in the plugin is exactly `ws://localhost:3055`
- Try clicking **Disconnect**, then **Connect** again
- Refresh the Figma page and reconnect

**Claude can read Figma but changes don't show up**
Make sure you're working in an open Figma file and the plugin shows **Connected**. Ask Claude to `join_channel` again if needed.
