"""Shared utility helpers for the Talk-to-Figma MCP server."""

import json
from typing import Any, Dict, List, Optional

from mcp.types import TextContent


def rgba_to_hex(color: Any) -> str:
    """Convert an RGBA dict (0-1 float values) to a CSS hex string.

    If *color* is already a hex string it is returned unchanged.
    """
    if isinstance(color, str):
        return color  # already hex (or unexpected string — pass through)

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
    if fills:
        processed_fills = []
        for fill in fills:
            pf = dict(fill)
            pf.pop("boundVariables", None)
            pf.pop("imageRef", None)

            if "gradientStops" in pf:
                pf["gradientStops"] = [
                    {**{k: v for k, v in stop.items() if k != "boundVariables"},
                     "color": rgba_to_hex(stop["color"])} if "color" in stop
                    else {k: v for k, v in stop.items() if k != "boundVariables"}
                    for stop in pf["gradientStops"]
                ]

            if "color" in pf:
                pf["color"] = rgba_to_hex(pf["color"])

            processed_fills.append(pf)
        filtered["fills"] = processed_fills

    # Strokes
    strokes = node.get("strokes")
    if strokes:
        processed_strokes = []
        for stroke in strokes:
            ps = dict(stroke)
            ps.pop("boundVariables", None)
            if "color" in ps:
                ps["color"] = rgba_to_hex(ps["color"])
            processed_strokes.append(ps)
        filtered["strokes"] = processed_strokes

    for key in ("cornerRadius", "absoluteBoundingBox", "characters"):
        if key in node:
            filtered[key] = node[key]

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
        filtered["children"] = [
            c for c in (filter_figma_node(child) for child in node["children"])
            if c is not None
        ]

    return filtered


def ok(result: Any) -> List[TextContent]:
    """Wrap a successful result in an MCP TextContent list."""
    return [TextContent(type="text", text=json.dumps(result))]


def err(msg: str) -> List[TextContent]:
    """Wrap an error message in an MCP TextContent list."""
    return [TextContent(type="text", text=msg)]
