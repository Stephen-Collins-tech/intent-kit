"""
Tests for single intent architecture constraints.
"""

import pytest
from intent_kit.graph.intent_graph import IntentGraph
from intent_kit.node.enums import NodeType
from intent_kit.utils.node_factory import action, llm_classifier


class TestSingleIntentConstraint:
    """Test that the single intent architecture constraints are enforced."""

    def test_root_nodes_must_be_classifiers(self):
        """Test that root nodes must be classifier nodes."""
        # Create a valid classifier root node
        classifier = llm_classifier(
            name="test_classifier",
            description="Test classifier",
            children=[],
            llm_config={"provider": "openai", "model": "gpt-4"},
        )

        # This should work
        graph = IntentGraph(root_nodes=[classifier])
        assert len(graph.root_nodes) == 1
        assert graph.root_nodes[0].node_type == NodeType.CLASSIFIER

    def test_action_node_cannot_be_root(self):
        """Test that action nodes cannot be root nodes."""
        # Create an action node
        action_node = action(
            name="test_action",
            description="Test action",
            action_func=lambda: "Hello",
            param_schema={},
        )

        # This should raise an error
        with pytest.raises(ValueError, match="must be a classifier node"):
            IntentGraph(root_nodes=[action_node])

    def test_add_classifier_root_node(self):
        """Test adding a classifier root node."""
        graph = IntentGraph()

        classifier = llm_classifier(
            name="test_classifier",
            description="Test classifier",
            children=[],
            llm_config={"provider": "openai", "model": "gpt-4"},
        )

        # This should work
        graph.add_root_node(classifier)
        assert len(graph.root_nodes) == 1
        assert graph.root_nodes[0].node_type == NodeType.CLASSIFIER

    def test_add_action_root_node_fails(self):
        """Test that adding an action root node fails."""
        graph = IntentGraph()

        action_node = action(
            name="test_action",
            description="Test action",
            action_func=lambda: "Hello",
            param_schema={},
        )

        # This should raise an error
        with pytest.raises(ValueError, match="must be a classifier node"):
            graph.add_root_node(action_node)

    def test_mixed_root_nodes_fails(self):
        """Test that mixing classifier and action root nodes fails."""
        classifier = llm_classifier(
            name="test_classifier",
            description="Test classifier",
            children=[],
            llm_config={"provider": "openai", "model": "gpt-4"},
        )

        action_node = action(
            name="test_action",
            description="Test action",
            action_func=lambda: "Hello",
            param_schema={},
        )

        # This should raise an error because action_node is not a classifier
        with pytest.raises(ValueError, match="must be a classifier node"):
            IntentGraph(root_nodes=[classifier, action_node])

    def test_multiple_classifier_root_nodes(self):
        """Test that multiple classifier root nodes work."""
        classifier1 = llm_classifier(
            name="classifier1",
            description="Test classifier 1",
            children=[],
            llm_config={"provider": "openai", "model": "gpt-4"},
        )

        classifier2 = llm_classifier(
            name="classifier2",
            description="Test classifier 2",
            children=[],
            llm_config={"provider": "openai", "model": "gpt-4"},
        )

        # This should work
        graph = IntentGraph(root_nodes=[classifier1, classifier2])
        assert len(graph.root_nodes) == 2
        assert all(node.node_type == NodeType.CLASSIFIER for node in graph.root_nodes)
