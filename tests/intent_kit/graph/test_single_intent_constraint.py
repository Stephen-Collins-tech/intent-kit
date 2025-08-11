"""
Tests for single intent architecture constraints.
"""

from intent_kit.graph.builder import IntentGraphBuilder


class TestSingleIntentConstraint:
    """Test the single intent constraint validation."""

    def test_classifier_node_can_be_root(self):
        """Test that root nodes must be classifier nodes."""
        # Create a valid classifier root node using JSON config
        graph_config = {
            "root": "test_classifier",
            "nodes": {
                "test_classifier": {
                    "id": "test_classifier",
                    "type": "classifier",
                    "classifier_type": "llm",
                    "name": "test_classifier",
                    "description": "Test classifier",
                    "llm_config": {"provider": "openai", "model": "gpt-4"},
                    "children": [],
                }
            },
        }

        # This should work
        graph = IntentGraphBuilder().with_json(graph_config).with_functions({}).build()
        assert len(graph.root_nodes) == 1
        assert graph.root_nodes[0].node_type.value == "classifier"

    def test_action_node_can_be_root(self):
        """Test that action nodes can be root nodes."""
        # Create an action node using JSON config
        graph_config = {
            "root": "test_action",
            "nodes": {
                "test_action": {
                    "id": "test_action",
                    "type": "action",
                    "name": "test_action",
                    "description": "Test action",
                    "function": "test_function",
                    "param_schema": {},
                }
            },
        }

        # This should work now
        graph = (
            IntentGraphBuilder()
            .with_json(graph_config)
            .with_functions({"test_function": lambda: "Hello"})
            .build()
        )
        assert len(graph.root_nodes) == 1
        assert graph.root_nodes[0].node_type.value == "action"
