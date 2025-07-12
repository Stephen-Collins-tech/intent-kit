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
import random
from dotenv import load_dotenv
from intent_kit.context import IntentContext
from intent_kit.node.types import ExecutionResult
from intent_kit import action
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


def unreliable_calculator(operation: str, a: float, b: float, context: IntentContext) -> str:
    """Unreliable calculator that sometimes fails."""
    if random.random() < 0.3:  # 30% chance of failure
        raise ValueError("Random calculation failure")

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
        return f"{a} {operation} {b} = {result}"
    except (SyntaxError, ZeroDivisionError) as e:
        raise ValueError(f"Calculation error: {str(e)}")


def reliable_calculator(operation: str, a: float, b: float, context: IntentContext) -> str:
    """Reliable calculator as fallback."""
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
    from intent_kit.node.actions import RemediationStrategy

    class LogAndContinueStrategy(RemediationStrategy):
        def __init__(self):
            super().__init__("log_and_continue", "Log error and return default response")

        def execute(
            self,
            node_name: str,
            user_input: str,
            context: Optional[IntentContext] = None,
            original_error: Optional[ExecutionError] = None,
            **kwargs,
        ) -> Optional[ExecutionResult]:
            self.logger.warning(
                f"LogAndContinue: {node_name} failed, continuing with default")

            return ExecutionResult(
                success=True,
                node_name=node_name,
                node_path=[node_name],
                node_type=NodeType.ACTION,
                input=user_input,
                output="Default response due to error",
                error=None,
                params={},
                children_results=[],
            )

    return LogAndContinueStrategy()


def create_intent_graph():
    """Create and configure the intent graph with remediation strategies."""

    # Create custom remediation strategy
    custom_strategy = create_custom_remediation_strategy()
    register_remediation_strategy("log_and_continue", custom_strategy)

    # Create actions with different remediation strategies
    actions = [
        # Action with retry strategy
        action(
            name="unreliable_calc",
            description="Unreliable calculator with retry strategy",
            action_func=unreliable_calculator,
            param_schema={"operation": str, "a": float, "b": float},
            llm_config=LLM_CONFIG,
            context_inputs={"calc_history"},
            context_outputs={"calc_history"},
            # Built-in retry strategy
            remediation_strategies=["retry_on_fail"],
        ),
        # Action with fallback strategy
        action(
            name="reliable_calc",
            description="Reliable calculator as fallback",
            action_func=reliable_calculator,
            param_schema={"operation": str, "a": float, "b": float},
            llm_config=LLM_CONFIG,
            context_inputs={"calc_history"},
            context_outputs={"calc_history"},
            # Built-in fallback strategy
            remediation_strategies=["fallback_to_another_node"],
        ),
        # Action with custom remediation strategy
        action(
            name="simple_greet",
            description="Simple greeter with custom remediation",
            action_func=simple_greeter,
            param_schema={"name": str},
            llm_config=LLM_CONFIG,
            context_inputs={"greeting_count"},
            context_outputs={"greeting_count"},
            remediation_strategies=["log_and_continue"],  # Custom strategy
        ),
    ]

    # Create classifier
    from intent_kit.node.classifiers import ClassifierNode

    def simple_classifier(user_input: str, children, context=None):
        """Simple classifier that routes to the first child."""
        return children[0]

    classifier = ClassifierNode(
        name="root",
        description="Simple classifier",
        classifier=simple_classifier,
        children=actions,
    )

    return classifier


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
    root_node = create_intent_graph()

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
            result: ExecutionResult = root_node.execute(
                user_input=user_input, context=context)
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
