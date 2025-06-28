#!/usr/bin/env python3
"""
Error Demo - Demonstrating the new structured error functionality

This example shows how the new ExecutionError dataclass provides
rich, structured error information instead of simple strings.
"""

from intent_kit.tree import TreeBuilder
from intent_kit.classifiers.keyword import keyword_classifier
from intent_kit.engine import execute_taxonomy


def extract_args(user_input: str, context=None) -> dict:
    """Extract arguments from user input."""
    words = user_input.split()
    # Skip the first word if it's "Greet"
    if words and words[0].lower() == "greet":
        words = words[1:]

    return {
        "name": words[0] if words else "",
        "age": words[1] if len(words) > 1 else ""
    }


def validate_args(params: dict) -> bool:
    """Validate extracted arguments."""
    return bool(params.get("name") and params.get("age"))


def greet_handler(name: str, age: int) -> str:
    """Handler that might raise an exception."""
    if age < 0:
        raise ValueError("Age cannot be negative")
    if age > 150:
        raise ValueError("Age seems unrealistic")
    return f"Hello {name}, you are {age} years old!"


def main():
    """Demonstrate structured error handling."""
    print("=== Intent Kit Structured Error Demo ===\n")

    # Create a simple taxonomy with an intent that can fail in various ways
    tree = TreeBuilder.classifier_node(
        name="Root",
        classifier=keyword_classifier,
        children=[
            TreeBuilder.intent_node(
                name="Greet",
                param_schema={"name": str, "age": int},
                handler=greet_handler,
                arg_extractor=extract_args,
                input_validator=validate_args,
                description="Greet someone with their name and age"
            ),
        ],
        description="Demo taxonomy"
    )

    # Test cases that will trigger different types of errors
    test_cases = [
        "Greet John 30",      # Success
        "Greet",              # Validation failure (missing age)
        "Greet John -5",      # Handler error (negative age)
        "Greet John 200",     # Handler error (unrealistic age)
        "Greet John abc",     # Type validation error (age not a number)
    ]

    for user_input in test_cases:
        print(f"Input: {user_input}")
        print("-" * 50)

        result = execute_taxonomy(user_input=user_input, node=tree, debug=True)

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
                success = step.success

                if step.error:
                    # Now we have rich error information!
                    error = step.error
                    print(f"  {node_name} ({node_type}): ❌ {error.error_type}")
                    print(f"    Message: {error.message}")
                    print(f"    Node Path: {' -> '.join(error.node_path)}")
                    if error.node_id:
                        print(f"    Node ID: {error.node_id}")
                    if error.taxonomy_name:
                        print(f"    Taxonomy: {error.taxonomy_name}")
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
