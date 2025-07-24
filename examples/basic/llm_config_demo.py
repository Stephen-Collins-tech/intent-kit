#!/usr/bin/env python3
"""
Demo showing how to use llm_config with IntentGraphBuilder.

This example demonstrates how to set LLM configuration at the graph level
so that it can be used for chunk classification.
"""

import os
import json
from intent_kit import IntentGraphBuilder


def greet(name: str) -> str:
    """Greet the user."""
    return f"Hello {name}!"


def calculate(a: int, b: int) -> str:
    """Calculate the sum of two numbers."""
    return f"The sum of {a} and {b} is {a + b}"


def main_classifier(user_input: str, children, context=None, **kwargs):
    """Simple classifier that routes to appropriate child nodes."""
    # Find child nodes by name
    greet_node = None
    calculate_node = None

    for child in children:
        if child.name == "greet_action":
            greet_node = child
        elif child.name == "calculate_action":
            calculate_node = child

    # Simple routing logic
    if "hello" in user_input.lower() or "hi" in user_input.lower():
        return greet_node
    elif "calculate" in user_input.lower() or "sum" in user_input.lower():
        return calculate_node
    else:
        # Default to greet if no clear match
        return greet_node


function_registry = {
    "greet": greet,
    "calculate": calculate,
    "main_classifier": main_classifier,
}


def create_intent_graph():
    """Create and configure the intent graph using JSON."""
    # Load the graph definition from local JSON (same directory as script)
    json_path = os.path.join(os.path.dirname(__file__), "llm_config_demo.json")
    with open(json_path, "r") as f:
        json_graph = json.load(f)

    # LLM configuration for chunk classification
    llm_config = {
        "provider": "openai",
        "model": "gpt-4",
        "api_key": os.getenv("OPENAI_API_KEY"),  # Use environment variable
    }

    return (
        IntentGraphBuilder()
        .with_json(json_graph)
        .with_functions(function_registry)
        .with_default_llm_config(llm_config)
        .build()
    )


def main():
    """Demonstrate llm_config usage with IntentGraphBuilder."""

    # Build the graph with llm_config
    graph = create_intent_graph()

    print("Graph created successfully!")
    print(f"Graph has {len(graph.root_nodes)} root nodes")
    print(f"LLM config set: {graph.llm_config is not None}")

    # Test the graph
    test_inputs = ["Hello John", "Calculate 5 plus 3", "Hi there", "What's 10 + 20?"]

    for user_input in test_inputs:
        print(f"\nInput: {user_input}")
        try:
            result = graph.route(user_input)
            if result.success:
                print(f"Output: {result.output}")
            else:
                print(
                    f"Error: {result.error.message if result.error else 'Unknown error'}"
                )
        except Exception as e:
            print(f"Exception: {e}")


if __name__ == "__main__":
    main()
