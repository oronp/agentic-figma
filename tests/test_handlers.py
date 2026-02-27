"""Tests for figma_mcp.handlers — validation paths and dispatch correctness."""

from unittest.mock import AsyncMock, call

import pytest
from mcp.types import TextContent

from figma_mcp.handlers import handle_tool


# ── Helpers ───────────────────────────────────────────────────────────────────


def make_client(return_value=None):
    """Return a mock FigmaClient with a pre-configured send_command."""
    client = AsyncMock()
    client.send_command = AsyncMock(return_value=return_value or {})
    client.join_channel = AsyncMock()
    client._channel = "test-channel"
    return client


def text_of(result) -> str:
    """Extract the text from the first TextContent in the result."""
    assert result, "Expected at least one result item"
    assert isinstance(result[0], TextContent)
    return result[0].text


# ── Unknown tool ──────────────────────────────────────────────────────────────


async def test_unknown_tool_returns_error():
    result = await handle_tool("does_not_exist", {}, make_client())
    assert "Unknown tool" in text_of(result)


# ── Group A: Document & Selection ────────────────────────────────────────────


async def test_get_node_info_missing_node_id():
    result = await handle_tool("get_node_info", {}, make_client())
    assert "nodeId" in text_of(result)


async def test_get_node_info_calls_correct_command():
    client = make_client({"id": "1:2", "name": "Box", "type": "RECTANGLE"})
    await handle_tool("get_node_info", {"nodeId": "1:2"}, client)
    client.send_command.assert_called_once_with("get_node_info", {"nodeId": "1:2"})


async def test_get_nodes_info_missing_node_ids():
    result = await handle_tool("get_nodes_info", {}, make_client())
    assert "nodeIds" in text_of(result)


async def test_get_reactions_missing_node_ids():
    result = await handle_tool("get_reactions", {}, make_client())
    assert "nodeIds" in text_of(result)


# ── Group B: Create & Modify ──────────────────────────────────────────────────


async def test_create_rectangle_missing_dimensions():
    result = await handle_tool("create_rectangle", {"x": 0, "y": 0}, make_client())
    assert "create_rectangle requires" in text_of(result)


async def test_create_rectangle_calls_correct_command():
    client = make_client({"id": "1"})
    await handle_tool("create_rectangle", {"x": 0, "y": 0, "width": 100, "height": 50}, client)
    client.send_command.assert_called_once()
    cmd, params = client.send_command.call_args[0]
    assert cmd == "create_rectangle"
    assert params["width"] == 100 and params["height"] == 50


async def test_create_frame_missing_dimensions():
    result = await handle_tool("create_frame", {"x": 0}, make_client())
    assert "create_frame requires" in text_of(result)


async def test_create_text_missing_text():
    result = await handle_tool("create_text", {"x": 0, "y": 0}, make_client())
    assert "create_text requires" in text_of(result)


async def test_create_component_instance_missing_component_key():
    result = await handle_tool("create_component_instance", {}, make_client())
    assert "componentKey" in text_of(result)


async def test_clone_node_missing_node_id():
    result = await handle_tool("clone_node", {}, make_client())
    assert "nodeId" in text_of(result)


async def test_delete_node_missing_node_id():
    result = await handle_tool("delete_node", {}, make_client())
    assert "nodeId" in text_of(result)


async def test_delete_multiple_nodes_missing_node_ids():
    result = await handle_tool("delete_multiple_nodes", {}, make_client())
    assert "nodeIds" in text_of(result)


# ── Group C: Style & Appearance ───────────────────────────────────────────────


async def test_set_fill_color_missing_node_id():
    result = await handle_tool("set_fill_color", {"r": 1, "g": 0, "b": 0}, make_client())
    assert "nodeId" in text_of(result)


async def test_set_fill_color_missing_channels():
    result = await handle_tool("set_fill_color", {"nodeId": "1", "r": 1}, make_client())
    assert "set_fill_color requires" in text_of(result)


async def test_set_fill_color_non_numeric_channels():
    result = await handle_tool(
        "set_fill_color", {"nodeId": "1", "r": "red", "g": 0, "b": 0}, make_client()
    )
    assert "must be numbers" in text_of(result)


async def test_set_stroke_color_missing_node_id():
    result = await handle_tool("set_stroke_color", {"r": 0, "g": 0, "b": 0}, make_client())
    assert "nodeId" in text_of(result)


async def test_set_stroke_color_non_numeric_channels():
    result = await handle_tool(
        "set_stroke_color", {"nodeId": "1", "r": 0, "g": "green", "b": 0}, make_client()
    )
    assert "must be numbers" in text_of(result)


async def test_set_corner_radius_missing_node_id():
    result = await handle_tool("set_corner_radius", {"radius": 8}, make_client())
    assert "nodeId" in text_of(result)


async def test_set_corner_radius_missing_radius():
    result = await handle_tool("set_corner_radius", {"nodeId": "1"}, make_client())
    assert "radius" in text_of(result)


async def test_set_text_content_missing_node_id():
    result = await handle_tool("set_text_content", {"text": "hello"}, make_client())
    assert "nodeId" in text_of(result)


async def test_set_text_content_missing_text():
    result = await handle_tool("set_text_content", {"nodeId": "1"}, make_client())
    assert "text" in text_of(result)


async def test_set_multiple_text_contents_missing_node_id():
    result = await handle_tool("set_multiple_text_contents", {"text": [{"key": "v"}]}, make_client())
    assert "nodeId" in text_of(result)


async def test_set_multiple_text_contents_missing_text():
    result = await handle_tool("set_multiple_text_contents", {"nodeId": "1"}, make_client())
    assert "requires text" in text_of(result)


async def test_export_node_as_image_missing_node_id():
    result = await handle_tool("export_node_as_image", {}, make_client())
    assert "nodeId" in text_of(result)


async def test_export_node_as_image_no_image_data_returns_error():
    client = make_client({"imageData": None})
    result = await handle_tool("export_node_as_image", {"nodeId": "1"}, client)
    assert "no image data" in text_of(result)


# ── Group D: Layout & Positioning ─────────────────────────────────────────────


async def test_move_node_missing_node_id():
    result = await handle_tool("move_node", {"x": 0, "y": 0}, make_client())
    assert "nodeId" in text_of(result)


async def test_move_node_missing_coordinates():
    result = await handle_tool("move_node", {"nodeId": "1"}, make_client())
    assert "x and y" in text_of(result)


async def test_move_node_non_numeric_coordinates():
    result = await handle_tool("move_node", {"nodeId": "1", "x": "left", "y": 0}, make_client())
    assert "must be numbers" in text_of(result)


async def test_resize_node_missing_node_id():
    result = await handle_tool("resize_node", {"width": 100, "height": 50}, make_client())
    assert "nodeId" in text_of(result)


async def test_resize_node_missing_dimensions():
    result = await handle_tool("resize_node", {"nodeId": "1"}, make_client())
    assert "width and height" in text_of(result)


async def test_resize_node_non_numeric_dimensions():
    result = await handle_tool("resize_node", {"nodeId": "1", "width": "big", "height": 50}, make_client())
    assert "must be numbers" in text_of(result)


async def test_set_layout_mode_missing_node_id():
    result = await handle_tool("set_layout_mode", {"layoutMode": "HORIZONTAL"}, make_client())
    assert "nodeId" in text_of(result)


async def test_set_layout_mode_missing_layout_mode():
    result = await handle_tool("set_layout_mode", {"nodeId": "1"}, make_client())
    assert "layoutMode" in text_of(result)


async def test_set_padding_missing_node_id():
    result = await handle_tool("set_padding", {"top": 10}, make_client())
    assert "nodeId" in text_of(result)


async def test_set_padding_no_values_provided():
    result = await handle_tool("set_padding", {"nodeId": "1"}, make_client())
    assert "at least one" in text_of(result)


async def test_set_padding_non_numeric_value():
    result = await handle_tool("set_padding", {"nodeId": "1", "top": "big"}, make_client())
    assert "must be a number" in text_of(result)


async def test_set_axis_align_missing_node_id():
    result = await handle_tool("set_axis_align", {"primaryAxisAlignItems": "CENTER"}, make_client())
    assert "nodeId" in text_of(result)


async def test_set_axis_align_no_alignment_provided():
    result = await handle_tool("set_axis_align", {"nodeId": "1"}, make_client())
    assert "at least one" in text_of(result)


async def test_set_layout_sizing_missing_node_id():
    result = await handle_tool("set_layout_sizing", {"layoutSizingHorizontal": "FILL"}, make_client())
    assert "nodeId" in text_of(result)


async def test_set_layout_sizing_no_sizing_provided():
    result = await handle_tool("set_layout_sizing", {"nodeId": "1"}, make_client())
    assert "at least one" in text_of(result)


async def test_set_item_spacing_missing_node_id():
    result = await handle_tool("set_item_spacing", {"itemSpacing": 8}, make_client())
    assert "nodeId" in text_of(result)


async def test_set_item_spacing_missing_spacing():
    result = await handle_tool("set_item_spacing", {"nodeId": "1"}, make_client())
    assert "itemSpacing" in text_of(result)


async def test_set_item_spacing_non_numeric_spacing():
    result = await handle_tool("set_item_spacing", {"nodeId": "1", "itemSpacing": "wide"}, make_client())
    assert "must be a number" in text_of(result)


# ── Group E: Annotations, Connections & Channel ───────────────────────────────


async def test_set_annotation_missing_node_id():
    result = await handle_tool("set_annotation", {"labelMarkdown": "note"}, make_client())
    assert "nodeId" in text_of(result)


async def test_set_annotation_missing_label():
    result = await handle_tool("set_annotation", {"nodeId": "1"}, make_client())
    assert "labelMarkdown" in text_of(result)


async def test_set_annotation_properties_non_list():
    result = await handle_tool(
        "set_annotation",
        {"nodeId": "1", "labelMarkdown": "note", "properties": "not-a-list"},
        make_client(),
    )
    assert "must be an array" in text_of(result)


async def test_set_multiple_annotations_missing():
    result = await handle_tool("set_multiple_annotations", {}, make_client())
    assert "requires annotations" in text_of(result)


async def test_set_multiple_annotations_non_list():
    result = await handle_tool("set_multiple_annotations", {"annotations": "bad"}, make_client())
    assert "must be an array" in text_of(result)


async def test_scan_text_nodes_missing_node_id():
    result = await handle_tool("scan_text_nodes", {}, make_client())
    assert "nodeId" in text_of(result)


async def test_scan_nodes_by_types_missing_node_id():
    result = await handle_tool("scan_nodes_by_types", {"types": ["TEXT"]}, make_client())
    assert "nodeId" in text_of(result)


async def test_scan_nodes_by_types_missing_types():
    result = await handle_tool("scan_nodes_by_types", {"nodeId": "1"}, make_client())
    assert "requires types" in text_of(result)


async def test_scan_nodes_by_types_non_list_types():
    result = await handle_tool("scan_nodes_by_types", {"nodeId": "1", "types": "TEXT"}, make_client())
    assert "must be an array" in text_of(result)


async def test_set_instance_overrides_missing_source():
    result = await handle_tool("set_instance_overrides", {"targetNodeIds": ["1"]}, make_client())
    assert "sourceInstanceId" in text_of(result)


async def test_set_instance_overrides_missing_targets():
    result = await handle_tool("set_instance_overrides", {"sourceInstanceId": "1"}, make_client())
    assert "targetNodeIds" in text_of(result)


async def test_set_instance_overrides_non_list_targets():
    result = await handle_tool(
        "set_instance_overrides", {"sourceInstanceId": "1", "targetNodeIds": "bad"}, make_client()
    )
    assert "must be an array" in text_of(result)


async def test_create_connections_missing():
    result = await handle_tool("create_connections", {}, make_client())
    assert "requires connections" in text_of(result)


async def test_create_connections_non_list():
    result = await handle_tool("create_connections", {"connections": "bad"}, make_client())
    assert "must be an array" in text_of(result)


async def test_create_connections_empty_list():
    # Empty list is falsy, so `if not connections:` fires before the len() check.
    # The "No connections provided" branch in the handler is unreachable dead code.
    result = await handle_tool("create_connections", {"connections": []}, make_client())
    assert "requires connections" in text_of(result)


async def test_create_connections_item_missing_start_node():
    conns = [{"endNodeId": "2"}]
    result = await handle_tool("create_connections", {"connections": conns}, make_client())
    assert "startNodeId" in text_of(result)


async def test_create_connections_item_missing_end_node():
    conns = [{"startNodeId": "1"}]
    result = await handle_tool("create_connections", {"connections": conns}, make_client())
    assert "endNodeId" in text_of(result)


async def test_set_focus_missing_node_id():
    result = await handle_tool("set_focus", {}, make_client())
    assert "nodeId" in text_of(result)


async def test_set_selections_missing_node_ids():
    result = await handle_tool("set_selections", {}, make_client())
    assert "nodeIds" in text_of(result)


async def test_set_selections_non_list():
    result = await handle_tool("set_selections", {"nodeIds": "1"}, make_client())
    assert "must be an array" in text_of(result)


async def test_execute_code_missing_code():
    result = await handle_tool("execute_code", {}, make_client())
    assert "non-empty" in text_of(result)


async def test_execute_code_empty_string():
    result = await handle_tool("execute_code", {"code": "   "}, make_client())
    assert "non-empty" in text_of(result)


async def test_join_channel_missing_channel():
    result = await handle_tool("join_channel", {}, make_client())
    assert "channel name" in text_of(result)


async def test_join_channel_calls_client_join():
    client = make_client()
    result = await handle_tool("join_channel", {"channel": "my-doc"}, client)
    client.join_channel.assert_called_once_with("my-doc")
    assert "my-doc" in text_of(result)
