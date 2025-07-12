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
from dotenv import load_dotenv
from intent_kit.context import IntentContext
from intent_kit.node.types import ExecutionResult
from intent_kit import action
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
        "plus": "+", "add": "+",
        "minus": "-", "subtract": "-",
        "times": "*", "multiply": "*",
        "divided": "/", "divide": "/",
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
            super().__init__("custom_classifier_fallback",
                             "Custom classifier fallback strategy")

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
            """Execute custom classifier fallback logic."""
            self.logger.info(
                f"CustomClassifierFallback: Attempting fallback for {node_name}")

            if not available_children:
                self.logger.warning("No children available for fallback")
                return None

            # Simple keyword-based fallback
            input_lower = user_input.lower()

            if any(word in input_lower for word in ["hello", "hi", "greet", "name"]):
                fallback_child = available_children[0]  # greet action
            elif any(word in input_lower for word in ["calculate", "math", "+", "-", "*", "/", "plus", "times"]):
                fallback_child = available_children[1]  # calculate action
            elif any(word in input_lower for word in ["weather", "temperature", "forecast"]):
                fallback_child = available_children[2]  # weather action
            else:
                fallback_child = available_children[3]  # help action

            try:
                # Execute the fallback child
                result = fallback_child.execute(user_input, context)
                self.logger.info(
                    f"CustomClassifierFallback: Successfully executed {fallback_child.name}")
                return result
            except Exception as e:
                self.logger.error(
                    f"CustomClassifierFallback: Failed to execute fallback: {e}")
                return None

    return CustomClassifierFallbackStrategy()


def create_failing_classifier():
    """Create a classifier that always fails to demonstrate remediation."""
    def failing_classifier(user_input: str, children, context=None):
        """Classifier that always raises an exception."""
        raise ValueError("Intentional classifier failure for demo purposes")

    return failing_classifier


def create_intent_graph():
    """Create and configure the intent graph with classifier remediation strategies."""

    # Create custom classifier fallback strategy
    custom_classifier_strategy = create_custom_classifier_fallback()
    register_remediation_strategy(
        "custom_classifier_fallback", custom_classifier_strategy
    )

    # Create actions
    actions = [
        action(
            name="greet",
            description="Greet the user",
            action_func=greet_action,
            param_schema={"name": str},
            llm_config=LLM_CONFIG,
            context_inputs={"greeting_count"},
            context_outputs={"greeting_count"},
        ),
        action(
            name="calculate",
            description="Perform calculations",
            action_func=calculate_action,
            param_schema={"operation": str, "a": float, "b": float},
            llm_config=LLM_CONFIG,
            context_inputs={"calc_history"},
            context_outputs={"calc_history"},
        ),
        action(
            name="weather",
            description="Get weather information",
            action_func=weather_action,
            param_schema={"location": str},
            llm_config=LLM_CONFIG,
            context_inputs={"weather_count"},
            context_outputs={"weather_count"},
        ),
        action(
            name="help",
            description="Provide help information",
            action_func=help_action,
            param_schema={},
            llm_config=LLM_CONFIG,
            context_inputs={"help_count"},
            context_outputs={"help_count"},
        ),
    ]

    # Create classifier with a failing classifier to force remediation
    from intent_kit.node.classifiers import ClassifierNode

    # Use a failing classifier instead of LLM classifier to demonstrate remediation
    failing_classifier = create_failing_classifier()

    classifier = ClassifierNode(
        name="main_classifier",
        description="Main intent classifier with remediation",
        classifier=failing_classifier,
        children=actions,
        remediation_strategies=["custom_classifier_fallback"],
    )

    return classifier


def main():
    context = IntentContext()
    print("=== Classifier Remediation Demo ===\n")

    print(
        "This demo shows how classifier remediation strategies handle classification failures:\n"
        "• Custom classifier fallback: Uses keyword-based routing when LLM classification fails\n"
        "• Intentional failures: Demonstrates remediation in action\n"
    )

    # Create the intent graph
    root_node = create_intent_graph()

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
            result: ExecutionResult = root_node.execute(
                user_input=user_input, context=context)
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
