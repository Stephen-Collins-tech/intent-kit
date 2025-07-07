#!/usr/bin/env python3
"""
Remediation Demo - Phase 2 Basic Remediation System

This demo showcases the new remediation system with:
- Retry strategies for transient failures
- Fallback strategies for permanent failures
- Custom remediation strategies
- Error handling and logging

Usage:
    python examples/remediation_demo.py
"""

from intent_kit.utils.logger import Logger
from intent_kit.handlers.remediation import (
    RemediationStrategy,
    register_remediation_strategy
)
from intent_kit.node.types import ExecutionResult, ExecutionError
from intent_kit.context import IntentContext
from intent_kit.builder import handler, llm_classifier, IntentGraphBuilder
import sys
import os
from typing import Optional
from dotenv import load_dotenv
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load environment variables
load_dotenv()


# Configure logging
logger = Logger("remediation_demo")

# LLM config using environment variables
LLM_CONFIG = {
    "provider": "openai",
    "model": "gpt-4.1-mini",
    "api_key": os.getenv("OPENAI_API_KEY")
}


def unreliable_calculator(operation: str, a: float, b: float, context: IntentContext) -> str:
    """
    A deliberately unreliable calculator that fails randomly to demonstrate remediation.
    """
    import random

    # Simulate random failures (30% failure rate)
    if random.random() < 0.3:
        raise Exception(
            "Random calculation failure - this is expected for demo purposes")

    ops = {"add": "+", "plus": "+", "multiply": "*", "times": "*"}
    op = ops.get(operation.lower(), operation)
    result = eval(f"{a} {op} {b}")

    history = context.get("calc_history", [])
    history.append(f"{a} {operation} {b} = {result}")
    context.set("calc_history", history, "unreliable_calculator")

    return f"{a} {operation} {b} = {result}"


def reliable_calculator(operation: str, a: float, b: float, context: IntentContext) -> str:
    """
    A reliable fallback calculator that always works.
    """
    ops = {"add": "+", "plus": "+", "multiply": "*", "times": "*"}
    op = ops.get(operation.lower(), operation)
    result = eval(f"{a} {op} {b}")

    history = context.get("calc_history", [])
    history.append(f"{a} {operation} {b} = {result} (fallback)")
    context.set("calc_history", history, "reliable_calculator")

    return f"FALLBACK: {a} {operation} {b} = {result}"


def simple_greeter(name: str, context: IntentContext) -> str:
    """Simple greeting handler."""
    greeting_count = context.get("greeting_count", 0) + 1
    context.set("greeting_count", greeting_count, "simple_greeter")
    return f"Hello {name}! (Greeting #{greeting_count})"


def create_custom_remediation_strategy() -> RemediationStrategy:
    """Create a custom remediation strategy that logs and continues."""

    class LogAndContinueStrategy(RemediationStrategy):
        def execute(
            self,
            node_name: str,
            user_input: str,
            context: Optional[IntentContext] = None,
            original_error: Optional[ExecutionError] = None,
            **kwargs
        ) -> Optional[ExecutionResult]:
            """Log the error and return a simple message."""
            self.logger.info(
                f"LogAndContinueStrategy: Handling error for {node_name}")

            from intent_kit.node.types import ExecutionResult
            from intent_kit.node.enums import NodeType

            return ExecutionResult(
                success=True,
                node_name=node_name,
                node_path=[node_name],
                node_type=NodeType.HANDLER,
                input=user_input,
                output=f"Operation completed with warnings (original error: {original_error.message if original_error else 'unknown'})",
                error=None,
                params=kwargs.get('validated_params', {}),
                children_results=[]
            )

    return LogAndContinueStrategy("log_and_continue", "Log error and continue with warning")


def create_intent_graph():
    """Create and configure the intent graph with remediation strategies."""

    # Create custom remediation strategy
    custom_strategy = create_custom_remediation_strategy()
    register_remediation_strategy("log_and_continue", custom_strategy)

    # Create handlers with different remediation strategies
    handlers = [
        # Handler with retry strategy
        handler(
            name="unreliable_calc",
            description="Unreliable calculator with retry strategy",
            handler_func=unreliable_calculator,
            param_schema={"operation": str, "a": float, "b": float},
            llm_config=LLM_CONFIG,
            context_inputs={"calc_history"},
            context_outputs={"calc_history"},
            remediation_strategies=["retry_on_fail"]  # Built-in retry strategy
        ),

        # Handler with fallback strategy
        handler(
            name="reliable_calc",
            description="Reliable calculator as fallback",
            handler_func=reliable_calculator,
            param_schema={"operation": str, "a": float, "b": float},
            llm_config=LLM_CONFIG,
            context_inputs={"calc_history"},
            context_outputs={"calc_history"},
            # Built-in fallback strategy
            remediation_strategies=["fallback_to_another_node"]
        ),

        # Handler with custom remediation strategy
        handler(
            name="simple_greet",
            description="Simple greeter with custom remediation",
            handler_func=simple_greeter,
            param_schema={"name": str},
            llm_config=LLM_CONFIG,
            context_inputs={"greeting_count"},
            context_outputs={"greeting_count"},
            remediation_strategies=["log_and_continue"]  # Custom strategy
        )
    ]

    # Create classifier
    classifier = llm_classifier(
        name="root",
        children=handlers,
        llm_config=LLM_CONFIG,
        description="Main intent classifier with remediation"
    )

    # Build and return the graph
    return IntentGraphBuilder().root(classifier).build()


def run_demo():
    """Run the remediation demo."""
    print("🔄 Phase 2: Basic Remediation System Demo")
    print("=" * 50)

    # Create intent graph
    graph = create_intent_graph()

    # Create context
    context = IntentContext()

    # Test cases
    test_cases = [
        "Calculate 5 plus 3",
        "What is 10 times 2?",
        "Hello Alice",
        "Add 7 and 4",
        "Multiply 3 by 6"
    ]

    print("\n📋 Test Cases:")
    print("-" * 30)

    for i, test_input in enumerate(test_cases, 1):
        print(f"\n{i}. Input: {test_input}")
        print("-" * 40)

        try:
            result = graph.route(test_input, context=context)

            if result.success:
                print(f"✅ Success: {result.output}")
            else:
                print(
                    f"❌ Failed: {result.error.message if result.error else 'Unknown error'}")

        except Exception as e:
            print(f"💥 Exception: {type(e).__name__}: {str(e)}")

    # Show context state
    print("\n📊 Final Context State:")
    print("-" * 30)
    print(f"Calculation History: {context.get('calc_history', [])}")
    print(f"Greeting Count: {context.get('greeting_count', 0)}")

    print("\n🎯 Demo Summary:")
    print("-" * 30)
    print("✅ Retry strategy: Automatically retries failed operations")
    print("✅ Fallback strategy: Routes to alternative handlers")
    print("✅ Custom strategy: Logs errors and continues with warnings")
    print("✅ Context preservation: All strategies maintain context state")
    print("✅ Error handling: Comprehensive logging and error reporting")


if __name__ == "__main__":
    run_demo()
