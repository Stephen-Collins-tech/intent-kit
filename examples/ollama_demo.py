#!/usr/bin/env python3
"""
IntentKit + Ollama Demo: Showcases IntentKit's intent classification, argument extraction, context, and taxonomy features, using Ollama as the LLM backend.

This demo:
- Uses IntentKit's abstractions for all LLM-powered tasks (classification, extraction, chat)
- Demonstrates context tracking, intent routing, and argument extraction
- Does NOT use OllamaClient or the Ollama SDK directly in handlers

Prerequisites:
- Ollama running locally with at least one model pulled (e.g., 'ollama pull llama3.2')
- ollama Python package installed: 'pip install ollama'
"""

from intent_kit.node import ExecutionResult
from intent_kit.engine import execute_taxonomy
from intent_kit.taxonomy import Taxonomy
from intent_kit.tree import TreeBuilder
from intent_kit.services.llm_factory import LLMFactory
from intent_kit.classifiers.llm_classifier import create_llm_classifier, create_llm_arg_extractor, get_default_classification_prompt, get_default_extraction_prompt
from intent_kit.context import IntentContext
from intent_kit.graph import IntentGraph
import sys
import os
from datetime import datetime
from typing import Dict, Any, Optional, List

# Add the parent directory to the path so we can import intent_kit
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Ollama LLM configuration for IntentKit
OLLAMA_CONFIG = {
    "provider": "ollama",
    "model": "gemma3:27b",
    "base_url": "http://localhost:11434"
}


def simple_ollama_splitter(user_input: str, taxonomies: Dict[str, Any], debug: bool = False) -> List[Dict[str, str]]:
    if debug:
        print(f"[SimpleSplitter] Routing '{user_input}' to ollama_demo")
    return [{"taxonomy": "ollama_demo", "text": user_input}]


def greet_handler(name: str, context: IntentContext) -> str:
    greeting_count = context.get("greeting_count", 0)
    last_greeted = context.get("last_greeted", "No one")
    context.set("greeting_count", greeting_count + 1, modified_by="greet")
    context.set("last_greeted", name, modified_by="greet")
    context.set("last_greeting_time",
                datetime.now().isoformat(), modified_by="greet")
    return f"Hello {name}! (Greeting #{greeting_count + 1}, last greeted: {last_greeted})"


def calculate_handler(operation: str, a: float, b: float, context: IntentContext) -> str:
    result = None
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
            result = "Error: Division by zero"
            operation_display = "divided by"
    else:
        result = f"Error: Unknown operation '{operation}'"
        operation_display = operation
    calc_history = context.get("calculation_history", [])
    calc_history.append({
        "operation": operation_display,
        "a": a,
        "b": b,
        "result": result,
        "timestamp": datetime.now().isoformat()
    })
    context.set("calculation_history", calc_history, modified_by="calculate")
    context.set("last_calculation",
                f"{a} {operation_display} {b} = {result}", modified_by="calculate")
    return f"{a} {operation_display} {b} = {result}"


def weather_handler(location: str, context: IntentContext) -> str:
    last_weather = context.get("last_weather", {})
    if last_weather.get("location") == location:
        return f"Weather in {location}: {last_weather.get('data')} (cached)"
    weather_data = f"72°F, Sunny (simulated for {location})"
    context.set("last_weather", {
        "location": location,
        "data": weather_data,
        "timestamp": datetime.now().isoformat()
    }, modified_by="weather")
    return f"Weather in {location}: {weather_data}"


def show_calculation_history_handler(context: IntentContext) -> str:
    calc_history = context.get("calculation_history", [])
    if not calc_history:
        return "No calculations have been performed yet."
    last_calc = calc_history[-1]
    return f"Your last calculation was: {last_calc['a']} {last_calc['operation']} {last_calc['b']} = {last_calc['result']}"


def chat_demo_handler(message: str, context: IntentContext) -> str:
    # This handler just stores the message and response in context; the actual chat is handled by IntentKit's LLM-powered arg extractor
    conversation_history = context.get("conversation_history", [])
    conversation_history.append({"role": "user", "content": message})
    # The LLM arg extractor will generate the assistant's response as the output
    # We'll store the response in context after execution
    return "(The assistant's response will be generated by the LLM and shown below.)"


def help_handler(context: IntentContext) -> str:
    return """I can help you with:\n- Greetings (e.g., 'Hello, my name is Alice')\n- Calculations (e.g., 'What's 15 plus 7?')\n- Weather (e.g., 'Weather in San Francisco')\n- Chat demo (e.g., 'Chat: Tell me a story')\n- Show calculation history (e.g., 'What was my last calculation?')\n- Help (e.g., 'Help me')"""


def build_ollama_taxonomy():
    classifier = create_llm_classifier(
        llm_config=OLLAMA_CONFIG,
        classification_prompt=get_default_classification_prompt(),
        node_descriptions=[
            "Greet the user",
            "Perform a calculation",
            "Get weather information",
            "Demonstrate chat functionality",
            "Show calculation history",
            "Get help"
        ]
    )
    greet_extractor = create_llm_arg_extractor(
        llm_config=OLLAMA_CONFIG,
        extraction_prompt=get_default_extraction_prompt(),
        param_schema={"name": str}
    )
    calc_extractor = create_llm_arg_extractor(
        llm_config=OLLAMA_CONFIG,
        extraction_prompt=get_default_extraction_prompt(),
        param_schema={"operation": str, "a": float, "b": float}
    )
    weather_extractor = create_llm_arg_extractor(
        llm_config=OLLAMA_CONFIG,
        extraction_prompt=get_default_extraction_prompt(),
        param_schema={"location": str}
    )
    chat_extractor = create_llm_arg_extractor(
        llm_config=OLLAMA_CONFIG,
        extraction_prompt="You are a helpful assistant. Respond to the user's message as a friendly chatbot.",
        param_schema={"message": str}
    )
    history_extractor = create_llm_arg_extractor(
        llm_config=OLLAMA_CONFIG,
        extraction_prompt=get_default_extraction_prompt(),
        param_schema={}
    )
    help_extractor = create_llm_arg_extractor(
        llm_config=OLLAMA_CONFIG,
        extraction_prompt=get_default_extraction_prompt(),
        param_schema={}
    )
    return TreeBuilder.classifier_node(
        name="ollama_classifier",
        classifier=classifier,
        children=[
            TreeBuilder.intent_node(
                name="greet",
                param_schema={"name": str},
                handler=greet_handler,
                arg_extractor=greet_extractor,
                context_inputs={"greeting_count", "last_greeted"},
                context_outputs={"greeting_count",
                                 "last_greeted", "last_greeting_time"},
                description="Greet the user with context tracking"
            ),
            TreeBuilder.intent_node(
                name="calculate",
                param_schema={"operation": str, "a": float, "b": float},
                handler=calculate_handler,
                arg_extractor=calc_extractor,
                context_inputs={"calculation_history"},
                context_outputs={"calculation_history", "last_calculation"},
                description="Perform calculations with history tracking"
            ),
            TreeBuilder.intent_node(
                name="weather",
                param_schema={"location": str},
                handler=weather_handler,
                arg_extractor=weather_extractor,
                context_inputs={"last_weather"},
                context_outputs={"last_weather"},
                description="Get weather with caching"
            ),
            TreeBuilder.intent_node(
                name="chat_demo",
                param_schema={"message": str},
                handler=chat_demo_handler,
                arg_extractor=chat_extractor,
                context_inputs={"conversation_history"},
                context_outputs={"conversation_history", "last_chat_time"},
                description="Demonstrate chat functionality"
            ),
            TreeBuilder.intent_node(
                name="show_history",
                param_schema={},
                handler=show_calculation_history_handler,
                arg_extractor=history_extractor,
                context_inputs={"calculation_history"},
                description="Show calculation history from context"
            ),
            TreeBuilder.intent_node(
                name="help",
                param_schema={},
                handler=help_handler,
                arg_extractor=help_extractor,
                description="Get help"
            )
        ],
        description="Ollama-powered intent classifier with context support"
    )


class OllamaTaxonomy(Taxonomy):
    def __init__(self):
        self.root = build_ollama_taxonomy()

    def route(self, user_input: str, context: Optional[IntentContext] = None, debug: bool = False) -> ExecutionResult:
        return self.root.execute(user_input, context)


def main():
    print("IntentKit + Ollama Demo (IntentKit features, Ollama as LLM backend)")
    print("This demo shows how to use IntentKit's taxonomy, context, and LLM-powered classification/extraction with Ollama.")
    print("Make sure Ollama is running locally with at least one model pulled.")
    print("\n" + "="*50)
    try:
        from ollama import Client
        print("✓ ollama package is available")
    except ImportError:
        print("✗ ollama package not available. Install with: pip install ollama")
        return
    context = IntentContext(session_id="ollama_demo_user_123", debug=True)
    graph = IntentGraph(splitter=simple_ollama_splitter, visualize=True)
    graph.register_taxonomy("ollama_demo", OllamaTaxonomy())
    test_sequence = [
        "Hello, my name is Alice",
        "What's 15 plus 7?",
        "Weather in San Francisco",
        "Chat: Tell me a story about a robot",
        "What was my last calculation?",
        "Help me"
    ]
    for i, user_input in enumerate(test_sequence, 1):
        print(f"\n--- Step {i} ---")
        print(f"Input: {user_input}")
        try:
            result = graph.route(user_input, context=context, debug=True)
            if result.success:
                print(f"  Intent: {result.node_name}")
                print(f"  Params: {result.params}")
                # For chat_demo, show the assistant's response if present
                if result.node_name == "chat_demo" and hasattr(result, "output") and isinstance(result.output, dict) and "assistant_response" in result.output:
                    print(f"  Output: {result.output['assistant_response']}")
                else:
                    print(f"  Output: {result.output}")
                if result.children_results:
                    print(f"  Execution Path:")
                    for i, child_result in enumerate(result.children_results):
                        path_str = '.'.join(child_result.node_path)
                        print(
                            f"    {i+1}. {child_result.node_name} ({child_result.node_type}) - Path: {path_str}")
                        if child_result.params:
                            print(f"       Params: {child_result.params}")
                        if child_result.output:
                            print(f"       Output: {child_result.output}")
                        if child_result.error:
                            print(f"       Error: {child_result.error}")
                print(f"  Context state:")
                print(
                    f"    Greeting count: {context.get('greeting_count', 0)}")
                print(
                    f"    Last greeted: {context.get('last_greeted', 'None')}")
                print(
                    f"    Calc history: {len(context.get('calculation_history', []))} entries")
                print(
                    f"    Last weather: {context.get('last_weather', {}).get('location', 'None')}")
                print(
                    f"    Chat messages: {len(context.get('conversation_history', []))}")
            else:
                print(f"  Error: {result.error}")
        except Exception as e:
            print(f"  Error: {e}")
    print(f"\n--- Final Context State ---")
    print(f"Session ID: {context.session_id}")
    print(f"Total fields: {len(context.keys())}")
    print(f"History entries: {len(context.get_history())}")
    print(f"Error count: {context.error_count()}")
    print(f"\n--- Context History (last 5 entries) ---")
    for entry in context.get_history(limit=5):
        print(f"  {entry.timestamp}: {entry.action} '{entry.key}' = {entry.value}")
    errors = context.get_errors(limit=3)
    if errors:
        print(f"\n--- Recent Errors (last 3) ---")
        for error in errors:
            print(
                f"  [{error.timestamp.strftime('%H:%M:%S')}] {error.node_name} in {error.taxonomy_name}")
            print(f"    Input: {error.user_input}")
            print(f"    Error: {error.error_message}")
            if error.params:
                print(f"    Params: {error.params}")
            print()


if __name__ == "__main__":
    main()
