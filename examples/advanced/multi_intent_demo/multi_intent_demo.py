#!/usr/bin/env python3
"""
Multi-Intent Demo

A demonstration showing how to handle multiple nodes in a single user input
using LLM-powered splitting.
"""

from typing import Callable, Any
import os
import json
from dotenv import load_dotenv
from intent_kit import IntentGraphBuilder
from intent_kit.context import IntentContext

load_dotenv()

LLM_CONFIG = {
    "provider": "openrouter",
    "api_key": os.getenv("OPENROUTER_API_KEY"),
    "model": "moonshotai/kimi-k2",
}


def llm_splitter(user_input: str, debug=False, llm_client=None, **kwargs):
    """LLM-powered splitter for intelligently splitting multi-intent inputs."""

    if not llm_client:
        # Fallback to simple rule-based splitting if no LLM client
        return _fallback_splitter(user_input)

    try:
        # Create LLM prompt for intelligent splitting
        prompt = _create_splitting_prompt(user_input)

        # Get LLM response with the correct model
        response = llm_client.generate(prompt, model="moonshotai/kimi-k2")

        # Parse the response to extract chunks
        chunks = _parse_splitting_response(response, user_input)

        return chunks

    except Exception as e:
        print(f"LLM splitter failed: {e}")
        # Fallback to simple splitting
        return _fallback_splitter(user_input)


def _create_splitting_prompt(user_input: str) -> str:
    """Create a prompt for LLM-based intelligent splitting."""
    return f"""Split this input into separate intents: "{user_input}"

Return ONLY a JSON array of strings. No explanations.

Examples:
- "Hello Alice, what's 15 plus 7?" → ["Hello Alice", "what's 15 plus 7"]
- "Weather in San Francisco and multiply 8 by 3" → ["Weather in San Francisco", "multiply 8 by 3"]
- "Hi Bob, help me with calculations" → ["Hi Bob, help me with calculations"]

Response:"""


def _parse_splitting_response(response: str, original_input: str) -> list:
    """Parse the LLM response to extract intent chunks."""
    try:
        import json
        import re

        # Look for the final JSON array in the response (most likely the actual answer)
        # Find all JSON arrays in the response
        json_arrays = re.findall(r"\[[^\]]*\]", response)

        if json_arrays:
            # Take the last JSON array found (most likely the final answer)
            last_json_array = json_arrays[-1]
            chunks = json.loads(last_json_array)

            if isinstance(chunks, list) and all(
                isinstance(chunk, str) for chunk in chunks
            ):
                # Remove duplicates while preserving order
                seen = set()
                unique_chunks = []
                for chunk in chunks:
                    chunk_clean = chunk.strip()
                    if chunk_clean and chunk_clean not in seen:
                        seen.add(chunk_clean)
                        unique_chunks.append(chunk_clean)

                if unique_chunks:
                    return unique_chunks

        # Fallback: try to parse the entire response as JSON
        chunks = json.loads(response)
        if isinstance(chunks, list) and all(isinstance(chunk, str) for chunk in chunks):
            return [chunk.strip() for chunk in chunks if chunk.strip()]

    except (json.JSONDecodeError, ValueError, TypeError):
        pass

    # If JSON parsing fails, try manual parsing
    return _manual_parse_splitting(response, original_input)


def _manual_parse_splitting(response: str, original_input: str) -> list:
    """Fallback manual parsing when JSON parsing fails."""
    # Look for quoted strings or numbered items
    import re

    # Look for quoted strings
    quoted_chunks = re.findall(r'"([^"]*)"', response)
    if quoted_chunks:
        return [chunk.strip() for chunk in quoted_chunks if chunk.strip()]

    # Look for numbered items (1., 2., etc.)
    numbered_chunks = re.findall(r"\d+\.\s*(.*?)(?=\d+\.|$)", response, re.DOTALL)
    if numbered_chunks:
        return [chunk.strip() for chunk in numbered_chunks if chunk.strip()]

    # Look for bullet points
    bullet_chunks = re.findall(r"[-*]\s*(.*?)(?=[-*]|$)", response, re.DOTALL)
    if bullet_chunks:
        return [chunk.strip() for chunk in bullet_chunks if chunk.strip()]

    # If all else fails, return the original input as a single chunk
    return [original_input]


def _fallback_splitter(user_input: str) -> list:
    """Simple rule-based fallback splitter when LLM is not available."""
    # Check for common conjunctions that indicate multiple intents
    conjunctions = [" and ", " plus ", " also ", " then ", " & "]

    for conjunction in conjunctions:
        if conjunction in user_input.lower():
            parts = user_input.split(conjunction)
            chunks = [part.strip() for part in parts if part.strip()]
            if len(chunks) > 1:
                return chunks

    # If no conjunctions found, treat as single intent
    return [user_input]


def calculate_action(operation: str, a: float, b: float, context=None, **kwargs) -> str:
    operation_map = {
        "plus": "+",
        "add": "+",
        "addition": "+",
        "minus": "-",
        "subtract": "-",
        "subtraction": "-",
        "times": "*",
        "multiply": "*",
        "multiplied": "*",
        "divided": "/",
        "divide": "/",
        "over": "/",
    }
    math_op = operation_map.get(operation.lower(), operation)
    try:
        result = eval(f"{a} {math_op} {b}")
        return f"{a} {operation} {b} = {result}"
    except (SyntaxError, ZeroDivisionError) as e:
        return f"Error: Cannot calculate {a} {operation} {b} - {str(e)}"


def greet_action(name: str, context=None, **kwargs) -> str:
    return f"Hello {name}!"


def weather_action(location: str, context=None, **kwargs) -> str:
    return f"Weather in {location}: 72°F, Sunny (simulated)"


def help_action(context=None, **kwargs) -> str:
    return "I can help with greetings, calculations, and weather!"


def main_classifier(user_input: str, children, debug=False, context=None, **kwargs):
    """Simple classifier that routes to appropriate child nodes."""
    # Find child nodes by name
    greet_node = None
    calculate_node = None
    weather_node = None
    help_node = None

    for child in children:
        if child.name == "greet_action":
            greet_node = child
        elif child.name == "calculate_action":
            calculate_node = child
        elif child.name == "weather_action":
            weather_node = child
        elif child.name == "help_action":
            help_node = child

    # Simple routing logic
    if "hello" in user_input.lower() or "hi" in user_input.lower():
        return greet_node
    elif any(
        word in user_input.lower()
        for word in ["calculate", "math", "plus", "minus", "multiply", "divide"]
    ):
        return calculate_node
    elif "weather" in user_input.lower():
        return weather_node
    elif "help" in user_input.lower():
        return help_node
    else:
        # Default to help if no clear match
        return help_node


function_registry: dict[str, Callable[..., Any]] = {
    "greet_action": greet_action,
    "calculate_action": calculate_action,
    "weather_action": weather_action,
    "help_action": help_action,
    "llm_splitter": llm_splitter,
    "llm_classifier": main_classifier,
}

if __name__ == "__main__":
    from intent_kit.utils.perf_util import PerfUtil

    with PerfUtil("multi_intent_demo.py run time") as perf:
        # Load the graph definition from local JSON (same directory as script)
        json_path = os.path.join(os.path.dirname(__file__), "multi_intent_demo.json")
        with open(json_path, "r") as f:
            json_graph = json.load(f)

        graph = (
            IntentGraphBuilder()
            .with_json(json_graph)
            .with_functions(function_registry)
            .with_default_llm_config(LLM_CONFIG)
            .build()
        )

        # Debug: Print the root nodes
        print(f"Graph root nodes: {[node.name for node in graph.root_nodes]}")
        print(f"Graph splitter: {graph.splitter}")

        context = IntentContext(session_id="multi_intent_demo")

        test_inputs = [
            "Hello Alice, what's 15 plus 7?",
            "Weather in San Francisco and multiply 8 by 3",
            "Hi Bob, help me with calculations",
            "What's 20 minus 5 and weather in New York",
        ]
        timings = []
        successes = []
        for user_input in test_inputs:
            with PerfUtil.collect(f"Input: {user_input}", timings) as input_perf:
                print(f"\nInput: {user_input}")
                result = graph.route(user_input, context=context)
                success = bool(getattr(result, "success", True))
                if success:
                    print(f"Intent: {getattr(result, 'node_name', 'N/A')}")
                    print(f"Output: {getattr(result, 'output', 'N/A')}")
                else:
                    print(f"Error: {getattr(result, 'error', 'N/A')}")
                successes.append(success)
    print(perf.format())
    print("\nTiming Summary:")
    print(f"  {'Label':<40} | {'Elapsed (sec)':>12} | {'Success':>7}")
    print("  " + "-" * 65)
    for (label, elapsed), success in zip(timings, successes):
        elapsed_str = f"{elapsed:12.4f}" if elapsed is not None else "     N/A   "
        print(f"  {label[:40]:<40} | {elapsed_str} | {str(success):>7}")
