#!/usr/bin/env python3
"""
Ollama Demo

A minimal demonstration showing how to use IntentGraph with local Ollama models.
"""

import os
import json
from intent_kit import IntentGraphBuilder
from intent_kit.context import IntentContext

# Ollama LLM configuration
OLLAMA_CONFIG = {
    "provider": "ollama",
    "model": "gemma3:27b",  # Change this to your available model
    "base_url": "http://localhost:11434",
}


def greet_action(name: str, **kwargs) -> str:
    """Greet the user."""
    return f"Hello {name}! Nice to meet you."


def calculate_action(operation: str, a: float, b: float, **kwargs) -> str:
    """Perform a calculation."""
    operation_map = {
        "plus": "+",
        "add": "+",
        "minus": "-",
        "subtract": "-",
        "times": "*",
        "multiply": "*",
        "divided": "/",
        "divide": "/",
    }
    math_op = operation_map.get(operation.lower(), operation)

    try:
        result = eval(f"{a} {math_op} {b}")
        return f"{a} {operation} {b} = {result}"
    except (SyntaxError, ZeroDivisionError) as e:
        return f"Error: Cannot calculate {a} {operation} {b} - {str(e)}"


def weather_action(location: str, **kwargs) -> str:
    """Get weather information."""
    return f"Weather in {location}: 72°F, Sunny (simulated)"


def history_action(context: IntentContext) -> str:
    """Show calculation history."""
    calc_history = context.get("calculation_history", [])
    if not calc_history:
        return "No calculations have been performed yet."

    last_calc = calc_history[-1]
    return f"Your last calculation was: {last_calc}"


def help_action(**kwargs) -> str:
    """Get help."""
    return "I can help with greetings, calculations, weather, and history!"


function_registry = {
    "greet_action": greet_action,
    "calculate_action": calculate_action,
    "weather_action": weather_action,
    "history_action": history_action,
    "help_action": help_action,
}


def create_intent_graph():
    """Create and configure the intent graph using JSON."""
    # Load the graph definition from local JSON (same directory as script)
    json_path = os.path.join(os.path.dirname(__file__), "ollama_demo.json")
    with open(json_path, "r") as f:
        json_graph = json.load(f)

    return (
        IntentGraphBuilder()
        .with_json(json_graph)
        .with_functions(function_registry)
        .with_default_llm_config(OLLAMA_CONFIG)
        .build()
    )


# Test the graph
if __name__ == "__main__":
    graph = create_intent_graph()
    context = IntentContext(session_id="ollama_demo")

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
