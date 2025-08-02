"""
Tests for intent_kit.graph.graph_components module.
"""

import pytest
from unittest.mock import patch, mock_open
from typing import Dict, cast

from intent_kit.graph.graph_components import (
    JsonParser,
    GraphValidator,
    RelationshipBuilder,
)
from intent_kit.nodes import TreeNode
from intent_kit.nodes.enums import NodeType


class MockTreeNode(TreeNode):
    """Mock TreeNode for testing."""

    def __init__(
        self, name: str, description: str = "", node_type: NodeType = NodeType.ACTION
    ):
        super().__init__(name=name, description=description)
        self._node_type = node_type
        self.children = []
        self.parent = None

    @property
    def node_type(self) -> NodeType:
        return self._node_type

    def execute(self, user_input: str, context=None):
        """Mock execution method."""
        from intent_kit.nodes import ExecutionResult

        return ExecutionResult(
            success=True,
            node_name=self.name,
            node_path=[self.name],
            node_type=self.node_type,
            input=user_input,
            output=f"Mock result for {user_input}",
            error=None,
            params={},
            children_results=[],
        )


class TestJsonParser:
    """Test JsonParser class."""

    def test_init(self):
        """Test JsonParser initialization."""
        parser = JsonParser()
        assert parser.logger is not None

    def test_parse_yaml_with_dict(self):
        """Test parse_yaml method with dict input."""
        parser = JsonParser()
        yaml_dict = {"key": "value", "nested": {"inner": "data"}}

        result = parser.parse_yaml(yaml_dict)

        assert result == yaml_dict

    @patch("builtins.open", new_callable=mock_open, read_data='{"key": "value"}')
    @patch("intent_kit.services.yaml_service.yaml_service.safe_load")
    def test_parse_yaml_with_file_path(self, mock_safe_load, mock_file):
        """Test parse_yaml method with file path input."""
        parser = JsonParser()
        mock_safe_load.return_value = {"key": "value"}

        result = parser.parse_yaml("test.yaml")

        mock_file.assert_called_once_with("test.yaml", "r")
        mock_safe_load.assert_called_once()
        assert result == {"key": "value"}

    @patch("builtins.open", side_effect=FileNotFoundError("File not found"))
    def test_parse_yaml_with_invalid_file_path(self, mock_file):
        """Test parse_yaml method with invalid file path."""
        parser = JsonParser()

        with pytest.raises(
            ValueError, match="Failed to load YAML file 'invalid.yaml': File not found"
        ):
            parser.parse_yaml("invalid.yaml")

    @patch("builtins.open", side_effect=PermissionError("Permission denied"))
    def test_parse_yaml_with_permission_error(self, mock_file):
        """Test parse_yaml method with permission error."""
        parser = JsonParser()

        with pytest.raises(
            ValueError,
            match="Failed to load YAML file 'restricted.yaml': Permission denied",
        ):
            parser.parse_yaml("restricted.yaml")


class TestGraphValidator:
    """Test GraphValidator class."""

    def test_init(self):
        """Test GraphValidator initialization."""
        validator = GraphValidator()
        assert validator.logger is not None

    def test_detect_cycles_no_cycles(self):
        """Test detect_cycles method with no cycles."""
        validator = GraphValidator()
        nodes = {
            "root": {"children": ["child1", "child2"]},
            "child1": {"children": ["grandchild1"]},
            "child2": {"children": []},
            "grandchild1": {"children": []},
        }

        cycles = validator.detect_cycles(nodes)

        assert cycles == []

    def test_detect_cycles_with_cycle(self):
        """Test detect_cycles method with a cycle."""
        validator = GraphValidator()
        nodes = {
            "root": {"children": ["child1"]},
            "child1": {"children": ["child2"]},
            "child2": {"children": ["child1"]},  # Creates cycle
        }

        cycles = validator.detect_cycles(nodes)

        assert len(cycles) > 0
        # Check that the cycle contains the expected nodes
        cycle_found = False
        for cycle in cycles:
            if "child1" in cycle and "child2" in cycle:
                cycle_found = True
                break
        assert cycle_found

    def test_detect_cycles_self_loop(self):
        """Test detect_cycles method with self-loop."""
        validator = GraphValidator()
        nodes = {
            "root": {"children": ["root"]},  # Self-loop
        }

        cycles = validator.detect_cycles(nodes)

        assert len(cycles) > 0
        # Check that the cycle contains the self-loop
        cycle_found = False
        for cycle in cycles:
            if len(cycle) == 2 and cycle[0] == cycle[1] == "root":
                cycle_found = True
                break
        assert cycle_found

    def test_detect_cycles_complex_cycle(self):
        """Test detect_cycles method with complex cycle."""
        validator = GraphValidator()
        nodes = {
            "root": {"children": ["a"]},
            "a": {"children": ["b"]},
            "b": {"children": ["c"]},
            "c": {"children": ["a"]},  # Creates cycle a->b->c->a
        }

        cycles = validator.detect_cycles(nodes)

        assert len(cycles) > 0
        # Check that the cycle contains the expected nodes
        cycle_found = False
        for cycle in cycles:
            if "a" in cycle and "b" in cycle and "c" in cycle:
                cycle_found = True
                break
        assert cycle_found

    def test_detect_cycles_empty_nodes(self):
        """Test detect_cycles method with empty nodes dict."""
        validator = GraphValidator()
        nodes = {}

        cycles = validator.detect_cycles(nodes)

        assert cycles == []

    def test_detect_cycles_nodes_without_children(self):
        """Test detect_cycles method with nodes that have no children field."""
        validator = GraphValidator()
        nodes = {
            "root": {},
            "child1": {},
            "child2": {},
        }

        cycles = validator.detect_cycles(nodes)

        assert cycles == []

    def test_find_unreachable_nodes_all_reachable(self):
        """Test find_unreachable_nodes method with all nodes reachable."""
        validator = GraphValidator()
        nodes = {
            "root": {"children": ["child1", "child2"]},
            "child1": {"children": ["grandchild1"]},
            "child2": {"children": []},
            "grandchild1": {"children": []},
        }

        unreachable = validator.find_unreachable_nodes(nodes, "root")

        assert unreachable == []

    def test_find_unreachable_nodes_with_unreachable(self):
        """Test find_unreachable_nodes method with unreachable nodes."""
        validator = GraphValidator()
        nodes = {
            "root": {"children": ["child1"]},
            "child1": {"children": []},
            "child2": {"children": []},  # Unreachable from root
            "child3": {"children": []},  # Unreachable from root
        }

        unreachable = validator.find_unreachable_nodes(nodes, "root")

        assert "child2" in unreachable
        assert "child3" in unreachable
        assert len(unreachable) == 2

    def test_find_unreachable_nodes_complex_graph(self):
        """Test find_unreachable_nodes method with complex graph."""
        validator = GraphValidator()
        nodes = {
            "root": {"children": ["a", "b"]},
            "a": {"children": ["c"]},
            "b": {"children": ["d"]},
            "c": {"children": []},
            "d": {"children": []},
            "isolated1": {"children": []},  # Isolated node
            "isolated2": {"children": ["isolated3"]},  # Isolated subgraph
            "isolated3": {"children": []},
        }

        unreachable = validator.find_unreachable_nodes(nodes, "root")

        assert "isolated1" in unreachable
        assert "isolated2" in unreachable
        assert "isolated3" in unreachable
        assert len(unreachable) == 3

    def test_find_unreachable_nodes_empty_nodes(self):
        """Test find_unreachable_nodes method with empty nodes dict."""
        validator = GraphValidator()
        nodes = {}

        unreachable = validator.find_unreachable_nodes(nodes, "root")

        assert unreachable == []

    def test_find_unreachable_nodes_root_not_in_nodes(self):
        """Test find_unreachable_nodes method when root is not in nodes."""
        validator = GraphValidator()
        nodes = {
            "child1": {"children": []},
            "child2": {"children": []},
        }

        unreachable = validator.find_unreachable_nodes(nodes, "root")

        # All nodes should be unreachable since root doesn't exist
        assert "child1" in unreachable
        assert "child2" in unreachable
        assert len(unreachable) == 2


class TestRelationshipBuilder:
    """Test RelationshipBuilder class."""

    def test_build_relationships_simple(self):
        """Test build_relationships method with simple relationships."""
        builder = RelationshipBuilder()
        graph_spec = {
            "nodes": {
                "root": {"children": ["child1", "child2"]},
                "child1": {"children": []},
                "child2": {"children": []},
            }
        }
        node_map = cast(
            Dict[str, TreeNode],
            {
                "root": MockTreeNode("root"),
                "child1": MockTreeNode("child1"),
                "child2": MockTreeNode("child2"),
            },
        )

        builder.build_relationships(graph_spec, node_map)

        # Check that children are set correctly
        assert len(node_map["root"].children) == 2
        assert node_map["child1"] in node_map["root"].children
        assert node_map["child2"] in node_map["root"].children

        # Check that parent relationships are set
        assert node_map["child1"].parent == node_map["root"]
        assert node_map["child2"].parent == node_map["root"]

    def test_build_relationships_nested(self):
        """Test build_relationships method with nested relationships."""
        builder = RelationshipBuilder()
        graph_spec = {
            "nodes": {
                "root": {"children": ["child1"]},
                "child1": {"children": ["grandchild1", "grandchild2"]},
                "grandchild1": {"children": []},
                "grandchild2": {"children": []},
            }
        }
        node_map = cast(
            Dict[str, TreeNode],
            {
                "root": MockTreeNode("root"),
                "child1": MockTreeNode("child1"),
                "grandchild1": MockTreeNode("grandchild1"),
                "grandchild2": MockTreeNode("grandchild2"),
            },
        )

        builder.build_relationships(graph_spec, node_map)

        # Check root relationships
        assert len(node_map["root"].children) == 1
        assert node_map["child1"] in node_map["root"].children

        # Check child1 relationships
        assert len(node_map["child1"].children) == 2
        assert node_map["grandchild1"] in node_map["child1"].children
        assert node_map["grandchild2"] in node_map["child1"].children

        # Check parent relationships
        assert node_map["child1"].parent == node_map["root"]
        assert node_map["grandchild1"].parent == node_map["child1"]
        assert node_map["grandchild2"].parent == node_map["child1"]

    def test_build_relationships_no_children(self):
        """Test build_relationships method with nodes that have no children."""
        builder = RelationshipBuilder()
        graph_spec = {
            "nodes": {
                "root": {},
                "child1": {},
                "child2": {},
            }
        }
        node_map = cast(
            Dict[str, TreeNode],
            {
                "root": MockTreeNode("root"),
                "child1": MockTreeNode("child1"),
                "child2": MockTreeNode("child2"),
            },
        )

        # Should not raise any exceptions
        builder.build_relationships(graph_spec, node_map)

        # Check that no children were set
        assert len(node_map["root"].children) == 0
        assert len(node_map["child1"].children) == 0
        assert len(node_map["child2"].children) == 0

    def test_build_relationships_missing_child_node(self):
        """Test build_relationships method with missing child node."""
        builder = RelationshipBuilder()
        graph_spec = {
            "nodes": {
                "root": {"children": ["child1", "missing_child"]},
                "child1": {"children": []},
            }
        }
        node_map = cast(
            Dict[str, TreeNode],
            {
                "root": MockTreeNode("root"),
                "child1": MockTreeNode("child1"),
                # missing_child is not in node_map
            },
        )

        with pytest.raises(
            ValueError, match="Child node 'missing_child' not found for node 'root'"
        ):
            builder.build_relationships(graph_spec, node_map)

    def test_build_relationships_empty_graph_spec(self):
        """Test build_relationships method with empty graph spec."""
        builder = RelationshipBuilder()
        graph_spec = {"nodes": {}}
        node_map = {}

        # Should not raise any exceptions
        builder.build_relationships(graph_spec, node_map)

    def test_build_relationships_complex_structure(self):
        """Test build_relationships method with complex node structure."""
        builder = RelationshipBuilder()
        graph_spec = {
            "nodes": {
                "root": {"children": ["branch1", "branch2"]},
                "branch1": {"children": ["leaf1", "leaf2"]},
                "branch2": {"children": ["leaf3"]},
                "leaf1": {"children": []},
                "leaf2": {"children": []},
                "leaf3": {"children": []},
            }
        }
        node_map = cast(
            Dict[str, TreeNode],
            {
                "root": MockTreeNode("root"),
                "branch1": MockTreeNode("branch1"),
                "branch2": MockTreeNode("branch2"),
                "leaf1": MockTreeNode("leaf1"),
                "leaf2": MockTreeNode("leaf2"),
                "leaf3": MockTreeNode("leaf3"),
            },
        )

        builder.build_relationships(graph_spec, node_map)

        # Check root relationships
        assert len(node_map["root"].children) == 2
        assert node_map["branch1"] in node_map["root"].children
        assert node_map["branch2"] in node_map["root"].children

        # Check branch1 relationships
        assert len(node_map["branch1"].children) == 2
        assert node_map["leaf1"] in node_map["branch1"].children
        assert node_map["leaf2"] in node_map["branch1"].children

        # Check branch2 relationships
        assert len(node_map["branch2"].children) == 1
        assert node_map["leaf3"] in node_map["branch2"].children

        # Check parent relationships
        assert node_map["branch1"].parent == node_map["root"]
        assert node_map["branch2"].parent == node_map["root"]
        assert node_map["leaf1"].parent == node_map["branch1"]
        assert node_map["leaf2"].parent == node_map["branch1"]
        assert node_map["leaf3"].parent == node_map["branch2"]
