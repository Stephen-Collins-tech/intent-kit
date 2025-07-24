#!/usr/bin/env python3
"""
Context Demo

A demonstration showing how context can be shared between workflow steps.
"""

import os
import json
from datetime import datetime
from dotenv import load_dotenv
from intent_kit import IntentGraphBuilder
from intent_kit.context import IntentContext

load_dotenv()

# LLM configuration
LLM_CONFIG = {
    "provider": "openrouter",
    "api_key": os.getenv("OPENROUTER_API_KEY"),
    "model": "mistralai/devstral-small",
}


def greet_action(name: str, context: IntentContext) -> str:
    """Greet the user and track greeting count."""
    # Get current greeting count
    greeting_count = context.get("greeting_count", 0) + 1
    last_greeted = context.get("last_greeted", "None")

    # Update context
    context.set("greeting_count", greeting_count, "greet_action")
    context.set("last_greeted", name, "greet_action")
    context.set("last_greeting_time", datetime.now().isoformat(), "greet_action")

    if greeting_count == 1:
        return f"Hello {name}! Nice to meet you."
    else:
        return f"Hello {name}! I've greeted you {greeting_count} times now. Last time I greeted {last_greeted}."


def calculate_action(operation: str, a: float, b: float, context: IntentContext) -> str:
    """Perform calculation and track history."""
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
        calc_result = f"{a} {operation} {b} = {result}"
    except (SyntaxError, ZeroDivisionError) as e:
        calc_result = f"Error: Cannot calculate {a} {operation} {b} - {str(e)}"
        result = None

    # Get calculation history
    history = context.get("calculation_history", [])
    history.append(
        {
            "a": a,
            "b": b,
            "operation": operation,
            "result": result,
            "timestamp": datetime.now().isoformat(),
        }
    )

    # Update context
    context.set("calculation_history", history, "calculate_action")
    context.set("last_calculation", calc_result, "calculate_action")

    return calc_result


def weather_action(location: str, context: IntentContext) -> str:
    """Get weather and cache the result."""
    # Check if we have cached weather for this location
    last_weather = context.get("last_weather", {})
    if last_weather.get("location") == location:
        return f"Weather in {location}: {last_weather.get('data', 'Unknown')} (cached)"

    # Simulate weather data
    weather_data = "72°F, Sunny"

    # Cache the weather data
    context.set(
        "last_weather",
        {
            "location": location,
            "data": weather_data,
            "timestamp": datetime.now().isoformat(),
        },
        "weather_action",
    )

    return f"Weather in {location}: {weather_data}"


def show_calculation_history_action(context: IntentContext) -> str:
    """Show calculation history from context."""
    history = context.get("calculation_history", [])
    if not history:
        return "No calculations have been performed yet."

    result = "Recent calculations:\n"
    for i, calc in enumerate(history[-3:], 1):  # Show last 3
        result += (
            f"{i}. {calc['a']} {calc['operation']} {calc['b']} = {calc['result']}\n"
        )

    return result


def help_action(context: IntentContext) -> str:
    """Get help."""
    return "I can help you with greetings, calculations, weather, and showing history!"


function_registry = {
    "greet_action": greet_action,
    "calculate_action": calculate_action,
    "weather_action": weather_action,
    "show_calculation_history_action": show_calculation_history_action,
    "help_action": help_action,
}


def create_intent_graph():
    """Create and configure the intent graph using JSON."""
    # Load the graph definition from local JSON (same directory as script)
    json_path = os.path.join(os.path.dirname(__file__), "context_demo.json")
    with open(json_path, "r") as f:
        json_graph = json.load(f)

    return (
        IntentGraphBuilder()
        .with_json(json_graph)
        .with_functions(function_registry)
        .with_default_llm_config(LLM_CONFIG)
        .build()
    )


def main():
    print("IntentKit Context Demo")
    print("This demo shows how context can be shared between workflow steps.")
    print("You must set a valid API key in LLM_CONFIG for this to work.")
    print("\n" + "=" * 50)

    # Create context for the session
    context = IntentContext(session_id="demo_user_123", debug=True)

    # Create IntentGraph using the JSON-led pattern
    graph = create_intent_graph()

    # Test sequence showing context persistence
    test_sequence = [
        "Hello, my name is Alice",
        "What's 15 plus 7?",
        "Weather in San Francisco",
        "Hi again",  # Should show greeting count
        "What's 8 times 3?",
        "Weather in San Francisco again",  # Should show cached result
        "What was my last calculation?",  # Should show context access
    ]

    for i, user_input in enumerate(test_sequence, 1):
        print(f"\n--- Step {i} ---")
        print(f"Input: {user_input}")

        try:
            # Route with context
            result = graph.route(user_input, context=context, debug=True)

            if result.success:
                print(f"  Intent: {result.node_name}")
                print(f"  Params: {result.params}")
                print(f"  Output: {result.output}")

                # Show execution path if available
                if result.children_results:
                    print("  Execution Path:")
                    for i, child_result in enumerate(result.children_results):
                        path_str = ".".join(child_result.node_path)
                        print(
                            f"    {i+1}. {child_result.node_name} ({child_result.node_type}) - Path: {path_str}"
                        )
                        if child_result.params:
                            print(f"       Params: {child_result.params}")
                        if child_result.output:
                            print(f"       Output: {child_result.output}")
                        if child_result.error:
                            print(f"       Error: {child_result.error}")

                # Show context state after execution
                print("  Context state:")
                print(f"    Greeting count: {context.get('greeting_count', 0)}")
                print(f"    Last greeted: {context.get('last_greeted', 'None')}")
                print(
                    f"    Calc history: {len(context.get('calculation_history', []))} entries"
                )
                print(
                    f"    Last weather: {context.get('last_weather', {}).get('location', 'None')}"
                )
            else:
                print(f"  Error: {result.error}")

            # Show context errors from result
            if result.error:
                print(f"  Context errors in result: {result.error.message}")

            # Show any errors from context (for backward compatibility)
            errors = context.get_errors()
            if errors:
                print(f"  Context errors: {len(errors)} total")
                for error in errors[-2:]:  # Show last 2 errors
                    print(
                        f"    [{error.timestamp.strftime('%H:%M:%S')}] {error.node_name}: {error.error_message}"
                    )

        except Exception as e:
            print(f"  Error: {e}")

    # Show final context state
    print("\n--- Final Context State ---")
    print(f"Session ID: {context.session_id}")
    print(f"Total fields: {len(context.keys())}")
    print(f"History entries: {len(context.get_history())}")
    print(f"Error count: {context.error_count()}")

    # Show some context history
    print("\n--- Context History (last 5 entries) ---")
    for entry in context.get_history(limit=5):
        print(f"  {entry.timestamp}: {entry.action} '{entry.key}' = {entry.value}")

    # Show recent errors if any
    errors = context.get_errors(limit=3)
    if errors:
        print("\n--- Recent Errors (last 3) ---")
        for error in errors:
            print(f"  [{error.timestamp.strftime('%H:%M:%S')}] {error.node_name}")
            print(f"    Input: {error.user_input}")
            print(f"    Error: {error.error_message}")
            if error.params:
                print(f"    Params: {error.params}")
            print()


if __name__ == "__main__":
    main()
