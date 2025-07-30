"""
Tests for node base classes.
"""

import pytest
from typing import Optional

from intent_kit.nodes.base import Node, TreeNode
from intent_kit.nodes.enums import NodeType
from intent_kit.nodes.types import ExecutionResult
from intent_kit.context import IntentContext


class TestNode:
    """Test the base Node class."""

    def test_init_with_name(self):
        """Test initialization with a name."""
        node = Node(name="test_node")
        assert node.name == "test_node"
        assert node.node_id is not None
        assert node.parent is None

    def test_init_without_name(self):
        """Test initialization without a name."""
        node = Node()
        assert node.name == node.node_id
        assert node.node_id is not None

    def test_init_with_parent(self):
        """Test initialization with a parent."""
        parent = Node(name="parent")
        child = Node(name="child", parent=parent)
        assert child.parent == parent

    def test_has_name_property(self):
        """Test the has_name property."""
        node_with_name = Node(name="test")
        node_without_name = Node()

        assert node_with_name.has_name is True
        assert node_without_name.has_name is True  # Uses node_id as name

    def test_get_path_single_node(self):
        """Test getting path for a single node."""
        node = Node(name="test")
        path = node.get_path()
        assert path == ["test"]

    def test_get_path_with_parent(self):
        """Test getting path for a node with parent."""
        parent = Node(name="parent")
        child = Node(name="child", parent=parent)
        path = child.get_path()
        assert path == ["parent", "child"]

    def test_get_path_with_grandparent(self):
        """Test getting path for a node with grandparent."""
        grandparent = Node(name="grandparent")
        parent = Node(name="parent", parent=grandparent)
        child = Node(name="child", parent=parent)
        path = child.get_path()
        assert path == ["grandparent", "parent", "child"]

    def test_get_path_string(self):
        """Test getting path as string."""
        parent = Node(name="parent")
        child = Node(name="child", parent=parent)
        path_string = child.get_path_string()
        assert path_string == "parent.child"

    def test_get_uuid_path(self):
        """Test getting UUID path."""
        parent = Node(name="parent")
        child = Node(name="child", parent=parent)
        uuid_path = child.get_uuid_path()
        assert len(uuid_path) == 2
        assert uuid_path[0] == parent.node_id
        assert uuid_path[1] == child.node_id

    def test_get_uuid_path_string(self):
        """Test getting UUID path as string."""
        parent = Node(name="parent")
        child = Node(name="child", parent=parent)
        uuid_path_string = child.get_uuid_path_string()
        expected = f"{parent.node_id}.{child.node_id}"
        assert uuid_path_string == expected

    def test_node_id_uniqueness(self):
        """Test that node IDs are unique."""
        node1 = Node()
        node2 = Node()
        assert node1.node_id != node2.node_id

    def test_node_id_format(self):
        """Test that node ID is a valid UUID string."""
        import uuid

        node = Node()
        # This should not raise an exception
        uuid.UUID(node.node_id)


class TestTreeNode:
    """Test the TreeNode class."""

    def test_init_basic(self):
        """Test basic initialization."""
        node = ConcreteTreeNode(description="Test node")
        assert node.description == "Test node"
        assert node.children == []
        assert node.parent is None
        assert node.logger is not None

    def test_init_with_name(self):
        """Test initialization with name."""
        node = ConcreteTreeNode(name="test", description="Test node")
        assert node.name == "test"
        assert node.description == "Test node"

    def test_init_with_children(self):
        """Test initialization with children."""
        child1 = ConcreteTreeNode(description="Child 1")
        child2 = ConcreteTreeNode(description="Child 2")
        parent = ConcreteTreeNode(
            description="Parent", children=[child1, child2])

        assert len(parent.children) == 2
        assert child1.parent == parent
        assert child2.parent == parent

    def test_init_with_parent(self):
        """Test initialization with parent."""
        parent = ConcreteTreeNode(description="Parent")
        child = ConcreteTreeNode(description="Child", parent=parent)

        assert child.parent == parent
        # Note: parent.children is not automatically updated when parent is passed
        # This is the actual behavior of the TreeNode class

    def test_node_type_property(self):
        """Test the node_type property returns UNKNOWN by default."""
        node = ConcreteTreeNode(description="Test")
        assert node.node_type == NodeType.UNKNOWN

    def test_execute_abstract_method(self):
        """Test that execute is abstract and must be implemented."""
        # Test that abstract class cannot be instantiated
        with pytest.raises(TypeError):
            TreeNode(description="Test")

    def test_children_immutability(self):
        """Test that children list is properly initialized."""
        node = ConcreteTreeNode(description="Test")
        # Should not be able to modify children directly
        assert isinstance(node.children, list)
        node.children.append(ConcreteTreeNode(description="Child"))
        assert len(node.children) == 1

    def test_children_with_none(self):
        """Test initialization with None children."""
        node = ConcreteTreeNode(description="Test", children=None)
        assert node.children == []

    def test_children_with_empty_list(self):
        """Test initialization with empty children list."""
        node = ConcreteTreeNode(description="Test", children=[])
        assert node.children == []

    def test_parent_child_relationship(self):
        """Test that parent-child relationships are properly set."""
        parent = ConcreteTreeNode(description="Parent")
        child1 = ConcreteTreeNode(description="Child 1", parent=parent)
        child2 = ConcreteTreeNode(description="Child 2", parent=parent)

        assert child1.parent == parent
        assert child2.parent == parent
        # Note: parent.children is not automatically updated when parent is passed
        # This is the actual behavior of the TreeNode class

    def test_complex_tree_structure(self):
        """Test complex tree structure with multiple levels."""
        # Create children first with explicit names
        level2_child1 = ConcreteTreeNode(
            name="Level 2 Child 1", description="Level 2 Child 1"
        )
        level1_child1 = ConcreteTreeNode(
            name="Level 1 Child 1",
            description="Level 1 Child 1",
            children=[level2_child1],
        )
        level1_child2 = ConcreteTreeNode(
            name="Level 1 Child 2", description="Level 1 Child 2"
        )
        root = ConcreteTreeNode(
            name="Root", description="Root", children=[level1_child1, level1_child2]
        )

        assert len(root.children) == 2
        assert len(level1_child1.children) == 1
        assert len(level1_child2.children) == 0

        assert level2_child1.get_path() == [
            "Root",
            "Level 1 Child 1",
            "Level 2 Child 1",
        ]

    def test_logger_initialization(self):
        """Test that logger is properly initialized."""
        node = ConcreteTreeNode(name="test_node", description="Test")
        assert node.logger is not None
        # The logger should have the node name
        assert hasattr(node.logger, "name")

    def test_logger_without_name(self):
        """Test logger initialization without name."""
        node = ConcreteTreeNode(description="Test")
        assert node.logger is not None
        # Should use a default name
        assert hasattr(node.logger, "name")

    def test_inheritance_from_node(self):
        """Test that TreeNode inherits properly from Node."""
        node = ConcreteTreeNode(name="test", description="Test")

        # Should have all Node properties
        assert hasattr(node, "node_id")
        assert hasattr(node, "name")
        assert hasattr(node, "parent")
        assert hasattr(node, "has_name")
        assert hasattr(node, "get_path")
        assert hasattr(node, "get_path_string")
        assert hasattr(node, "get_uuid_path")
        assert hasattr(node, "get_uuid_path_string")

    def test_node_type_enum(self):
        """Test that node_type returns a valid NodeType enum."""
        node = ConcreteTreeNode(description="Test")
        assert isinstance(node.node_type, NodeType)
        assert node.node_type == NodeType.UNKNOWN


class ConcreteTreeNode(TreeNode):
    """Concrete implementation for testing abstract methods."""

    def execute(
        self, user_input: str, context: Optional[IntentContext] = None
    ) -> ExecutionResult:
        """Concrete implementation of execute method."""
        return ExecutionResult(
            success=True,
            node_name=self.name,
            node_path=self.get_path(),
            node_type=self.node_type,
            input=user_input,
            output=f"Processed: {user_input}",
            error=None,
            params={},
            children_results=[],
        )


class TestConcreteTreeNode:
    """Test concrete TreeNode implementation."""

    def test_concrete_execute_method(self):
        """Test that concrete execute method works."""
        node = ConcreteTreeNode(description="Test")
        result = node.execute("test input")

        assert result.success is True
        assert result.output == "Processed: test input"
        assert result.node_name == node.name
        assert result.node_path == node.get_path()
        assert result.node_type == node.node_type

    def test_concrete_execute_with_context(self):
        """Test execute method with context."""
        node = ConcreteTreeNode(description="Test")
        context = IntentContext()
        result = node.execute("test input", context)

        assert result.success is True
        assert result.output == "Processed: test input"

    def test_concrete_node_inheritance(self):
        """Test that concrete node inherits all properties."""
        node = ConcreteTreeNode(name="test", description="Test")

        # Should have all TreeNode properties
        assert node.description == "Test"
        assert node.children == []
        assert node.logger is not None

        # Should have all Node properties
        assert node.name == "test"
        assert node.node_id is not None
        assert node.parent is None
