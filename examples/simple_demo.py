"""
Simple Intent Kit Demo - Programmatic DAG Example

A minimal example showing basic DAG building and execution using the programmatic API.
"""

import os
from dotenv import load_dotenv
from intent_kit.core import DAGBuilder, run_dag
from intent_kit.core.traversal import resolve_impl_direct
from intent_kit.context import Context
from intent_kit.services.ai.llm_service import LLMService

load_dotenv()


def greet(name: str) -> str:
    return f"Hello {name}!"


def create_simple_dag():
    """Create a minimal DAG with classifier, extractor, action, and clarification."""
    builder = DAGBuilder()

    # Add classifier node
    builder.add_node("classifier", "dag_classifier",
                     output_labels=["greet"],
                     description="Classify if input is a greeting",
                     llm_config={
                         "provider": "openrouter",
                         "api_key": os.getenv("OPENROUTER_API_KEY"),
                         "model": "google/gemma-2-9b-it"
                     })

    # Add extractor node
    builder.add_node("extractor", "dag_extractor",
                     param_schema={"name": str},
                     description="Extract name from greeting",
                     llm_config={
                         "provider": "openrouter",
                         "api_key": os.getenv("OPENROUTER_API_KEY"),
                         "model": "google/gemma-2-9b-it"
                     },
                     output_key="extracted_params")

    # Add action node
    builder.add_node("greet_action", "dag_action",
                     action=greet,
                     description="Greet the user")

    # Add clarification node
    builder.add_node("clarification", "dag_clarification",
                     clarification_message="I'm not sure what you'd like me to do. Please try saying hello!",
                     available_options=["Say hello to someone"],
                     description="Ask for clarification when intent is unclear")

    # Connect nodes
    builder.add_edge("classifier", "extractor", "greet")
    builder.add_edge("extractor", "greet_action", "success")
    builder.add_edge("classifier", "clarification", "clarification")
    builder.set_entrypoints(["classifier"])
    return builder


if __name__ == "__main__":
    print("=== Simple DAG Demo ===\n")

    builder = create_simple_dag()
    llm_service = LLMService()

    test_inputs = ["Hello, I'm Alice!", "What's the weather?", "Hi there!"]

    for user_input in test_inputs:
        print(f"\nInput: '{user_input}'")
        ctx = Context()
        dag = builder.build()
        result, _ = run_dag(
            dag, ctx, user_input, resolve_impl=resolve_impl_direct, llm_service=llm_service)

        if result and result.data:
            if "action_result" in result.data:
                print(f"Result: {result.data['action_result']}")
            elif "clarification_message" in result.data:
                print(f"Clarification: {result.data['clarification_message']}")
            else:
                print(f"Result: {result.data}")
        else:
            print("No result detected")
