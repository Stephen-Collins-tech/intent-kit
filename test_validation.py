#!/usr/bin/env python3
"""
Simple test script to verify the validation functionality.
"""

from intent_kit.tree import TreeBuilder
from intent_kit.graph import IntentGraph
from intent_kit.graph.validation import GraphValidationError, validate_splitter_routing


def test_valid_graph():
    """Test a valid graph configuration."""
    print("Testing valid graph...")

    # Create intent nodes
    greet_node = TreeBuilder.handler_node(
        name="greet",
        param_schema={"name": str},
        handler=lambda name: f"Hello {name}!",
        arg_extractor=lambda text, context: {"name": "User"},
        description="Greet the user"
    )

    # Create classifier node
    classifier_node = TreeBuilder.classifier_node(
        name="main_classifier",
        classifier=lambda text, children, context: children[0],
        children=[greet_node],
        description="Main classifier"
    )

    # Create splitter node that routes to classifier (VALID)
    splitter_node = TreeBuilder.rule_splitter_node(
        name="main_splitter",
        children=[classifier_node],  # Routes to classifier - VALID
        description="Split multi-intent inputs"
    )

    # Create graph and validate
    graph = IntentGraph()
    graph.add_root_node(splitter_node, validate=True)

    print("✓ Valid graph test passed!")


def test_invalid_graph():
    """Test an invalid graph configuration."""
    print("Testing invalid graph...")

    # Create intent nodes
    greet_node = TreeBuilder.handler_node(
        name="greet",
        param_schema={"name": str},
        handler=lambda name: f"Hello {name}!",
        arg_extractor=lambda text, context: {"name": "User"},
        description="Greet the user"
    )

    # Create splitter node that routes directly to intent nodes (INVALID)
    splitter_node = TreeBuilder.rule_splitter_node(
        name="invalid_splitter",
        children=[greet_node],  # Routes directly to intent - INVALID
        description="Invalid splitter"
    )

    # Create graph and try to validate
    graph = IntentGraph()

    try:
        graph.add_root_node(splitter_node, validate=True)
        print("✗ Invalid graph test failed - should have raised an error")
    except GraphValidationError as e:
        print(f"✓ Invalid graph test passed - caught error: {e.message}")
        print(f"  Node: {e.node_name}")
        print(f"  Child: {e.child_name}")
        print(f"  Child type: {e.child_type}")


def main():
    print("Validation System Test")
    print("=" * 40)

    test_valid_graph()
    test_invalid_graph()

    print("\n" + "=" * 40)
    print("All tests completed!")


if __name__ == "__main__":
    main()
