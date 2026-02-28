#!/usr/bin/env python3
"""
Talk to Figma — Relay Server Launcher

Run this script to start the WebSocket relay that connects
Claude Desktop to the Figma plugin. Keep the window open while working.

Usage:
    Mac / Linux:  python3 start.py
    Windows:      python start.py
"""

import os
import subprocess
import sys
from pathlib import Path


def check_python_version():
    if sys.version_info < (3, 10):
        print("ERROR: Python 3.10 or higher is required.")
        print(f"       You have Python {sys.version_info.major}.{sys.version_info.minor}.")
        print("       Download a newer version from: https://www.python.org/downloads/")
        print()
        input("Press Enter to exit...")
        sys.exit(1)


def setup_venv(repo_root: Path, venv_dir: Path, is_windows: bool) -> tuple[Path, Path]:
    """Create venv and install dependencies if not already done. Returns (venv_python, venv_relay)."""
    if is_windows:
        venv_python = venv_dir / "Scripts" / "python.exe"
        venv_pip    = venv_dir / "Scripts" / "pip.exe"
        venv_relay  = venv_dir / "Scripts" / "figma-relay.exe"
        venv_mcp    = venv_dir / "Scripts" / "figma-mcp.exe"
    else:
        venv_python = venv_dir / "bin" / "python"
        venv_pip    = venv_dir / "bin" / "pip"
        venv_relay  = venv_dir / "bin" / "figma-relay"
        venv_mcp    = venv_dir / "bin" / "figma-mcp"

    if not venv_python.exists():
        print("First-time setup — this only happens once.")
        print()
        print("  [1/2] Creating virtual environment...")
        subprocess.run([sys.executable, "-m", "venv", str(venv_dir)], check=True)

        print("  [2/2] Installing dependencies (may take a minute)...")
        subprocess.run(
            [str(venv_pip), "install", "-e", str(repo_root), "-q"],
            check=True,
        )
        print()
        print("  Setup complete!")
        print()
    else:
        # Silently ensure deps are up to date
        subprocess.run(
            [str(venv_pip), "install", "-e", str(repo_root), "-q"],
            check=True,
        )

    return venv_python, venv_relay, venv_mcp


def print_claude_config(venv_mcp: Path, is_windows: bool):
    """Print the Claude Desktop MCP configuration the user needs to paste."""
    if is_windows:
        config_path = Path(os.environ.get("APPDATA", "~")) / "Claude" / "claude_desktop_config.json"
        # JSON requires forward slashes or escaped backslashes
        cmd = str(venv_mcp).replace("\\", "\\\\")
    else:
        config_path = Path.home() / "Library" / "Application Support" / "Claude" / "claude_desktop_config.json"
        cmd = str(venv_mcp)

    config_json = f'''{{\n  "mcpServers": {{\n    "TalkToFigma": {{\n      "command": "{cmd}"\n    }}\n  }}\n}}'''

    print("=" * 60)
    print("  CLAUDE DESKTOP CONFIGURATION")
    print("=" * 60)
    print()
    print("  1. Open this file (create it if it doesn't exist):")
    print(f"     {config_path}")
    print()
    print("  2. Paste the following into the file:")
    print()
    for line in config_json.splitlines():
        print(f"     {line}")
    print()
    print("  Note: if the file already has content, merge the")
    print('  "TalkToFigma" block under the existing "mcpServers" key.')
    print()
    print("  3. Save the file, then quit and reopen Claude Desktop.")
    print("=" * 60)
    print()


def start_relay(venv_relay: Path):
    print("Starting WebSocket relay on port 3055...")
    print("Keep this window open while using the Figma plugin.")
    print("Press Ctrl+C to stop.")
    print()
    try:
        subprocess.run([str(venv_relay)])
    except KeyboardInterrupt:
        print()
        print("Relay stopped.")


def main():
    check_python_version()

    repo_root  = Path(__file__).parent.resolve()
    venv_dir   = repo_root / ".venv"
    is_windows = sys.platform == "win32"

    try:
        venv_python, venv_relay, venv_mcp = setup_venv(repo_root, venv_dir, is_windows)
    except subprocess.CalledProcessError as exc:
        print(f"\nERROR during setup: {exc}")
        print("Try running with administrator/sudo privileges, or check your internet connection.")
        input("\nPress Enter to exit...")
        sys.exit(1)

    print_claude_config(venv_mcp, is_windows)
    start_relay(venv_relay)


if __name__ == "__main__":
    main()
