"""
Simple Intent Kit Demo - Programmatic DAG Example

A minimal example showing basic DAG building and execution using the programmatic API.
"""

import os
from dotenv import load_dotenv
from intent_kit import DAGBuilder, run_dag

load_dotenv()


def greet(name: str) -> str:
    return f"Hello {name}!"


def create_simple_dag():
    """Create a minimal DAG with classifier, extractor, action, and clarification."""
    builder = DAGBuilder()

    # Add classifier node
    builder.add_node(
        "classifier",
        "classifier",
        output_labels=["greet"],
        description="Classify if input is a greeting",
        llm_config={
            "provider": "openrouter",
            "api_key": os.getenv("OPENROUTER_API_KEY"),
            "model": "google/gemma-2-9b-it",
        },
    )

    # Add extractor node
    builder.add_node(
        "extractor",
        "extractor",
        param_schema={"name": str},
        description="Extract name from greeting",
        llm_config={
            "provider": "openrouter",
            "api_key": os.getenv("OPENROUTER_API_KEY"),
            "model": "google/gemma-2-9b-it",
        },
        output_key="extracted_params",
    )

    # Add action node
    builder.add_node(
        "greet_action", "action", action=greet, description="Greet the user"
    )

    # Add clarification node
    builder.add_node(
        "clarification",
        "clarification",
        clarification_message="I'm not sure what you'd like me to do. Please try saying hello!",
        available_options=["Say hello to someone"],
        description="Ask for clarification when intent is unclear",
    )

    # Connect nodes
    builder.add_edge("classifier", "extractor", "greet")
    builder.add_edge("extractor", "greet_action", "success")
    builder.add_edge("classifier", "clarification", "clarification")
    builder.set_entrypoints(["classifier"])
    return builder


if __name__ == "__main__":
    print("=== Simple DAG Demo ===\n")

    builder = create_simple_dag()

    test_inputs = ["Hello, I'm Alice!", "What's the weather?", "Hi there!"]

    for user_input in test_inputs:
        print(f"\nInput: '{user_input}'")
        dag = builder.build()
        result, ctx = run_dag(dag, user_input)

        if result and result.data:
            if "action_result" in result.data:
                print(f"Result: {result.data['action_result']}")
            elif "clarification_message" in result.data:
                print(f"Clarification: {result.data['clarification_message']}")
            else:
                print(f"Result: {result.data}")
        if ctx:
            print(ctx.snapshot())
        else:
            print("No result detected")
