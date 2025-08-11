"""
Context Management Demo

Shows how Context stores data across graph executions.
"""

import os
from dotenv import load_dotenv
from intent_kit.graph.builder import IntentGraphBuilder
from intent_kit.context import Context

load_dotenv()

# Context-aware functions


def remember_name(name: str, context: Context | None = None) -> str:
    if context:
        context.set("user_name", name, "remember_name")
    return f"I'll remember your name is {name}"


def get_name(context: Context | None = None) -> str:
    if context and context.has("user_name"):
        name = context.get("user_name")
        return f"Your name is {name}"
    return "I don't know your name yet"


def count_interactions(context: Context | None = None) -> str:
    if context:
        count = context.get_operation_count()
        return f"We've had {count} interactions"
    return "No context available"


# Simple graph
context_graph = {
    "root": "context_classifier",
    "nodes": {
        "context_classifier": {
            "id": "context_classifier",
            "name": "context_classifier",
            "type": "classifier",
            "classifier_type": "llm",
            "llm_config": {
                "provider": "openrouter",
                "api_key": os.getenv("OPENROUTER_API_KEY"),
                "model": "google/gemma-2-9b-it",
            },
            "children": [
                "remember_name_action",
                "get_name_action",
                "count_interactions_action",
            ],
        },
        "remember_name_action": {
            "id": "remember_name_action",
            "name": "remember_name_action",
            "type": "action",
            "function": "remember_name",
            "param_schema": {"name": "str"},
        },
        "get_name_action": {
            "id": "get_name_action",
            "name": "get_name_action",
            "type": "action",
            "function": "get_name",
            "param_schema": {},
        },
        "count_interactions_action": {
            "id": "count_interactions_action",
            "name": "count_interactions_action",
            "type": "action",
            "function": "count_interactions",
            "param_schema": {},
        },
    },
}

if __name__ == "__main__":
    # Build graph
    graph = (
        IntentGraphBuilder()
        .with_json(context_graph)
        .with_functions(
            {
                "remember_name": remember_name,
                "get_name": get_name,
                "count_interactions": count_interactions,
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

    # Test context persistence
    test_inputs = [
        "My name is Alice",
        "What's my name?",
        "How many times have we talked?",
        "What's my name again?",
    ]

    print("🔄 Context Management Demo")
    print("-" * 30)

    for user_input in test_inputs:
        result = graph.route(user_input, context=context)
        print(f"Input: '{user_input}' → {result.output}")

    print(f"\nFinal context keys: {list(context.keys())}")
    print(f"Total operations: {context.get_operation_count()}")
