"""Tool schema definitions for the Talk-to-Figma MCP server."""

from typing import List

from mcp.types import Tool

ALL_TOOLS: List[Tool] = [
    # ── Group A: Document & Selection ──────────────────────────────────────
    Tool(
        name="get_document_info",
        description="Get detailed information about the current Figma document",
        inputSchema={"type": "object", "properties": {}, "required": []},
    ),
    Tool(
        name="get_selection",
        description="Get information about the current selection in Figma",
        inputSchema={"type": "object", "properties": {}, "required": []},
    ),
    Tool(
        name="read_my_design",
        description=(
            "Get detailed information about the current selection in Figma, "
            "including all node details"
        ),
        inputSchema={"type": "object", "properties": {}, "required": []},
    ),
    Tool(
        name="get_node_info",
        description="Get detailed information about a specific node in Figma",
        inputSchema={
            "type": "object",
            "properties": {
                "nodeId": {
                    "type": "string",
                    "description": "The ID of the node to get information about",
                }
            },
            "required": ["nodeId"],
        },
    ),
    Tool(
        name="get_nodes_info",
        description="Get detailed information about multiple nodes in Figma",
        inputSchema={
            "type": "object",
            "properties": {
                "nodeIds": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of node IDs to get information about",
                }
            },
            "required": ["nodeIds"],
        },
    ),
    Tool(
        name="get_styles",
        description="Get all styles defined in the current Figma document",
        inputSchema={"type": "object", "properties": {}, "required": []},
    ),
    Tool(
        name="get_local_components",
        description="Get all local components defined in the current Figma document",
        inputSchema={"type": "object", "properties": {}, "required": []},
    ),
    Tool(
        name="get_annotations",
        description="Get annotations from the current Figma document or a specific node",
        inputSchema={
            "type": "object",
            "properties": {
                "nodeId": {
                    "type": "string",
                    "description": "The ID of the node to get annotations for (optional)",
                },
                "includeCategories": {
                    "type": "boolean",
                    "description": "Whether to include annotation categories",
                },
            },
            "required": [],
        },
    ),
    Tool(
        name="get_reactions",
        description="Get reactions (interactions/prototyping) for specified nodes",
        inputSchema={
            "type": "object",
            "properties": {
                "nodeIds": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of node IDs to get reactions for",
                }
            },
            "required": ["nodeIds"],
        },
    ),
    # ── Group B: Create & Modify ────────────────────────────────────────────
    Tool(
        name="create_rectangle",
        description="Create a new rectangle node in Figma",
        inputSchema={
            "type": "object",
            "properties": {
                "x": {"type": "number", "description": "X position"},
                "y": {"type": "number", "description": "Y position"},
                "width": {"type": "number", "description": "Width"},
                "height": {"type": "number", "description": "Height"},
                "name": {"type": "string", "description": "Name of the rectangle (optional)"},
                "parentId": {"type": "string", "description": "Parent node ID (optional)"},
            },
            "required": ["x", "y", "width", "height"],
        },
    ),
    Tool(
        name="create_frame",
        description="Create a new frame node in Figma",
        inputSchema={
            "type": "object",
            "properties": {
                "x": {"type": "number", "description": "X position"},
                "y": {"type": "number", "description": "Y position"},
                "width": {"type": "number", "description": "Width"},
                "height": {"type": "number", "description": "Height"},
                "name": {"type": "string", "description": "Name of the frame (optional)"},
                "parentId": {"type": "string", "description": "Parent node ID (optional)"},
                "fillColor": {"type": "object", "description": "Fill color as RGBA {r,g,b,a} with 0-1 values"},
                "strokeColor": {"type": "object", "description": "Stroke color as RGBA {r,g,b,a}"},
                "strokeWeight": {"type": "number", "description": "Stroke weight in pixels"},
                "layoutMode": {"type": "string", "description": "Auto layout mode: HORIZONTAL, VERTICAL, or NONE"},
                "layoutWrap": {"type": "string", "description": "Layout wrap: NO_WRAP or WRAP"},
                "paddingTop": {"type": "number", "description": "Top padding"},
                "paddingRight": {"type": "number", "description": "Right padding"},
                "paddingBottom": {"type": "number", "description": "Bottom padding"},
                "paddingLeft": {"type": "number", "description": "Left padding"},
                "primaryAxisAlignItems": {"type": "string", "description": "Primary axis alignment"},
                "counterAxisAlignItems": {"type": "string", "description": "Counter axis alignment"},
                "layoutSizingHorizontal": {"type": "string", "description": "Horizontal sizing mode"},
                "layoutSizingVertical": {"type": "string", "description": "Vertical sizing mode"},
                "itemSpacing": {"type": "number", "description": "Item spacing in auto layout"},
            },
            "required": ["x", "y", "width", "height"],
        },
    ),
    Tool(
        name="create_text",
        description="Create a new text node in Figma",
        inputSchema={
            "type": "object",
            "properties": {
                "x": {"type": "number", "description": "X position"},
                "y": {"type": "number", "description": "Y position"},
                "text": {"type": "string", "description": "Text content"},
                "fontSize": {"type": "number", "description": "Font size (optional)"},
                "fontWeight": {"type": "number", "description": "Font weight (optional)"},
                "fontColor": {"type": "object", "description": "Font color as RGBA {r,g,b,a} with 0-1 values. Defaults to black."},
                "name": {"type": "string", "description": "Name of the text node (optional)"},
                "parentId": {"type": "string", "description": "Parent node ID (optional)"},
            },
            "required": ["x", "y", "text"],
        },
    ),
    Tool(
        name="create_component_instance",
        description="Create an instance of an existing component in Figma",
        inputSchema={
            "type": "object",
            "properties": {
                "componentKey": {
                    "type": "string",
                    "description": "Key of the component to instantiate",
                },
                "x": {"type": "number", "description": "X position (optional)"},
                "y": {"type": "number", "description": "Y position (optional)"},
            },
            "required": ["componentKey"],
        },
    ),
    Tool(
        name="clone_node",
        description="Clone an existing node in Figma",
        inputSchema={
            "type": "object",
            "properties": {
                "nodeId": {"type": "string", "description": "ID of the node to clone"},
                "x": {"type": "number", "description": "X position for the clone (optional)"},
                "y": {"type": "number", "description": "Y position for the clone (optional)"},
            },
            "required": ["nodeId"],
        },
    ),
    Tool(
        name="delete_node",
        description="Delete a node from the Figma document",
        inputSchema={
            "type": "object",
            "properties": {
                "nodeId": {"type": "string", "description": "ID of the node to delete"}
            },
            "required": ["nodeId"],
        },
    ),
    Tool(
        name="delete_multiple_nodes",
        description="Delete multiple nodes from the Figma document",
        inputSchema={
            "type": "object",
            "properties": {
                "nodeIds": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of node IDs to delete",
                }
            },
            "required": ["nodeIds"],
        },
    ),
    # ── Group C: Style & Appearance ─────────────────────────────────────────
    Tool(
        name="set_fill_color",
        description="Set the fill color of a node in Figma",
        inputSchema={
            "type": "object",
            "properties": {
                "nodeId": {"type": "string", "description": "ID of the node"},
                "r": {"type": "number", "description": "Red (0-1)"},
                "g": {"type": "number", "description": "Green (0-1)"},
                "b": {"type": "number", "description": "Blue (0-1)"},
                "a": {"type": "number", "description": "Alpha (0-1, optional)"},
            },
            "required": ["nodeId", "r", "g", "b"],
        },
    ),
    Tool(
        name="set_stroke_color",
        description="Set the stroke color of a node in Figma",
        inputSchema={
            "type": "object",
            "properties": {
                "nodeId": {"type": "string", "description": "ID of the node"},
                "r": {"type": "number", "description": "Red (0-1)"},
                "g": {"type": "number", "description": "Green (0-1)"},
                "b": {"type": "number", "description": "Blue (0-1)"},
                "a": {"type": "number", "description": "Alpha (0-1, optional)"},
                "weight": {
                    "type": "number",
                    "description": "Stroke weight in pixels (optional)",
                },
            },
            "required": ["nodeId", "r", "g", "b"],
        },
    ),
    Tool(
        name="set_corner_radius",
        description="Set the corner radius of a node in Figma",
        inputSchema={
            "type": "object",
            "properties": {
                "nodeId": {"type": "string", "description": "ID of the node"},
                "radius": {"type": "number", "description": "Corner radius value"},
                "corners": {
                    "type": "array",
                    "items": {"type": "boolean"},
                    "description": "Which corners to apply the radius to: [topLeft, topRight, bottomRight, bottomLeft]. Defaults to all true.",
                },
            },
            "required": ["nodeId", "radius"],
        },
    ),
    Tool(
        name="set_text_content",
        description="Set the text content of a text node in Figma",
        inputSchema={
            "type": "object",
            "properties": {
                "nodeId": {"type": "string", "description": "ID of the text node"},
                "text": {"type": "string", "description": "New text content"},
            },
            "required": ["nodeId", "text"],
        },
    ),
    Tool(
        name="set_multiple_text_contents",
        description="Set the text content of multiple text nodes in Figma",
        inputSchema={
            "type": "object",
            "properties": {
                "nodeId": {
                    "type": "string",
                    "description": "ID of the parent node (used as context)",
                },
                "text": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "nodeId": {"type": "string"},
                            "text": {"type": "string"},
                        },
                        "required": ["nodeId", "text"],
                    },
                    "description": "List of nodeId/text pairs to update",
                },
            },
            "required": ["nodeId", "text"],
        },
    ),
    Tool(
        name="export_node_as_image",
        description="Export a node as an image from Figma",
        inputSchema={
            "type": "object",
            "properties": {
                "nodeId": {"type": "string", "description": "ID of the node to export"},
                "format": {
                    "type": "string",
                    "description": "Export format. Note: currently the Figma plugin only supports PNG regardless of this value.",
                },
                "scale": {"type": "number", "description": "Export scale (optional)"},
            },
            "required": ["nodeId"],
        },
    ),
    # ── Group D: Layout & Positioning ──────────────────────────────────────
    Tool(
        name="move_node",
        description="Move a node to a new position in Figma",
        inputSchema={
            "type": "object",
            "properties": {
                "nodeId": {"type": "string", "description": "ID of the node to move"},
                "x": {"type": "number", "description": "New X position"},
                "y": {"type": "number", "description": "New Y position"},
            },
            "required": ["nodeId", "x", "y"],
        },
    ),
    Tool(
        name="resize_node",
        description="Resize a node in Figma",
        inputSchema={
            "type": "object",
            "properties": {
                "nodeId": {"type": "string", "description": "ID of the node to resize"},
                "width": {"type": "number", "description": "New width"},
                "height": {"type": "number", "description": "New height"},
            },
            "required": ["nodeId", "width", "height"],
        },
    ),
    Tool(
        name="set_layout_mode",
        description="Set the auto-layout mode of a frame node in Figma",
        inputSchema={
            "type": "object",
            "properties": {
                "nodeId": {"type": "string", "description": "ID of the frame node"},
                "layoutMode": {
                    "type": "string",
                    "description": "Layout mode: NONE, HORIZONTAL, or VERTICAL",
                },
                "layoutWrap": {
                    "type": "string",
                    "description": "Wrap mode: NO_WRAP or WRAP (optional, defaults to NO_WRAP)",
                },
            },
            "required": ["nodeId", "layoutMode"],
        },
    ),
    Tool(
        name="set_padding",
        description="Set the padding of an auto-layout frame in Figma",
        inputSchema={
            "type": "object",
            "properties": {
                "nodeId": {"type": "string", "description": "ID of the frame node"},
                "top": {"type": "number", "description": "Top padding (optional)"},
                "right": {"type": "number", "description": "Right padding (optional)"},
                "bottom": {"type": "number", "description": "Bottom padding (optional)"},
                "left": {"type": "number", "description": "Left padding (optional)"},
            },
            "required": ["nodeId"],
        },
    ),
    Tool(
        name="set_axis_align",
        description="Set the axis alignment of an auto-layout frame in Figma",
        inputSchema={
            "type": "object",
            "properties": {
                "nodeId": {"type": "string", "description": "ID of the frame node"},
                "primaryAxisAlignItems": {
                    "type": "string",
                    "description": "Primary axis alignment (optional)",
                },
                "counterAxisAlignItems": {
                    "type": "string",
                    "description": "Counter axis alignment (optional)",
                },
            },
            "required": ["nodeId"],
        },
    ),
    Tool(
        name="set_layout_sizing",
        description="Set the layout sizing of a node in Figma",
        inputSchema={
            "type": "object",
            "properties": {
                "nodeId": {"type": "string", "description": "ID of the node"},
                "layoutSizingHorizontal": {
                    "type": "string",
                    "description": "Horizontal sizing mode: FIXED, HUG, or FILL (optional)",
                },
                "layoutSizingVertical": {
                    "type": "string",
                    "description": "Vertical sizing mode: FIXED, HUG, or FILL (optional)",
                },
            },
            "required": ["nodeId"],
        },
    ),
    Tool(
        name="set_item_spacing",
        description="Set the item spacing of an auto-layout frame in Figma",
        inputSchema={
            "type": "object",
            "properties": {
                "nodeId": {"type": "string", "description": "ID of the frame node"},
                "itemSpacing": {"type": "number", "description": "Item spacing between auto-layout children"},
                "counterAxisSpacing": {"type": "number", "description": "Distance between wrapped rows/columns. Only applies when layoutWrap is WRAP (optional)"},
            },
            "required": ["nodeId", "itemSpacing"],
        },
    ),
    # ── Group E: Annotations, Connections & Channel ─────────────────────────
    Tool(
        name="set_annotation",
        description="Set an annotation on a node in Figma",
        inputSchema={
            "type": "object",
            "properties": {
                "nodeId": {"type": "string", "description": "ID of the node"},
                "labelMarkdown": {
                    "type": "string",
                    "description": "Annotation label in Markdown",
                },
                "annotationId": {
                    "type": "string",
                    "description": "ID of an existing annotation to update (optional)",
                },
                "categoryId": {
                    "type": "string",
                    "description": "Category ID for the annotation (optional)",
                },
                "properties": {
                    "type": "array",
                    "items": {"type": "object"},
                    "description": "Additional annotation properties (optional)",
                },
            },
            "required": ["nodeId", "labelMarkdown"],
        },
    ),
    Tool(
        name="set_multiple_annotations",
        description="Set annotations on multiple nodes in Figma",
        inputSchema={
            "type": "object",
            "properties": {
                "nodeId": {
                    "type": "string",
                    "description": "ID of the node to add annotations to (optional)",
                },
                "annotations": {
                    "type": "array",
                    "items": {"type": "object"},
                    "description": "List of annotation objects",
                }
            },
            "required": ["annotations"],
        },
    ),
    Tool(
        name="scan_text_nodes",
        description="Scan text nodes within a node in Figma",
        inputSchema={
            "type": "object",
            "properties": {
                "nodeId": {"type": "string", "description": "ID of the node to scan"},
                "useChunking": {
                    "type": "boolean",
                    "description": "Whether to use chunked scanning (optional)",
                },
                "chunkSize": {
                    "type": "integer",
                    "description": "Chunk size for chunked scanning (optional)",
                },
            },
            "required": ["nodeId"],
        },
    ),
    Tool(
        name="scan_nodes_by_types",
        description="Scan nodes by their type within a node in Figma",
        inputSchema={
            "type": "object",
            "properties": {
                "nodeId": {"type": "string", "description": "ID of the parent node"},
                "types": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of node types to scan for",
                },
            },
            "required": ["nodeId", "types"],
        },
    ),
    Tool(
        name="get_instance_overrides",
        description="Get overrides from a component instance in Figma",
        inputSchema={
            "type": "object",
            "properties": {
                "nodeId": {
                    "type": "string",
                    "description": "ID of the component instance (optional — uses current selection if omitted)",
                }
            },
            "required": [],
        },
    ),
    Tool(
        name="set_instance_overrides",
        description="Apply instance overrides from one instance to multiple target instances",
        inputSchema={
            "type": "object",
            "properties": {
                "sourceInstanceId": {
                    "type": "string",
                    "description": "ID of the source component instance",
                },
                "targetNodeIds": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "IDs of target instances to apply overrides to",
                },
            },
            "required": ["sourceInstanceId", "targetNodeIds"],
        },
    ),
    Tool(
        name="set_default_connector",
        description="Set the default connector style for new connections in Figma",
        inputSchema={
            "type": "object",
            "properties": {
                "connectorId": {
                    "type": "string",
                    "description": "ID of the connector node to use as default (optional)",
                }
            },
            "required": [],
        },
    ),
    Tool(
        name="create_connections",
        description="Create connections (connectors) between nodes in Figma",
        inputSchema={
            "type": "object",
            "properties": {
                "connections": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "startNodeId": {"type": "string"},
                            "endNodeId": {"type": "string"},
                            "text": {"type": "string"},
                        },
                        "required": ["startNodeId", "endNodeId"],
                    },
                    "description": "List of connections to create",
                }
            },
            "required": ["connections"],
        },
    ),
    Tool(
        name="set_focus",
        description="Set the viewport focus on a specific node in Figma",
        inputSchema={
            "type": "object",
            "properties": {
                "nodeId": {
                    "type": "string",
                    "description": "ID of the node to focus on",
                }
            },
            "required": ["nodeId"],
        },
    ),
    Tool(
        name="set_selections",
        description="Set the current selection to a list of nodes in Figma",
        inputSchema={
            "type": "object",
            "properties": {
                "nodeIds": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of node IDs to select",
                }
            },
            "required": ["nodeIds"],
        },
    ),
    Tool(
        name="execute_code",
        description=(
            "Execute arbitrary JavaScript code in the Figma plugin context. "
            "The code runs as the body of an async function with `figma` (full Figma Plugin API) "
            "and `params` (your data object) in scope. Returns whatever the code returns. "
            "Use this to run complex, multi-step Figma operations in a single call — ideal for "
            "skills that create templated designs (e.g. typography systems, component sets)."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "code": {
                    "type": "string",
                    "description": "JavaScript code to execute. Runs as the body of: async function(figma, params) { <your code> }. Has full figma.* API access and async/await support.",
                },
                "params": {
                    "type": "object",
                    "description": "Data to pass into the code as the `params` argument (fonts, sizes, node IDs, etc.)",
                    "additionalProperties": True,
                },
            },
            "required": ["code"],
        },
    ),
    Tool(
        name="join_channel",
        description="Join a specific channel to communicate with Figma",
        inputSchema={
            "type": "object",
            "properties": {
                "channel": {
                    "type": "string",
                    "description": "The name of the channel to join",
                    "default": "",
                }
            },
            "required": [],
        },
    ),
]

_TOOL_NAME_SET = {t.name for t in ALL_TOOLS}
