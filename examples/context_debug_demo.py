"""
Context Debugging Demo - Concise Version

Demonstrates the new context debugging features in under 150 lines.
"""

import os
from intent_kit import IntentGraphBuilder, action, llm_classifier
from intent_kit import trace_context_execution
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


def build_graph():
    """Build a simple intent graph with context debugging."""
    actions = [
        action(
            name="greet",
            description="Greet user",
            action_func=greet_action,
            param_schema={"name": str},
            llm_config=LLM_CONFIG,
            context_inputs={"greeting_count"},
            context_outputs={"greeting_count", "last_greeted"},
        ),
        action(
            name="calculate",
            description="Calculate",
            action_func=calculate_action,
            param_schema={"operation": str, "a": float, "b": float},
            llm_config=LLM_CONFIG,
            context_inputs={"calc_history"},
            context_outputs={"calc_history"},
        ),
    ]

    classifier = llm_classifier(name="root", children=actions, llm_config=LLM_CONFIG)
    return (
        IntentGraphBuilder()
        .root(classifier)
        ._debug_context(True)
        ._context_trace(True)
        .build()
    )


def main():
    print("Context Debugging Demo")
    print("=" * 40)

    # Create context and graph
    context = IntentContext("demo_session")
    graph = build_graph()

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
