#!/usr/bin/env python3
"""
Advanced Remediation Demo: Sentiment Analysis

This script demonstrates advanced remediation strategies in intent-kit:
  - Self-reflection (model rethinks its output)
  - Consensus voting (multiple models must agree)
  - Alternate prompt retry (model tries new phrasing if it fails)

Each strategy is shown handling ambiguous or conflicting review input.

Usage:
    python examples/advanced_remediation_demo.py
"""

import os
import json
import random
from dotenv import load_dotenv
from intent_kit import IntentGraphBuilder
from intent_kit.context import IntentContext
from intent_kit.node.types import ExecutionResult
from intent_kit.node.actions import (
    create_self_reflect_strategy,
    create_consensus_vote_strategy,
    create_alternate_prompt_strategy,
    register_remediation_strategy,
)

# --- Setup LLM configs ---
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY") or "sk-mock-openai"
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY") or "sk-mock-gemini"

LLM_CONFIG_1 = {
    "provider": "openai",
    "model": "gpt-4.1-mini",
    "api_key": OPENAI_API_KEY,
}
LLM_CONFIG_2 = {
    "provider": "google",
    "model": "gemini-2.5-flash",
    "api_key": GOOGLE_API_KEY,
}

# --- Core Action: Simulates model confusion and ambiguity ---


def analyze_sentiment(review_text: str, context: IntentContext) -> str:
    """Simulates sentiment analysis, sometimes failing on ambiguous cases."""
    text = review_text.lower()

    if "not bad" in text:
        if random.random() < 0.5:
            raise ValueError("Model confused by double negatives.")
        return "neutral"
    if "love" in text:
        return "positive"
    if "hate" in text:
        if random.random() < 0.5:
            raise ValueError("Model tripped by strong negative sentiment.")
        return "negative"
    if any(x in text for x in ("okay", "fine", "meh", "whatever")):
        if random.random() < 0.3:
            raise ValueError("Model is unsure about ambiguous neutral terms.")
        return random.choice(["neutral", "positive", "negative"])

    # If it's still ambiguous, just pick randomly (to simulate LLM uncertainty)
    return random.choice(["positive", "neutral", "negative"])


def main_classifier(user_input: str, children, context=None, **kwargs):
    """Simple classifier that routes to appropriate child nodes."""
    # Find child nodes by name
    self_reflect_node = None
    consensus_vote_node = None
    alternate_prompt_node = None

    for child in children:
        if child.name == "self_reflect_sentiment":
            self_reflect_node = child
        elif child.name == "consensus_vote_sentiment":
            consensus_vote_node = child
        elif child.name == "alternate_prompt_sentiment":
            alternate_prompt_node = child

    # Simple routing logic - for demo purposes, route based on input length
    if len(user_input) < 50:
        return self_reflect_node
    elif len(user_input) < 100:
        return consensus_vote_node
    else:
        return alternate_prompt_node


function_registry = {
    "analyze_sentiment": analyze_sentiment,
    "main_classifier": main_classifier,
}


def create_intent_graph():
    """Create and configure the intent graph using JSON."""
    # Register custom remediation strategies
    register_remediation_strategy(
        "self_reflect_strategy",
        create_self_reflect_strategy(LLM_CONFIG_1, max_reflections=1),
    )
    register_remediation_strategy(
        "consensus_vote_strategy",
        create_consensus_vote_strategy(
            [LLM_CONFIG_1, LLM_CONFIG_2], vote_threshold=0.5
        ),
    )
    register_remediation_strategy(
        "alternate_prompt_strategy", create_alternate_prompt_strategy(LLM_CONFIG_1)
    )

    # Load the graph definition from local JSON (same directory as script)
    json_path = os.path.join(
        os.path.dirname(__file__), "advanced_remediation_demo.json"
    )
    with open(json_path, "r") as f:
        json_graph = json.load(f)

    return (
        IntentGraphBuilder()
        .with_json(json_graph)
        .with_functions(function_registry)
        .build()
    )


def main():
    context = IntentContext()
    print("=== Advanced Remediation Strategies Demo ===\n")

    print(
        "This demo shows how self-reflection, consensus voting, and alternate prompts can recover\n"
        "from ambiguous or conflicting results in real-world sentiment analysis tasks.\n"
    )

    # Create the graph
    graph = create_intent_graph()

    # Each case is designed to *require* remediation.
    test_cases = [
        (
            "This product is not bad at all, actually quite good!",
            "Triggers self-reflection: Model may misinterpret 'not bad'.",
        ),
        (
            "I hate the design but love the features, not my favorite but not bad.",
            "Triggers consensus voting: LLMs likely to disagree on mixed sentiment.",
        ),
        (
            "Okay, fine, whatever, not bad I guess, meh",
            "Triggers alternate prompt: All terms are vague, likely to fail first try.",
        ),
    ]

    for i, (review_text, case_desc) in enumerate(test_cases):
        print(f"\n--- Test Case {i+1} ---")
        print(f"Review: {review_text}")
        print(f"Case: {case_desc}")

        try:
            result: ExecutionResult = graph.route(
                user_input=review_text, context=context
            )
            print(f"Success: {result.success}")
            print(f"Output:  {result.output}")
            if result.error:
                print(f"Error:   {result.error.message}")
        except Exception as e:
            print(f"Action crashed: {e}")

    print("\n=== What did you just see? ===")
    print("• Self-reflection: Model reviews its own output and tries to fix mistakes.")
    print("• Consensus voting: Multiple models must agree before output is accepted.")
    print("• Alternate prompt: Action retries with a new prompt if it can't answer.")

    if "mock" in OPENAI_API_KEY or "mock" in GOOGLE_API_KEY:
        print(
            "\n💡 Pro Tip: For real LLM behavior, add your OpenAI and Gemini API keys to a .env file."
        )


if __name__ == "__main__":
    main()
