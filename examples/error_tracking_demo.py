"""
Error Tracking Demo

Shows how Context automatically tracks operation success/failure.
"""

import os
from dotenv import load_dotenv
from intent_kit.graph.builder import IntentGraphBuilder
from intent_kit.context import Context
from intent_kit.exceptions import ValidationError

load_dotenv()

# Functions with deliberate errors for demo


def divide_numbers(a: float, b: float) -> str:
    if b == 0:
        raise ValidationError("Cannot divide by zero", validation_type="math_error")
    return f"{a} / {b} = {a / b}"


def check_positive(number: float) -> str:
    if number <= 0:
        raise ValidationError(
            "Number must be positive", validation_type="validation_error"
        )
    return f"{number} is positive!"


def always_works() -> str:
    return "This always works!"


# Graph with error-prone actions
error_graph = {
    "root": "error_classifier",
    "nodes": {
        "error_classifier": {
            "id": "error_classifier",
            "name": "error_classifier",
            "type": "classifier",
            "classifier_type": "llm",
            "llm_config": {
                "provider": "openrouter",
                "api_key": os.getenv("OPENROUTER_API_KEY"),
                "model": "google/gemma-2-9b-it",
            },
            "children": ["divide_action", "positive_action", "works_action"],
        },
        "divide_action": {
            "id": "divide_action",
            "name": "divide_action",
            "type": "action",
            "function": "divide_numbers",
            "param_schema": {"a": "float", "b": "float"},
        },
        "positive_action": {
            "id": "positive_action",
            "name": "positive_action",
            "type": "action",
            "function": "check_positive",
            "param_schema": {"number": "float"},
        },
        "works_action": {
            "id": "works_action",
            "name": "works_action",
            "type": "action",
            "function": "always_works",
            "param_schema": {},
        },
    },
}

if __name__ == "__main__":
    # Build graph
    graph = (
        IntentGraphBuilder()
        .with_json(error_graph)
        .with_functions(
            {
                "divide_numbers": divide_numbers,
                "check_positive": check_positive,
                "always_works": always_works,
            }
        )
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

    # Test inputs (some will fail)
    test_inputs = [
        "Divide 10 by 2",  # Success
        "Divide 10 by 0",  # Error
        "Check if 5 is positive",  # Success
        "Check if -3 is positive",  # Error
        "Test the working function",  # Success
    ]

    print("📊 Error Tracking Demo")
    print("-" * 25)

    for user_input in test_inputs:
        result = graph.route(user_input, context=context)
        status = "✅" if result.success else "❌"
        print(f"{status} '{user_input}' → {result.output or 'Error occurred'}")

    # Show tracking summary
    print("\n" + "=" * 40)
    context.print_operation_summary()
