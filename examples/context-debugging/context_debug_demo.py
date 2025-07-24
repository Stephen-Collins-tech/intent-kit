"""
Context Debugging Demo - Concise Version

Demonstrates the new context debugging features in under 150 lines.
"""

import os
import json
from intent_kit import IntentGraphBuilder
from intent_kit.context.debug import trace_context_execution
from intent_kit.context import IntentContext
from dotenv import load_dotenv

load_dotenv()

# LLM configuration
LLM_CONFIG = {
    "provider": "openrouter",
    "api_key": os.getenv("OPENROUTER_API_KEY"),
    "model": "meta-llama/llama-4-maverick-17b-128e-instruct",
}


def greet_action(name: str, context: IntentContext) -> str:
    """Simple greet action with context tracking."""
    count = context.get("greeting_count", 0) + 1
    context.set("greeting_count", count, "greet")
    context.set("last_greeted", name, "greet")
    return f"Hello {name}! (Greeting #{count})"


def calculate_action(operation: str, a: float, b: float, context: IntentContext) -> str:
    """Simple calculate action with history."""
    ops = {"add": "+", "plus": "+", "multiply": "*", "times": "*"}
    op = ops.get(operation.lower(), operation)
    result = eval(f"{a} {op} {b}")

    history = context.get("calc_history", [])
    history.append(f"{a} {operation} {b} = {result}")
    context.set("calc_history", history, "calculate")
    return f"{a} {operation} {b} = {result}"


def main_classifier(user_input: str, children, context=None, **kwargs):
    """Simple classifier that routes to appropriate child nodes."""
    # Find child nodes by name
    greet_node = None
    calculate_node = None

    for child in children:
        if child.name == "greet_action":
            greet_node = child
        elif child.name == "calculate_action":
            calculate_node = child

    # Simple routing logic
    if "hello" in user_input.lower() or "hi" in user_input.lower():
        return greet_node
    elif any(
        word in user_input.lower()
        for word in ["calculate", "plus", "multiply", "times"]
    ):
        return calculate_node
    else:
        # Default to greet if no clear match
        return greet_node


function_registry = {
    "greet_action": greet_action,
    "calculate_action": calculate_action,
    "main_classifier": main_classifier,
}


def create_intent_graph():
    """Create and configure the intent graph using JSON."""
    # Load the graph definition from local JSON (same directory as script)
    json_path = os.path.join(os.path.dirname(__file__), "context_debug_demo.json")
    with open(json_path, "r") as f:
        json_graph = json.load(f)

    return (
        IntentGraphBuilder()
        .with_json(json_graph)
        .with_functions(function_registry)
        .with_default_llm_config(LLM_CONFIG)
        ._debug_context(True)
        ._context_trace(True)
        .build()
    )


def main():
    print("Context Debugging Demo")
    print("=" * 40)

    # Create context and graph
    context = IntentContext("demo_session")
    graph = create_intent_graph()

    # Test sequence
    test_inputs = [
        "Hello, my name is Alice",
        "What's 5 plus 3?",
        "Hi again",
        "Multiply 4 and 2",
    ]

    for user_input in test_inputs:
        print(f"\nInput: {user_input}")

        result = graph.route(user_input, context=context, debug=True)
        if result.success:
            print(f"Output: {result.output}")
            print("Debug Context (Colorized Console format):")
            debug_output = trace_context_execution(
                graph, user_input, context, "console"
            )
            print(debug_output)

            # Also available: "json" format for plain JSON
        else:
            print(f"Error: {result.error}")


if __name__ == "__main__":
    main()
