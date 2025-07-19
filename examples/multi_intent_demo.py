#!/usr/bin/env python3
"""
Multi-Intent Demo

A demonstration showing how to handle multiple intents in a single user input
using LLM-powered splitting.
"""

import os



load_dotenv()

# LLM configuration
LLM_CONFIG = {
    "provider": "openrouter",
    "api_key": os.getenv("OPENROUTER_API_KEY"),
    "model": "meta-llama/llama-4-maverick-17b-128e-instruct",
}


def _calculate_action(operation: str, a: float, b: float) -> str:
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
    """Create and configure the intent graph for multi-intent handling."""

    # Define actions
    actions = [
        action(
            name="greet",
            description="Greet the user",
            action_func=lambda name, **kwargs: f"Hello {name}!",
            param_schema={"name": str},
            llm_config=LLM_CONFIG,
        ),
        action(
            name="calculate",
            description="Perform a calculation",
            action_func=lambda operation, a, b, **kwargs: _calculate_action(
                operation, a, b
            ),
            param_schema={"operation": str, "a": float, "b": float},
            llm_config=LLM_CONFIG,
        ),
        action(
            name="weather",
            description="Get weather information",
            action_func=lambda location, **kwargs: f"Weather in {location}: 72°F, Sunny (simulated)",
            param_schema={"location": str},
            llm_config=LLM_CONFIG,
        ),
        action(
            name="help",
            description="Get help",
            action_func=lambda **kwargs: "I can help with greetings, calculations, and weather!",
            param_schema={},
        ),
    ]

    # Create classifier
    classifier = llm_classifier(
        name="root",
        children=actions,
        llm_config=LLM_CONFIG,
        description="Main intent classifier",
    )

    # Build and return the graph with LLM-powered splitter for intelligent multi-intent handling
    return IntentGraphBuilder().root(classifier).splitter(llm_splitter_node).build()


# Test the graph
if __name__ == "__main__":


    graph = create_intent_graph()
    context = IntentContext(session_id="multi_intent_demo")

    test_inputs = [
        "Hello Alice, what's 15 plus 7?",
        "Weather in San Francisco and multiply 8 by 3",
        "Hi Bob, help me with calculations",
        "What's 20 minus 5 and weather in New York",
    ]

    for user_input in test_inputs:
        print(f"\nInput: {user_input}")
        result = graph.route(user_input, context=context)
        if result.success:
            print(f"Intent: {result.node_name}")
            print(f"Output: {result.output}")
        else:
            print(f"Error: {result.error}")
