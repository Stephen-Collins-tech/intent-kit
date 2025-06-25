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

# Define the taxonomy using only LLMs


def build_llm_taxonomy():
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


class LLMTaxonomy:
    def __init__(self):
        self.root = build_llm_taxonomy()

    def route(self, user_input: str, debug: bool = False) -> Dict[str, Any]:
        if debug:
            print(f"[LLM] Processing: {user_input}")
        result = self.root.execute(user_input)
        if result["success"]:
            return {
                "intent": self.root.name,
                "params": result["params"],
                "output": result["output"],
                "error": None
            }
        else:
            return {
                "intent": None,
                "params": result["params"],
                "output": None,
                "error": result["error"]
            }


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
    graph = IntentGraph(splitter=lambda user_input, taxonomies, debug, **kwargs:
                        llm_splitter(user_input, taxonomies, debug, LLM_CLIENT))
    graph.register_taxonomy("llm", LLMTaxonomy())

    for user_input in test_inputs:
        print(f"\nInput: {user_input}")
        try:
            result = graph.route(user_input, debug=True)
            if result['results']:
                for res in result['results']:
                    print(f"  Intent: {res['intent']}")
                    print(f"  Params: {res['params']}")
                    print(f"  Output: {res['output']}")
            else:
                print(f"  Error: {result['errors']}")
        except Exception as e:
            print(f"  LLM error: {e}")


if __name__ == "__main__":
    main()
