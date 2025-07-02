"""
Validation Demo for IntentKit

A demonstration of the new graph validation system showing how to enforce
splitter-to-classifier routing constraints and validate graph structure.
"""

import os
from typing import Dict, Any
from intent_kit.classifiers.llm_classifier import create_llm_classifier, create_llm_arg_extractor, get_default_classification_prompt, get_default_extraction_prompt
from intent_kit.graph import IntentGraph
from intent_kit.graph.validation import GraphValidationError
from intent_kit.services.llm_factory import LLMFactory
from intent_kit.tree import TreeBuilder
from intent_kit.node import ExecutionResult
from dotenv import load_dotenv

load_dotenv()

# LLM configuration
LLM_CONFIG = {
    "provider": "openrouter",
    "api_key": os.getenv("OPENROUTER_API_KEY"),
    "model": "meta-llama/llama-4-maverick-17b-128e-instruct"
}

# Create LLM client
LLM_CLIENT = LLMFactory.create_client(LLM_CONFIG)


def build_valid_graph():
    """Build a valid graph with proper splitter-to-classifier routing."""
    print("Building valid graph with proper splitter-to-classifier routing...")

    # Create intent nodes
    greet_node = TreeBuilder.handler_node(
        name="greet",
        param_schema={"name": str},
        handler=lambda name: f"Hello {name}!",
        arg_extractor=lambda text, context: {
            "name": text.split()[-1] if text.split() else "User"},
        description="Greet the user"
    )

    calc_node = TreeBuilder.handler_node(
        name="calculate",
        param_schema={"operation": str, "a": float, "b": float},
        handler=lambda operation, a, b: f"{a} {operation} {b} = {a + b if operation == 'add' else a * b}",
        arg_extractor=lambda text, context: {
            "operation": "add" if "add" in text.lower() else "multiply",
            "a": 10.0,
            "b": 5.0
        },
        description="Perform calculations"
    )

    weather_node = TreeBuilder.handler_node(
        name="weather",
        param_schema={"location": str},
        handler=lambda location: f"Weather in {location}: 72°F, Sunny",
        arg_extractor=lambda text, context: {
            "location": text.split()[-1] if text.split() else "Unknown"},
        description="Get weather information"
    )

    # Create classifier node
    classifier = create_llm_classifier(
        llm_config=LLM_CONFIG,
        classification_prompt=get_default_classification_prompt(),
        node_descriptions=[
            "Greet the user",
            "Perform a calculation",
            "Get weather information"
        ]
    )

    classifier_node = TreeBuilder.classifier_node(
        name="main_classifier",
        classifier=classifier,
        children=[greet_node, calc_node, weather_node],
        description="Main classifier for routing intents"
    )

    # Create splitter node that routes to classifier (VALID)
    splitter_node = TreeBuilder.rule_splitter_node(
        name="main_splitter",
        children=[classifier_node],  # Routes to classifier - VALID
        description="Split multi-intent inputs using rule-based logic"
    )

    return splitter_node


def build_invalid_graph():
    """Build an invalid graph with splitter routing directly to intent nodes."""
    print("Building invalid graph with splitter routing directly to intent nodes...")

    # Create intent nodes
    greet_node = TreeBuilder.handler_node(
        name="greet",
        param_schema={"name": str},
        handler=lambda name: f"Hello {name}!",
        arg_extractor=lambda text, context: {
            "name": text.split()[-1] if text.split() else "User"},
        description="Greet the user"
    )

    calc_node = TreeBuilder.handler_node(
        name="calculate",
        param_schema={"operation": str, "a": float, "b": float},
        handler=lambda operation, a, b: f"{a} {operation} {b} = {a + b if operation == 'add' else a * b}",
        arg_extractor=lambda text, context: {
            "operation": "add" if "add" in text.lower() else "multiply",
            "a": 10.0,
            "b": 5.0
        },
        description="Perform calculations"
    )

    weather_node = TreeBuilder.handler_node(
        name="weather",
        param_schema={"location": str},
        handler=lambda location: f"Weather in {location}: 72°F, Sunny",
        arg_extractor=lambda text, context: {
            "location": text.split()[-1] if text.split() else "Unknown"},
        description="Get weather information"
    )

    # Create splitter node that routes directly to intent nodes (INVALID)
    splitter_node = TreeBuilder.rule_splitter_node(
        name="invalid_splitter",
        # Routes directly to intents - INVALID
        children=[greet_node, calc_node, weather_node],
        description="Invalid splitter that routes directly to intent nodes"
    )

    return splitter_node


def demo_valid_graph():
    """Demonstrate a valid graph configuration."""
    print("\n" + "="*60)
    print("VALID GRAPH DEMO")
    print("="*60)

    try:
        # Create graph with valid configuration
        graph = IntentGraph()
        valid_root = build_valid_graph()

        print("Adding valid root node...")
        graph.add_root_node(valid_root, validate=True)

        print("Validating graph structure...")
        stats = graph.validate_graph()

        print("✓ Graph validation passed!")
        print(f"Graph statistics:")
        print(f"  Total nodes: {stats['total_nodes']}")
        print(f"  Node counts: {stats['node_counts']}")
        print(f"  Routing valid: {stats['routing_valid']}")
        print(f"  Has cycles: {stats['has_cycles']}")
        print(f"  Orphaned nodes: {stats['orphaned_count']}")

        # Test routing
        print("\nTesting routing with valid graph...")
        result = graph.route("Hello Alice and calculate 5 plus 3", debug=True)

        if result.success:
            print(f"✓ Routing successful: {result.output}")
        else:
            print(f"✗ Routing failed: {result.error}")

    except GraphValidationError as e:
        print(f"✗ Validation failed: {e.message}")
    except Exception as e:
        print(f"✗ Unexpected error: {e}")


def demo_invalid_graph():
    """Demonstrate an invalid graph configuration."""
    print("\n" + "="*60)
    print("INVALID GRAPH DEMO")
    print("="*60)

    try:
        # Create graph with invalid configuration
        graph = IntentGraph()
        invalid_root = build_invalid_graph()

        print("Adding invalid root node...")
        graph.add_root_node(invalid_root, validate=True)

    except GraphValidationError as e:
        print(f"✗ Validation correctly caught error: {e.message}")
        print(f"  Node: {e.node_name}")
        print(f"  Child: {e.child_name}")
        print(f"  Child type: {e.child_type}")

        # Try to validate manually to show the error
        print("\nManual validation:")
        try:
            graph.validate_splitter_routing()
        except GraphValidationError as e2:
            print(f"  Manual validation also caught: {e2.message}")

    except Exception as e:
        print(f"✗ Unexpected error: {e}")


def demo_validation_methods():
    """Demonstrate different validation methods."""
    print("\n" + "="*60)
    print("VALIDATION METHODS DEMO")
    print("="*60)

    # Create a graph with both valid and invalid configurations
    graph = IntentGraph()

    # Add valid root first
    valid_root = build_valid_graph()
    graph.add_root_node(valid_root, validate=False)  # Skip validation for now

    print("Testing validation methods:")

    # Test splitter routing validation
    print("\n1. Testing splitter routing validation...")
    try:
        graph.validate_splitter_routing()
        print("✓ Splitter routing validation passed")
    except GraphValidationError as e:
        print(f"✗ Splitter routing validation failed: {e.message}")

    # Test full graph validation
    print("\n2. Testing full graph validation...")
    try:
        stats = graph.validate_graph()
        print("✓ Full graph validation passed")
        print(f"  Statistics: {stats}")
    except GraphValidationError as e:
        print(f"✗ Full graph validation failed: {e.message}")

    # Test validation with different options
    print("\n3. Testing validation with custom options...")
    try:
        stats = graph.validate_graph(
            validate_routing=True, validate_types=True)
        print("✓ Custom validation passed")
    except GraphValidationError as e:
        print(f"✗ Custom validation failed: {e.message}")


def demo_graph_statistics():
    """Demonstrate graph statistics and analysis."""
    print("\n" + "="*60)
    print("GRAPH STATISTICS DEMO")
    print("="*60)

    try:
        # Create a complex valid graph
        graph = IntentGraph()

        # Build a multi-level graph
        greet_node = TreeBuilder.handler_node(
            name="greet",
            param_schema={"name": str},
            handler=lambda name: f"Hello {name}!",
            arg_extractor=lambda text, context: {
                "name": text.split()[-1] if text.split() else "User"},
            description="Greet the user"
        )

        calc_node = TreeBuilder.handler_node(
            name="calculate",
            param_schema={"operation": str, "a": float, "b": float},
            handler=lambda operation, a, b: f"{a} {operation} {b} = {a + b if operation == 'add' else a * b}",
            arg_extractor=lambda text, context: {
                "operation": "add" if "add" in text.lower() else "multiply",
                "a": 10.0,
                "b": 5.0
            },
            description="Perform calculations"
        )

        # Create nested classifier
        nested_classifier = TreeBuilder.classifier_node(
            name="nested_classifier",
            # Simple classifier
            classifier=lambda text, children, context: children[0],
            children=[calc_node],
            description="Nested classifier"
        )

        # Create main classifier
        main_classifier = TreeBuilder.classifier_node(
            name="main_classifier",
            classifier=lambda text, children, context: children[0] if "greet" in text.lower(
            ) else children[1],
            children=[greet_node, nested_classifier],
            description="Main classifier"
        )

        # Create splitter
        splitter = TreeBuilder.rule_splitter_node(
            name="main_splitter",
            children=[main_classifier],
            description="Main splitter"
        )

        graph.add_root_node(splitter, validate=False)

        # Get comprehensive statistics
        stats = graph.validate_graph()

        print("Graph Statistics:")
        print(f"  Total nodes: {stats['total_nodes']}")
        print(f"  Node counts by type:")
        for node_type, count in stats['node_counts'].items():
            print(f"    {node_type}: {count}")
        print(f"  Routing valid: {stats['routing_valid']}")
        print(f"  Has cycles: {stats['has_cycles']}")
        print(f"  Orphaned nodes: {stats['orphaned_count']}")
        if stats['orphaned_nodes']:
            print(f"  Orphaned node names: {stats['orphaned_nodes']}")

    except Exception as e:
        print(f"✗ Error: {e}")


def main():
    print("IntentKit Graph Validation Demo")
    print("This demo showcases the new graph validation system that enforces")
    print("splitter-to-classifier routing constraints and validates graph structure.")
    print("You must set a valid API key in LLM_CONFIG for LLM features to work.")

    # Demo valid graph
    demo_valid_graph()

    # Demo invalid graph
    demo_invalid_graph()

    # Demo validation methods
    demo_validation_methods()

    # Demo graph statistics
    demo_graph_statistics()

    print("\n" + "="*60)
    print("VALIDATION DEMO COMPLETE")
    print("="*60)
    print("Key takeaways:")
    print("1. Splitter nodes must only route to classifier nodes")
    print("2. Validation happens automatically when adding root nodes")
    print("3. Manual validation is available for debugging")
    print("4. Comprehensive statistics help analyze graph structure")


if __name__ == "__main__":
    main()
