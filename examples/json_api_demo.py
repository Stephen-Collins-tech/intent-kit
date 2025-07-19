"""
JSON API Demo for IntentGraphBuilder

This demo showcases the new JSON-based construction capabilities
of IntentGraphBuilder with flat JSON specifications.

Requires: Set the environment variable OPENROUTER_API_KEY with your OpenRouter API key.
"""

import os




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


def main() -> None:
    """Demonstrate JSON-based IntentGraph construction with LLM classifier."""

    # Get OpenRouter API key from environment
    openrouter_api_key = os.environ.get("OPENROUTER_API_KEY", "")
    if not openrouter_api_key:
        print("❌ Please set the OPENROUTER_API_KEY environment variable.")
        return

    # Define the function registry (no classifier function needed for LLM node)
    function_registry = {
        "greet_user": greet_user,
        "calculate": calculate,
        "weather_info": weather_info,
        "help_user": help_user,
    }

    # Define the LLM config for OpenRouter/Gemma
    llm_config = {
        "provider": "openrouter",
        "model": "google/gemma-3-27b-it",
        "api_key": openrouter_api_key,
    }

    # Define the JSON graph specification with LLM classifier as root
    json_graph = {
        "root": "llm_classifier_node",
        "intents": {
            "llm_classifier_node": {
                "type": "llm_classifier",
                "name": "llm_classifier_node",
                "description": "LLM-powered intent classifier (Gemma via OpenRouter)",
                "llm_config": llm_config,
                "children": [
                    "greet_action",
                    "calculate_action",
                    "weather_action",
                    "help_action",
                ],
            },
            "greet_action": {
                "type": "action",
                "name": "greet_action",
                "description": "Greet the user",
                "function": "greet_user",
                "param_schema": {"name": "str"},
                "llm_config": llm_config,  # Add LLM config for parameter extraction
                "context_inputs": [],
                "context_outputs": [],
            },
            "calculate_action": {
                "type": "action",
                "name": "calculate_action",
                "description": "Perform calculations",
                "function": "calculate",
                "param_schema": {"operation": "str", "a": "float", "b": "float"},
                "llm_config": llm_config,  # Add LLM config for parameter extraction
                "context_inputs": [],
                "context_outputs": [],
            },
            "weather_action": {
                "type": "action",
                "name": "weather_action",
                "description": "Get weather information",
                "function": "weather_info",
                "param_schema": {"location": "str"},
                "llm_config": llm_config,  # Add LLM config for parameter extraction
                "context_inputs": [],
                "context_outputs": [],
            },
            "help_action": {
                "type": "action",
                "name": "help_action",
                "description": "Provide help",
                "function": "help_user",
                "param_schema": {},
                "llm_config": llm_config,  # Add LLM config for parameter extraction
                "context_inputs": [],
                "context_outputs": [],
            },
        },
    }

    print("=== IntentGraphBuilder JSON API Demo (LLM Classifier) ===\n")

    # Create the graph using JSON specification
    print("1. Creating IntentGraph from JSON specification...")
    graph = (
        IntentGraphBuilder()
        .with_json(json_graph)
        .with_functions(function_registry)
        .build()
    )
    print("✅ Graph created successfully!")

    # Validate the graph
    print("\n2. Validating graph structure...")
    try:
        validation_results = (
            IntentGraphBuilder().with_json(json_graph).validate_json_graph()
        )
        print("✅ Graph validation passed!")
        print(f"   - Nodes: {validation_results['node_count']}")
        print(f"   - Edges: {validation_results['edge_count']}")
        if validation_results["warnings"]:
            print(f"   - Warnings: {validation_results['warnings']}")
    except ValueError as e:
        print(f"❌ Graph validation failed: {e}")
        return

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
