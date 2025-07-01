"""
Simple LLM Demo for IntentGraph

A minimal demonstration of IntentGraph using only LLM-powered classification and argument extraction.
Requires a valid LLM API key (e.g., OpenAI).
"""

import os
from intent_kit.classifiers.llm_classifier import create_llm_classifier, create_llm_arg_extractor, get_default_classification_prompt, get_default_extraction_prompt
from intent_kit.graph import IntentGraph
from intent_kit.graph.splitters import llm_splitter
from intent_kit.services.llm_factory import LLMFactory
from intent_kit.tree import TreeBuilder
from typing import Dict, Any
from dotenv import load_dotenv
from intent_kit.node import ExecutionResult
load_dotenv()

# LLM-powered classifier and arg extractor

# Set your API key here or use environment variables
LLM_CONFIG = {
    "provider": "openrouter",
    "api_key": os.getenv("OPENROUTER_API_KEY"),
    "model": "meta-llama/llama-4-maverick-17b-128e-instruct"
}

# Create LLM client for the splitter
LLM_CLIENT = LLMFactory.create_client(LLM_CONFIG)

# Define the intent tree using only LLMs


def build_llm_tree():
    # LLM classifier for top-level intent
    classifier = create_llm_classifier(
        llm_config=LLM_CONFIG,
        classification_prompt=get_default_classification_prompt(),
        node_descriptions=[
            "Greet the user",
            "Perform a calculation",
            "Get weather information",
            "Get help"
        ]
    )

    # LLM arg extractors for each intent
    greet_extractor = create_llm_arg_extractor(
        llm_config=LLM_CONFIG,
        extraction_prompt=get_default_extraction_prompt(),
        param_schema={"name": str}
    )
    calc_extractor = create_llm_arg_extractor(
        llm_config=LLM_CONFIG,
        extraction_prompt=get_default_extraction_prompt(),
        param_schema={"operation": str, "a": float, "b": float}
    )
    weather_extractor = create_llm_arg_extractor(
        llm_config=LLM_CONFIG,
        extraction_prompt=get_default_extraction_prompt(),
        param_schema={"location": str}
    )
    help_extractor = create_llm_arg_extractor(
        llm_config=LLM_CONFIG,
        extraction_prompt=get_default_extraction_prompt(),
        param_schema={}
    )

    return TreeBuilder.classifier_node(
        name="llm_classifier",
        classifier=classifier,
        children=[
            TreeBuilder.intent_node(
                name="greet",
                param_schema={"name": str},
                handler=lambda name: f"Hello {name}!",
                arg_extractor=greet_extractor,
                description="Greet the user"
            ),
            TreeBuilder.intent_node(
                name="calculate",
                param_schema={"operation": str, "a": float, "b": float},
                handler=lambda operation, a, b: f"{a} {operation} {b}",
                arg_extractor=calc_extractor,
                description="Perform a calculation"
            ),
            TreeBuilder.intent_node(
                name="weather",
                param_schema={"location": str},
                handler=lambda location: f"Weather in {location}: (simulated)",
                arg_extractor=weather_extractor,
                description="Get weather information"
            ),
            TreeBuilder.intent_node(
                name="help",
                param_schema={},
                handler=lambda: "I can help you with greetings, calculations, and weather!",
                arg_extractor=help_extractor,
                description="Get help"
            )
        ],
        description="LLM-powered intent classifier"
    )


def main():
    print("IntentGraph LLM-Only Demo")
    print("This demo uses only LLMs for intent classification and argument extraction.")
    print("You must set a valid API key in LLM_CONFIG for this to work.")
    print("\nExample inputs:")
    test_inputs = [
        "Hello, my name is Alice",
        "What's 15 plus 7?",
        "Weather in San Francisco",
        "Help me",
        "Multiply 8 and 3"
    ]

    # Create IntentGraph with LLM splitter
    graph = IntentGraph(splitter=lambda user_input, debug, llm_client=LLM_CLIENT:
                        llm_splitter(user_input, debug, llm_client))
    graph.add_root_node(build_llm_tree())

    for user_input in test_inputs:
        print(f"\nInput: {user_input}")
        try:
            result = graph.route(user_input, debug=True)
            if result.success:
                print(f"  Intent: {result.node_name}")
                print(f"  Params: {result.params}")
                print(f"  Output: {result.output}")
                # Show execution path if available
                print(f"  Execution Path:")
                for i, node_result in enumerate(result.children_results):
                    path_str = '.'.join(node_result.node_path)
                    print(
                        f"    {i+1}. {node_result.node_name} ({node_result.node_type}) - Path: {path_str}")
                    if node_result.params:
                        print(
                            f"       Params: {node_result.params}")
                    if node_result.output:
                        print(
                            f"       Output: {node_result.output}")
                    if node_result.error:
                        print(f"       Error: {node_result.error}")
            else:
                print(f"  Error: {result.error}")
        except Exception as e:
            print(f"  LLM error: {e}")


if __name__ == "__main__":
    main()
