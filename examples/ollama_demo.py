#!/usr/bin/env python3
"""
Ollama Demo

A minimal demonstration showing how to use IntentGraph with local Ollama models.
"""

from intent_kit import IntentGraphBuilder, handler, llm_classifier
from intent_kit.context import IntentContext
from datetime import datetime

# Ollama LLM configuration
OLLAMA_CONFIG = {
    "provider": "ollama",
    "model": "gemma3:27b",  # Change this to your available model
    "base_url": "http://localhost:11434",
}

# Configure your intent graph here


def create_intent_graph():
    """Create and configure the intent graph using Ollama."""

    # Define handlers with context support
    handlers = [
        handler(
            name="greet",
            description="Greet the user",
            handler_func=_greet_handler,
            param_schema={"name": str},
            llm_config=OLLAMA_CONFIG,
        ),
        handler(
            name="calculate",
            description="Perform a calculation",
            handler_func=_calculate_handler,
            param_schema={"operation": str, "a": float, "b": float},
            llm_config=OLLAMA_CONFIG,
        ),
        handler(
            name="weather",
            description="Get weather information",
            handler_func=_weather_handler,
            param_schema={"location": str},
            llm_config=OLLAMA_CONFIG,
        ),
        handler(
            name="history",
            description="Show calculation history",
            handler_func=_history_handler,
            param_schema={},
            llm_config=OLLAMA_CONFIG,
        ),
        handler(
            name="help",
            description="Get help",
            handler_func=lambda **kwargs: "I can help with greetings, calculations, weather, and history!",
            param_schema={},
            llm_config=OLLAMA_CONFIG,
        ),
    ]

    # Create classifier
    classifier = llm_classifier(
        name="root",
        children=handlers,
        llm_config=OLLAMA_CONFIG,
        description="Ollama-powered intent classifier",
    )

    # Build and return the graph
    return IntentGraphBuilder().root(classifier).build()


# Handler functions with context support
def _greet_handler(name: str, context: IntentContext) -> str:
    greeting_count = context.get("greeting_count", 0) + 1
    context.set("greeting_count", greeting_count, modified_by="greet")
    context.set("last_greeted", name, modified_by="greet")
    return f"Hello {name}! (Greeting #{greeting_count})"


def _calculate_handler(
    operation: str, a: float, b: float, context: IntentContext
) -> str:
    if operation.lower() in ["add", "plus", "+"]:
        result = a + b
        op_display = "plus"
    elif operation.lower() in ["multiply", "times", "*"]:
        result = a * b
        op_display = "times"
    else:
        return f"Error: Unknown operation '{operation}'"

    # Store in context
    calc_history = context.get("calculation_history", [])
    calc_history.append(
        {
            "operation": op_display,
            "a": a,
            "b": b,
            "result": result,
            "timestamp": datetime.now().isoformat(),
        }
    )
    context.set("calculation_history", calc_history, modified_by="calculate")

    return f"{a} {op_display} {b} = {result}"


def _weather_handler(location: str, context: IntentContext) -> str:
    # Simple caching
    last_weather = context.get("last_weather", {})
    if last_weather.get("location") == location:
        return f"Weather in {location}: {last_weather.get('data')} (cached)"

    weather_data = f"72°F, Sunny (simulated for {location})"
    context.set(
        "last_weather",
        {
            "location": location,
            "data": weather_data,
            "timestamp": datetime.now().isoformat(),
        },
        modified_by="weather",
    )

    return f"Weather in {location}: {weather_data}"


def _history_handler(context: IntentContext) -> str:
    calc_history = context.get("calculation_history", [])
    if not calc_history:
        return "No calculations have been performed yet."

    last_calc = calc_history[-1]
    return f"Last calculation: {last_calc['a']} {last_calc['operation']} {last_calc['b']} = {last_calc['result']}"


# Test the graph
if __name__ == "__main__":
    print("Ollama Demo - Local LLM IntentGraph")
    print(
        "Make sure Ollama is running and you have a model pulled (e.g., 'ollama pull gemma3:27b')"
    )
    print()

    graph = create_intent_graph()
    context = IntentContext(session_id="ollama_demo")

    test_inputs = [
        "Hello, my name is Alice",
        "What's 15 plus 7?",
        "Weather in San Francisco",
        "What was my last calculation?",
        "Multiply 8 and 3",
        "Help me",
    ]

    for user_input in test_inputs:
        print(f"\nInput: {user_input}")
        result = graph.route(user_input, context=context)
        if result.success:
            print(f"Intent: {result.node_name}")
            print(f"Output: {result.output}")
        else:
            print(f"Error: {result.error}")
