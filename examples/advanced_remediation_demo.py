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
import random
from dotenv import load_dotenv
from intent_kit.context import IntentContext
from intent_kit.node.types import ExecutionResult
from intent_kit.builder import handler
from intent_kit.handlers.remediation import (
    create_self_reflect_strategy,
    create_consensus_vote_strategy,
    create_alternate_prompt_strategy,
)

# --- Setup LLM configs ---
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY") or "sk-mock-openai"
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") or "sk-mock-gemini"

LLM_CONFIG_1 = {"provider": "openai",
                "model": "gpt-4.1-mini", "api_key": OPENAI_API_KEY}
LLM_CONFIG_2 = {"provider": "google",
                "model": "gemini-2.5-flash", "api_key": GEMINI_API_KEY}

# --- Core Handler: Simulates model confusion and ambiguity ---


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


# --- Remediation Handlers ---
handlers = [
    handler(
        name="self_reflect_sentiment",
        description="Uses self-reflection if it fails on ambiguous reviews.",
        handler_func=analyze_sentiment,
        param_schema={"review_text": str},
        remediation_strategies=[create_self_reflect_strategy(
            LLM_CONFIG_1, max_reflections=1)],
    ),
    handler(
        name="consensus_vote_sentiment",
        description="Uses consensus voting between two LLMs on conflicting reviews.",
        handler_func=analyze_sentiment,
        param_schema={"review_text": str},
        remediation_strategies=[create_consensus_vote_strategy(
            [LLM_CONFIG_1, LLM_CONFIG_2], vote_threshold=0.5)],
    ),
    handler(
        name="alternate_prompt_sentiment",
        description="Retries with alternate prompt if ambiguous input causes a failure.",
        handler_func=analyze_sentiment,
        param_schema={"review_text": str},
        remediation_strategies=[
            create_alternate_prompt_strategy(LLM_CONFIG_1)],
    ),
]


def main():
    context = IntentContext()
    print("=== Advanced Remediation Strategies Demo ===\n")

    print("This demo shows how self-reflection, consensus voting, and alternate prompts can recover\n"
          "from ambiguous or conflicting results in real-world sentiment analysis tasks.\n")

    # Each case is designed to *require* remediation.
    test_cases = [
        (
            "This product is not bad at all, actually quite good!",
            "Triggers self-reflection: Model may misinterpret 'not bad'."
        ),
        (
            "I hate the design but love the features, not my favorite but not bad.",
            "Triggers consensus voting: LLMs likely to disagree on mixed sentiment."
        ),
        (
            "Okay, fine, whatever, not bad I guess, meh",
            "Triggers alternate prompt: All terms are vague, likely to fail first try."
        ),
    ]

    for i, (review_text, case_desc) in enumerate(test_cases):
        h = handlers[i]
        print(f"\n--- Handler: {h.name} ---")
        print(f"Review: {review_text}")
        print(f"Case: {case_desc}")

        try:
            result: ExecutionResult = h.execute(
                user_input=review_text, context=context)
            print(f"Success: {result.success}")
            print(f"Output:  {result.output}")
            if result.error:
                print(f"Error:   {result.error.message}")
        except Exception as e:
            print(f"Handler crashed: {e}")

    print("\n=== What did you just see? ===")
    print("• Self-reflection: Model reviews its own output and tries to fix mistakes.")
    print("• Consensus voting: Multiple models must agree before output is accepted.")
    print("• Alternate prompt: Handler retries with a new prompt if it can't answer.")

    if "mock" in OPENAI_API_KEY or "mock" in GEMINI_API_KEY:
        print("\n💡 Pro Tip: For real LLM behavior, add your OpenAI and Gemini API keys to a .env file.")


if __name__ == "__main__":
    main()
