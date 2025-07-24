#!/usr/bin/env python3
"""
Error Demo - Demonstrating the new structured error functionality

This example shows how the new ExecutionError dataclass provides
rich, structured error information instead of simple strings.
"""

import os
import json
from intent_kit import IntentGraphBuilder


def extract_args(user_input: str, context=None) -> dict:
    """Extract arguments from user input."""
    words = user_input.split()
    # Skip the first word if it's "Greet"
    if words and words[0].lower() == "greet":
        words = words[1:]

    return {
        "name": words[0] if words else "",
        "age": words[1] if len(words) > 1 else "",
    }


def validate_args(params: dict) -> bool:
    """Validate extracted arguments."""
    return bool(params.get("name") and params.get("age"))


def greet_action(name: str, age: int) -> str:
    """Action that might raise an exception."""
    if age < 0:
        raise ValueError("Age cannot be negative")
    if age > 150:
        raise ValueError("Age seems unrealistic")
    return f"Hello {name}, you are {age} years old!"


def main_classifier(user_input: str, children, context=None, **kwargs):
    """Simple classifier that routes to the greet action."""
    # Find the greet action node
    greet_node = None
    for child in children:
        if child.name == "greet_action":
            greet_node = child
            break

    # Always route to greet action for this demo
    return greet_node


function_registry = {
    "greet_action": greet_action,
    "main_classifier": main_classifier,
}


def create_intent_graph():
    """Create and configure the intent graph using JSON."""
    # Load the graph definition from local JSON (same directory as script)
    json_path = os.path.join(os.path.dirname(__file__), "error_demo.json")
    with open(json_path, "r") as f:
        json_graph = json.load(f)

    return (
        IntentGraphBuilder()
        .with_json(json_graph)
        .with_functions(function_registry)
        .build()
    )


def main():
    """Demonstrate structured error handling."""
    print("=== Intent Kit Structured Error Demo ===\n")

    # Create intent graph using JSON
    graph = create_intent_graph()

    # Test cases that will trigger different types of errors
    test_cases = [
        "Greet John 30",  # Success
        "Greet",  # Validation failure (missing age)
        "Greet John -5",  # Action error (negative age)
        "Greet John 200",  # Action error (unrealistic age)
        "Greet John abc",  # Type validation error (age not a number)
    ]

    for user_input in test_cases:
        print(f"Input: {user_input}")
        print("-" * 50)

        result = graph.route(user_input=user_input)

        if result.error:
            print(f"❌ Error: {result.error}")
        else:
            print(f"✅ Success: {result.output}")

        # Show the execution path with structured error information
        if result.children_results:
            print("\nExecution Path:")
            for step in result.children_results:
                node_name = step.node_name
                node_type = step.node_type

                if step.error:
                    # Now we have rich error information!
                    error = step.error
                    print(f"  {node_name} ({node_type}): ❌ {error.error_type}")
                    print(f"    Message: {error.message}")
                    print(f"    Node Path: {' -> '.join(error.node_path)}")
                    if error.node_id:
                        print(f"    Node ID: {error.node_id}")
                    if error.node_path:
                        print(f"    Path: {' -> '.join(error.node_path)}")
                    if error.input_data:
                        print(f"    Input Data: {error.input_data}")
                    if error.output_data:
                        print(f"    Output Data: {error.output_data}")
                    if error.params:
                        print(f"    Params: {error.params}")
                else:
                    print(f"  {node_name} ({node_type}): ✅ Success")

        print("\n" + "=" * 60 + "\n")


if __name__ == "__main__":
    main()
