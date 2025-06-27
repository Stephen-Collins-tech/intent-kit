"""
Context Demo for IntentKit

A demonstration of the new IntentContext system showing how state can be shared
between different steps of a workflow and across multiple user interactions.
"""

import os
from datetime import datetime
from typing import Dict, Any, Optional, List
from intent_kit.context import IntentContext
from intent_kit.classifiers.llm_classifier import create_llm_classifier, create_llm_arg_extractor, get_default_classification_prompt, get_default_extraction_prompt
from intent_kit.graph import IntentGraph
from intent_kit.graph.splitters import rule_splitter
from intent_kit.services.llm_factory import LLMFactory
from intent_kit.tree import TreeBuilder
from intent_kit.taxonomy import Taxonomy
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


def simple_context_splitter(user_input: str, taxonomies: Dict[str, Any], debug: bool = False) -> List[Dict[str, str]]:
    """
    Simple splitter that always routes to the context_demo taxonomy.
    This is needed because rule_splitter tries to match against taxonomy names.
    """
    if debug:
        print(f"[SimpleSplitter] Routing '{user_input}' to context_demo")

    return [{"taxonomy": "context_demo", "text": user_input}]


def greet_handler(name: str, context: IntentContext) -> str:
    """Greet handler with context tracking."""
    # Read from context
    greeting_count = context.get("greeting_count", 0)
    last_greeted = context.get("last_greeted", "No one")

    # Update context
    context.set("greeting_count", greeting_count + 1, modified_by="greet")
    context.set("last_greeted", name, modified_by="greet")
    context.set("last_greeting_time",
                datetime.now().isoformat(), modified_by="greet")

    return f"Hello {name}! (Greeting #{greeting_count + 1}, last greeted: {last_greeted})"


def calculate_handler(operation: str, a: float, b: float, context: IntentContext) -> str:
    """Calculate handler with history tracking."""
    result = None
    if operation == "add":
        result = a + b
    elif operation == "subtract":
        result = a - b
    elif operation == "multiply":
        result = a * b
    elif operation == "divide":
        result = a / b if b != 0 else "Error: Division by zero"

    # Store calculation history in context
    calc_history = context.get("calculation_history", [])
    calc_history.append({
        "operation": operation,
        "a": a,
        "b": b,
        "result": result,
        "timestamp": datetime.now().isoformat()
    })
    context.set("calculation_history", calc_history, modified_by="calculate")
    context.set("last_calculation",
                f"{a} {operation} {b} = {result}", modified_by="calculate")

    return f"{a} {operation} {b} = {result}"


def weather_handler(location: str, context: IntentContext) -> str:
    """Weather handler with caching."""
    # Check if we've already fetched weather for this location recently
    last_weather = context.get("last_weather", {})
    if last_weather.get("location") == location:
        time_diff = datetime.now().isoformat()
        return f"Weather in {location}: {last_weather.get('data')} (cached)"

    # Simulate weather data
    weather_data = f"72°F, Sunny (simulated for {location})"

    # Store in context
    context.set("last_weather", {
        "location": location,
        "data": weather_data,
        "timestamp": datetime.now().isoformat()
    }, modified_by="weather")

    return f"Weather in {location}: {weather_data}"


def build_context_aware_taxonomy():
    """Build a taxonomy with context-aware handlers."""
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
                name="help",
                param_schema={},
                handler=lambda context: "I can help you with greetings, calculations, and weather!",
                arg_extractor=help_extractor,
                description="Get help"
            )
        ],
        description="LLM-powered intent classifier with context support"
    )


class ContextAwareTaxonomy(Taxonomy):
    def __init__(self):
        self.root = build_context_aware_taxonomy()

    def route(self, user_input: str, context: Optional[IntentContext] = None, debug: bool = False) -> Dict[str, Any]:
        if debug:
            print(f"[ContextAware] Processing: {user_input}")
            if context:
                print(f"[ContextAware] Context state: {context}")

        result = self.root.execute(user_input, context)
        if result["success"]:
            return {
                "intent": self.root.name,
                "node_name": self.root.name,
                "params": result["params"],
                "output": result["output"],
                "error": None
            }
        else:
            return {
                "intent": None,
                "node_name": None,
                "params": result["params"],
                "output": None,
                "error": result["error"]
            }


def main():
    print("IntentKit Context Demo")
    print("This demo shows how context can be shared between workflow steps.")
    print("You must set a valid API key in LLM_CONFIG for this to work.")
    print("\n" + "="*50)

    # Create context for the session
    context = IntentContext(session_id="demo_user_123", debug=True)

    # Create IntentGraph with our simple splitter
    graph = IntentGraph(splitter=simple_context_splitter)
    graph.register_taxonomy("context_demo", ContextAwareTaxonomy())

    # Test sequence showing context persistence
    test_sequence = [
        "Hello, my name is Alice",
        "What's 15 plus 7?",
        "Weather in San Francisco",
        "Hi again",  # Should show greeting count
        "What's 8 times 3?",
        "Weather in San Francisco again",  # Should show cached result
        "What was my last calculation?"  # Should show context access
    ]

    for i, user_input in enumerate(test_sequence, 1):
        print(f"\n--- Step {i} ---")
        print(f"Input: {user_input}")

        try:
            # Route with context
            result = graph.route(user_input, context=context, debug=True)

            if result['results']:
                for res in result['results']:
                    print(f"  Intent: {res['intent']}")
                    print(f"  Params: {res['params']}")
                    print(f"  Output: {res['output']}")

                    # Show context state after execution
                    print(f"  Context state:")
                    print(
                        f"    Greeting count: {context.get('greeting_count', 0)}")
                    print(
                        f"    Last greeted: {context.get('last_greeted', 'None')}")
                    print(
                        f"    Calc history: {len(context.get('calculation_history', []))} entries")
                    print(
                        f"    Last weather: {context.get('last_weather', {}).get('location', 'None')}")
            else:
                print(f"  Error: {result['errors']}")

            # Show context errors from result
            if result.get('context_errors'):
                print(
                    f"  Context errors in result: {len(result['context_errors'])} total")
                for error in result['context_errors'][-2:]:  # Show last 2 errors
                    print(
                        f"    [{error['timestamp'][11:19]}] {error['node_name']} in {error['taxonomy_name']}: {error['error_message']}")

            # Show any errors from context (for backward compatibility)
            errors = context.get_errors()
            if errors:
                print(f"  Context errors: {len(errors)} total")
                for error in errors[-2:]:  # Show last 2 errors
                    print(
                        f"    [{error.timestamp.strftime('%H:%M:%S')}] {error.node_name} in {error.taxonomy_name}: {error.error_message}")

        except Exception as e:
            print(f"  Error: {e}")

    # Show final context state
    print(f"\n--- Final Context State ---")
    print(f"Session ID: {context.session_id}")
    print(f"Total fields: {len(context.keys())}")
    print(f"History entries: {len(context.get_history())}")
    print(f"Error count: {context.error_count()}")

    # Show some context history
    print(f"\n--- Context History (last 5 entries) ---")
    for entry in context.get_history(limit=5):
        print(f"  {entry.timestamp}: {entry.action} '{entry.key}' = {entry.value}")

    # Show recent errors if any
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
