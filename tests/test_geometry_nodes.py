"""Tests for Geometry Nodes support.

Covers serialize/encode/decode round-trips for ``GeometryNodeTree`` data
using the same mock infrastructure as the shader-node tests.
"""

from unittest.mock import MagicMock

from node_runner.serialize import serialize_node_tree
from node_runner.encoding import (
    encode,
    decode,
    encode_json,
    decode_json,
    encode_ai_json,
    decode_ai_json,
    encode_xml,
    decode_xml,
)

from tests.helpers import MockNode, MockNodeTree


class TestSerializeGeometryTree:
    """Geometry node trees should serialize with tree_type set."""

    def test_empty_geometry_tree(self):
        tree = MockNodeTree(name="Geo", bl_idname="GeometryNodeTree")
        result = serialize_node_tree(tree)
        assert result["tree_type"] == "GeometryNodeTree"
        assert result["name"] == "Geo"
        assert not result["nodes"]
        assert not result["links"]

    def test_simple_set_position_graph(self):
        tree = MockNodeTree(name="Geo", bl_idname="GeometryNodeTree")
        gi = MockNode(name="Group Input", bl_idname="NodeGroupInput")
        sp = MockNode(
            name="Set Position",
            bl_idname="GeometryNodeSetPosition",
        )
        go = MockNode(name="Group Output", bl_idname="NodeGroupOutput")
        for n in (gi, sp, go):
            tree.nodes.add(n)

        result = serialize_node_tree(tree)
        assert result["tree_type"] == "GeometryNodeTree"
        assert set(result["nodes"]) == {"Group Input", "Set Position", "Group Output"}
        assert result["nodes"]["Set Position"]["type"] == "GeometryNodeSetPosition"

    def test_geometry_only_socket_types_preserved_in_links(self):
        """Links involving Geometry/Object/Material sockets keep their
        ``bl_idname`` so deserialization can rebuild the socket types
        on group input/output."""
        tree = MockNodeTree(name="Geo", bl_idname="GeometryNodeTree")
        src = MockNode(name="Src", bl_idname="GeometryNodeObjectInfo")
        dst = MockNode(name="Dst", bl_idname="GeometryNodeSetPosition")
        tree.nodes.add(src)
        tree.nodes.add(dst)

        link = MagicMock()
        link.from_node.name = "Src"
        link.to_node.name = "Dst"
        link.from_socket.name = "Geometry"
        link.from_socket.bl_idname = "NodeSocketGeometry"
        link.from_socket.identifier = "geometry"
        link.to_socket.name = "Geometry"
        link.to_socket.bl_idname = "NodeSocketGeometry"
        link.to_socket.identifier = "Geometry"
        tree.links.append(link)

        result = serialize_node_tree(tree, selected_node_names=["Src", "Dst"])
        assert len(result["links"]) == 1
        link_data = result["links"][0]
        assert link_data["from_socket_type"] == "NodeSocketGeometry"
        assert link_data["to_socket_type"] == "NodeSocketGeometry"


class TestSerializeRepeatZonePairing:
    """Repeat / simulation zone inputs must record their paired output."""

    def _make_paired(self, in_bl_idname, out_name="ZoneOut"):
        in_node = MockNode(name="ZoneIn", bl_idname=in_bl_idname)
        out_node = MockNode(name=out_name, bl_idname=in_bl_idname.replace("Input", "Output"))
        in_node.paired_output = out_node
        return in_node, out_node

    def test_repeat_input_records_paired_output(self):
        tree = MockNodeTree(name="Geo", bl_idname="GeometryNodeTree")
        zin, zout = self._make_paired("GeometryNodeRepeatInput")
        tree.nodes.add(zin)
        tree.nodes.add(zout)

        result = serialize_node_tree(tree)
        assert result["nodes"]["ZoneIn"].get("_paired_output") == "ZoneOut"

    def test_simulation_input_records_paired_output(self):
        tree = MockNodeTree(name="Geo", bl_idname="GeometryNodeTree")
        zin, zout = self._make_paired("GeometryNodeSimulationInput")
        tree.nodes.add(zin)
        tree.nodes.add(zout)

        result = serialize_node_tree(tree)
        assert result["nodes"]["ZoneIn"].get("_paired_output") == "ZoneOut"

    def test_foreach_input_records_paired_output(self):
        tree = MockNodeTree(name="Geo", bl_idname="GeometryNodeTree")
        zin, zout = self._make_paired("GeometryNodeForeachGeometryElementInput")
        tree.nodes.add(zin)
        tree.nodes.add(zout)

        result = serialize_node_tree(tree)
        assert result["nodes"]["ZoneIn"].get("_paired_output") == "ZoneOut"


class TestEncodingRoundTripPreservesGeometryTreeType:
    """All four encoders must round-trip ``tree_type = GeometryNodeTree``."""

    def _payload(self):
        return {
            "name": "Geo",
            "tree_type": "GeometryNodeTree",
            "nodes": {
                "SetPos": {
                    "type": "GeometryNodeSetPosition",
                    "label": "",
                    "location": [100.0, 200.0],
                    "location_absolute": [100.0, 200.0],
                }
            },
            "links": [],
        }

    def test_compact_hash_roundtrip(self):
        decoded = decode(encode(self._payload()))
        assert decoded["tree_type"] == "GeometryNodeTree"

    def test_json_roundtrip(self):
        decoded = decode_json(encode_json(self._payload()))
        assert decoded["tree_type"] == "GeometryNodeTree"

    def test_ai_json_roundtrip(self):
        decoded = decode_ai_json(encode_ai_json(self._payload()))
        assert decoded["tree_type"] == "GeometryNodeTree"

    def test_xml_roundtrip(self):
        decoded = decode_xml(encode_xml(self._payload()))
        assert decoded["tree_type"] == "GeometryNodeTree"
