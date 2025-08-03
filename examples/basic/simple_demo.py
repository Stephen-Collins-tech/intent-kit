"""
Simple IntentGraph Demo with Reporting

A minimal demonstration showing how to configure an intent graph with actions and classifiers,
using the new reporting functionality.
"""

import os
from dotenv import load_dotenv
from intent_kit import IntentGraphBuilder
from intent_kit.utils.perf_util import PerfUtil
from intent_kit.utils.report_utils import ReportUtil
from typing import Dict, Callable, Any, List, Tuple

load_dotenv()

LLM_CONFIG = {
    "provider": "openrouter",
    "api_key": os.getenv("OPENROUTER_API_KEY"),
    "model": "mistralai/ministral-8b",
}


def greet(name, context=None):
    return f"Hello {name}!"


def calculate(operation, a, b, context=None):
    # Simple operation mapping
    operation = operation.lower()
    if operation == "plus":
        return a + b
    if operation == "minus":
        return a - b
    if operation == "times":
        return a * b
    if operation == "divided":
        return a / b
    if operation == "add":
        return a + b
    if operation == "multiply":
        return a * b
    return None


def weather(location, context=None):
    return f"Weather in {location}: 72°F, Sunny (simulated)"


def help_action(context=None):
    return "I can help with greetings, calculations, and weather!"


function_registry: Dict[str, Callable[..., Any]] = {
    "greet": greet,
    "calculate": calculate,
    "weather": weather,
    "help_action": help_action,
}

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

if __name__ == "__main__":
    with PerfUtil("simple_demo.py run time") as perf:
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
        for test_input in test_inputs:
            with PerfUtil.collect(test_input, timings) as perf:
                result = graph.route(test_input)
                results.append(result)

        # Use the new format_execution_results method to format the existing results
        report = ReportUtil.format_execution_results(
            results=results,
            llm_config=LLM_CONFIG,
            perf_info=perf.format(),
            timings=timings,
        )

        print(report)
