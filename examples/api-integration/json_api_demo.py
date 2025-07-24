"""
JSON API Demo for IntentGraphBuilder

This demo showcases the new JSON-based construction capabilities
of IntentGraphBuilder with flat JSON specifications.

Requires: Set the environment variable OPENROUTER_API_KEY with your OpenRouter API key.
"""

import os
import json
from intent_kit.builders import IntentGraphBuilder
from intent_kit.context import IntentContext
from dotenv import load_dotenv

load_dotenv()


def greet_user(name: str, context=None) -> str:
    """Greet a user by name."""
    return f"Hello {name}! Nice to meet you."


def calculate(operation: str, a: float, b: float, context=None) -> str:
    """Perform a calculation."""
    if operation == "add":
        result = a + b
    elif operation == "subtract":
        result = a - b
    elif operation == "multiply":
        result = a * b
    elif operation == "divide":
        if b == 0:
            return "Error: Cannot divide by zero"
        result = a / b
    else:
        return f"Error: Unknown operation '{operation}'"

    return f"The result of {a} {operation} {b} is {result}"


def weather_info(location: str, context=None) -> str:
    """Get weather information for a location."""
    return f"Weather information for {location}: Sunny, 72°F"


def help_user(context=None) -> str:
    """Provide help information."""
    return "I can help you with greetings, calculations, and weather information. Just ask!"


function_registry = {
    "greet_user": greet_user,
    "calculate": calculate,
    "weather_info": weather_info,
    "help_user": help_user,
}


def create_intent_graph():
    """Create and configure the intent graph using JSON."""
    # Load the graph definition from local JSON (same directory as script)
    json_path = os.path.join(os.path.dirname(__file__), "json_api_demo.json")
    with open(json_path, "r") as f:
        json_graph = json.load(f)

    # Get OpenRouter API key from environment
    openrouter_api_key = os.environ.get("OPENROUTER_API_KEY", "")
    if not openrouter_api_key:
        raise ValueError("Please set the OPENROUTER_API_KEY environment variable.")

    # Define the LLM config for OpenRouter/Gemma
    llm_config = {
        "provider": "openrouter",
        "model": "google/gemma-3-27b-it",
        "api_key": os.getenv("OPENROUTER_API_KEY"),
    }

    return (
        IntentGraphBuilder()
        .with_json(json_graph)
        .with_functions(function_registry)
        .with_default_llm_config(llm_config)
        .build()
    )


def main():
    """Demonstrate JSON-based IntentGraph construction with LLM classifier."""

    print("=== IntentGraphBuilder JSON API Demo (LLM Classifier) ===\n")

    # Create the graph using JSON specification
    print("1. Creating IntentGraph from JSON specification...")
    try:
        graph = create_intent_graph()
        print("✅ Graph created successfully!")
    except ValueError as e:
        print(f"❌ Graph creation failed: {e}")
        return

    # Optional: Validate the graph and show detailed results
    print("\n2. Validating graph structure (optional)...")
    try:
        # Load the JSON graph for validation
        json_path = os.path.join(os.path.dirname(__file__), "json_api_demo.json")
        with open(json_path, "r") as f:
            json_graph = json.load(f)

        validation_results = (
            IntentGraphBuilder().with_json(json_graph).validate_json_graph()
        )

        if validation_results["valid"]:
            print("✅ Graph validation passed!")
            print(f"   - Nodes: {validation_results['node_count']}")
            print(f"   - Edges: {validation_results['edge_count']}")
            if validation_results["warnings"]:
                print(f"   - Warnings: {validation_results['warnings']}")
        else:
            print("❌ Graph validation failed!")
            print(f"   - Errors: {validation_results['errors']}")
            if validation_results["warnings"]:
                print(f"   - Warnings: {validation_results['warnings']}")
    except Exception as e:
        print(f"❌ Validation failed: {e}")

    # Test the graph with some inputs
    print("\n3. Testing the graph with various inputs...")
    test_inputs = [
        "Hello, my name is Alice",
        "What is 5 plus 3?",
        "What's the weather like in New York?",
        "Can you help me?",
        "This is an unknown request",
        "I want to multiply 7 and 8",
        "Tell me the temperature in Paris",
        "How do I use this bot?",
    ]

    context = IntentContext()

    for user_input in test_inputs:
        print(f"\nInput: {user_input}")
        try:
            result = graph.route(user_input, context=context, debug=True)
            if result.success:
                print(f"✅ Success: {result.output}")
            else:
                print(
                    f"❌ Failed: {result.error.message if result.error else 'Unknown error'}"
                )
        except Exception as e:
            print(f"❌ Exception: {e}")

    print("\n=== Demo completed successfully! ===")


if __name__ == "__main__":
    main()
