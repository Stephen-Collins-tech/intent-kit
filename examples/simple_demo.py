"""
Simple Intent Kit Demo - The Basics

This is the most minimal example to get started with Intent Kit.
Shows basic graph building and execution in ~30 lines.
"""

import os
from dotenv import load_dotenv
from intent_kit.graph.builder import IntentGraphBuilder
from intent_kit.context import Context

# Import strategies module to ensure strategies are available in registry

load_dotenv()

# Simple action functions


def greet(name: str) -> str:
    return f"Hello {name}!"


def calculate(operation: str, a: float, b: float) -> str:
    calc_result = 0.0
    if operation == "+":
        calc_result = a + b
    elif operation == "-":
        calc_result = a - b
    elif operation == "*":
        calc_result = a * b
    elif operation == "/":
        if b == 0:
            raise ValueError("Cannot divide by zero")
        calc_result = a / b
    else:
        raise ValueError(f"Unsupported operation: {operation}. Use +, -, *, or /")

    return f"{a} {operation} {b} = {calc_result}"


def weather(location: str) -> str:
    return f"Weather in {location}: 72°F, Sunny (simulated)"


# Validation functions for each action
def validate_greet_params(params: dict) -> bool:
    """Validate greet action parameters."""
    if "name" not in params:
        return False
    name = params["name"]
    return isinstance(name, str) and len(name.strip()) > 0


def validate_calculate_params(params: dict) -> bool:
    """Validate calculate action parameters."""
    required_keys = {"operation", "a", "b"}
    if not required_keys.issubset(params.keys()):
        return False

    operation = (
        params["operation"].lower()
        if isinstance(params["operation"], str)
        else str(params["operation"])
    )

    # Map various operation formats to standard symbols
    operation_map = {
        "+": "+",
        "add": "+",
        "addition": "+",
        "plus": "+",
        "-": "-",
        "subtract": "-",
        "subtraction": "-",
        "minus": "-",
        "*": "*",
        "multiply": "*",
        "multiplication": "*",
        "times": "*",
        "/": "/",
        "divide": "/",
        "division": "/",
        "divided by": "/",
    }

    if operation not in operation_map:
        return False

    # Normalize the operation in the params dict
    params["operation"] = operation_map[operation]

    try:
        float(params["a"])
        float(params["b"])
        return True
    except (ValueError, TypeError):
        return False


def validate_weather_params(params: dict) -> bool:
    """Validate weather action parameters."""
    if "location" not in params:
        return False
    location = params["location"]
    return isinstance(location, str) and len(location.strip()) > 0


# Minimal graph configuration
demo_graph = {
    "root": "main_classifier",
    "nodes": {
        "main_classifier": {
            "id": "main_classifier",
            "name": "main_classifier",
            "type": "classifier",
            "classifier_type": "llm",
            "llm_config": {
                "provider": "openrouter",
                # "provider": "openai",
                "api_key": os.getenv("OPENROUTER_API_KEY"),
                "model": "google/gemma-2-9b-it",
                # "model": "gpt-5-2025-08-07",
                # "model": "mistralai/ministral-8b",
            },
            "children": ["greet_action", "calculate_action", "weather_action"],
            "remediation_strategies": ["keyword_fallback"],
        },
        "greet_action": {
            "id": "greet_action",
            "name": "greet_action",
            "type": "action",
            "function": "greet",
            "description": "Greet the user with a personalized message",
            "param_schema": {"name": "str"},
            "input_validator": "validate_greet_params",
            "remediation_strategies": ["retry_on_fail", "keyword_fallback"],
        },
        "calculate_action": {
            "id": "calculate_action",
            "name": "calculate_action",
            "type": "action",
            "function": "calculate",
            "description": "Perform mathematical calculations (addition, subtraction, multiplication, division)",
            "param_schema": {"operation": "str", "a": "float", "b": "float"},
            "input_validator": "validate_calculate_params",
            "remediation_strategies": ["retry_on_fail", "keyword_fallback"],
        },
        "weather_action": {
            "id": "weather_action",
            "name": "weather_action",
            "type": "action",
            "function": "weather",
            "description": "Get weather information for a specific location",
            "param_schema": {"location": "str"},
            "input_validator": "validate_weather_params",
            "remediation_strategies": ["retry_on_fail", "keyword_fallback"],
        },
    },
}

if __name__ == "__main__":
    # Build graph
    llm_config = {
        "provider": "openrouter",
        "api_key": os.getenv("OPENROUTER_API_KEY"),
        "model": "google/gemma-2-9b-it",
    }

    graph = (
        IntentGraphBuilder()
        .with_json(demo_graph)
        .with_functions(
            {
                "greet": greet,
                "calculate": calculate,
                "weather": weather,
                "validate_greet_params": validate_greet_params,
                "validate_calculate_params": validate_calculate_params,
                "validate_weather_params": validate_weather_params,
            }
        )
        .with_default_llm_config(llm_config)
        .build()
    )
    context = Context()

    # Test with different inputs
    test_inputs = [
        #     # Overlapping semantics
        #     "Hey there, what’s 5 plus 3? And also, how’s the weather?",
        #     "Good morning, can you tell me if it's sunny?",
        #     # Implicit intent
        # "I’m shivering and the sky’s grey — do you think I’ll need a coat?",
        #     "Could you help me with something?",
        #     # Ambiguous wording
        #     "It’s a beautiful day, isn’t it?",
        #     "Can you work out if I’ll need an umbrella tomorrow?",
        #     # Adversarial keyword placement
        #     "Calculate whether it’s going to rain today.",
        "Weather you could greet me or do the math doesn’t matter.",
        #     # Context shift in same sentence
        "Hello! Actually, never mind the small talk — what’s 42 times 13?",
        #     "Before you answer my math question, how warm is it outside?",
        #     # Mixed signals and indirect requests
        #     "Morning! Quick — what’s 15 squared?",
        #     "Is it sunny today or should I bring my calculator?",
        #     "If it’s raining, tell me. Otherwise, say hi.",
        #     "Greet me, then solve 8 × 7.",
        #     # Puns and idioms
        #     "I’m feeling under the weather — how about you?",
        #     "You really brighten my day like the sun.",
        #     # Trick phrasing
        #     "Give me the forecast for my mood.",
        # "Work out the temperature in London.",
        #     "Say hello in the warmest way possible.",
        # "Check if it’s snowing, then tell me a joke."
    ]

    for user_input in test_inputs:
        result = graph.route(user_input, context=context)
        print(f"Input: '{user_input}' → {result.output}")
