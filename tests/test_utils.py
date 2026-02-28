"""Tests for figma_mcp.utils — pure helpers, no mocking needed."""

import pytest
from mcp.types import TextContent

from figma_mcp.utils import err, filter_figma_node, ok, rgba_to_hex


# ── rgba_to_hex ───────────────────────────────────────────────────────────────


class TestRgbaToHex:
    def test_black(self):
        assert rgba_to_hex({"r": 0, "g": 0, "b": 0, "a": 1}) == "#000000"

    def test_white(self):
        assert rgba_to_hex({"r": 1, "g": 1, "b": 1, "a": 1}) == "#ffffff"

    def test_red(self):
        assert rgba_to_hex({"r": 1, "g": 0, "b": 0, "a": 1}) == "#ff0000"

    def test_full_alpha_omitted_from_output(self):
        result = rgba_to_hex({"r": 0, "g": 0, "b": 0, "a": 1})
        assert len(result) == 7  # #rrggbb only

    def test_partial_alpha_appended(self):
        # round(0.5 * 255) = 128 = 0x80
        assert rgba_to_hex({"r": 1, "g": 0, "b": 0, "a": 0.5}) == "#ff000080"

    def test_zero_alpha_appended(self):
        # round(0 * 255) = 0 = 0x00
        assert rgba_to_hex({"r": 0, "g": 0, "b": 0, "a": 0}) == "#00000000"

    def test_default_alpha_is_opaque(self):
        # missing 'a' key defaults to 1, so no alpha suffix
        result = rgba_to_hex({"r": 1, "g": 0, "b": 0})
        assert result == "#ff0000"

    def test_already_hex_string_passthrough(self):
        assert rgba_to_hex("#aabbcc") == "#aabbcc"

    def test_arbitrary_string_passthrough(self):
        assert rgba_to_hex("transparent") == "transparent"

    def test_channel_values_rounded(self):
        # 0.502 * 255 = 128.01 → rounds to 128 = 0x80
        result = rgba_to_hex({"r": 0, "g": 0.502, "b": 0, "a": 1})
        assert result == "#008000"


# ── filter_figma_node ─────────────────────────────────────────────────────────


class TestFilterFigmaNode:
    def test_vector_node_returns_none(self):
        assert filter_figma_node({"type": "VECTOR", "id": "1", "name": "v"}) is None

    def test_non_dict_returned_unchanged(self):
        assert filter_figma_node("not a dict") == "not a dict"
        assert filter_figma_node(42) == 42
        assert filter_figma_node(None) is None

    def test_basic_fields_preserved(self):
        result = filter_figma_node({"id": "1:2", "name": "Box", "type": "RECTANGLE"})
        assert result == {"id": "1:2", "name": "Box", "type": "RECTANGLE"}

    def test_fill_color_converted_to_hex(self):
        node = {
            "id": "1", "name": "n", "type": "FRAME",
            "fills": [{"type": "SOLID", "color": {"r": 1, "g": 0, "b": 0, "a": 1}}],
        }
        result = filter_figma_node(node)
        assert result["fills"][0]["color"] == "#ff0000"

    def test_fill_bound_variables_removed(self):
        node = {
            "id": "1", "name": "n", "type": "FRAME",
            "fills": [{"type": "SOLID", "color": {"r": 0, "g": 0, "b": 0, "a": 1}, "boundVariables": {"color": "var1"}}],
        }
        result = filter_figma_node(node)
        assert "boundVariables" not in result["fills"][0]

    def test_fill_image_ref_removed(self):
        node = {
            "id": "1", "name": "n", "type": "RECTANGLE",
            "fills": [{"type": "IMAGE", "imageRef": "abc123"}],
        }
        result = filter_figma_node(node)
        assert "imageRef" not in result["fills"][0]

    def test_empty_fills_list_omitted(self):
        node = {"id": "1", "name": "n", "type": "FRAME", "fills": []}
        result = filter_figma_node(node)
        assert "fills" not in result

    def test_stroke_color_converted(self):
        node = {
            "id": "1", "name": "n", "type": "RECTANGLE",
            "strokes": [{"type": "SOLID", "color": {"r": 0, "g": 0, "b": 1, "a": 1}}],
        }
        result = filter_figma_node(node)
        assert result["strokes"][0]["color"] == "#0000ff"

    def test_stroke_bound_variables_removed(self):
        node = {
            "id": "1", "name": "n", "type": "RECTANGLE",
            "strokes": [{"type": "SOLID", "color": {"r": 0, "g": 0, "b": 0, "a": 1}, "boundVariables": {}}],
        }
        result = filter_figma_node(node)
        assert "boundVariables" not in result["strokes"][0]

    def test_gradient_stop_colors_converted(self):
        node = {
            "id": "1", "name": "n", "type": "FRAME",
            "fills": [{
                "type": "GRADIENT_LINEAR",
                "gradientStops": [
                    {"position": 0, "color": {"r": 1, "g": 0, "b": 0, "a": 1}},
                    {"position": 1, "color": {"r": 0, "g": 0, "b": 1, "a": 1}},
                ],
            }],
        }
        result = filter_figma_node(node)
        stops = result["fills"][0]["gradientStops"]
        assert stops[0]["color"] == "#ff0000"
        assert stops[1]["color"] == "#0000ff"

    def test_gradient_stop_bound_variables_removed(self):
        node = {
            "id": "1", "name": "n", "type": "FRAME",
            "fills": [{
                "type": "GRADIENT_LINEAR",
                "gradientStops": [
                    {"position": 0, "color": {"r": 0, "g": 0, "b": 0, "a": 1}, "boundVariables": {"color": "var"}},
                ],
            }],
        }
        result = filter_figma_node(node)
        assert "boundVariables" not in result["fills"][0]["gradientStops"][0]

    def test_optional_fields_included_when_present(self):
        node = {
            "id": "1", "name": "n", "type": "RECTANGLE",
            "cornerRadius": 8,
            "absoluteBoundingBox": {"x": 0, "y": 0, "width": 100, "height": 50},
            "characters": "Hello",
        }
        result = filter_figma_node(node)
        assert result["cornerRadius"] == 8
        assert result["absoluteBoundingBox"] == {"x": 0, "y": 0, "width": 100, "height": 50}
        assert result["characters"] == "Hello"

    def test_optional_fields_absent_when_missing(self):
        node = {"id": "1", "name": "n", "type": "RECTANGLE"}
        result = filter_figma_node(node)
        assert "cornerRadius" not in result
        assert "absoluteBoundingBox" not in result
        assert "characters" not in result

    def test_style_extracted_with_known_keys(self):
        node = {
            "id": "1", "name": "n", "type": "TEXT",
            "style": {
                "fontFamily": "Inter",
                "fontStyle": "Regular",
                "fontWeight": 400,
                "fontSize": 16,
                "textAlignHorizontal": "LEFT",
                "letterSpacing": 0,
                "lineHeightPx": 20,
                "unknownKey": "ignored",
            },
        }
        result = filter_figma_node(node)
        assert result["style"]["fontFamily"] == "Inter"
        assert result["style"]["fontSize"] == 16
        assert "unknownKey" not in result["style"]

    def test_vector_children_filtered_out(self):
        node = {
            "id": "1", "name": "n", "type": "FRAME",
            "children": [
                {"id": "2", "name": "rect", "type": "RECTANGLE"},
                {"id": "3", "name": "vec", "type": "VECTOR"},
            ],
        }
        result = filter_figma_node(node)
        assert len(result["children"]) == 1
        assert result["children"][0]["type"] == "RECTANGLE"

    def test_nested_children_recursively_filtered(self):
        node = {
            "id": "1", "name": "root", "type": "FRAME",
            "children": [{
                "id": "2", "name": "group", "type": "GROUP",
                "children": [
                    {"id": "3", "name": "vec", "type": "VECTOR"},
                    {"id": "4", "name": "rect", "type": "RECTANGLE"},
                ],
            }],
        }
        result = filter_figma_node(node)
        inner_children = result["children"][0]["children"]
        assert len(inner_children) == 1
        assert inner_children[0]["id"] == "4"

    def test_unknown_top_level_fields_not_included(self):
        node = {"id": "1", "name": "n", "type": "FRAME", "opacity": 0.5, "visible": True}
        result = filter_figma_node(node)
        assert "opacity" not in result
        assert "visible" not in result


# ── ok / err ──────────────────────────────────────────────────────────────────


class TestOkAndErr:
    def test_ok_wraps_dict_as_json(self):
        result = ok({"status": "success"})
        assert len(result) == 1
        assert isinstance(result[0], TextContent)
        assert result[0].type == "text"
        assert '"status"' in result[0].text
        assert '"success"' in result[0].text

    def test_ok_wraps_string(self):
        result = ok("hello")
        assert result[0].text == '"hello"'

    def test_ok_wraps_list(self):
        result = ok([1, 2, 3])
        assert result[0].text == "[1, 2, 3]"

    def test_err_wraps_message_as_plain_text(self):
        result = err("something went wrong")
        assert len(result) == 1
        assert isinstance(result[0], TextContent)
        assert result[0].text == "something went wrong"

    def test_err_does_not_json_encode(self):
        # err returns the raw string, not JSON-encoded
        result = err("plain message")
        assert result[0].text == "plain message"
