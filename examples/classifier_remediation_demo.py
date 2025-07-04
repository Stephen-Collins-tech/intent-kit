#!/usr/bin/env python3
"""
Classifier Remediation Demo - Phase 2 Extended Remediation System

This demo showcases remediation strategies for classifiers:
- Keyword fallback when LLM classification fails
- Custom classifier fallback strategies
- Error handling and logging for classification failures

Usage:
    python examples/classifier_remediation_demo.py
"""

from intent_kit.utils.logger import Logger
from intent_kit.node.types import ExecutionResult, ExecutionError
from intent_kit.handlers.remediation import (
    RemediationStrategy,
    create_keyword_fallback_strategy,
    register_remediation_strategy
)
from intent_kit.context import IntentContext
from intent_kit.builder import handler, llm_classifier, IntentGraphBuilder
import sys
import os
from typing import Optional, Callable, List
from dotenv import load_dotenv
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load environment variables
load_dotenv()


# Configure logging
logger = Logger("classifier_remediation_demo")

# LLM config using environment variables
LLM_CONFIG = {
    "provider": "openai",
    "model": "gpt-4.1-mini",
    "api_key": os.getenv("OPENAI_API_KEY")
}


def greet_handler(name: str, context: IntentContext) -> str:
    """Simple greeting handler."""
    greeting_count = context.get("greeting_count", 0) + 1
    context.set("greeting_count", greeting_count, "greet_handler")
    return f"Hello {name}! (Greeting #{greeting_count})"


def calculate_handler(operation: str, a: float, b: float, context: IntentContext) -> str:
    """Simple calculation handler."""
    ops = {"add": "+", "plus": "+", "multiply": "*", "times": "*"}
    op = ops.get(operation.lower(), operation)
    result = eval(f"{a} {op} {b}")

    history = context.get("calc_history", [])
    history.append(f"{a} {operation} {b} = {result}")
    context.set("calc_history", history, "calculate_handler")

    return f"{a} {operation} {b} = {result}"


def weather_handler(location: str, context: IntentContext) -> str:
    """Simple weather handler."""
    weather_count = context.get("weather_count", 0) + 1
    context.set("weather_count", weather_count, "weather_handler")
    return f"Weather in {location}: 72°F, Sunny (simulated) - Request #{weather_count}"


def help_handler(context: IntentContext) -> str:
    """Help handler."""
    help_count = context.get("help_count", 0) + 1
    context.set("help_count", help_count, "help_handler")
    return f"I can help with greetings, calculations, and weather! (Help #{help_count})"


def create_failing_classifier():
    """Create a classifier that deliberately fails to trigger remediation."""

    def failing_classifier(user_input: str, children: List, context: Optional[dict] = None):
        """A classifier that always fails to demonstrate remediation."""
        logger.warning(
            "FailingClassifier: Deliberately failing to trigger remediation")
        return None  # Always return None to trigger remediation

    return failing_classifier


def create_custom_classifier_fallback() -> RemediationStrategy:
    """Create a custom classifier fallback strategy."""

    class CustomClassifierFallbackStrategy(RemediationStrategy):
        def execute(
            self,
            node_name: str,
            user_input: str,
            context: Optional[IntentContext] = None,
            original_error: Optional[ExecutionError] = None,
            classifier_func: Optional[Callable] = None,
            available_children: Optional[List] = None,
            **kwargs
        ) -> Optional[ExecutionResult]:
            """Use a simple rule-based classifier as fallback."""
            self.logger.info(
                f"CustomClassifierFallbackStrategy: Using rule-based classification for {node_name}")

            if not available_children:
                self.logger.warning(
                    f"CustomClassifierFallbackStrategy: No available children for {node_name}")
                return None

            # Simple rule-based classification
            user_input_lower = user_input.lower()

            # Define simple rules
            rules = [
                (["hello", "hi", "hey", "greet"], "greet"),
                (["calculate", "compute", "math", "add",
                 "multiply", "plus", "times"], "calculate"),
                (["weather", "temperature", "forecast"], "weather"),
                (["help", "assist", "support"], "help")
            ]

            # Find matching rule
            for keywords, intent_name in rules:
                for keyword in keywords:
                    if keyword in user_input_lower:
                        # Find the matching child
                        for child in available_children:
                            if child.name.lower() == intent_name:
                                self.logger.info(
                                    f"CustomClassifierFallbackStrategy: Matched '{child.name}' using keyword '{keyword}'")

                                # Execute the chosen child
                                child_result = child.execute(
                                    user_input, context)

                                from intent_kit.node.enums import NodeType
                                return ExecutionResult(
                                    success=True,
                                    node_name=node_name,
                                    node_path=[node_name],
                                    node_type=NodeType.CLASSIFIER,
                                    input=user_input,
                                    output=child_result.output,
                                    error=None,
                                    params={
                                        "chosen_child": child.name,
                                        "available_children": [c.name for c in available_children],
                                        "remediation_strategy": self.name,
                                        "matched_keyword": keyword
                                    },
                                    children_results=[child_result]
                                )

            self.logger.warning(
                f"CustomClassifierFallbackStrategy: No rule match found for {node_name}")
            return None

    return CustomClassifierFallbackStrategy("custom_classifier_fallback", "Custom rule-based classifier fallback")


def create_intent_graph():
    """Create and configure the intent graph with classifier remediation strategies."""

    # Create custom classifier fallback strategy
    custom_classifier_strategy = create_custom_classifier_fallback()
    register_remediation_strategy(
        "custom_classifier_fallback", custom_classifier_strategy)

    # Create handlers
    handlers = [
        handler(
            name="greet",
            description="Greet the user",
            handler_func=greet_handler,
            param_schema={"name": str},
            llm_config=LLM_CONFIG,
            context_inputs={"greeting_count"},
            context_outputs={"greeting_count"}
        ),
        handler(
            name="calculate",
            description="Perform calculations",
            handler_func=calculate_handler,
            param_schema={"operation": str, "a": float, "b": float},
            llm_config=LLM_CONFIG,
            context_inputs={"calc_history"},
            context_outputs={"calc_history"}
        ),
        handler(
            name="weather",
            description="Get weather information",
            handler_func=weather_handler,
            param_schema={"location": str},
            llm_config=LLM_CONFIG,
            context_inputs={"weather_count"},
            context_outputs={"weather_count"}
        ),
        handler(
            name="help",
            description="Provide help information",
            handler_func=help_handler,
            param_schema={},
            llm_config=LLM_CONFIG,
            context_inputs={"help_count"},
            context_outputs={"help_count"}
        )
    ]

    # Create classifier with a failing classifier to force remediation
    from intent_kit.classifiers.node import ClassifierNode

    # Use a failing classifier instead of LLM classifier to demonstrate remediation
    failing_classifier = create_failing_classifier()

    classifier = ClassifierNode(
        name="root",
        classifier=failing_classifier,
        children=handlers,
        description="Main intent classifier with remediation",
        # Try keyword first, then custom
        remediation_strategies=[
            "keyword_fallback", "custom_classifier_fallback"]
    )

    # Build and return the graph
    return IntentGraphBuilder().root(classifier).build()


def run_demo():
    """Run the classifier remediation demo."""
    print("🔄 Phase 2: Classifier Remediation System Demo")
    print("=" * 55)
    print("This demo uses a deliberately failing classifier to showcase remediation strategies.")
    print()

    # Create intent graph
    graph = create_intent_graph()

    # Create context
    context = IntentContext()

    # Test cases that will trigger classifier remediation
    test_cases = [
        "Hello there",  # Should match greet via keyword fallback
        "What's 5 plus 3?",  # Should match calculate via keyword fallback
        "How's the weather in NYC?",  # Should match weather via keyword fallback
        "Can you help me?",  # Should match help via keyword fallback
        "Hi Alice",  # Should match greet via keyword fallback
        "Calculate 10 times 5",  # Should match calculate via keyword fallback
        "Weather forecast for London",  # Should match weather via keyword fallback
        "I need assistance",  # Should match help via keyword fallback
        "Greetings",  # Should match greet via keyword fallback
        "Math: 7 plus 2",  # Should match calculate via keyword fallback
    ]

    print("\n📋 Test Cases (All should trigger remediation):")
    print("-" * 50)

    for i, test_input in enumerate(test_cases, 1):
        print(f"\n{i}. Input: {test_input}")
        print("-" * 40)

        try:
            result = graph.route(test_input, context=context)

            if result.success:
                print(f"✅ Success: {result.output}")
                if result.params and "remediation_strategy" in result.params:
                    print(
                        f"🔄 Remediation used: {result.params['remediation_strategy']}")
                    if "confidence_score" in result.params:
                        print(
                            f"📊 Confidence score: {result.params['confidence_score']:.2f}")
                    if "matched_keyword" in result.params:
                        print(
                            f"🔍 Matched keyword: {result.params['matched_keyword']}")
                    if "chosen_child" in result.params:
                        print(
                            f"🎯 Chosen child: {result.params['chosen_child']}")
            else:
                print(
                    f"❌ Failed: {result.error.message if result.error else 'Unknown error'}")

        except Exception as e:
            print(f"💥 Exception: {type(e).__name__}: {str(e)}")

    # Show context state
    print("\n📊 Final Context State:")
    print("-" * 30)
    print(f"Greeting Count: {context.get('greeting_count', 0)}")
    print(f"Calculation History: {context.get('calc_history', [])}")
    print(f"Weather Count: {context.get('weather_count', 0)}")
    print(f"Help Count: {context.get('help_count', 0)}")

    print("\n🎯 Demo Summary:")
    print("-" * 30)
    print("✅ Deliberately failing classifier: Forces remediation to activate")
    print("✅ Keyword fallback: Uses keyword matching when LLM classification fails")
    print("✅ Custom classifier fallback: Uses rule-based classification as backup")
    print("✅ Multiple strategies: Tries strategies in order until one succeeds")
    print("✅ Context preservation: All strategies maintain context state")
    print("✅ Error handling: Comprehensive logging and error reporting")
    print("✅ Confidence scoring: Provides confidence scores for keyword matches")


if __name__ == "__main__":
    run_demo()
