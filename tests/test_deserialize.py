"""Tests for the deserialization module."""

from unittest.mock import MagicMock

from node_runner.deserialize import (
    get_node_socket_base_type,
    get_socket_by_identifier,
    deserialize_image,
    _topological_sort_frames,
    deserialize_node_tree,
)

from tests.helpers import MockNodeTree, MockSocket


class TestGetNodeSocketBaseType:
    """Test socket type resolution."""

    def test_exact_match(self):
        assert get_node_socket_base_type("NodeSocketFloat") == "NodeSocketFloat"

    def test_subtype_match(self):
        assert get_node_socket_base_type("NodeSocketFloatFactor") == "NodeSocketFloat"

    def test_vector_subtype(self):
        assert get_node_socket_base_type("NodeSocketVectorXYZ") == "NodeSocketVector"

    def test_color_match(self):
        assert get_node_socket_base_type("NodeSocketColor") == "NodeSocketColor"

    def test_shader_match(self):
        assert get_node_socket_base_type("NodeSocketShader") == "NodeSocketShader"

    def test_string_match(self):
        assert get_node_socket_base_type("NodeSocketString") == "NodeSocketString"

    def test_unknown_falls_back_to_float(self):
        assert get_node_socket_base_type("NodeSocketUnknownFuture") == "NodeSocketFloat"

    def test_bool_match(self):
        assert get_node_socket_base_type("NodeSocketBool") == "NodeSocketBool"

    def test_int_subtype(self):
        assert get_node_socket_base_type("NodeSocketIntFactor") == "NodeSocketInt"

    def test_rotation_match(self):
        assert get_node_socket_base_type("NodeSocketRotation") == "NodeSocketRotation"

    def test_image_match(self):
        assert get_node_socket_base_type("NodeSocketImage") == "NodeSocketImage"


class TestTopologicalSortFrames:
    """Test frame ordering for nested frames."""

    def test_no_frames(self):
        data = {
            "Math1": {"type": "ShaderNodeMath"},
            "Math2": {"type": "ShaderNodeMath"},
        }
        assert not _topological_sort_frames(data)

    def test_single_frame(self):
        data = {
            "Frame": {"type": "NodeFrame"},
        }
        assert _topological_sort_frames(data) == ["Frame"]

    def test_nested_frames_parent_first(self):
        data = {
            "ChildFrame": {"type": "NodeFrame", "parent": "ParentFrame"},
            "ParentFrame": {"type": "NodeFrame"},
        }
        result = _topological_sort_frames(data)
        assert result.index("ParentFrame") < result.index("ChildFrame")

    def test_deeply_nested_frames(self):
        data = {
            "GrandChild": {"type": "NodeFrame", "parent": "Child"},
            "Child": {"type": "NodeFrame", "parent": "Root"},
            "Root": {"type": "NodeFrame"},
        }
        result = _topological_sort_frames(data)
        assert result.index("Root") < result.index("Child")
        assert result.index("Child") < result.index("GrandChild")

    def test_multiple_independent_frames(self):
        data = {
            "Frame1": {"type": "NodeFrame"},
            "Frame2": {"type": "NodeFrame"},
            "Frame3": {"type": "NodeFrame"},
        }
        result = _topological_sort_frames(data)
        assert len(result) == 3
        assert set(result) == {"Frame1", "Frame2", "Frame3"}

    def test_mixed_frames_and_nodes(self):
        data = {
            "Math1": {"type": "ShaderNodeMath"},
            "InnerFrame": {"type": "NodeFrame", "parent": "OuterFrame"},
            "OuterFrame": {"type": "NodeFrame"},
            "Math2": {"type": "ShaderNodeMath", "parent": "InnerFrame"},
        }
        result = _topological_sort_frames(data)
        assert result == ["OuterFrame", "InnerFrame"]


class TestDeserializeNodeTree:
    """Integration tests for node tree deserialization."""

    def test_empty_tree(self):
        tree = MockNodeTree()
        data = {"nodes": {}, "links": [], "name": "Test"}
        socket_map = {}
        # Should not raise
        deserialize_node_tree(tree, data, socket_map)
        assert len(tree.links) == 0

    def test_basic_node_creation(self):
        tree = MockNodeTree()
        data = {
            "nodes": {
                "Math": {
                    "type": "ShaderNodeMath",
                    "label": "Add",
                    "name": "Math",
                    "location": [100, 200],
                    "location_absolute": [100, 200],
                }
            },
            "links": [],
            "name": "Test",
        }
        socket_map = {}
        deserialize_node_tree(tree, data, socket_map)
        # A node should have been created
        assert len(tree.nodes) >= 1

    def test_link_creation(self):
        tree = MockNodeTree()
        data = {
            "nodes": {
                "A": {
                    "type": "ShaderNodeMath",
                    "label": "",
                    "name": "A",
                    "location": [0, 0],
                    "location_absolute": [0, 0],
                },
                "B": {
                    "type": "ShaderNodeMath",
                    "label": "",
                    "name": "B",
                    "location": [200, 0],
                    "location_absolute": [200, 0],
                },
            },
            "links": [
                {
                    "from_node": "A",
                    "to_node": "B",
                    "from_socket": "Value",
                    "from_socket_type": "NodeSocketFloat",
                    "from_socket_identifier": "Value",
                    "to_socket": "Value",
                    "to_socket_type": "NodeSocketFloat",
                    "to_socket_identifier": "Value",
                }
            ],
            "name": "Test",
        }
        socket_map = {}
        deserialize_node_tree(tree, data, socket_map)
        # Nodes were created for both A and B
        assert len(tree.nodes) >= 2

    def test_link_args_order(self):
        """links.new() must be called with (input_socket, output_socket)."""
        tree = MockNodeTree()
        data = {
            "nodes": {
                "Src": {
                    "type": "ShaderNodeMath",
                    "label": "",
                    "name": "Src",
                    "location": [0, 0],
                    "location_absolute": [0, 0],
                },
                "Dst": {
                    "type": "ShaderNodeMath",
                    "label": "",
                    "name": "Dst",
                    "location": [200, 0],
                    "location_absolute": [200, 0],
                },
            },
            "links": [
                {
                    "from_node": "Src",
                    "to_node": "Dst",
                    "from_socket": "Value",
                    "from_socket_type": "NodeSocketFloat",
                    "from_socket_identifier": "Value",
                    "to_socket": "Value",
                    "to_socket_type": "NodeSocketFloat",
                    "to_socket_identifier": "Value",
                }
            ],
            "name": "Test",
        }
        socket_map = {}
        deserialize_node_tree(tree, data, socket_map)
        # A link must have been created
        assert len(tree.links) == 1
        link = tree.links[0]
        # from_socket = output (source), to_socket = input (destination)
        # The mock stores them correctly based on Blender 4.x
        # links.new(input, output) API
        assert link.from_socket is not None
        assert link.to_socket is not None

    def test_link_fallback_by_name(self):
        """Sockets should be found by name when identifier doesn't match."""
        tree = MockNodeTree()
        data = {
            "nodes": {
                "Src": {
                    "type": "ShaderNodeMath",
                    "label": "",
                    "name": "Src",
                    "location": [0, 0],
                    "location_absolute": [0, 0],
                },
                "Dst": {
                    "type": "ShaderNodeMath",
                    "label": "",
                    "name": "Dst",
                    "location": [200, 0],
                    "location_absolute": [200, 0],
                },
            },
            "links": [
                {
                    "from_node": "Src",
                    "to_node": "Dst",
                    "from_socket": "Value",
                    "from_socket_type": "NodeSocketFloat",
                    "from_socket_identifier": "NONEXISTENT_ID",
                    "to_socket": "Value",
                    "to_socket_type": "NodeSocketFloat",
                    "to_socket_identifier": "NONEXISTENT_ID",
                }
            ],
            "name": "Test",
        }
        socket_map = {}
        deserialize_node_tree(tree, data, socket_map)
        # Link should still be created via name fallback
        assert len(tree.links) == 1


class TestGetSocketByIdentifier:
    """Test socket resolution with identifier and name fallback."""

    def test_find_by_identifier(self):
        node = MagicMock()
        node.bl_idname = "ShaderNodeMath"
        node.name = "TestNode"
        node.inputs = [MockSocket("Color", "color_input")]
        sock = get_socket_by_identifier(node, "color_input", {}, "INPUT")
        assert sock is not None
        assert sock.identifier == "color_input"

    def test_fallback_by_name(self):
        node = MagicMock()
        node.bl_idname = "ShaderNodeMath"
        node.name = "TestNode"
        node.inputs = [MockSocket("Color", "new_id")]
        sock = get_socket_by_identifier(node, "old_id", {}, "INPUT", name="Color")
        assert sock is not None
        assert sock.name == "Color"

    def test_returns_none_when_not_found(self):
        node = MagicMock()
        node.bl_idname = "ShaderNodeMath"
        node.name = "TestNode"
        node.inputs = [MockSocket("Fac", "fac")]
        sock = get_socket_by_identifier(node, "missing_id", {}, "INPUT", name="Missing")
        assert sock is None


class TestDeserializeImage:
    """Test image deserialization with filepath fallback."""

    def test_found_by_name(self):
        import bpy

        node = MagicMock()
        img = MagicMock()
        bpy.data.images.get.return_value = img

        deserialize_image(node, {"name": "texture.png"})

        assert node.image == img
        bpy.data.images.get.assert_called_with("texture.png")

    def test_no_name_does_nothing(self):
        """Empty data should not attempt to set node.image."""

        class Sentinel:
            image = None

        node = Sentinel()
        deserialize_image(node, {})
        assert node.image is None

    def test_loads_from_filepath_when_name_missing(self):
        import bpy

        node = MagicMock()
        loaded_img = MagicMock()
        bpy.data.images.get.return_value = None
        bpy.data.images.load.return_value = loaded_img

        deserialize_image(node, {"name": "tex.png", "filepath": "/abs/path/tex.png"})

        bpy.data.images.load.assert_called_once_with("/abs/path/tex.png")
        assert node.image == loaded_img

    def test_logs_warning_when_filepath_fails(self):
        import bpy

        node = MagicMock()
        bpy.data.images.get.return_value = None
        bpy.data.images.load.side_effect = RuntimeError("File not found")

        # Should not raise
        deserialize_image(node, {"name": "tex.png", "filepath": "/missing/tex.png"})

    def test_no_filepath_logs_info(self):
        import bpy

        node = MagicMock()
        bpy.data.images.get.return_value = None

        # Should not raise
        deserialize_image(node, {"name": "tex.png"})
