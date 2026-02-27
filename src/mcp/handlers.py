"""MCP tool handler implementations for the Talk-to-Figma MCP server."""

import asyncio
import json
from typing import Any, Dict, List

import mcp.types as types
from mcp.types import ImageContent, TextContent

from .utils import err, filter_figma_node, ok
from .ws_client import FigmaClient


async def handle_tool(
    name: str, arguments: Dict[str, Any], client: FigmaClient
) -> List[TextContent | ImageContent]:
    """Dispatch an MCP tool call to the appropriate handler."""
    # ── Group A: Document & Selection ────────────────────────────────────────
    if name == "get_document_info":
        try:
            result = await client.send_command("get_document_info")
            return ok(result)
        except Exception as e:
            return err(f"Error getting document info: {e}")
    elif name == "get_selection":
        try:
            result = await client.send_command("get_selection")
            return ok(result)
        except Exception as e:
            return err(f"Error getting selection: {e}")
    elif name == "read_my_design":
        try:
            result = await client.send_command("read_my_design", {})
            return ok(result)
        except Exception as e:
            return err(f"Error reading design: {e}")
    elif name == "get_node_info":
        try:
            if not arguments or "nodeId" not in arguments:
                return err("Missing required parameter: nodeId")
            node_id: str = arguments["nodeId"]
            result = await client.send_command("get_node_info", {"nodeId": node_id})
            return ok(filter_figma_node(result))
        except Exception as e:
            return err(f"Error getting node info: {e}")
    elif name == "get_nodes_info":
        try:
            if not arguments or "nodeIds" not in arguments:
                return err("Missing required parameter: nodeIds")
            node_ids: List[str] = arguments["nodeIds"]
            results = await asyncio.gather(
                *[client.send_command("get_node_info", {"nodeId": nid}) for nid in node_ids],
                return_exceptions=True
            )
            filtered = [
                filter_figma_node(r)
                for r in results
                if not isinstance(r, Exception)
            ]
            filtered = [f for f in filtered if f is not None]
            return ok(filtered)
        except Exception as e:
            return err(f"Error getting nodes info: {e}")
    elif name == "get_styles":
        try:
            result = await client.send_command("get_styles")
            return ok(result)
        except Exception as e:
            return err(f"Error getting styles: {e}")
    elif name == "get_local_components":
        try:
            result = await client.send_command("get_local_components")
            return ok(result)
        except Exception as e:
            return err(f"Error getting local components: {e}")
    elif name == "get_annotations":
        try:
            params: Dict[str, Any] = {}
            if arguments and "nodeId" in arguments:
                params["nodeId"] = arguments["nodeId"]
            if arguments and "includeCategories" in arguments:
                params["includeCategories"] = arguments["includeCategories"]
            result = await client.send_command("get_annotations", params)
            return ok(result)
        except Exception as e:
            return err(f"Error getting annotations: {e}")
    elif name == "get_reactions":
        try:
            if not arguments or "nodeIds" not in arguments:
                return err("Missing required parameter: nodeIds")
            node_ids = arguments["nodeIds"]
            result = await client.send_command("get_reactions", {"nodeIds": node_ids})
            return ok(result)
        except Exception as e:
            return err(f"Error getting reactions: {e}")
    # ── Group B: Create & Modify ──────────────────────────────────────────────
    elif name == "create_rectangle":
        try:
            x = arguments.get("x")
            y = arguments.get("y")
            width = arguments.get("width")
            height = arguments.get("height")
            if x is None or y is None or width is None or height is None:
                return err("create_rectangle requires x, y, width, and height")
            params: Dict[str, Any] = {
                "x": x,
                "y": y,
                "width": width,
                "height": height,
                "name": arguments.get("name") or "Rectangle",
            }
            parent_id = arguments.get("parentId")
            if parent_id is not None:
                params["parentId"] = parent_id
            result = await client.send_command("create_rectangle", params)
            return ok(result)
        except Exception as e:
            return err(f"Error creating rectangle: {e}")
    elif name == "create_frame":
        try:
            x = arguments.get("x")
            y = arguments.get("y")
            width = arguments.get("width")
            height = arguments.get("height")
            if x is None or y is None or width is None or height is None:
                return err("create_frame requires x, y, width, and height")
            params: Dict[str, Any] = {
                "x": x,
                "y": y,
                "width": width,
                "height": height,
                "name": arguments.get("name") or "Frame",
                "fillColor": arguments.get("fillColor") or {"r": 1, "g": 1, "b": 1, "a": 1},
            }
            for opt_key in (
                "parentId",
                "strokeColor",
                "strokeWeight",
                "layoutMode",
                "layoutWrap",
                "paddingTop",
                "paddingRight",
                "paddingBottom",
                "paddingLeft",
                "primaryAxisAlignItems",
                "counterAxisAlignItems",
                "layoutSizingHorizontal",
                "layoutSizingVertical",
                "itemSpacing",
            ):
                val = arguments.get(opt_key)
                if val is not None:
                    params[opt_key] = val
            result = await client.send_command("create_frame", params)
            return ok(result)
        except Exception as e:
            return err(f"Error creating frame: {e}")
    elif name == "create_text":
        try:
            x = arguments.get("x")
            y = arguments.get("y")
            text = arguments.get("text")
            if x is None or y is None or text is None:
                return err("create_text requires x, y, and text")
            params: Dict[str, Any] = {
                "x": x,
                "y": y,
                "text": text,
                "fontSize": arguments.get("fontSize") if arguments.get("fontSize") is not None else 14,
                "fontWeight": arguments.get("fontWeight") if arguments.get("fontWeight") is not None else 400,
                "fontColor": arguments.get("fontColor") or {"r": 0, "g": 0, "b": 0, "a": 1},
                "name": arguments.get("name") or "Text",
            }
            parent_id = arguments.get("parentId")
            if parent_id is not None:
                params["parentId"] = parent_id
            result = await client.send_command("create_text", params)
            return ok(result)
        except Exception as e:
            return err(f"Error creating text: {e}")
    elif name == "create_component_instance":
        try:
            component_id = arguments.get("componentKey")
            if not component_id:
                return err("create_component_instance requires componentKey")
            params: Dict[str, Any] = {"componentKey": component_id}
            x = arguments.get("x")
            if x is not None:
                params["x"] = x
            y = arguments.get("y")
            if y is not None:
                params["y"] = y
            result = await client.send_command("create_component_instance", params)
            return ok(result)
        except Exception as e:
            return err(f"Error creating component instance: {e}")
    elif name == "clone_node":
        try:
            node_id = arguments.get("nodeId")
            if not node_id:
                return err("clone_node requires nodeId")
            params: Dict[str, Any] = {"nodeId": node_id}
            x = arguments.get("x")
            if x is not None:
                params["x"] = x
            y = arguments.get("y")
            if y is not None:
                params["y"] = y
            result = await client.send_command("clone_node", params)
            return ok(result)
        except Exception as e:
            return err(f"Error cloning node: {e}")
    elif name == "delete_node":
        try:
            node_id = arguments.get("nodeId")
            if not node_id:
                return err("delete_node requires nodeId")
            await client.send_command("delete_node", {"nodeId": node_id})
            return ok({"deleted": node_id})
        except Exception as e:
            return err(f"Error deleting node: {e}")
    elif name == "delete_multiple_nodes":
        try:
            node_ids = arguments.get("nodeIds")
            if not node_ids:
                return err("delete_multiple_nodes requires nodeIds")
            result = await client.send_command("delete_multiple_nodes", {"nodeIds": node_ids})
            return ok(result)
        except Exception as e:
            return err(f"Error deleting multiple nodes: {e}")
    # ── Group C: Style & Appearance ───────────────────────────────────────────
    elif name == "set_fill_color":
        try:
            node_id = arguments.get("nodeId")
            r = arguments.get("r")
            g = arguments.get("g")
            b = arguments.get("b")
            if node_id is None or r is None or g is None or b is None:
                return err("set_fill_color requires nodeId, r, g, and b")
            if not all(isinstance(v, (int, float)) for v in (r, g, b)):
                return err("set_fill_color: r, g, b must be numbers in range 0-1")
            a_val = arguments.get("a")
            a = a_val if a_val is not None else 1
            result = await client.send_command("set_fill_color", {
                "nodeId": node_id,
                "color": {"r": r, "g": g, "b": b, "a": a},
            })
            typed = result if isinstance(result, dict) else {}
            node_name = typed.get("name", node_id)
            return [TextContent(type="text", text=f'Set fill color of node "{node_name}" to RGBA({r}, {g}, {b}, {a})')]
        except Exception as e:
            return err(f"Error setting fill color: {e}")
    elif name == "set_stroke_color":
        try:
            node_id = arguments.get("nodeId")
            r = arguments.get("r")
            g = arguments.get("g")
            b = arguments.get("b")
            if node_id is None or r is None or g is None or b is None:
                return err("set_stroke_color requires nodeId, r, g, and b")
            if not all(isinstance(v, (int, float)) for v in (r, g, b)):
                return err("set_stroke_color: r, g, b must be numbers in range 0-1")
            a_val = arguments.get("a")
            a = a_val if a_val is not None else 1
            weight_val = arguments.get("weight")
            weight = weight_val if weight_val is not None else 1
            result = await client.send_command("set_stroke_color", {
                "nodeId": node_id,
                "color": {"r": r, "g": g, "b": b, "a": a},
                "weight": weight,
            })
            typed = result if isinstance(result, dict) else {}
            node_name = typed.get("name", node_id)
            return [TextContent(type="text", text=f'Set stroke color of node "{node_name}" to RGBA({r}, {g}, {b}, {a}) with weight {weight}')]
        except Exception as e:
            return err(f"Error setting stroke color: {e}")
    elif name == "set_corner_radius":
        try:
            node_id = arguments.get("nodeId")
            radius = arguments.get("radius")
            if node_id is None or radius is None:
                return err("set_corner_radius requires nodeId and radius")
            corners = arguments.get("corners")
            result = await client.send_command("set_corner_radius", {
                "nodeId": node_id,
                "radius": radius,
                "corners": corners if corners is not None else [True, True, True, True],
            })
            typed = result if isinstance(result, dict) else {}
            node_name = typed.get("name", node_id)
            return [TextContent(type="text", text=f'Set corner radius of node "{node_name}" to {radius}px')]
        except Exception as e:
            return err(f"Error setting corner radius: {e}")
    elif name == "set_text_content":
        try:
            node_id = arguments.get("nodeId")
            text = arguments.get("text")
            if node_id is None or text is None:
                return err("set_text_content requires nodeId and text")
            result = await client.send_command("set_text_content", {"nodeId": node_id, "text": text})
            typed = result if isinstance(result, dict) else {}
            node_name = typed.get("name", node_id)
            return [TextContent(type="text", text=f'Updated text content of node "{node_name}" to "{text}"')]
        except Exception as e:
            return err(f"Error setting text content: {e}")
    elif name == "set_multiple_text_contents":
        try:
            node_id = arguments.get("nodeId")
            text = arguments.get("text")
            if node_id is None:
                return err("set_multiple_text_contents requires nodeId")
            if text is None:
                return err("set_multiple_text_contents requires text")
            if len(text) == 0:
                return [TextContent(type="text", text="No text provided")]
            result = await client.send_command("set_multiple_text_contents", {
                "nodeId": node_id,
                "text": text,
            })
            typed = result if isinstance(result, dict) else {}
            replacements_applied = typed.get("replacementsApplied", 0)
            replacements_failed = typed.get("replacementsFailed", 0)
            total = typed.get("totalReplacements", len(text))
            return ok({
                "success": typed.get("success", True),
                "replacementsApplied": replacements_applied,
                "replacementsFailed": replacements_failed,
                "totalReplacements": total,
                "completedInChunks": typed.get("completedInChunks", 0),
            })
        except Exception as e:
            return err(f"Error setting multiple text contents: {e}")
    elif name == "export_node_as_image":
        try:
            node_id = arguments.get("nodeId")
            if node_id is None:
                return err("export_node_as_image requires nodeId")
            fmt_val = arguments.get("format")
            fmt = fmt_val if fmt_val is not None else "PNG"
            scale_val = arguments.get("scale")
            scale = scale_val if scale_val is not None else 1
            result = await client.send_command("export_node_as_image", {
                "nodeId": node_id,
                "format": fmt,
                "scale": scale,
            })
            typed = result if isinstance(result, dict) else {}
            image_data = typed.get("imageData")
            if not image_data:
                return err("export_node_as_image: plugin returned no image data")
            mime_type = typed.get("mimeType", "image/png")
            return [types.ImageContent(type="image", data=image_data, mimeType=mime_type)]
        except Exception as e:
            return err(f"Error exporting node as image: {e}")
    # ── Group D: Layout & Positioning ─────────────────────────────────────────
    elif name == "move_node":
        try:
            node_id = arguments.get("nodeId")
            x = arguments.get("x")
            y = arguments.get("y")
            if node_id is None:
                return err("move_node requires nodeId")
            if x is None:
                return err("move_node requires x")
            if y is None:
                return err("move_node requires y")
            if not isinstance(x, (int, float)) or not isinstance(y, (int, float)):
                return err("move_node: x and y must be numbers")
            result = await client.send_command("move_node", {"nodeId": node_id, "x": x, "y": y})
            typed = result if isinstance(result, dict) else {}
            node_name = typed.get("name", node_id)
            return [TextContent(type="text", text=f'Moved node "{node_name}" to position ({x}, {y})')]
        except Exception as e:
            return err(f"Error moving node: {e}")
    elif name == "resize_node":
        try:
            node_id = arguments.get("nodeId")
            width = arguments.get("width")
            height = arguments.get("height")
            if node_id is None:
                return err("resize_node requires nodeId")
            if width is None:
                return err("resize_node requires width")
            if height is None:
                return err("resize_node requires height")
            if not isinstance(width, (int, float)) or not isinstance(height, (int, float)):
                return err("resize_node: width and height must be numbers")
            result = await client.send_command("resize_node", {"nodeId": node_id, "width": width, "height": height})
            typed = result if isinstance(result, dict) else {}
            node_name = typed.get("name", node_id)
            return [TextContent(type="text", text=f'Resized node "{node_name}" to width {width} and height {height}')]
        except Exception as e:
            return err(f"Error resizing node: {e}")
    elif name == "set_layout_mode":
        try:
            node_id = arguments.get("nodeId")
            layout_mode = arguments.get("layoutMode")
            if node_id is None:
                return err("set_layout_mode requires nodeId")
            if layout_mode is None:
                return err("set_layout_mode requires layoutMode")
            layout_wrap_val = arguments.get("layoutWrap")
            layout_wrap = layout_wrap_val if layout_wrap_val is not None else "NO_WRAP"
            result = await client.send_command("set_layout_mode", {
                "nodeId": node_id,
                "layoutMode": layout_mode,
                "layoutWrap": layout_wrap,
            })
            typed = result if isinstance(result, dict) else {}
            node_name = typed.get("name", node_id)
            wrap_suffix = f" with {layout_wrap_val}" if layout_wrap_val is not None else ""
            return [TextContent(type="text", text=f'Set layout mode of frame "{node_name}" to {layout_mode}{wrap_suffix}')]
        except Exception as e:
            return err(f"Error setting layout mode: {e}")
    elif name == "set_padding":
        try:
            node_id = arguments.get("nodeId")
            if node_id is None:
                return err("set_padding requires nodeId")
            params: Dict[str, Any] = {"nodeId": node_id}
            top = arguments.get("top")
            right = arguments.get("right")
            bottom = arguments.get("bottom")
            left = arguments.get("left")
            if top is not None and not isinstance(top, (int, float)):
                return err("set_padding: top must be a number")
            if right is not None and not isinstance(right, (int, float)):
                return err("set_padding: right must be a number")
            if bottom is not None and not isinstance(bottom, (int, float)):
                return err("set_padding: bottom must be a number")
            if left is not None and not isinstance(left, (int, float)):
                return err("set_padding: left must be a number")
            if not any(v is not None for v in (top, right, bottom, left)):
                return err("set_padding requires at least one of: top, right, bottom, left")
            if top is not None:
                params["paddingTop"] = top
            if right is not None:
                params["paddingRight"] = right
            if bottom is not None:
                params["paddingBottom"] = bottom
            if left is not None:
                params["paddingLeft"] = left
            result = await client.send_command("set_padding", params)
            typed = result if isinstance(result, dict) else {}
            node_name = typed.get("name", node_id)
            padding_parts = []
            if top is not None:
                padding_parts.append(f"top: {top}")
            if right is not None:
                padding_parts.append(f"right: {right}")
            if bottom is not None:
                padding_parts.append(f"bottom: {bottom}")
            if left is not None:
                padding_parts.append(f"left: {left}")
            padding_text = f"padding ({', '.join(padding_parts)})" if padding_parts else "padding"
            return [TextContent(type="text", text=f'Set {padding_text} for frame "{node_name}"')]
        except Exception as e:
            return err(f"Error setting padding: {e}")
    elif name == "set_axis_align":
        try:
            node_id = arguments.get("nodeId")
            if node_id is None:
                return err("set_axis_align requires nodeId")
            params: Dict[str, Any] = {"nodeId": node_id}
            primary = arguments.get("primaryAxisAlignItems")
            if primary is not None:
                params["primaryAxisAlignItems"] = primary
            counter = arguments.get("counterAxisAlignItems")
            if counter is not None:
                params["counterAxisAlignItems"] = counter
            if primary is None and counter is None:
                return err("set_axis_align requires at least one of: primaryAxisAlignItems, counterAxisAlignItems")
            result = await client.send_command("set_axis_align", params)
            typed = result if isinstance(result, dict) else {}
            node_name = typed.get("name", node_id)
            align_parts = []
            if primary is not None:
                align_parts.append(f"primary: {primary}")
            if counter is not None:
                align_parts.append(f"counter: {counter}")
            align_text = f"axis alignment ({', '.join(align_parts)})" if align_parts else "axis alignment"
            return [TextContent(type="text", text=f'Set {align_text} for frame "{node_name}"')]
        except Exception as e:
            return err(f"Error setting axis alignment: {e}")
    elif name == "set_layout_sizing":
        try:
            node_id = arguments.get("nodeId")
            if node_id is None:
                return err("set_layout_sizing requires nodeId")
            params: Dict[str, Any] = {"nodeId": node_id}
            h_sizing = arguments.get("layoutSizingHorizontal")
            if h_sizing is not None:
                params["layoutSizingHorizontal"] = h_sizing
            v_sizing = arguments.get("layoutSizingVertical")
            if v_sizing is not None:
                params["layoutSizingVertical"] = v_sizing
            if h_sizing is None and v_sizing is None:
                return err("set_layout_sizing requires at least one of: layoutSizingHorizontal, layoutSizingVertical")
            result = await client.send_command("set_layout_sizing", params)
            typed = result if isinstance(result, dict) else {}
            node_name = typed.get("name", node_id)
            sizing_parts = []
            if h_sizing is not None:
                sizing_parts.append(f"horizontal: {h_sizing}")
            if v_sizing is not None:
                sizing_parts.append(f"vertical: {v_sizing}")
            sizing_text = f"layout sizing ({', '.join(sizing_parts)})" if sizing_parts else "layout sizing"
            return [TextContent(type="text", text=f'Set {sizing_text} for frame "{node_name}"')]
        except Exception as e:
            return err(f"Error setting layout sizing: {e}")
    elif name == "set_item_spacing":
        try:
            node_id = arguments.get("nodeId")
            spacing = arguments.get("itemSpacing")
            if node_id is None:
                return err("set_item_spacing requires nodeId")
            if spacing is None:
                return err("set_item_spacing requires itemSpacing")
            if not isinstance(spacing, (int, float)):
                return err("set_item_spacing: itemSpacing must be a number")
            params: Dict[str, Any] = {"nodeId": node_id, "itemSpacing": spacing}
            counter_spacing = arguments.get("counterAxisSpacing")
            if counter_spacing is not None:
                if not isinstance(counter_spacing, (int, float)):
                    return err("set_item_spacing: counterAxisSpacing must be a number")
                params["counterAxisSpacing"] = counter_spacing
            result = await client.send_command("set_item_spacing", params)
            typed = result if isinstance(result, dict) else {}
            node_name = typed.get("name", node_id)
            return [TextContent(type="text", text=f'Updated spacing for frame "{node_name}": itemSpacing={spacing}')]
        except Exception as e:
            return err(f"Error setting item spacing: {e}")
    # ── Group E: Annotations, Connections & Channel ───────────────────────────
    elif name == "set_annotation":
        try:
            node_id = arguments.get("nodeId")
            label_markdown = arguments.get("labelMarkdown")
            if node_id is None:
                return err("set_annotation requires nodeId")
            if label_markdown is None:
                return err("set_annotation requires labelMarkdown")
            params: Dict[str, Any] = {
                "nodeId": node_id,
                "labelMarkdown": label_markdown,
            }
            annotation_id = arguments.get("annotationId")
            if annotation_id is not None:
                params["annotationId"] = annotation_id
            category_id = arguments.get("categoryId")
            if category_id is not None:
                params["categoryId"] = category_id
            properties = arguments.get("properties")
            if properties is not None:
                if not isinstance(properties, list):
                    return err("set_annotation: properties must be an array")
                params["properties"] = properties
            result = await client.send_command("set_annotation", params)
            return ok(result)
        except Exception as e:
            return err(f"Error setting annotation: {e}")
    elif name == "set_multiple_annotations":
        try:
            node_id = arguments.get("nodeId")
            annotations = arguments.get("annotations")
            if not annotations:
                return err("set_multiple_annotations requires annotations")
            if not isinstance(annotations, list):
                return err("set_multiple_annotations: annotations must be an array")
            params: Dict[str, Any] = {"nodeId": node_id, "annotations": annotations}
            result = await client.send_command("set_multiple_annotations", params)
            typed = result if isinstance(result, dict) else {}
            annotations_applied = typed.get("annotationsApplied", 0)
            annotations_failed = typed.get("annotationsFailed", 0)
            completed_in_chunks = typed.get("completedInChunks", 1)
            detailed_results = typed.get("results", [])
            failed_results = [item for item in detailed_results if not item.get("success", False)]
            response_text = (
                f"Annotation process completed:\n"
                f"- {annotations_applied} of {len(annotations)} successfully applied\n"
                f"- {annotations_failed} failed\n"
                f"- Processed in {completed_in_chunks} batches"
            )
            if failed_results:
                failed_text = "\n\nNodes that failed:\n" + "\n".join(
                    f"- {item.get('nodeId', 'unknown')}: {item.get('error', 'Unknown error')}"
                    for item in failed_results
                )
                response_text += failed_text
            return [TextContent(type="text", text=response_text)]
        except Exception as e:
            return err(f"Error setting multiple annotations: {e}")
    elif name == "scan_text_nodes":
        try:
            node_id = arguments.get("nodeId")
            if node_id is None:
                return err("scan_text_nodes requires nodeId")
            params: Dict[str, Any] = {
                "nodeId": node_id,
                "useChunking": arguments.get("useChunking", True),
                "chunkSize": arguments.get("chunkSize", 10),
            }
            result = await client.send_command("scan_text_nodes", params)
            typed = result if isinstance(result, dict) else {}
            if "chunks" in typed:
                total_nodes = typed.get("totalNodes", 0)
                chunks = typed.get("chunks", 0)
                text_nodes = typed.get("textNodes", [])
                return [
                    TextContent(type="text", text="Starting text node scanning. This may take a moment for large designs..."),
                    TextContent(type="text", text=f"\nScan completed:\n- Found {total_nodes} text nodes\n- Processed in {chunks} chunks"),
                    TextContent(type="text", text=json.dumps(text_nodes, indent=2)),
                ]
            return [
                TextContent(type="text", text="Starting text node scanning. This may take a moment for large designs..."),
                TextContent(type="text", text=json.dumps(result, indent=2)),
            ]
        except Exception as e:
            return err(f"Error scanning text nodes: {e}")
    elif name == "scan_nodes_by_types":
        try:
            node_id = arguments.get("nodeId")
            node_types = arguments.get("types")
            if node_id is None:
                return err("scan_nodes_by_types requires nodeId")
            if node_types is None:
                return err("scan_nodes_by_types requires types")
            if not isinstance(node_types, list):
                return err("scan_nodes_by_types: types must be an array")
            params: Dict[str, Any] = {
                "nodeId": node_id,
                "types": node_types,
            }
            result = await client.send_command("scan_nodes_by_types", params)
            typed = result if isinstance(result, dict) else {}
            if "matchingNodes" in typed:
                count = typed.get("count", 0)
                searched_types = typed.get("searchedTypes", [])
                matching_nodes = typed.get("matchingNodes", [])
                return [
                    TextContent(type="text", text=f"Starting node type scanning for types: {', '.join(searched_types)}..."),
                    TextContent(type="text", text=f"Scan completed: Found {count} nodes matching types: {', '.join(searched_types)}"),
                    TextContent(type="text", text=json.dumps(matching_nodes, indent=2)),
                ]
            return [
                TextContent(type="text", text=f"Starting node type scanning for types: {', '.join(node_types)}..."),
                TextContent(type="text", text=json.dumps(result, indent=2)),
            ]
        except Exception as e:
            return err(f"Error scanning nodes by types: {e}")
    elif name == "get_instance_overrides":
        try:
            node_id = arguments.get("nodeId")
            params: Dict[str, Any] = {}
            if node_id is not None:
                params["instanceNodeId"] = node_id
            result = await client.send_command("get_instance_overrides", params)
            return ok(result)
        except Exception as e:
            return err(f"Error getting instance overrides: {e}")
    elif name == "set_instance_overrides":
        try:
            source_node_id = arguments.get("sourceInstanceId")
            target_node_ids = arguments.get("targetNodeIds")
            if source_node_id is None:
                return err("set_instance_overrides requires sourceInstanceId")
            if target_node_ids is None:
                return err("set_instance_overrides requires targetNodeIds")
            if not isinstance(target_node_ids, list):
                return err("set_instance_overrides: targetNodeIds must be an array")
            params: Dict[str, Any] = {
                "sourceInstanceId": source_node_id,
                "targetNodeIds": target_node_ids,
            }
            result = await client.send_command("set_instance_overrides", params)
            typed = result if isinstance(result, dict) else {}
            success = typed.get("success", False)
            message = typed.get("message", "")
            if success:
                total_count = typed.get("totalCount", 0)
                results = typed.get("results", [])
                success_count = len([r for r in results if r.get("success", False)])
                return ok(f"Successfully applied {total_count} overrides to {success_count} instances.")
            return err(f"Failed to set instance overrides: {message}")
        except Exception as e:
            return err(f"Error setting instance overrides: {e}")
    elif name == "set_default_connector":
        try:
            connector_id = arguments.get("connectorId")
            params: Dict[str, Any] = {}
            if connector_id is not None:
                params["connectorId"] = connector_id
            result = await client.send_command("set_default_connector", params)
            return ok(f"Default connector set: {json.dumps(result)}")
        except Exception as e:
            return err(f"Error setting default connector: {e}")
    elif name == "create_connections":
        try:
            connections = arguments.get("connections")
            if connections is None:
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
            params: Dict[str, Any] = {"connections": connections}
            result = await client.send_command("create_connections", params)
            return ok(f"Created {len(connections)} connections: {json.dumps(result)}")
        except Exception as e:
            return err(f"Error creating connections: {e}")
    elif name == "set_focus":
        try:
            node_id = arguments.get("nodeId")
            if node_id is None:
                return err("set_focus requires nodeId")
            result = await client.send_command("set_focus", {"nodeId": node_id})
            typed = result if isinstance(result, dict) else {}
            node_name = typed.get("name", node_id)
            node_id_result = typed.get("id", node_id)
            return ok(f'Focused on node "{node_name}" (ID: {node_id_result})')
        except Exception as e:
            return err(f"Error setting focus: {e}")
    elif name == "set_selections":
        try:
            node_ids = arguments.get("nodeIds")
            if not node_ids:
                return err("set_selections requires nodeIds")
            if not isinstance(node_ids, list):
                return err("set_selections: nodeIds must be an array")
            result = await client.send_command("set_selections", {"nodeIds": node_ids})
            typed = result if isinstance(result, dict) else {}
            selected_nodes = typed.get("selectedNodes", [])
            count = typed.get("count", len(node_ids))
            nodes_text = ', '.join(
                f'"{node.get("name", node.get("id", "unknown"))}" ({node.get("id", "unknown")})'
                for node in selected_nodes
            )
            return ok(f"Selected {count} nodes: {nodes_text}")
        except Exception as e:
            return err(f"Error setting selections: {e}")
    elif name == "execute_code":
        try:
            code = arguments.get("code")
            if not code or not isinstance(code, str) or not code.strip():
                return err("execute_code requires a non-empty code string")
            params: Dict[str, Any] = {
                "code": code,
                "params": arguments.get("params") or {},
            }
            result = await client.send_command("execute_code", params, timeout_ms=120000)
            return ok(result)
        except Exception as e:
            return err(f"Error executing code: {e}")
    elif name == "join_channel":
        try:
            channel = arguments.get("channel", "")
            if not channel:
                return err("Please provide a channel name to join")
            await client.join_channel(channel)
            return ok(f"Successfully joined channel: {channel}")
        except Exception as e:
            return err(f"Error joining channel: {e}")
    else:
        return err(f"Unknown tool: {name}")
