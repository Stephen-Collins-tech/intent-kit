#!/usr/bin/env python3
"""
Remediation Demo

This script demonstrates basic remediation strategies in intent-kit:
  - Retry on failure
  - Fallback to another action
  - Custom remediation strategies

Usage:
    python examples/remediation_demo.py
"""

import os
import json
import random
from dotenv import load_dotenv
from intent_kit import IntentGraphBuilder
from intent_kit.context import IntentContext
from intent_kit.node.types import ExecutionResult
from intent_kit.node.actions import (
    register_remediation_strategy,
)
from intent_kit.node.types import ExecutionError
from intent_kit.node.enums import NodeType
from typing import Optional


# --- Setup LLM config ---
load_dotenv()
LLM_CONFIG = {
    "provider": "openrouter",
    "api_key": os.getenv("OPENROUTER_API_KEY"),
    "model": "meta-llama/llama-4-maverick-17b-128e-instruct",
}


# --- Core Actions ---


def unreliable_calculator(
    operation: str, a: float, b: float, context: IntentContext
) -> str:
    """Unreliable calculator that sometimes fails."""
    if random.random() < 0.3:  # 30% chance of failure
        raise ValueError("Random calculation failure")

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
        return f"{a} {operation} {b} = {result}"
    except (SyntaxError, ZeroDivisionError) as e:
        raise ValueError(f"Calculation error: {str(e)}")


def reliable_calculator(
    operation: str, a: float, b: float, context: IntentContext
) -> str:
    """Reliable calculator as fallback."""
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
        return f"{a} {operation} {b} = {result} (reliable)"
    except (SyntaxError, ZeroDivisionError) as e:
        return f"Error: Cannot calculate {a} {operation} {b} - {str(e)}"


def simple_greeter(name: str, context: IntentContext) -> str:
    """Simple greeter with custom remediation."""
    if random.random() < 0.2:  # 20% chance of failure
        raise ValueError("Random greeting failure")

    return f"Hello {name}! Nice to meet you."


def create_custom_remediation_strategy():
    """Create a custom remediation strategy that logs and continues."""
    from intent_kit.node.actions.remediation import RemediationStrategy

    class LogAndContinueStrategy(RemediationStrategy):
        def __init__(self):
            super().__init__(
                "log_and_continue", "Logs error and returns default response"
            )

        def execute(
            self,
            node_name: str,
            user_input: str,
            context: Optional[IntentContext] = None,
            original_error: Optional[ExecutionError] = None,
            **kwargs,
        ) -> Optional[ExecutionResult]:
            print(f"🔧 Custom remediation: Logging error for {node_name}")
            print(
                f"   Original error: {original_error.message if original_error else 'None'}"
            )
            print(f"   User input: {user_input}")

            # Return a default response
            return ExecutionResult(
                success=True,
                node_name=node_name,
                node_path=[node_name],
                node_type=NodeType.ACTION,
                input=user_input,
                output="Hello! (default response from custom remediation)",
                error=None,
                params={"remediated": True},
                children_results=[],
            )

    return LogAndContinueStrategy()


def main_classifier(user_input: str, children, context=None, **kwargs):
    """Simple classifier that routes to appropriate child nodes."""
    # Find child nodes by name
    unreliable_calc_node = None
    simple_greet_node = None

    for child in children:
        if child.name == "unreliable_calc":
            unreliable_calc_node = child
        elif child.name == "simple_greet":
            simple_greet_node = child

    # Simple routing logic
    if "calculate" in user_input.lower() or any(
        word in user_input.lower() for word in ["plus", "minus", "times", "divide"]
    ):
        return unreliable_calc_node
    elif "greet" in user_input.lower() or "hello" in user_input.lower():
        return simple_greet_node
    else:
        # Default to unreliable calc if no clear match
        return unreliable_calc_node


function_registry = {
    "unreliable_calculator": unreliable_calculator,
    "reliable_calculator": reliable_calculator,
    "simple_greeter": simple_greeter,
    "main_classifier": main_classifier,
}


def create_intent_graph():
    """Create and configure the intent graph using JSON."""
    # Register custom remediation strategy
    custom_strategy = create_custom_remediation_strategy()
    register_remediation_strategy("log_and_continue", custom_strategy)

    # Load the graph definition from local JSON (same directory as script)
    json_path = os.path.join(os.path.dirname(__file__), "remediation_demo.json")
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
    print("=== Remediation Strategies Demo ===\n")

    print(
        "This demo shows how different remediation strategies handle failures:\n"
        "• Retry on failure: Tries again with exponential backoff\n"
        "• Fallback to another action: Uses a different action when one fails\n"
        "• Custom strategy: Logs error and returns default response\n"
    )

    # Create the intent graph
    graph = create_intent_graph()

    # Test cases
    test_cases = [
        ("Calculate 5 plus 3", "Should retry if unreliable_calc fails"),
        ("Calculate 10 times 2", "Should use fallback if primary fails"),
        ("Greet Alice", "Should use custom remediation if greeting fails"),
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
    print("• Retry strategy: Automatically retries failed actions")
    print("• Fallback strategy: Uses alternative actions when primary fails")
    print("• Custom strategy: Implements custom error handling logic")


if __name__ == "__main__":
    main()
