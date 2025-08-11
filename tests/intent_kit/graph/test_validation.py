#!/usr/bin/env python3
"""
Simple test script to verify the validation functionality.
"""

import pytest
from intent_kit.graph.builder import IntentGraphBuilder


class TestGraphBuilding:
    """Test basic graph building functionality."""

    def test_valid_graph_builds_successfully(self):
        """Test that a valid graph builds successfully."""
        # Create a simple valid graph using JSON config
        graph_config = {
            "root": "main_classifier",
            "nodes": {
                "main_classifier": {
                    "id": "main_classifier",
                    "type": "classifier",
                    "classifier_type": "llm",
                    "name": "main_classifier",
                    "description": "Main intent classifier",
                    "llm_config": {"provider": "openai", "model": "gpt-4"},
                    "children": ["greet_action"],
                },
                "greet_action": {
                    "id": "greet_action",
                    "type": "action",
                    "name": "greet_action",
                    "description": "Greet the user",
                    "function": "greet",
                    "param_schema": {"name": "str"},
                },
            },
        }

        # Build graph
        graph = (
            IntentGraphBuilder()
            .with_json(graph_config)
            .with_functions({"greet": lambda name: f"Hello {name}!"})
            .build()
        )

        # This should build successfully
        assert graph is not None
        assert len(graph.root_nodes) == 1
        assert graph.root_nodes[0].name == "main_classifier"

    def test_invalid_graph_fails_to_build(self):
        """Test that an invalid graph fails to build."""
        # Create a graph with missing required fields
        graph_config = {
            "root": "main_classifier",
            "nodes": {
                "main_classifier": {
                    "id": "main_classifier",
                    "type": "classifier",
                    # Missing required fields
                },
            },
        }

        # This should fail to build
        with pytest.raises(Exception):
            IntentGraphBuilder().with_json(graph_config).build()
