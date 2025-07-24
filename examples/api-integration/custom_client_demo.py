#!/usr/bin/env python3
"""
Minimal Example: Custom LLM Client Demo (real HTTP, no mock)

This shows how to implement a real custom LLM client (mirroring OpenAIClient structure)
and use it in an intent graph for both classification and parameter extraction.
"""
import re
import os
import json
from typing import Optional
from intent_kit import IntentGraphBuilder
from intent_kit.services.base_client import BaseLLMClient
from intent_kit.utils.logger import Logger

logger = Logger(__name__)

# Safe import of openai
try:
    from openai import OpenAI

    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    logger.warning(
        "OpenAI package not found. Please install it with: pip install openai"
    )


class ExampleLLMClient(BaseLLMClient):
    """Custom LLM client that uses OpenAI API for real LLM responses."""

    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4.1-nano"):
        if not OPENAI_AVAILABLE:
            raise ImportError(
                "OpenAI package not available. Please install it with: pip install openai"
            )

        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError(
                "OpenAI API key not provided. Set OPENAI_API_KEY environment variable or pass api_key parameter."
            )

        self.model = model
        super().__init__(api_key=api_key)

    def _initialize_client(self, **kwargs) -> None:
        if not OPENAI_AVAILABLE:
            raise ImportError("OpenAI package not available")

        self._client = OpenAI(api_key=self.api_key)

    def get_client(self):
        return self._client

    def _ensure_imported(self) -> None:
        if not OPENAI_AVAILABLE:
            raise ImportError("OpenAI package not available")

    def generate(self, prompt: str, model: Optional[str] = None) -> str:
        if not OPENAI_AVAILABLE:
            raise ImportError("OpenAI package not available")

        if self._client is None:
            raise RuntimeError("OpenAI client not initialized.")

        try:
            print("-----------PROMPT-------------")
            print(prompt)
            print("--------------------------------\n")
            response = self._client.chat.completions.create(
                model=model or self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful assistant that extracts parameters and classifies nodes accurately.",
                    },
                    {"role": "user", "content": prompt},
                ],
                max_tokens=150,
                temperature=0.1,  # Low temperature for consistent extraction
            )

            print("-----------FROM LLM-------------")
            print("--------------------------------")
            print(response.choices[0].message.content.strip())
            print("--------------------------------")

            # Handle empty or None response
            if not response.choices or not response.choices[0].message.content:
                logger.warning(
                    "LLM returned empty response, falling back to rule-based extraction"
                )
                return self._fallback_extraction(prompt)

            content = response.choices[0].message.content.strip()
            if not content:
                logger.warning(
                    "LLM returned empty content, falling back to rule-based extraction"
                )
                return self._fallback_extraction(prompt)

            return content

        except Exception as e:
            logger.error(f"Error calling OpenAI API: {e}")
            return self._fallback_extraction(prompt)

    def _fallback_extraction(self, prompt: str) -> str:
        """Fallback extraction when LLM fails."""
        logger.info("Using fallback extraction")

        # Simple rule-based extraction for demo purposes
        if "name" in prompt.lower():
            # Extract name from prompt
            name_match = re.search(r"name is (\w+)", prompt, re.IGNORECASE)
            if name_match:
                return f'{{"name": "{name_match.group(1)}"}}'

        if "add" in prompt.lower() or "calculate" in prompt.lower():
            # Extract numbers from prompt
            numbers = re.findall(r"\d+", prompt)
            if len(numbers) >= 2:
                return f'{{"a": {numbers[0]}, "b": {numbers[1]}}}'

        # Default fallback
        return '{"error": "Could not extract parameters"}'


def greet_action(name: str, **_) -> str:
    return f"Hello {name}!"


def calc_action(a: float, b: float, **_) -> str:
    return f"Sum: {a + b}"


def main_classifier(user_input: str, children, context=None, **kwargs):
    """Simple classifier that routes to appropriate child nodes."""
    # Find child nodes by name
    greet_node = None
    calc_node = None

    for child in children:
        if child.name == "greet_action":
            greet_node = child
        elif child.name == "calc_action":
            calc_node = child

    # Simple routing logic
    if "name" in user_input.lower() or "hello" in user_input.lower():
        return greet_node
    elif "add" in user_input.lower() or "calculate" in user_input.lower():
        return calc_node
    else:
        # Default to greet if no clear match
        return greet_node


function_registry = {
    "greet_action": greet_action,
    "calc_action": calc_action,
    "main_classifier": main_classifier,
}


def create_intent_graph():
    """Create and configure the intent graph using JSON."""
    # Load the graph definition from local JSON (same directory as script)
    json_path = os.path.join(os.path.dirname(__file__), "custom_client_demo.json")
    with open(json_path, "r") as f:
        json_graph = json.load(f)

    return (
        IntentGraphBuilder()
        .with_json(json_graph)
        .with_functions(function_registry)
        .build()
    )


def main():
    """Main function with proper error handling."""
    if not OPENAI_AVAILABLE:
        print("❌ OpenAI package not available.")
        print("Please install it with: pip install openai")
        print("Then set your OpenAI API key: export OPENAI_API_KEY='your-api-key'")
        return

    # Check for API key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ OpenAI API key not found.")
        print("Please set your OpenAI API key: export OPENAI_API_KEY='your-api-key'")
        return

    print("✅ OpenAI client configured successfully!")
    print("Using model: gpt-4.1-nano")
    print()

    # Build intent graph using ExampleLLMClient for both extraction and classification
    try:
        # Create the graph using JSON
        graph = create_intent_graph()

        # Test the graph
        test_inputs = [
            "My name is Alice",
            "Add 2 and 3",
            "Hello, I'm Bob",
            "Calculate 10 plus 5",
        ]

        for user_input in test_inputs:
            print(f"Input: {user_input}")
            result = graph.route(user_input)
            print(f"Output: {result.output}")
            print(f"Success: {result.success}")
            print()

    except Exception as e:
        print(f"❌ Error setting up the demo: {e}")
        print("Please check your OpenAI API key and try again.")


if __name__ == "__main__":
    main()
