"""
Simple JSON + LLM Demo for IntentKit

This demo shows how to create IntentGraph instances from JSON definitions
with LLM-based argument extraction for intelligent parameter parsing.
"""

import os



load_dotenv()

# LLM configuration for intelligent argument extraction
LLM_CONFIG = {
    "provider": "openrouter",
    "api_key": os.getenv("OPENROUTER_API_KEY"),
    "model": "meta-llama/llama-4-maverick-17b-128e-instruct",
}


def greet_function(name: str) -> str:
    """Greet the user with their name."""
    return f"Hello {name}! Nice to meet you."


def calculate_function(operation: str, a: float, b: float) -> str:
    """Perform a calculation and return the result."""
    operation_map = {
        "plus": "+",
        "add": "+",
        "addition": "+",
        "sum": "+",
        "minus": "-",
        "subtract": "-",
        "subtraction": "-",
        "times": "*",
        "multiply": "*",
        "multiplication": "*",
        "divided": "/",
        "divide": "/",
        "division": "/",
    }
    math_op = operation_map.get(operation.lower(), operation)
    try:
        result = eval(f"{a} {math_op} {b}")
        return f"{a} {operation} {b} = {result}"
    except (SyntaxError, ZeroDivisionError) as e:
        return f"Error: Cannot calculate {a} {operation} {b} - {str(e)}"


def weather_function(location: str) -> str:
    """Get weather information for a location."""
    return f"Weather in {location}: 72°F, Sunny with light breeze (simulated)"


def help_function() -> str:
    """Provide help information."""
    return """I can help you with:

• Greetings: Say hello and introduce yourself
• Calculations: Add, subtract, multiply, divide numbers
• Weather: Get weather information for any location
• Help: Get this help message

Just tell me what you'd like to do!"""


def smart_classifier(user_input: str, children, context=None):
    """Smart classifier that routes to the most appropriate action."""
    input_lower = user_input.lower()

    # Greeting patterns
    if any(
        word in input_lower for word in ["hello", "hi", "greet", "name", "introduce"]
    ):
        return children[0]  # greet action

    # Calculation patterns
    elif any(
        word in input_lower
        for word in [
            "calculate",
            "math",
            "+",
            "-",
            "*",
            "/",
            "plus",
            "times",
            "add",
            "subtract",
        ]
    ):
        return children[1]  # calculate action

    # Weather patterns
    elif any(
        word in input_lower
        for word in ["weather", "temperature", "forecast", "climate"]
    ):
        return children[2]  # weather action

    # Help patterns
    elif any(
        word in input_lower for word in ["help", "assist", "support", "what can you do"]
    ):
        return children[3]  # help action

    # Default to help
    else:
        return children[3]


def main() -> None:
    """Demonstrate JSON serialization with LLM-based argument extraction."""

    print("🤖 IntentKit JSON + LLM Demo")
    print("=" * 50)

    # Define the function registry
    function_registry = {
        "greet_function": greet_function,
        "calculate_function": calculate_function,
        "weather_function": weather_function,
        "help_function": help_function,
        "smart_classifier": smart_classifier,
    }

    # Define the graph structure in JSON
    json_graph = {
        "root": "main_classifier",
        "intents": {
            "main_classifier": {
                "type": "classifier",
                "name": "main_classifier",
                "classifier_function": "smart_classifier",
                "description": "Smart intent classifier",
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
                "description": "Greet the user with their name",
                "function": "greet_function",
                "param_schema": {"name": "str"},
                "llm_config": LLM_CONFIG,  # Enable LLM-based extraction
                "context_inputs": [],
                "context_outputs": [],
            },
            "calculate_action": {
                "type": "action",
                "name": "calculate_action",
                "description": "Perform mathematical calculations",
                "function": "calculate_function",
                "param_schema": {"operation": "str", "a": "float", "b": "float"},
                "llm_config": LLM_CONFIG,  # Enable LLM-based extraction
                "context_inputs": [],
                "context_outputs": [],
            },
            "weather_action": {
                "type": "action",
                "name": "weather_action",
                "description": "Get weather information for a location",
                "function": "weather_function",
                "param_schema": {"location": "str"},
                "llm_config": LLM_CONFIG,  # Enable LLM-based extraction
                "context_inputs": [],
                "context_outputs": [],
            },
            "help_action": {
                "type": "action",
                "name": "help_action",
                "description": "Provide help information",
                "function": "help_function",
                "param_schema": {},
                "context_inputs": [],
                "context_outputs": [],
            },
        },
    }

    # Create the graph using the Builder pattern
    print("Creating IntentGraph using Builder pattern...")
    graph = (
        IntentGraphBuilder()
        .with_json(json_graph)
        .with_functions(function_registry)
        .build()
    )
    print("✅ Graph created successfully!")

    # Test with various natural language inputs
    test_inputs = [
        "Hello, my name is Alice",
        "Hi there, I'm Bob Smith",
        "What's 15 plus 7?",
        "Can you calculate 8 times 3?",
        "What's the weather like in San Francisco?",
        "Tell me the weather for New York City",
        "Help me with calculations",
        "My name is Charlie and I need help",
        "What can you do?",
        "Calculate 100 divided by 5",
    ]

    print("\n🧪 Testing with natural language inputs:")
    print("=" * 50)

    for i, user_input in enumerate(test_inputs, 1):
        print(f"\n{i}. Input: {user_input}")
        result = graph.route(user_input)

        if result.success:
            print(f"   Output: {result.output}")
            print(f"   Action: {result.node_name}")
        else:
            print(
                f"   Error: {result.error.message if result.error else 'Unknown error'}"
            )

    print(f"\n🎉 Demo completed! {len(test_inputs)} inputs processed.")
    print("\n💡 Key Features Demonstrated:")
    print("   • JSON-based graph configuration")
    print("   • LLM-powered argument extraction")
    print("   • Natural language understanding")
    print("   • Function registry system")
    print("   • Intelligent parameter parsing")
    print("   • Builder pattern for clean construction")


if __name__ == "__main__":
    main()
