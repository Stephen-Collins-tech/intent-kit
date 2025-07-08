"""
Simple IntentGraph Demo

A minimal demonstration showing how to configure an intent graph with handlers and classifiers.
"""

import os
from dotenv import load_dotenv
from intent_kit import IntentGraphBuilder, handler, llm_classifier

load_dotenv()

# LLM configuration (optional - remove if you don't want LLM features)
LLM_CONFIG = {
    "provider": "openrouter",
    "api_key": os.getenv("OPENROUTER_API_KEY"),
    "model": "meta-llama/llama-4-maverick-17b-128e-instruct",
}

# Configure your intent graph here


def _calculate_handler(operation: str, a: float, b: float) -> str:
    """Handle calculation with proper operator mapping."""
    # Map word operations to mathematical operators
    operation_map = {
        "plus": "+",
        "add": "+",
        "minus": "-",
        "subtract": "-",
        "times": "*",
        "multiply": "*",
        "multiplied": "*",
        "divided": "/",
        "divide": "/",
        "over": "/",
    }

    # Get the mathematical operator
    math_op = operation_map.get(operation.lower(), operation)

    try:
        result = eval(f"{a} {math_op} {b}")
        return f"{a} {operation} {b} = {result}"
    except (SyntaxError, ZeroDivisionError) as e:
        return f"Error: Cannot calculate {a} {operation} {b} - {str(e)}"


def create_intent_graph():
    """Create and configure the intent graph."""

    # Define handlers
    handlers = [
        handler(
            name="greet",
            description="Greet the user",
            handler_func=lambda name, **kwargs: f"Hello {name}!",
            param_schema={"name": str},
            llm_config=LLM_CONFIG,  # Remove this line for rule-based extraction
        ),
        handler(
            name="calculate",
            description="Perform a calculation",
            handler_func=lambda operation, a, b, **kwargs: _calculate_handler(
                operation, a, b
            ),
            param_schema={"operation": str, "a": float, "b": float},
            llm_config=LLM_CONFIG,
        ),
        handler(
            name="weather",
            description="Get weather information",
            handler_func=lambda location, **kwargs: f"Weather in {location}: 72°F, Sunny (simulated)",
            param_schema={"location": str},
            llm_config=LLM_CONFIG,
        ),
        handler(
            name="help",
            description="Get help",
            handler_func=lambda **kwargs: "I can help with greetings, calculations, and weather!",
            param_schema={},
            llm_config=LLM_CONFIG,
        ),
    ]

    # Create classifier
    classifier = llm_classifier(
        name="root",
        children=handlers,
        llm_config=LLM_CONFIG,
        description="Main intent classifier",
    )

    # Build and return the graph (uses default pass-through splitter)
    return IntentGraphBuilder().root(classifier).build()


# Test the graph
if __name__ == "__main__":
    from intent_kit.context import IntentContext

    graph = create_intent_graph()
    context = IntentContext(session_id="simple_demo")

    test_inputs = [
        "Hello, my name is Alice",
        "What's 15 plus 7?",
        "Weather in San Francisco",
        "Help me",
        "Multiply 8 and 3",
    ]

    for user_input in test_inputs:
        print(f"\nInput: {user_input}")
        result = graph.route(user_input, context=context)
        if result.success:
            print(f"Intent: {result.node_name}")
            print(f"Output: {result.output}")
        else:
            print(f"Error: {result.error}")
