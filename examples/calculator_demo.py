"""
Calculator Demo

Simple calculator showing parameter extraction and math operations.
"""

import os
import math
from dotenv import load_dotenv
from intent_kit.graph.builder import IntentGraphBuilder
from intent_kit.context import Context

load_dotenv()

# Calculator functions


def basic_math(operation: str, a: float, b: float) -> str:
    if operation == "+":
        result = a + b
    elif operation == "-":
        result = a - b
    elif operation == "*":
        result = a * b
    elif operation == "/":
        if b == 0:
            raise ValueError("Cannot divide by zero")
        result = a / b
    else:
        raise ValueError(f"Unknown operation: {operation}")

    return f"{a} {operation} {b} = {result}"


def advanced_math(operation: str, number: float) -> str:
    if operation == "sqrt":
        result = math.sqrt(number)
    elif operation == "square":
        result = number**2
    else:
        raise ValueError(f"Unknown operation: {operation}")

    return f"{operation}({number}) = {result}"


# Graph configuration
calculator_graph = {
    "root": "calc_classifier",
    "nodes": {
        "calc_classifier": {
            "id": "calc_classifier",
            "name": "calc_classifier",
            "type": "classifier",
            "classifier_type": "llm",
            "llm_config": {
                "provider": "openrouter",
                "api_key": os.getenv("OPENROUTER_API_KEY"),
                "model": "google/gemma-2-9b-it",
            },
            "children": ["basic_math_action", "advanced_math_action"],
        },
        "basic_math_action": {
            "id": "basic_math_action",
            "name": "basic_math_action",
            "type": "action",
            "function": "basic_math",
            "param_schema": {"operation": "str", "a": "float", "b": "float"},
        },
        "advanced_math_action": {
            "id": "advanced_math_action",
            "name": "advanced_math_action",
            "type": "action",
            "function": "advanced_math",
            "param_schema": {"operation": "str", "number": "float"},
        },
    },
}

if __name__ == "__main__":
    # Build calculator
    graph = (
        IntentGraphBuilder()
        .with_json(calculator_graph)
        .with_functions({"basic_math": basic_math, "advanced_math": advanced_math})
        .with_default_llm_config(
            {
                "provider": "openrouter",
                "api_key": os.getenv("OPENROUTER_API_KEY"),
                "model": "google/gemma-2-9b-it",
            }
        )
        .build()
    )

    context = Context()

    # Test calculations
    test_inputs = [
        "Calculate 15 + 7",
        "What's 20 * 3?",
        "Square root of 64",
        "Square 8",
    ]

    print("🧮 Calculator Demo")
    print("-" * 20)

    for user_input in test_inputs:
        result = graph.route(user_input, context=context)
        print(f"Input: '{user_input}' → {result.output}")

    print(f"\nOperations: {context.get_operation_count()}")
