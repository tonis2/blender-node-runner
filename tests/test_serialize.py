"""Tests for the serialization module."""

from unittest.mock import MagicMock

from mathutils import Color, Euler, Vector

from node_runner.serialize import (
    serialize_color,
    serialize_vector,
    serialize_euler,
    serialize_image,
    serialize_attr,
    serialize_node,
    serialize_node_tree,
)

from tests.helpers import MockNode, MockNodeTree, MockRNAProperty


class TestPrimitiveSerializers:
    """Test basic type serializers."""

    def test_serialize_color(self):
        c = Color((0.5, 0.2, 0.8))
        result = serialize_color(c)
        assert result == [0.5, 0.2, 0.8]

    def test_serialize_vector(self):
        v = Vector((1.0, 2.0, 3.0))
        result = serialize_vector(v)
        assert result == [1.0, 2.0, 3.0]

    def test_serialize_euler(self):
        e = Euler((0.1, 0.2, 0.3))
        result = serialize_euler(e)
        assert result == [0.1, 0.2, 0.3]


class TestSerializeAttr:
    """Test the generic attribute dispatcher."""

    def test_serialize_plain_int(self):
        node = MockNode()
        assert serialize_attr(node, 42) == 42

    def test_serialize_plain_float(self):
        node = MockNode()
        assert serialize_attr(node, 3.14) == 3.14

    def test_serialize_plain_string(self):
        node = MockNode()
        assert serialize_attr(node, "hello") == "hello"

    def test_serialize_plain_bool(self):
        node = MockNode()
        assert serialize_attr(node, True) is True

    def test_serialize_none(self):
        """None should pass through (pickle-safe)."""
        node = MockNode()
        assert serialize_attr(node, None) is None

    def test_serialize_vector(self):
        node = MockNode()
        v = Vector((1.0, 2.0))
        result = serialize_attr(node, v)
        assert result == [1.0, 2.0]

    def test_serialize_list(self):
        node = MockNode()
        result = serialize_attr(node, [1, 2, 3])
        assert result == [1, 2, 3]


class TestSerializeNode:
    """Test node serialization."""

    def test_basic_node(self):
        node = MockNode(
            name="Math",
            bl_idname="ShaderNodeMath",
            label="My Math",
            location=(100, -50),
            operation="ADD",
        )
        result = serialize_node(node)
        assert result["type"] == "ShaderNodeMath"
        assert result["label"] == "My Math"
        assert result["location_absolute"] == [100, -50]
        assert result["operation"] == "ADD"

    def test_node_with_parent(self):
        parent_node = MockNode(name="Frame1", bl_idname="NodeFrame")
        child_node = MockNode(
            name="Child",
            bl_idname="ShaderNodeMath",
            location=(10, 20),
            parent=parent_node,
        )
        # Need to add parent to bl_rna properties
        result = serialize_node(child_node)
        assert result.get("parent") == "Frame1"

    def test_type_always_present(self):
        node = MockNode(bl_idname="ShaderNodeRGB")
        result = serialize_node(node)
        assert "type" in result
        assert result["type"] == "ShaderNodeRGB"


class TestSerializeNodeTree:
    """Test node tree serialization."""

    def test_empty_tree(self):
        tree = MockNodeTree(name="TestTree")
        result = serialize_node_tree(tree)
        assert result["name"] == "TestTree"
        assert not result["nodes"]
        assert not result["links"]

    def test_tree_with_nodes(self):
        tree = MockNodeTree(name="MyMaterial")
        n1 = MockNode(name="Math1", bl_idname="ShaderNodeMath", operation="ADD")
        n2 = MockNode(name="Math2", bl_idname="ShaderNodeMath", operation="MULTIPLY")
        tree.nodes.add(n1)
        tree.nodes.add(n2)

        result = serialize_node_tree(tree)
        assert "Math1" in result["nodes"]
        assert "Math2" in result["nodes"]

    def test_selected_nodes_filter(self):
        tree = MockNodeTree(name="Mat")
        n1 = MockNode(name="Keep", bl_idname="ShaderNodeMath")
        n2 = MockNode(name="Skip", bl_idname="ShaderNodeMath")
        tree.nodes.add(n1)
        tree.nodes.add(n2)

        result = serialize_node_tree(tree, selected_node_names=["Keep"])
        assert "Keep" in result["nodes"]
        assert "Skip" not in result["nodes"]

    def test_tree_type_is_stored(self):
        tree = MockNodeTree(name="Geo", bl_idname="GeometryNodeTree")
        result = serialize_node_tree(tree)
        assert result["tree_type"] == "GeometryNodeTree"

    def test_tree_type_shader(self):
        tree = MockNodeTree(name="Mat", bl_idname="ShaderNodeTree")
        result = serialize_node_tree(tree)
        assert result["tree_type"] == "ShaderNodeTree"


class TestReadonlyPropSerialization:
    """Test that readonly pointer properties are still serialized."""

    def test_readonly_color_ramp_included(self):
        """color_ramp is readonly but should be serialized."""
        node = MockNode(
            name="ValToRGB",
            bl_idname="ShaderNodeValToRGB",
        )
        # Add color_ramp as a readonly property
        node.bl_rna.properties.append(MockRNAProperty("color_ramp", is_readonly=True))
        node.color_ramp = "mock_ramp_value"
        result = serialize_node(node)
        assert "color_ramp" in result

    def test_readonly_mapping_included(self):
        """mapping is readonly but should be serialized."""
        node = MockNode(
            name="RGBCurve",
            bl_idname="ShaderNodeRGBCurve",
        )
        node.bl_rna.properties.append(MockRNAProperty("mapping", is_readonly=True))
        node.mapping = "mock_mapping_value"
        result = serialize_node(node)
        assert "mapping" in result

    def test_truly_readonly_props_excluded(self):
        """Properties that are readonly and NOT in the allow list should be skipped."""
        node = MockNode(
            name="TestNode",
            bl_idname="ShaderNodeMath",
        )
        node.bl_rna.properties.append(
            MockRNAProperty("some_internal", is_readonly=True)
        )
        node.some_internal = "should_not_appear"
        result = serialize_node(node)
        assert "some_internal" not in result


class TestLinkSerialization:
    """Test that links are serialized correctly using name-based matching."""

    def test_links_serialized_by_name(self):
        """Links must be matched by node name, not Python id()."""
        tree = MockNodeTree(name="Mat")
        n1 = MockNode(name="Src", bl_idname="ShaderNodeMath")
        n2 = MockNode(name="Dst", bl_idname="ShaderNodeMath")
        tree.nodes.add(n1)
        tree.nodes.add(n2)

        # Create a mock link where from_node/to_node are DIFFERENT
        # Python objects from what's in nodes (simulating Blender 5.x
        # behaviour where each property access creates a new wrapper).
        mock_link = MagicMock()
        mock_from_node = MagicMock()
        mock_from_node.name = "Src"
        mock_to_node = MagicMock()
        mock_to_node.name = "Dst"

        mock_link.from_node = mock_from_node
        mock_link.to_node = mock_to_node
        mock_link.from_socket.name = "Value"
        mock_link.from_socket.bl_idname = "NodeSocketFloat"
        mock_link.from_socket.identifier = "Value"
        mock_link.to_socket.name = "Value"
        mock_link.to_socket.bl_idname = "NodeSocketFloat"
        mock_link.to_socket.identifier = "Value"
        tree.links.append(mock_link)

        result = serialize_node_tree(tree, selected_node_names=["Src", "Dst"])
        # The link must be included even though the from_node/to_node
        # objects differ from what's stored in tree.nodes
        assert len(result["links"]) == 1
        assert result["links"][0]["from_node"] == "Src"
        assert result["links"][0]["to_node"] == "Dst"

    def test_links_not_serialized_for_unselected_nodes(self):
        """Links to unselected nodes should be excluded."""
        tree = MockNodeTree(name="Mat")
        n1 = MockNode(name="Src", bl_idname="ShaderNodeMath")
        n2 = MockNode(name="Dst", bl_idname="ShaderNodeMath")
        tree.nodes.add(n1)
        tree.nodes.add(n2)

        mock_link = MagicMock()
        mock_link.from_node.name = "Src"
        mock_link.to_node.name = "Dst"
        tree.links.append(mock_link)

        # Only select Src, not Dst
        result = serialize_node_tree(tree, selected_node_names=["Src"])
        assert len(result["links"]) == 0


class TestSerializeImage:
    """Test image serialization with filepath support."""

    def test_name_only_when_no_filepath(self):
        img = MagicMock()
        img.name = "texture.png"
        img.filepath = ""
        result = serialize_image(img)
        assert result == {"name": "texture.png"}
        assert "filepath" not in result

    def test_includes_filepath_when_present(self):
        img = MagicMock()
        img.name = "texture.png"
        img.filepath = "/home/user/textures/texture.png"
        result = serialize_image(img)
        assert result["name"] == "texture.png"
        assert result["filepath"] == "/home/user/textures/texture.png"

    def test_no_filepath_attr(self):
        """Images without a filepath attribute at all should work."""
        img = MagicMock(spec=["name"])
        img.name = "generated"
        result = serialize_image(img)
        assert result == {"name": "generated"}
