"""
Simple IntentGraph Demo

A minimal demonstration showing how to configure an intent graph with actions and classifiers.
This example shows both the programmatic API and JSON configuration approaches.
"""

import os
from dotenv import load_dotenv
from intent_kit import IntentGraphBuilder
from intent_kit import action, llm_classifier
from intent_kit.utils.perf_util import PerfUtil
from intent_kit.utils.report_utils import ReportUtil
from typing import Dict, Callable, Any, List, Tuple

load_dotenv()

# LLM Configuration
LLM_CONFIG = {
    "provider": "openrouter",
    "api_key": os.getenv("OPENROUTER_API_KEY"),
    "model": "mistralai/ministral-8b",
}

# Define action functions


def greet(name, context=None):
    """Greet a user by name."""
    return f"Hello {name}!"


def calculate(operation, a, b, context=None):
    """Perform a simple calculation."""
    operation = operation.lower()
    if operation in ["plus", "add"]:
        return a + b
    elif operation in ["minus", "subtract"]:
        return a - b
    elif operation in ["times", "multiply"]:
        return a * b
    elif operation in ["divided", "divide"]:
        return a / b
    return None


def weather(location, context=None):
    """Get weather information for a location."""
    return f"Weather in {location}: 72°F, Sunny (simulated)"


def help_action(context=None):
    """Provide help information."""
    return "I can help with greetings, calculations, and weather!"


# Create function registry
function_registry: Dict[str, Callable[..., Any]] = {
    "greet": greet,
    "calculate": calculate,
    "weather": weather,
    "help_action": help_action,
}

# JSON configuration for the graph
simple_demo_graph = {
    "root": "main_classifier",
    "nodes": {
        "main_classifier": {
            "id": "main_classifier",
            "type": "classifier",
            "classifier_type": "llm",
            "name": "main_classifier",
            "description": "Main intent classifier",
            "llm_config": {
                "provider": "openrouter",
                "api_key": os.getenv("OPENROUTER_API_KEY"),
                "model": "mistralai/ministral-8b",
            },
            "classification_prompt": "Classify the user input: '{user_input}'\n\nAvailable intents:\n{node_descriptions}\n\nReturn ONLY the intent name (e.g., calculate_action). No explanation or other text.",
            "children": [
                "greet_action",
                "calculate_action",
                "weather_action",
                "help_action",
            ],
        },
        "greet_action": {
            "id": "greet_action",
            "type": "action",
            "name": "greet_action",
            "description": "Greet the user",
            "function": "greet",
            "param_schema": {"name": "str"},
        },
        "calculate_action": {
            "id": "calculate_action",
            "type": "action",
            "name": "calculate_action",
            "description": "Perform a calculation",
            "function": "calculate",
            "param_schema": {"operation": "str", "a": "float", "b": "float"},
        },
        "weather_action": {
            "id": "weather_action",
            "type": "action",
            "name": "weather_action",
            "description": "Get weather information",
            "function": "weather",
            "param_schema": {"location": "str"},
        },
        "help_action": {
            "id": "help_action",
            "type": "action",
            "name": "help_action",
            "description": "Get help",
            "function": "help_action",
            "param_schema": {},
        },
    },
}


def demonstrate_programmatic_api():
    """Demonstrate building a graph using the programmatic API."""
    print("=== Programmatic API Demo ===")

    # Define actions using the node factory
    greet_action = action(
        name="greet",
        description="Greet the user by name",
        action_func=lambda name: f"Hello {name}!",
        param_schema={"name": str},
    )

    # Create classifier
    classifier = llm_classifier(
        name="main",
        description="Route to appropriate action",
        children=[greet_action],
        llm_config=LLM_CONFIG,
    )

    # Build graph
    graph = IntentGraphBuilder().root(classifier).build()

    # Test it
    result = graph.route("Hello Alice")
    print("Input: 'Hello Alice'")
    print(f"Output: {result.output}")
    print()


def demonstrate_json_configuration():
    """Demonstrate building a graph using JSON configuration."""
    print("=== JSON Configuration Demo ===")

    # Build graph from JSON
    graph = (
        IntentGraphBuilder()
        .with_json(simple_demo_graph)
        .with_functions(function_registry)
        .with_default_llm_config(LLM_CONFIG)
        .build()
    )

    # Test inputs
    test_inputs = [
        "Hello, my name is Alice",
        "What's 15 plus 7?",
        "Weather in San Francisco",
        "Help me",
        "Multiply 8 and 3",
    ]

    print("Testing various inputs:")
    for test_input in test_inputs:
        result = graph.route(test_input)
        print(f"Input: '{test_input}'")
        print(f"Output: {result.output}")
        print()


def demonstrate_performance_tracking():
    """Demonstrate performance tracking and reporting."""
    print("=== Performance Tracking Demo ===")

    graph = (
        IntentGraphBuilder()
        .with_json(simple_demo_graph)
        .with_functions(function_registry)
        .with_default_llm_config(LLM_CONFIG)
        .build()
    )

    test_inputs = [
        "Hello, my name is Alice",
        "What's 15 plus 7?",
        "Weather in San Francisco",
        "Help me",
        "Multiply 8 and 3",
    ]

    results = []
    timings: List[Tuple[str, float]] = []

    with PerfUtil("simple_demo.py run time") as perf:
        for test_input in test_inputs:
            with PerfUtil.collect(test_input, timings) as perf:
                result = graph.route(test_input)
                results.append(result)

    # Generate performance report
    report = ReportUtil.format_execution_results(
        results=results,
        llm_config=LLM_CONFIG,
        perf_info=perf.format(),
        timings=timings,
    )

    print("Performance Report:")
    print(report)


if __name__ == "__main__":
    print("Intent Kit Simple Demo")
    print("=" * 50)
    print()

    # Demonstrate different approaches
    demonstrate_programmatic_api()
    demonstrate_json_configuration()
    demonstrate_performance_tracking()
