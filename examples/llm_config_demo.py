#!/usr/bin/env python3
"""
Demo showing how to use llm_config with IntentGraphBuilder.

This example demonstrates how to set LLM configuration at the graph level
so that it can be used for chunk classification.
"""

from intent_kit.builders import IntentGraphBuilder, ActionBuilder, ClassifierBuilder


def greet(name: str) -> str:
    """Greet the user."""
    return f"Hello {name}!"


def calculate(a: int, b: int) -> str:
    """Calculate the sum of two numbers."""
    return f"The sum of {a} and {b} is {a + b}"


def main():
    """Demonstrate llm_config usage with IntentGraphBuilder."""

    # Create action nodes
    greet_action = (
        ActionBuilder("greet")
        .with_action(greet)
        .with_param_schema({"name": str})
        .with_description("Greet the user")
        .build()
    )

    calc_action = (
        ActionBuilder("calculate")
        .with_action(calculate)
        .with_param_schema({"a": int, "b": int})
        .with_description("Calculate sum of two numbers")
        .build()
    )

    # Create a classifier to route between actions
    classifier = (
        ClassifierBuilder("main_classifier")
        .with_children([greet_action, calc_action])
        .with_description("Route to appropriate action")
        .build()
    )

    # LLM configuration for chunk classification
    llm_config = {
        "provider": "openai",
        "model": "gpt-4",
        "api_key": "your-api-key-here",  # Replace with actual API key
    }

    # Build the graph with llm_config
    graph = IntentGraphBuilder().root(classifier).with_llm_config(llm_config).build()

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
