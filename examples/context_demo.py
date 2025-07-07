"""
Context Demo for IntentKit

A demonstration of the new IntentContext system showing how state can be shared
between different steps of a workflow and across multiple user interactions.
"""

import os
from datetime import datetime
from intent_kit.context import IntentContext
from intent_kit import IntentGraphBuilder, handler, llm_classifier
from intent_kit.services.llm_factory import LLMFactory
from dotenv import load_dotenv
load_dotenv()

# LLM configuration
LLM_CONFIG = {
    "provider": "openrouter",
    "api_key": os.getenv("OPENROUTER_API_KEY"),
    "model": "meta-llama/llama-4-maverick-17b-128e-instruct"
}

# Create LLM client
LLM_CLIENT = LLMFactory.create_client(LLM_CONFIG)


def greet_handler(name: str, context: IntentContext) -> str:
    """Greet handler with context tracking."""
    # Read from context
    greeting_count = context.get("greeting_count", 0)
    last_greeted = context.get("last_greeted", "No one")

    # Update context
    context.set("greeting_count", greeting_count + 1, modified_by="greet")
    context.set("last_greeted", name, modified_by="greet")
    context.set("last_greeting_time",
                datetime.now().isoformat(), modified_by="greet")

    return f"Hello {name}! (Greeting #{greeting_count + 1}, last greeted: {last_greeted})"


def calculate_handler(operation: str, a: float, b: float, context: IntentContext) -> str:
    """Calculate handler with history tracking."""
    result = None

    # Map common operation names to actual operations
    operation_lower = operation.lower()
    if operation_lower in ["add", "plus", "addition", "+"]:
        result = a + b
        operation_display = "plus"
    elif operation_lower in ["subtract", "minus", "subtraction", "-"]:
        result = a - b
        operation_display = "minus"
    elif operation_lower in ["multiply", "times", "multiplication", "*"]:
        result = a * b
        operation_display = "times"
    elif operation_lower in ["divide", "division", "/"]:
        if b != 0:
            result = a / b
            operation_display = "divided by"
        else:
            result = "Error: Division by zero"
            operation_display = "divided by"
    else:
        # Unknown operation
        result = f"Error: Unknown operation '{operation}'"
        operation_display = operation

    # Store calculation history in context
    calc_history = context.get("calculation_history", [])
    calc_history.append({
        "operation": operation_display,
        "a": a,
        "b": b,
        "result": result,
        "timestamp": datetime.now().isoformat()
    })
    context.set("calculation_history", calc_history, modified_by="calculate")
    context.set("last_calculation",
                f"{a} {operation_display} {b} = {result}", modified_by="calculate")

    return f"{a} {operation_display} {b} = {result}"


def weather_handler(location: str, context: IntentContext) -> str:
    """Weather handler with caching."""
    # Check if we've already fetched weather for this location recently
    last_weather = context.get("last_weather", {})
    if last_weather.get("location") == location:
        return f"Weather in {location}: {last_weather.get('data')} (cached)"

    # Simulate weather data
    weather_data = f"72°F, Sunny (simulated for {location})"

    # Store in context
    context.set("last_weather", {
        "location": location,
        "data": weather_data,
        "timestamp": datetime.now().isoformat()
    }, modified_by="weather")

    return f"Weather in {location}: {weather_data}"


def show_calculation_history_handler(context: IntentContext) -> str:
    """Show calculation history from context."""
    calc_history = context.get("calculation_history", [])

    if not calc_history:
        return "No calculations have been performed yet."

    # Get the last calculation
    last_calc = calc_history[-1]

    if last_calc.get("result") is not None:
        return f"Your last calculation was: {last_calc['a']} {last_calc['operation']} {last_calc['b']} = {last_calc['result']}"
    else:
        return f"Your last calculation was: {last_calc['a']} {last_calc['operation']} {last_calc['b']} (result not available)"


def build_context_aware_tree():
    """Build an intent tree with context-aware handlers using the new API."""

    # Create handlers using the new handler() function with context support
    greet_handler_node = handler(
        name="greet",
        description="Greet the user with context tracking",
        handler_func=greet_handler,
        param_schema={"name": str},
        llm_config=LLM_CONFIG,
        context_inputs={"greeting_count", "last_greeted"},
        context_outputs={"greeting_count",
                         "last_greeted", "last_greeting_time"}
    )

    calc_handler_node = handler(
        name="calculate",
        description="Perform calculations with history tracking",
        handler_func=calculate_handler,
        param_schema={"operation": str, "a": float, "b": float},
        llm_config=LLM_CONFIG,
        context_inputs={"calculation_history"},
        context_outputs={"calculation_history", "last_calculation"}
    )

    weather_handler_node = handler(
        name="weather",
        description="Get weather with caching",
        handler_func=weather_handler,
        param_schema={"location": str},
        llm_config=LLM_CONFIG,
        context_inputs={"last_weather"},
        context_outputs={"last_weather"}
    )

    history_handler_node = handler(
        name="show_calculation_history",
        description="Show calculation history from context",
        handler_func=show_calculation_history_handler,
        param_schema={},
        llm_config=LLM_CONFIG,
        context_inputs={"calculation_history"}
    )

    help_handler_node = handler(
        name="help",
        description="Get help",
        handler_func=lambda: "I can help you with greetings, calculations, weather, and showing history!",
        param_schema={},
        llm_config=LLM_CONFIG
    )

    # Create classifier with auto-wired children descriptions
    return llm_classifier(
        name="llm_classifier",
        children=[
            greet_handler_node,
            calc_handler_node,
            weather_handler_node,
            history_handler_node,
            help_handler_node
        ],
        llm_config=LLM_CONFIG,
        description="LLM-powered intent classifier with context support"
    )


def main():
    print("IntentKit Context Demo")
    print("This demo shows how context can be shared between workflow steps.")
    print("You must set a valid API key in LLM_CONFIG for this to work.")
    print("\n" + "="*50)

    # Create context for the session
    context = IntentContext(session_id="demo_user_123", debug=True)

    # Create IntentGraph using the new builder pattern
    graph = (
        IntentGraphBuilder()
        .root(build_context_aware_tree())
        .build()
    )

    # Test sequence showing context persistence
    test_sequence = [
        "Hello, my name is Alice",
        "What's 15 plus 7?",
        "Weather in San Francisco",
        "Hi again",  # Should show greeting count
        "What's 8 times 3?",
        "Weather in San Francisco again",  # Should show cached result
        "What was my last calculation?"  # Should show context access
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
                        path_str = '.'.join(child_result.node_path)
                        print(
                            f"    {i+1}. {child_result.node_name} ({child_result.node_type}) - Path: {path_str}")
                        if child_result.params:
                            print(
                                f"       Params: {child_result.params}")
                        if child_result.output:
                            print(
                                f"       Output: {child_result.output}")
                        if child_result.error:
                            print(f"       Error: {child_result.error}")

                # Show context state after execution
                print("  Context state:")
                print(
                    f"    Greeting count: {context.get('greeting_count', 0)}")
                print(
                    f"    Last greeted: {context.get('last_greeted', 'None')}")
                print(
                    f"    Calc history: {len(context.get('calculation_history', []))} entries")
                print(
                    f"    Last weather: {context.get('last_weather', {}).get('location', 'None')}")
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
                        f"    [{error.timestamp.strftime('%H:%M:%S')}] {error.node_name}: {error.error_message}")

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
            print(
                f"  [{error.timestamp.strftime('%H:%M:%S')}] {error.node_name}")
            print(f"    Input: {error.user_input}")
            print(f"    Error: {error.error_message}")
            if error.params:
                print(f"    Params: {error.params}")
            print()


if __name__ == "__main__":
    main()
