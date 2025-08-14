"""
Simple Intent Kit Demo - JSON DAG Example

A minimal example showing how to define and execute a DAG using JSON configuration.
"""

import os
import json
from dotenv import load_dotenv
from intent_kit import DAGBuilder, run_dag

load_dotenv()


def greet(name: str) -> str:
    return f"Hello {name}!"


def create_dag_from_json():
    """Create a DAG using JSON configuration."""

    # Define the entire DAG as a dictionary
    dag_config = {
        "nodes": {
            "classifier": {
                "type": "classifier",
                "output_labels": ["greet"],
                "description": "Classify if input is a greeting",
                "llm_config": {
                    "provider": "openrouter",
                    "api_key": os.getenv("OPENROUTER_API_KEY"),
                    "model": "google/gemma-2-9b-it",
                },
            },
            "extractor": {
                "type": "extractor",
                "param_schema": {"name": str},
                "description": "Extract name from greeting",
                "llm_config": {
                    "provider": "openrouter",
                    "api_key": os.getenv("OPENROUTER_API_KEY"),
                    "model": "google/gemma-2-9b-it",
                },
                "output_key": "extracted_params",
            },
            "greet_action": {
                "type": "action",
                "action": greet,
                "description": "Greet the user",
            },
            "clarification": {
                "type": "clarification",
                "clarification_message": "I'm not sure what you'd like me to do. Please try saying hello!",
                "available_options": ["Say hello to someone"],
                "description": "Ask for clarification when intent is unclear",
            },
        },
        "edges": [
            {"from": "classifier", "to": "extractor", "label": "greet"},
            {"from": "extractor", "to": "greet_action", "label": "success"},
            {"from": "classifier", "to": "clarification", "label": "clarification"},
        ],
        "entrypoints": ["classifier"],
    }

    # Use the convenience method to create DAG from JSON
    return DAGBuilder.from_json(dag_config)


if __name__ == "__main__":
    print("=== JSON DAG Demo ===\n")

    # Show the JSON structure (with string types for display)
    print("DAG Configuration:")
    display_config = {
        "nodes": {
            "classifier": {
                "type": "classifier",
                "output_labels": ["greet"],
                "description": "Classify if input is a greeting",
                "llm_config": {
                    "provider": "openrouter",
                    "model": "google/gemma-2-9b-it",
                },
            },
            "extractor": {
                "type": "extractor",
                "param_schema": {"name": "str"},
                "description": "Extract name from greeting",
            },
            "greet_action": {
                "type": "action",
                "action": "greet",
                "description": "Greet the user",
            },
            "clarification": {
                "type": "clarification",
                "clarification_message": "I'm not sure what you'd like me to do. Please try saying hello!",
            },
        },
        "edges": [
            {"from": "classifier", "to": "extractor", "label": "greet"},
            {"from": "extractor", "to": "greet_action", "label": "success"},
            {"from": "classifier", "to": "clarification", "label": "clarification"},
        ],
        "entrypoints": ["classifier"],
    }

    print(json.dumps(display_config, indent=2))

    print("\n" + "=" * 50)
    print("Executing DAG from JSON config:")

    # Execute the DAG using the convenience method
    builder = create_dag_from_json()

    test_inputs = ["Hello, I'm Alice!", "What's the weather?", "Hi there!"]

    for user_input in test_inputs:
        print(f"\nInput: '{user_input}'")
        dag = builder.build()
        result, _ = run_dag(dag, user_input)

        if result and result.data:
            if "action_result" in result.data:
                print(f"Result: {result.data['action_result']}")
            elif "clarification_message" in result.data:
                print(f"Clarification: {result.data['clarification_message']}")
            else:
                print(f"Result: {result.data}")
        else:
            print("No result detected")
