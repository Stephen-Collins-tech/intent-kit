"""
Simple IntentGraph Demo

A minimal demonstration showing how to configure an intent graph with actions and classifiers.
"""

import os
import json
from dotenv import load_dotenv
from intent_kit import IntentGraphBuilder

load_dotenv()

LLM_CONFIG = {
    "provider": "openrouter",
    "api_key": os.getenv("OPENROUTER_API_KEY"),
    "model": "moonshotai/kimi-k2",
}


def greet(name, context=None):
    return f"Hello {name}!"


def calculate(operation, a, b, context=None):
    # Simple operation mapping
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


function_registry = {
    "greet": greet,
    "calculate": calculate,
    "weather": weather,
    "help_action": help_action,
}


def create_intent_graph():
    # Load the graph definition from local JSON (same directory as script)
    json_path = os.path.join(os.path.dirname(__file__), "simple_demo.json")
    with open(json_path, "r") as f:
        json_graph = json.load(f)

    return (
        IntentGraphBuilder()
        .with_json(json_graph)
        .with_functions(function_registry)
        .with_default_llm_config(LLM_CONFIG)
        .build()
    )


if __name__ == "__main__":
    from intent_kit.context import IntentContext

    graph = create_intent_graph()
    context = IntentContext(session_id="simple_demo")

    test_inputs = [
        "Hello, my name is Alice",
        "What's 15 plus 7?",
        "Weather in San Francisco",
        "Help me",
        "Multiply 8 and 3",
    ]

    for user_input in test_inputs:
        print(f"\nInput: {user_input}")
        result = graph.route(user_input, context=context)
        if result.success:
            print(f"Intent: {result.node_name}")
            print(f"Output: {result.output}")
        else:
            print(f"Error: {result.error}")
