"""
SplitterNode Demo for IntentKit

A demonstration of the new SplitterNode functionality showing how to split
multi-intent user inputs and route them to appropriate handlers.
"""

import os
from typing import Dict, Any
from intent_kit.classifiers.llm_classifier import create_llm_classifier, create_llm_arg_extractor, get_default_classification_prompt, get_default_extraction_prompt
from intent_kit.graph import IntentGraph
from intent_kit.splitters import rule_splitter
from intent_kit.services.llm_factory import LLMFactory
from intent_kit.tree import TreeBuilder
from intent_kit.node import ExecutionResult
from dotenv import load_dotenv

load_dotenv()

# LLM configuration
LLM_CONFIG = {
    "provider": "openrouter",
    "api_key": os.getenv("OPENROUTER_API_KEY"),
    "model": "meta-llama/llama-4-maverick-17b-128e-instruct"
}

# Create LLM client
LLM_CLIENT = LLMFactory.create_client(LLM_CONFIG)


def greet_handler(name: str) -> str:
    """Simple greet handler."""
    return f"Hello {name}! Nice to meet you."


def calculate_handler(operation: str, a: float, b: float) -> str:
    """Simple calculation handler."""
    operation_lower = operation.lower()
    if operation_lower in ["add", "plus", "addition", "+"]:
        result = a + b
        operation_display = "plus"
    elif operation_lower in ["subtract", "minus", "subtraction", "-"]:
        result = a - b
        operation_display = "minus"
    elif operation_lower in ["multiply", "times", "multiplication", "*"]:
        result = a * b
        operation_display = "times"
    elif operation_lower in ["divide", "division", "/"]:
        if b != 0:
            result = a / b
            operation_display = "divided by"
        else:
            return "Error: Division by zero"
    else:
        return f"Error: Unknown operation '{operation}'"

    return f"{a} {operation_display} {b} = {result}"


def weather_handler(location: str) -> str:
    """Simple weather handler."""
    return f"Weather in {location}: 72°F, Sunny (simulated)"


def help_handler() -> str:
    """Simple help handler."""
    return "I can help you with greetings, calculations, and weather information!"


def build_rule_splitter_tree():
    """Build a tree using rule-based splitting."""
    print("Building rule-based splitter tree...")

    # Create individual intent nodes
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
        handler=calculate_handler,
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
    # Create rule-based splitter node (children = classifier node)
    splitter_node = TreeBuilder.rule_splitter_node(
        name="rule_splitter",
        children=[classifier_node],
        description="Split multi-intent inputs using rule-based logic"
    )
    return splitter_node


def build_llm_splitter_tree():
    """Build a tree using LLM-powered splitting."""
    print("Building LLM-powered splitter tree...")
    # Create individual intent nodes with LLM extractors
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
    greet_node = TreeBuilder.handler_node(
        name="greet",
        param_schema={"name": str},
        handler=greet_handler,
        arg_extractor=greet_extractor,
        description="Greet the user"
    )
    calc_node = TreeBuilder.handler_node(
        name="calculate",
        param_schema={"operation": str, "a": float, "b": float},
        handler=calculate_handler,
        arg_extractor=calc_extractor,
        description="Perform calculations"
    )
    weather_node = TreeBuilder.handler_node(
        name="weather",
        param_schema={"location": str},
        handler=weather_handler,
        arg_extractor=weather_extractor,
        description="Get weather information"
    )
    help_node = TreeBuilder.handler_node(
        name="help",
        param_schema={},
        handler=help_handler,
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
    splitter_node = TreeBuilder.llm_splitter_node(
        name="llm_splitter",
        children=[classifier_node],
        llm_config={"llm_client": LLM_CLIENT},
        description="Split multi-intent inputs using AI-powered analysis"
    )
    return splitter_node


def demo_rule_splitter():
    """Demonstrate rule-based splitting."""
    print("\n" + "="*60)
    print("RULE-BASED SPLITTER DEMO")
    print("="*60)

    # Create graph with rule-based splitter
    graph = IntentGraph()
    graph.add_root_node(build_rule_splitter_tree())

    # Test inputs that should be split
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
            print(f"Success: {result.success}")
            print(f"Node Type: {result.node_type}")
            print(f"Output: {result.output}")
            print(f"Params: {result.params}")

            if result.children_results:
                print("Child Results:")
                for i, child_result in enumerate(result.children_results):
                    print(
                        f"  {i+1}. {child_result.node_name} ({child_result.node_type})")
                    print(f"     Input: {child_result.input}")
                    print(f"     Output: {child_result.output}")
                    if child_result.error:
                        print(f"     Error: {child_result.error.message}")
        except Exception as e:
            print(f"Error: {e}")


def demo_llm_splitter():
    """Demonstrate LLM-powered splitting."""
    print("\n" + "="*60)
    print("LLM-POWERED SPLITTER DEMO")
    print("="*60)

    # Create graph with LLM-powered splitter
    graph = IntentGraph()
    graph.add_root_node(build_llm_splitter_tree())

    # Test inputs that should be split
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
            print(f"Success: {result.success}")
            print(f"Node Type: {result.node_type}")
            print(f"Output: {result.output}")
            print(f"Params: {result.params}")

            if result.children_results:
                print("Child Results:")
                for i, child_result in enumerate(result.children_results):
                    print(
                        f"  {i+1}. {child_result.node_name} ({child_result.node_type})")
                    print(f"     Input: {child_result.input}")
                    print(f"     Output: {child_result.output}")
                    if child_result.error:
                        print(f"     Error: {child_result.error.message}")
        except Exception as e:
            print(f"Error: {e}")


def main():
    """Main demo function."""
    print("IntentKit SplitterNode Demo")
    print("This demo showcases the new SplitterNode functionality.")
    print("It demonstrates both rule-based and LLM-powered splitting of multi-intent inputs.")

    # Demo rule-based splitting
    demo_rule_splitter()

    # Demo LLM-powered splitting (if LLM is available)
    if LLM_CLIENT:
        demo_llm_splitter()
    else:
        print("\n" + "="*60)
        print("LLM-POWERED SPLITTER DEMO SKIPPED")
        print("="*60)
        print("No LLM client available. Set OPENROUTER_API_KEY environment variable to enable LLM splitting.")


if __name__ == "__main__":
    main()
