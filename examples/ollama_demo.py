#!/usr/bin/env python3
"""
Ollama Demo

A minimal demonstration showing how to use IntentGraph with local Ollama models.
"""

from intent_kit import IntentGraphBuilder, action, llm_classifier
from intent_kit.context import IntentContext

# Ollama LLM configuration
OLLAMA_CONFIG = {
    "provider": "ollama",
    "model": "gemma3:27b",  # Change this to your available model
    "base_url": "http://localhost:11434",
}

# Configure your intent graph here


def _greet_action(name: str, **kwargs) -> str:
    """Greet the user."""
    return f"Hello {name}! Nice to meet you."


def _calculate_action(operation: str, a: float, b: float, **kwargs) -> str:
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


def _weather_action(location: str, **kwargs) -> str:
    """Get weather information."""
    return f"Weather in {location}: 72°F, Sunny (simulated)"


def _history_action(context: IntentContext) -> str:
    """Show calculation history."""
    calc_history = context.get("calculation_history", [])
    if not calc_history:
        return "No calculations have been performed yet."

    last_calc = calc_history[-1]
    return f"Your last calculation was: {last_calc}"


def create_intent_graph():
    """Create and configure the intent graph using Ollama."""

    # Define actions with context support
    actions = [
        action(
            name="greet",
            description="Greet the user",
            action_func=_greet_action,
            param_schema={"name": str},
            llm_config=OLLAMA_CONFIG,
        ),
        action(
            name="calculate",
            description="Perform a calculation",
            action_func=_calculate_action,
            param_schema={"operation": str, "a": float, "b": float},
            llm_config=OLLAMA_CONFIG,
        ),
        action(
            name="weather",
            description="Get weather information",
            action_func=_weather_action,
            param_schema={"location": str},
            llm_config=OLLAMA_CONFIG,
        ),
        action(
            name="history",
            description="Show calculation history",
            action_func=_history_action,
            param_schema={},
            llm_config=OLLAMA_CONFIG,
        ),
        action(
            name="help",
            description="Get help",
            action_func=lambda **kwargs: "I can help with greetings, calculations, weather, and history!",
            param_schema={},
            llm_config=OLLAMA_CONFIG,
        ),
    ]

    # Create classifier
    classifier = llm_classifier(
        name="root",
        children=actions,
        llm_config=OLLAMA_CONFIG,
        description="Main intent classifier",
    )

    # Build and return the graph
    return IntentGraphBuilder().root(classifier).build()


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
