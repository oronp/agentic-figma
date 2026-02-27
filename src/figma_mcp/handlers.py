"""MCP tool handler implementations for the Talk-to-Figma MCP server.

Each tool is an independent async function that receives the raw arguments dict
and a FigmaClient. handle_tool() looks up the right function in _DISPATCH and
calls it; unknown tool names return an error without an exception.
"""

import asyncio
import json
from typing import Any, Callable, Coroutine, Dict, List

import mcp.types as types
from mcp.types import ImageContent, TextContent

from .utils import err, filter_figma_node, ok
from .ws_client import FigmaClient

# Type alias for handler functions
_Handler = Callable[
    [Dict[str, Any], FigmaClient],
    Coroutine[Any, Any, List[TextContent | ImageContent]],
]


# ── Group A: Document & Selection ────────────────────────────────────────────

async def _get_document_info(args: Dict, client: FigmaClient):
    result = await client.send_command("get_document_info")
    return ok(result)


async def _get_selection(args: Dict, client: FigmaClient):
    result = await client.send_command("get_selection")
    return ok(result)


async def _read_my_design(args: Dict, client: FigmaClient):
    result = await client.send_command("read_my_design", {})
    return ok(result)


async def _get_node_info(args: Dict, client: FigmaClient):
    if "nodeId" not in args:
        return err("Missing required parameter: nodeId")
    result = await client.send_command("get_node_info", {"nodeId": args["nodeId"]})
    return ok(filter_figma_node(result))


async def _get_nodes_info(args: Dict, client: FigmaClient):
    if "nodeIds" not in args:
        return err("Missing required parameter: nodeIds")
    results = await asyncio.gather(
        *[client.send_command("get_node_info", {"nodeId": nid}) for nid in args["nodeIds"]],
        return_exceptions=True,
    )
    filtered = [
        filter_figma_node(r) for r in results if not isinstance(r, Exception)
    ]
    return ok([f for f in filtered if f is not None])


async def _get_styles(args: Dict, client: FigmaClient):
    return ok(await client.send_command("get_styles"))


async def _get_local_components(args: Dict, client: FigmaClient):
    return ok(await client.send_command("get_local_components"))


async def _get_annotations(args: Dict, client: FigmaClient):
    params: Dict[str, Any] = {}
    if "nodeId" in args:
        params["nodeId"] = args["nodeId"]
    if "includeCategories" in args:
        params["includeCategories"] = args["includeCategories"]
    return ok(await client.send_command("get_annotations", params))


async def _get_reactions(args: Dict, client: FigmaClient):
    if "nodeIds" not in args:
        return err("Missing required parameter: nodeIds")
    return ok(await client.send_command("get_reactions", {"nodeIds": args["nodeIds"]}))


# ── Group B: Create & Modify ──────────────────────────────────────────────────

async def _create_rectangle(args: Dict, client: FigmaClient):
    x, y, w, h = args.get("x"), args.get("y"), args.get("width"), args.get("height")
    if any(v is None for v in (x, y, w, h)):
        return err("create_rectangle requires x, y, width, and height")
    params: Dict[str, Any] = {"x": x, "y": y, "width": w, "height": h,
                               "name": args.get("name") or "Rectangle"}
    if args.get("parentId") is not None:
        params["parentId"] = args["parentId"]
    return ok(await client.send_command("create_rectangle", params))


async def _create_frame(args: Dict, client: FigmaClient):
    x, y, w, h = args.get("x"), args.get("y"), args.get("width"), args.get("height")
    if any(v is None for v in (x, y, w, h)):
        return err("create_frame requires x, y, width, and height")
    params: Dict[str, Any] = {
        "x": x, "y": y, "width": w, "height": h,
        "name": args.get("name") or "Frame",
        "fillColor": args.get("fillColor") or {"r": 1, "g": 1, "b": 1, "a": 1},
    }
    for key in (
        "parentId", "strokeColor", "strokeWeight", "layoutMode", "layoutWrap",
        "paddingTop", "paddingRight", "paddingBottom", "paddingLeft",
        "primaryAxisAlignItems", "counterAxisAlignItems",
        "layoutSizingHorizontal", "layoutSizingVertical", "itemSpacing",
    ):
        if args.get(key) is not None:
            params[key] = args[key]
    return ok(await client.send_command("create_frame", params))


async def _create_text(args: Dict, client: FigmaClient):
    x, y, text = args.get("x"), args.get("y"), args.get("text")
    if any(v is None for v in (x, y, text)):
        return err("create_text requires x, y, and text")
    params: Dict[str, Any] = {
        "x": x, "y": y, "text": text,
        "fontSize": args.get("fontSize") if args.get("fontSize") is not None else 14,
        "fontWeight": args.get("fontWeight") if args.get("fontWeight") is not None else 400,
        "fontColor": args.get("fontColor") or {"r": 0, "g": 0, "b": 0, "a": 1},
        "name": args.get("name") or "Text",
    }
    if args.get("parentId") is not None:
        params["parentId"] = args["parentId"]
    return ok(await client.send_command("create_text", params))


async def _create_component_instance(args: Dict, client: FigmaClient):
    if not args.get("componentKey"):
        return err("create_component_instance requires componentKey")
    params: Dict[str, Any] = {"componentKey": args["componentKey"]}
    for key in ("x", "y"):
        if args.get(key) is not None:
            params[key] = args[key]
    return ok(await client.send_command("create_component_instance", params))


async def _clone_node(args: Dict, client: FigmaClient):
    if not args.get("nodeId"):
        return err("clone_node requires nodeId")
    params: Dict[str, Any] = {"nodeId": args["nodeId"]}
    for key in ("x", "y"):
        if args.get(key) is not None:
            params[key] = args[key]
    return ok(await client.send_command("clone_node", params))


async def _delete_node(args: Dict, client: FigmaClient):
    if not args.get("nodeId"):
        return err("delete_node requires nodeId")
    await client.send_command("delete_node", {"nodeId": args["nodeId"]})
    return ok({"deleted": args["nodeId"]})


async def _delete_multiple_nodes(args: Dict, client: FigmaClient):
    if not args.get("nodeIds"):
        return err("delete_multiple_nodes requires nodeIds")
    return ok(await client.send_command("delete_multiple_nodes", {"nodeIds": args["nodeIds"]}))


# ── Group C: Style & Appearance ───────────────────────────────────────────────

async def _set_fill_color(args: Dict, client: FigmaClient):
    node_id, r, g, b = args.get("nodeId"), args.get("r"), args.get("g"), args.get("b")
    if any(v is None for v in (node_id, r, g, b)):
        return err("set_fill_color requires nodeId, r, g, and b")
    if not all(isinstance(v, (int, float)) for v in (r, g, b)):
        return err("set_fill_color: r, g, b must be numbers in range 0-1")
    a = args.get("a", 1)
    result = await client.send_command("set_fill_color",
                                       {"nodeId": node_id, "color": {"r": r, "g": g, "b": b, "a": a}})
    node_name = (result or {}).get("name", node_id) if isinstance(result, dict) else node_id
    return [TextContent(type="text", text=f'Set fill color of node "{node_name}" to RGBA({r}, {g}, {b}, {a})')]


async def _set_stroke_color(args: Dict, client: FigmaClient):
    node_id, r, g, b = args.get("nodeId"), args.get("r"), args.get("g"), args.get("b")
    if any(v is None for v in (node_id, r, g, b)):
        return err("set_stroke_color requires nodeId, r, g, and b")
    if not all(isinstance(v, (int, float)) for v in (r, g, b)):
        return err("set_stroke_color: r, g, b must be numbers in range 0-1")
    a = args.get("a", 1)
    weight = args.get("weight", 1)
    result = await client.send_command("set_stroke_color",
                                       {"nodeId": node_id, "color": {"r": r, "g": g, "b": b, "a": a}, "weight": weight})
    node_name = (result or {}).get("name", node_id) if isinstance(result, dict) else node_id
    return [TextContent(type="text", text=f'Set stroke color of node "{node_name}" to RGBA({r}, {g}, {b}, {a}) with weight {weight}')]


async def _set_corner_radius(args: Dict, client: FigmaClient):
    node_id, radius = args.get("nodeId"), args.get("radius")
    if node_id is None or radius is None:
        return err("set_corner_radius requires nodeId and radius")
    result = await client.send_command("set_corner_radius", {
        "nodeId": node_id, "radius": radius,
        "corners": args.get("corners") or [True, True, True, True],
    })
    node_name = (result or {}).get("name", node_id) if isinstance(result, dict) else node_id
    return [TextContent(type="text", text=f'Set corner radius of node "{node_name}" to {radius}px')]


async def _set_text_content(args: Dict, client: FigmaClient):
    node_id, text = args.get("nodeId"), args.get("text")
    if node_id is None or text is None:
        return err("set_text_content requires nodeId and text")
    result = await client.send_command("set_text_content", {"nodeId": node_id, "text": text})
    node_name = (result or {}).get("name", node_id) if isinstance(result, dict) else node_id
    return [TextContent(type="text", text=f'Updated text content of node "{node_name}" to "{text}"')]


async def _set_multiple_text_contents(args: Dict, client: FigmaClient):
    node_id, text = args.get("nodeId"), args.get("text")
    if node_id is None:
        return err("set_multiple_text_contents requires nodeId")
    if not text:
        return err("set_multiple_text_contents requires text")
    if len(text) == 0:
        return [TextContent(type="text", text="No text provided")]
    result = await client.send_command("set_multiple_text_contents", {"nodeId": node_id, "text": text})
    typed = result if isinstance(result, dict) else {}
    return ok({
        "success": typed.get("success", True),
        "replacementsApplied": typed.get("replacementsApplied", 0),
        "replacementsFailed": typed.get("replacementsFailed", 0),
        "totalReplacements": typed.get("totalReplacements", len(text)),
        "completedInChunks": typed.get("completedInChunks", 0),
    })


async def _export_node_as_image(args: Dict, client: FigmaClient):
    if not args.get("nodeId"):
        return err("export_node_as_image requires nodeId")
    result = await client.send_command("export_node_as_image", {
        "nodeId": args["nodeId"],
        "format": args.get("format", "PNG"),
        "scale": args.get("scale", 1),
    })
    typed = result if isinstance(result, dict) else {}
    image_data = typed.get("imageData")
    if not image_data:
        return err("export_node_as_image: plugin returned no image data")
    return [types.ImageContent(type="image", data=image_data, mimeType=typed.get("mimeType", "image/png"))]


# ── Group D: Layout & Positioning ─────────────────────────────────────────────

async def _move_node(args: Dict, client: FigmaClient):
    node_id, x, y = args.get("nodeId"), args.get("x"), args.get("y")
    if node_id is None:
        return err("move_node requires nodeId")
    if x is None or y is None:
        return err("move_node requires x and y")
    if not isinstance(x, (int, float)) or not isinstance(y, (int, float)):
        return err("move_node: x and y must be numbers")
    result = await client.send_command("move_node", {"nodeId": node_id, "x": x, "y": y})
    node_name = (result or {}).get("name", node_id) if isinstance(result, dict) else node_id
    return [TextContent(type="text", text=f'Moved node "{node_name}" to position ({x}, {y})')]


async def _resize_node(args: Dict, client: FigmaClient):
    node_id, width, height = args.get("nodeId"), args.get("width"), args.get("height")
    if node_id is None:
        return err("resize_node requires nodeId")
    if width is None or height is None:
        return err("resize_node requires width and height")
    if not isinstance(width, (int, float)) or not isinstance(height, (int, float)):
        return err("resize_node: width and height must be numbers")
    result = await client.send_command("resize_node", {"nodeId": node_id, "width": width, "height": height})
    node_name = (result or {}).get("name", node_id) if isinstance(result, dict) else node_id
    return [TextContent(type="text", text=f'Resized node "{node_name}" to width {width} and height {height}')]


async def _set_layout_mode(args: Dict, client: FigmaClient):
    node_id, layout_mode = args.get("nodeId"), args.get("layoutMode")
    if node_id is None:
        return err("set_layout_mode requires nodeId")
    if layout_mode is None:
        return err("set_layout_mode requires layoutMode")
    layout_wrap = args.get("layoutWrap", "NO_WRAP")
    result = await client.send_command("set_layout_mode",
                                       {"nodeId": node_id, "layoutMode": layout_mode, "layoutWrap": layout_wrap})
    node_name = (result or {}).get("name", node_id) if isinstance(result, dict) else node_id
    wrap_suffix = f" with {args['layoutWrap']}" if "layoutWrap" in args else ""
    return [TextContent(type="text", text=f'Set layout mode of frame "{node_name}" to {layout_mode}{wrap_suffix}')]


async def _set_padding(args: Dict, client: FigmaClient):
    node_id = args.get("nodeId")
    if node_id is None:
        return err("set_padding requires nodeId")
    top, right, bottom, left = args.get("top"), args.get("right"), args.get("bottom"), args.get("left")
    for name, val in (("top", top), ("right", right), ("bottom", bottom), ("left", left)):
        if val is not None and not isinstance(val, (int, float)):
            return err(f"set_padding: {name} must be a number")
    if not any(v is not None for v in (top, right, bottom, left)):
        return err("set_padding requires at least one of: top, right, bottom, left")
    params: Dict[str, Any] = {"nodeId": node_id}
    mapping = {"paddingTop": top, "paddingRight": right, "paddingBottom": bottom, "paddingLeft": left}
    params.update({k: v for k, v in mapping.items() if v is not None})
    result = await client.send_command("set_padding", params)
    node_name = (result or {}).get("name", node_id) if isinstance(result, dict) else node_id
    parts = [f"{s}: {v}" for s, v in (("top", top), ("right", right), ("bottom", bottom), ("left", left)) if v is not None]
    return [TextContent(type="text", text=f'Set padding ({", ".join(parts)}) for frame "{node_name}"')]


async def _set_axis_align(args: Dict, client: FigmaClient):
    node_id = args.get("nodeId")
    if node_id is None:
        return err("set_axis_align requires nodeId")
    primary, counter = args.get("primaryAxisAlignItems"), args.get("counterAxisAlignItems")
    if primary is None and counter is None:
        return err("set_axis_align requires at least one of: primaryAxisAlignItems, counterAxisAlignItems")
    params: Dict[str, Any] = {"nodeId": node_id}
    if primary is not None:
        params["primaryAxisAlignItems"] = primary
    if counter is not None:
        params["counterAxisAlignItems"] = counter
    result = await client.send_command("set_axis_align", params)
    node_name = (result or {}).get("name", node_id) if isinstance(result, dict) else node_id
    parts = ([f"primary: {primary}"] if primary else []) + ([f"counter: {counter}"] if counter else [])
    return [TextContent(type="text", text=f'Set axis alignment ({", ".join(parts)}) for frame "{node_name}"')]


async def _set_layout_sizing(args: Dict, client: FigmaClient):
    node_id = args.get("nodeId")
    if node_id is None:
        return err("set_layout_sizing requires nodeId")
    h_sizing, v_sizing = args.get("layoutSizingHorizontal"), args.get("layoutSizingVertical")
    if h_sizing is None and v_sizing is None:
        return err("set_layout_sizing requires at least one of: layoutSizingHorizontal, layoutSizingVertical")
    params: Dict[str, Any] = {"nodeId": node_id}
    if h_sizing is not None:
        params["layoutSizingHorizontal"] = h_sizing
    if v_sizing is not None:
        params["layoutSizingVertical"] = v_sizing
    result = await client.send_command("set_layout_sizing", params)
    node_name = (result or {}).get("name", node_id) if isinstance(result, dict) else node_id
    parts = ([f"horizontal: {h_sizing}"] if h_sizing else []) + ([f"vertical: {v_sizing}"] if v_sizing else [])
    return [TextContent(type="text", text=f'Set layout sizing ({", ".join(parts)}) for frame "{node_name}"')]


async def _set_item_spacing(args: Dict, client: FigmaClient):
    node_id, spacing = args.get("nodeId"), args.get("itemSpacing")
    if node_id is None:
        return err("set_item_spacing requires nodeId")
    if spacing is None:
        return err("set_item_spacing requires itemSpacing")
    if not isinstance(spacing, (int, float)):
        return err("set_item_spacing: itemSpacing must be a number")
    params: Dict[str, Any] = {"nodeId": node_id, "itemSpacing": spacing}
    counter_spacing = args.get("counterAxisSpacing")
    if counter_spacing is not None:
        if not isinstance(counter_spacing, (int, float)):
            return err("set_item_spacing: counterAxisSpacing must be a number")
        params["counterAxisSpacing"] = counter_spacing
    result = await client.send_command("set_item_spacing", params)
    node_name = (result or {}).get("name", node_id) if isinstance(result, dict) else node_id
    return [TextContent(type="text", text=f'Updated spacing for frame "{node_name}": itemSpacing={spacing}')]


# ── Group E: Annotations, Connections & Channel ───────────────────────────────

async def _set_annotation(args: Dict, client: FigmaClient):
    node_id, label = args.get("nodeId"), args.get("labelMarkdown")
    if node_id is None:
        return err("set_annotation requires nodeId")
    if label is None:
        return err("set_annotation requires labelMarkdown")
    params: Dict[str, Any] = {"nodeId": node_id, "labelMarkdown": label}
    for key in ("annotationId", "categoryId"):
        if args.get(key) is not None:
            params[key] = args[key]
    properties = args.get("properties")
    if properties is not None:
        if not isinstance(properties, list):
            return err("set_annotation: properties must be an array")
        params["properties"] = properties
    return ok(await client.send_command("set_annotation", params))


async def _set_multiple_annotations(args: Dict, client: FigmaClient):
    annotations = args.get("annotations")
    if not annotations:
        return err("set_multiple_annotations requires annotations")
    if not isinstance(annotations, list):
        return err("set_multiple_annotations: annotations must be an array")
    result = await client.send_command("set_multiple_annotations",
                                       {"nodeId": args.get("nodeId"), "annotations": annotations})
    typed = result if isinstance(result, dict) else {}
    applied = typed.get("annotationsApplied", 0)
    failed = typed.get("annotationsFailed", 0)
    chunks = typed.get("completedInChunks", 1)
    failed_results = [r for r in typed.get("results", []) if not r.get("success", False)]
    text = (
        f"Annotation process completed:\n"
        f"- {applied} of {len(annotations)} successfully applied\n"
        f"- {failed} failed\n"
        f"- Processed in {chunks} batches"
    )
    if failed_results:
        text += "\n\nNodes that failed:\n" + "\n".join(
            f"- {r.get('nodeId', 'unknown')}: {r.get('error', 'Unknown error')}"
            for r in failed_results
        )
    return [TextContent(type="text", text=text)]


async def _scan_text_nodes(args: Dict, client: FigmaClient):
    if not args.get("nodeId"):
        return err("scan_text_nodes requires nodeId")
    result = await client.send_command("scan_text_nodes", {
        "nodeId": args["nodeId"],
        "useChunking": args.get("useChunking", True),
        "chunkSize": args.get("chunkSize", 10),
    })
    typed = result if isinstance(result, dict) else {}
    preamble = TextContent(type="text", text="Starting text node scanning. This may take a moment for large designs...")
    if "chunks" in typed:
        return [
            preamble,
            TextContent(type="text", text=f"\nScan completed:\n- Found {typed.get('totalNodes', 0)} text nodes\n- Processed in {typed.get('chunks', 0)} chunks"),
            TextContent(type="text", text=json.dumps(typed.get("textNodes", []), indent=2)),
        ]
    return [preamble, TextContent(type="text", text=json.dumps(result, indent=2))]


async def _scan_nodes_by_types(args: Dict, client: FigmaClient):
    node_id, node_types = args.get("nodeId"), args.get("types")
    if node_id is None:
        return err("scan_nodes_by_types requires nodeId")
    if not node_types:
        return err("scan_nodes_by_types requires types")
    if not isinstance(node_types, list):
        return err("scan_nodes_by_types: types must be an array")
    result = await client.send_command("scan_nodes_by_types", {"nodeId": node_id, "types": node_types})
    typed = result if isinstance(result, dict) else {}
    searched = typed.get("searchedTypes", node_types)
    preamble = TextContent(type="text", text=f"Starting node type scanning for types: {', '.join(searched)}...")
    if "matchingNodes" in typed:
        return [
            preamble,
            TextContent(type="text", text=f"Scan completed: Found {typed.get('count', 0)} nodes matching types: {', '.join(searched)}"),
            TextContent(type="text", text=json.dumps(typed.get("matchingNodes", []), indent=2)),
        ]
    return [preamble, TextContent(type="text", text=json.dumps(result, indent=2))]


async def _get_instance_overrides(args: Dict, client: FigmaClient):
    params: Dict[str, Any] = {}
    if args.get("nodeId") is not None:
        params["instanceNodeId"] = args["nodeId"]
    return ok(await client.send_command("get_instance_overrides", params))


async def _set_instance_overrides(args: Dict, client: FigmaClient):
    source = args.get("sourceInstanceId")
    targets = args.get("targetNodeIds")
    if source is None:
        return err("set_instance_overrides requires sourceInstanceId")
    if targets is None:
        return err("set_instance_overrides requires targetNodeIds")
    if not isinstance(targets, list):
        return err("set_instance_overrides: targetNodeIds must be an array")
    result = await client.send_command("set_instance_overrides",
                                       {"sourceInstanceId": source, "targetNodeIds": targets})
    typed = result if isinstance(result, dict) else {}
    if typed.get("success", False):
        success_count = sum(1 for r in typed.get("results", []) if r.get("success", False))
        return ok(f"Successfully applied {typed.get('totalCount', 0)} overrides to {success_count} instances.")
    return err(f"Failed to set instance overrides: {typed.get('message', '')}")


async def _set_default_connector(args: Dict, client: FigmaClient):
    params: Dict[str, Any] = {}
    if args.get("connectorId") is not None:
        params["connectorId"] = args["connectorId"]
    result = await client.send_command("set_default_connector", params)
    return ok(f"Default connector set: {json.dumps(result)}")


async def _create_connections(args: Dict, client: FigmaClient):
    connections = args.get("connections")
    if not connections:
        return err("create_connections requires connections")
    if not isinstance(connections, list):
        return err("create_connections: connections must be an array")
    if len(connections) == 0:
        return [TextContent(type="text", text="No connections provided")]
    for i, conn in enumerate(connections):
        if not isinstance(conn, dict):
            return err(f"create_connections: item {i} must be an object")
        if not conn.get("startNodeId"):
            return err(f"create_connections: item {i} missing startNodeId")
        if not conn.get("endNodeId"):
            return err(f"create_connections: item {i} missing endNodeId")
    result = await client.send_command("create_connections", {"connections": connections})
    return ok(f"Created {len(connections)} connections: {json.dumps(result)}")


async def _set_focus(args: Dict, client: FigmaClient):
    if not args.get("nodeId"):
        return err("set_focus requires nodeId")
    result = await client.send_command("set_focus", {"nodeId": args["nodeId"]})
    typed = result if isinstance(result, dict) else {}
    return ok(f'Focused on node "{typed.get("name", args["nodeId"])}" (ID: {typed.get("id", args["nodeId"])})')


async def _set_selections(args: Dict, client: FigmaClient):
    node_ids = args.get("nodeIds")
    if not node_ids:
        return err("set_selections requires nodeIds")
    if not isinstance(node_ids, list):
        return err("set_selections: nodeIds must be an array")
    result = await client.send_command("set_selections", {"nodeIds": node_ids})
    typed = result if isinstance(result, dict) else {}
    selected = typed.get("selectedNodes", [])
    count = typed.get("count", len(node_ids))
    nodes_text = ", ".join(
        f'"{n.get("name", n.get("id", "unknown"))}" ({n.get("id", "unknown")})'
        for n in selected
    )
    return ok(f"Selected {count} nodes: {nodes_text}")


async def _execute_code(args: Dict, client: FigmaClient):
    code = args.get("code")
    if not code or not isinstance(code, str) or not code.strip():
        return err("execute_code requires a non-empty code string")
    result = await client.send_command("execute_code", {"code": code}, timeout_ms=120000)
    return ok(result)


async def _join_channel(args: Dict, client: FigmaClient):
    channel = args.get("channel", "")
    if not channel:
        return err("Please provide a channel name to join")
    await client.join_channel(channel)
    return ok(f"Successfully joined channel: {channel}")


# ── Dispatch table ────────────────────────────────────────────────────────────

_DISPATCH: Dict[str, _Handler] = {
    "get_document_info": _get_document_info,
    "get_selection": _get_selection,
    "read_my_design": _read_my_design,
    "get_node_info": _get_node_info,
    "get_nodes_info": _get_nodes_info,
    "get_styles": _get_styles,
    "get_local_components": _get_local_components,
    "get_annotations": _get_annotations,
    "get_reactions": _get_reactions,
    "create_rectangle": _create_rectangle,
    "create_frame": _create_frame,
    "create_text": _create_text,
    "create_component_instance": _create_component_instance,
    "clone_node": _clone_node,
    "delete_node": _delete_node,
    "delete_multiple_nodes": _delete_multiple_nodes,
    "set_fill_color": _set_fill_color,
    "set_stroke_color": _set_stroke_color,
    "set_corner_radius": _set_corner_radius,
    "set_text_content": _set_text_content,
    "set_multiple_text_contents": _set_multiple_text_contents,
    "export_node_as_image": _export_node_as_image,
    "move_node": _move_node,
    "resize_node": _resize_node,
    "set_layout_mode": _set_layout_mode,
    "set_padding": _set_padding,
    "set_axis_align": _set_axis_align,
    "set_layout_sizing": _set_layout_sizing,
    "set_item_spacing": _set_item_spacing,
    "set_annotation": _set_annotation,
    "set_multiple_annotations": _set_multiple_annotations,
    "scan_text_nodes": _scan_text_nodes,
    "scan_nodes_by_types": _scan_nodes_by_types,
    "get_instance_overrides": _get_instance_overrides,
    "set_instance_overrides": _set_instance_overrides,
    "set_default_connector": _set_default_connector,
    "create_connections": _create_connections,
    "set_focus": _set_focus,
    "set_selections": _set_selections,
    "execute_code": _execute_code,
    "join_channel": _join_channel,
}


async def handle_tool(
    name: str, arguments: Dict[str, Any], client: FigmaClient
) -> List[TextContent | ImageContent]:
    """Look up and call the handler for *name*, wrapping any exception as an error."""
    handler = _DISPATCH.get(name)
    if handler is None:
        return err(f"Unknown tool: {name}")
    try:
        return await handler(arguments, client)
    except Exception as e:
        return err(f"Error in {name}: {e}")
