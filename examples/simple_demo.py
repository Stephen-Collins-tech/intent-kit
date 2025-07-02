"""
Simple LLM Demo for IntentGraph

A minimal demonstration of IntentGraph using only LLM-powered classification and argument extraction.
Requires a valid LLM API key (e.g., OpenAI).
"""

import os
from intent_kit.classifiers.llm_classifier import create_llm_classifier, create_llm_arg_extractor, get_default_classification_prompt, get_default_extraction_prompt
from intent_kit.graph import IntentGraph
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
            TreeBuilder.handler_node(
                name="greet",
                param_schema={"name": str},
                handler=lambda name: f"Hello {name}!",
                arg_extractor=greet_extractor,
                description="Greet the user"
            ),
            TreeBuilder.handler_node(
                name="calculate",
                param_schema={"operation": str, "a": float, "b": float},
                handler=lambda operation, a, b: f"{a} {operation} {b}",
                arg_extractor=calc_extractor,
                description="Perform a calculation"
            ),
            TreeBuilder.handler_node(
                name="weather",
                param_schema={"location": str},
                handler=lambda location: f"Weather in {location}: (simulated)",
                arg_extractor=weather_extractor,
                description="Get weather information"
            ),
            TreeBuilder.handler_node(
                name="help",
                param_schema={},
                handler=lambda: "I can help you with greetings, calculations, and weather!",
                arg_extractor=help_extractor,
                description="Get help"
            )
        ],
        description="LLM-powered intent classifier"
    )


def build_llm_splitter_tree():
    """Build a tree using LLM-powered SplitterNode."""
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

    # Create intent nodes
    greet_node = TreeBuilder.handler_node(
        name="greet",
        param_schema={"name": str},
        handler=lambda name: f"Hello {name}!",
        arg_extractor=greet_extractor,
        description="Greet the user"
    )
    calc_node = TreeBuilder.handler_node(
        name="calculate",
        param_schema={"operation": str, "a": float, "b": float},
        handler=lambda operation, a, b: f"{a} {operation} {b}",
        arg_extractor=calc_extractor,
        description="Perform a calculation"
    )
    weather_node = TreeBuilder.handler_node(
        name="weather",
        param_schema={"location": str},
        handler=lambda location: f"Weather in {location}: (simulated)",
        arg_extractor=weather_extractor,
        description="Get weather information"
    )
    help_node = TreeBuilder.handler_node(
        name="help",
        param_schema={},
        handler=lambda: "I can help you with greetings, calculations, and weather!",
        arg_extractor=help_extractor,
        description="Get help"
    )

    # Create a classifier node for the splitter's children
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
    classifier_node = TreeBuilder.classifier_node(
        name="splitter_classifier",
        classifier=classifier,
        children=[greet_node, calc_node, weather_node, help_node],
        description="Classifier for splitter children"
    )

    # Create LLM-powered splitter node (children = classifier node)
    return TreeBuilder.llm_splitter_node(
        name="llm_splitter",
        children=[classifier_node],
        llm_config={"llm_client": LLM_CLIENT},
        description="Split multi-intent inputs using AI-powered analysis"
    )


def build_rule_splitter_tree():
    """Build a tree using rule-based SplitterNode for multi-intent handling."""
    # Simple handlers
    def greet_handler(name: str) -> str:
        return f"Hello {name}!"

    def calc_handler(operation: str, a: float, b: float) -> str:
        if operation.lower() in ["add", "plus", "+"]:
            return f"{a} + {b} = {a + b}"
        elif operation.lower() in ["multiply", "times", "*"]:
            return f"{a} * {b} = {a * b}"
        else:
            return f"Unknown operation: {operation}"

    def weather_handler(location: str) -> str:
        return f"Weather in {location}: 72°F, Sunny (simulated)"

    def help_handler() -> str:
        return "I can help with greetings, calculations, and weather!"
    # Create intent nodes
    greet_node = TreeBuilder.handler_node(
        name="greet",
        param_schema={"name": str},
        handler=greet_handler,
        arg_extractor=lambda text, context: {
            "name": text.split()[-1] if text.split() else "User"},
        description="Greet the user"
    )
    calc_node = TreeBuilder.handler_node(
        name="calculate",
        param_schema={"operation": str, "a": float, "b": float},
        handler=calc_handler,
        arg_extractor=lambda text, context: {
            "operation": "add" if "add" in text.lower() or "plus" in text.lower() else "multiply",
            "a": 10.0,
            "b": 5.0
        },
        description="Perform calculations"
    )
    weather_node = TreeBuilder.handler_node(
        name="weather",
        param_schema={"location": str},
        handler=weather_handler,
        arg_extractor=lambda text, context: {
            "location": text.split()[-1] if text.split() else "Unknown"},
        description="Get weather information"
    )
    help_node = TreeBuilder.handler_node(
        name="help",
        param_schema={},
        handler=help_handler,
        arg_extractor=lambda text, context: {},
        description="Get help"
    )
    # Create a simple classifier node for the splitter's children
    classifier_node = TreeBuilder.classifier_node(
        name="splitter_classifier",
        classifier=lambda text, children, context: children[0] if "greet" in text.lower() else (
            children[1] if "calc" in text.lower() or "plus" in text.lower() or "multiply" in text.lower() else (
                children[2] if "weather" in text.lower() else children[3]
            )
        ),
        children=[greet_node, calc_node, weather_node, help_node],
        description="Classifier for splitter children"
    )
    # Create splitter node (children = classifier node)
    return TreeBuilder.rule_splitter_node(
        name="multi_intent_splitter",
        children=[classifier_node],
        description="Split multi-intent inputs using rule-based logic"
    )


def demo_llm_classifier():
    """Demo using traditional LLM classification."""
    print("\n" + "="*60)
    print("LLM CLASSIFIER DEMO")
    print("="*60)

    # Create IntentGraph with traditional classifier
    graph = IntentGraph()
    graph.add_root_node(build_llm_tree())

    test_inputs = [
        "Hello, my name is Alice",
        "What's 15 plus 7?",
        "Weather in San Francisco",
        "Help me",
        "Multiply 8 and 3"
    ]

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
                        print(f"       Error: {result.error}")
            else:
                print(f"  Error: {result.error}")
        except Exception as e:
            print(f"  LLM error: {e}")


def demo_llm_splitter():
    """Demo using LLM-powered SplitterNode."""
    print("\n" + "="*60)
    print("LLM SPLITTER NODE DEMO")
    print("="*60)

    # Create IntentGraph with LLM-powered splitter
    graph = IntentGraph()
    graph.add_root_node(build_llm_splitter_tree())

    # Test multi-intent inputs
    test_inputs = [
        "Hello Alice and what's the weather in San Francisco",
        "Calculate 5 plus 3 and also greet Bob",
        "Help me and get weather for New York",
        "Greet John, calculate 10 times 2, and weather in London"
    ]

    for user_input in test_inputs:
        print(f"\nInput: {user_input}")
        try:
            result = graph.route(user_input, debug=True)
            if result.success:
                print(f"  Success: {result.success}")
                print(f"  Node Type: {result.node_type}")
                print(f"  Output: {result.output}")
                print(f"  Params: {result.params}")

                if result.children_results:
                    print("  Child Results:")
                    for i, child_result in enumerate(result.children_results):
                        print(
                            f"    {i+1}. {child_result.node_name} ({child_result.node_type})")
                        print(f"       Input: {child_result.input}")
                        print(f"       Output: {child_result.output}")
                        if child_result.error:
                            print(
                                f"       Error: {child_result.error.message}")
            else:
                print(f"  Error: {result.error}")
        except Exception as e:
            print(f"  Error: {e}")


def demo_rule_splitter():
    """Demo using rule-based SplitterNode for multi-intent handling."""
    print("\n" + "="*60)
    print("RULE-BASED SPLITTER NODE DEMO")
    print("="*60)

    # Create IntentGraph with rule-based splitter
    graph = IntentGraph()
    graph.add_root_node(build_rule_splitter_tree())

    # Test multi-intent inputs
    test_inputs = [
        "Hello Alice and what's the weather in San Francisco",
        "Calculate 5 plus 3 and also greet Bob",
        "Help me and get weather for New York",
        "Greet John, calculate 10 times 2, and weather in London"
    ]

    for user_input in test_inputs:
        print(f"\nInput: {user_input}")
        try:
            result = graph.route(user_input, debug=True)
            if result.success:
                print(f"  Success: {result.success}")
                print(f"  Node Type: {result.node_type}")
                print(f"  Output: {result.output}")
                print(f"  Params: {result.params}")

                if result.children_results:
                    print("  Child Results:")
                    for i, child_result in enumerate(result.children_results):
                        print(
                            f"    {i+1}. {child_result.node_name} ({child_result.node_type})")
                        print(f"       Input: {child_result.input}")
                        print(f"       Output: {child_result.output}")
                        if child_result.error:
                            print(
                                f"       Error: {child_result.error.message}")
            else:
                print(f"  Error: {result.error}")
        except Exception as e:
            print(f"  Error: {e}")


def main():
    print("IntentGraph Demo - Three Approaches")
    print("This demo shows three different approaches to intent handling:")
    print("1. Traditional LLM classification (single intent)")
    print("2. LLM-powered SplitterNode (multi-intent)")
    print("3. Rule-based SplitterNode (multi-intent)")
    print("You must set a valid API key in LLM_CONFIG for LLM features to work.")

    # Demo traditional LLM classifier approach
    if LLM_CLIENT:
        demo_llm_classifier()
    else:
        print("\nLLM classifier demo skipped - no API key available")

    # Demo LLM-powered SplitterNode approach
    if LLM_CLIENT:
        demo_llm_splitter()
    else:
        print("\nLLM splitter demo skipped - no API key available")

    # Demo rule-based SplitterNode approach
    demo_rule_splitter()


if __name__ == "__main__":
    main()
