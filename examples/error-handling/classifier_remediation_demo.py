#!/usr/bin/env python3
"""
Classifier Remediation Demo

This script demonstrates classifier remediation strategies in intent-kit:
  - Classifier fallback strategies
  - Keyword-based fallback when LLM classification fails
  - Custom classifier remediation

Usage:
    python examples/classifier_remediation_demo.py
"""

import os
import json
from dotenv import load_dotenv
from intent_kit import IntentGraphBuilder
from intent_kit.context import IntentContext
from intent_kit.node.types import ExecutionResult
from intent_kit.node.actions import (
    register_remediation_strategy,
)
from typing import Optional, Callable, List

# --- Setup LLM config ---
load_dotenv()
LLM_CONFIG = {
    "provider": "openrouter",
    "api_key": os.getenv("OPENROUTER_API_KEY"),
    "model": "meta-llama/llama-4-maverick-17b-128e-instruct",
}


# --- Core Actions ---


def greet_action(name: str, context: IntentContext) -> str:
    """Simple greeting action."""
    greeting_count = context.get("greeting_count", 0) + 1
    context.set("greeting_count", greeting_count, "greet_action")
    return f"Hello {name}! (Greeting #{greeting_count})"


def calculate_action(operation: str, a: float, b: float, context: IntentContext) -> str:
    """Simple calculation action."""
    # Map word operations to mathematical operators
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
        calc_result = f"{a} {operation} {b} = {result}"
    except (SyntaxError, ZeroDivisionError) as e:
        calc_result = f"Error: Cannot calculate {a} {operation} {b} - {str(e)}"

    # Track calculation history
    history = context.get("calc_history", [])
    history.append(calc_result)
    context.set("calc_history", history, "calculate_action")

    return calc_result


def weather_action(location: str, context: IntentContext) -> str:
    """Simple weather action."""
    weather_count = context.get("weather_count", 0) + 1
    context.set("weather_count", weather_count, "weather_action")
    return f"Weather in {location}: 72°F, Sunny (simulated)"


def help_action(context: IntentContext) -> str:
    """Help action."""
    help_count = context.get("help_count", 0) + 1
    context.set("help_count", help_count, "help_action")
    return "I can help with greetings, calculations, and weather!"


# --- Custom Classifier Fallback Strategy ---


def create_custom_classifier_fallback():
    """Create a custom classifier fallback strategy."""
    from intent_kit.node.actions import RemediationStrategy
    from intent_kit.node.types import ExecutionResult, ExecutionError

    class CustomClassifierFallbackStrategy(RemediationStrategy):
        def __init__(self):
            super().__init__(
                "custom_classifier_fallback", "Custom classifier fallback strategy"
            )

        def execute(
            self,
            node_name: str,
            user_input: str,
            context: Optional[IntentContext] = None,
            original_error: Optional[ExecutionError] = None,
            classifier_func: Optional[Callable] = None,
            available_children: Optional[List] = None,
            **kwargs,
        ) -> Optional[ExecutionResult]:
            print(
                f"🔧 Custom classifier fallback: {node_name} failed, using keyword fallback"
            )
            print(
                f"   Original error: {original_error.message if original_error else 'None'}"
            )
            print(f"   User input: {user_input}")

            if not available_children:
                return None

            # Simple keyword-based fallback routing
            user_input_lower = user_input.lower()

            for child in available_children:
                if child.name == "greet_action" and any(
                    word in user_input_lower for word in ["hello", "hi", "greet"]
                ):
                    print(f"   Fallback routing to: {child.name}")
                    return child.execute(user_input, context)
                elif child.name == "calculate_action" and any(
                    word in user_input_lower
                    for word in ["calculate", "plus", "minus", "multiply", "divide"]
                ):
                    print(f"   Fallback routing to: {child.name}")
                    return child.execute(user_input, context)
                elif child.name == "weather_action" and "weather" in user_input_lower:
                    print(f"   Fallback routing to: {child.name}")
                    return child.execute(user_input, context)
                elif child.name == "help_action" and "help" in user_input_lower:
                    print(f"   Fallback routing to: {child.name}")
                    return child.execute(user_input, context)

            # Default to help if no keywords match
            help_child = next(
                (child for child in available_children if child.name == "help_action"),
                None,
            )
            if help_child:
                print(f"   Fallback routing to: {help_child.name} (default)")
                return help_child.execute(user_input, context)

            return None

    return CustomClassifierFallbackStrategy()


def create_failing_classifier():
    """Create a classifier that intentionally fails to demonstrate remediation."""

    def failing_classifier(user_input: str, children, context=None):
        # Intentionally fail to trigger remediation
        raise ValueError("Intentional classifier failure for demo purposes")

    return failing_classifier


def main_classifier(user_input: str, children, context=None, **kwargs):
    """Simple classifier that routes to appropriate child nodes."""
    # Find child nodes by name
    greet_node = None
    calculate_node = None
    weather_node = None
    help_node = None

    for child in children:
        if child.name == "greet_action":
            greet_node = child
        elif child.name == "calculate_action":
            calculate_node = child
        elif child.name == "weather_action":
            weather_node = child
        elif child.name == "help_action":
            help_node = child

    # Simple routing logic
    if "hello" in user_input.lower() or "hi" in user_input.lower():
        return greet_node
    elif any(
        word in user_input.lower()
        for word in ["calculate", "plus", "minus", "multiply", "divide"]
    ):
        return calculate_node
    elif "weather" in user_input.lower():
        return weather_node
    elif "help" in user_input.lower():
        return help_node
    else:
        # Default to help if no clear match
        return help_node


function_registry = {
    "greet_action": greet_action,
    "calculate_action": calculate_action,
    "weather_action": weather_action,
    "help_action": help_action,
    "main_classifier": main_classifier,
}


def create_intent_graph():
    """Create and configure the intent graph using JSON."""
    # Register custom classifier fallback strategy
    custom_classifier_strategy = create_custom_classifier_fallback()
    register_remediation_strategy(
        "custom_classifier_fallback", custom_classifier_strategy
    )

    # Load the graph definition from local JSON (same directory as script)
    json_path = os.path.join(
        os.path.dirname(__file__), "classifier_remediation_demo.json"
    )
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
    context = IntentContext()
    print("=== Classifier Remediation Demo ===\n")

    print(
        "This demo shows how classifier remediation strategies handle classification failures:\n"
        "• Custom classifier fallback: Uses keyword-based routing when LLM classification fails\n"
        "• Intentional failures: Demonstrates remediation in action\n"
    )

    # Create the intent graph
    graph = create_intent_graph()

    # Test cases
    test_cases = [
        ("Hello, my name is Alice", "Should trigger classifier fallback"),
        ("Calculate 5 plus 3", "Should use keyword fallback for calculation"),
        ("Weather in San Francisco", "Should use keyword fallback for weather"),
        ("Help me", "Should use keyword fallback for help"),
    ]

    for user_input, description in test_cases:
        print(f"\n--- Test: {description} ---")
        print(f"Input: {user_input}")

        try:
            result: ExecutionResult = graph.route(
                user_input=user_input, context=context
            )
            print(f"Success: {result.success}")
            print(f"Output: {result.output}")
            if result.error:
                print(f"Error: {result.error.message}")
        except Exception as e:
            print(f"Node crashed: {e}")

    print("\n=== What did you just see? ===")
    print("• Classifier fallback: When LLM classification fails, use keyword matching")
    print("• Custom remediation: Implement your own fallback logic")
    print("• Error recovery: System continues working even when classifiers fail")


if __name__ == "__main__":
    main()
