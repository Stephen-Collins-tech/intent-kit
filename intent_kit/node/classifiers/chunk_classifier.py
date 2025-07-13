"""
LLM-powered chunk classifier for intent chunks.
"""

from intent_kit.types import (
    IntentChunk,
    IntentClassification,
    IntentAction,
    ClassifierOutput,
)
from intent_kit.services.llm_factory import LLMFactory
from intent_kit.utils.logger import Logger
from intent_kit.utils.text_utils import extract_json_from_text, extract_key_value_pairs
import re
from typing import Optional

logger = Logger(__name__)


def classify_intent_chunk(
    chunk: IntentChunk, llm_config: Optional[dict] = None
) -> ClassifierOutput:
    """
    LLM-powered classifier for intent chunks.

    Args:
        chunk: The intent chunk to classify
        llm_config: LLM configuration (optional, will use fallback if not provided)

    Returns:
        Classification result with action to take
    """
    chunk_text = (
        chunk["text"] if isinstance(chunk, dict) and "text" in chunk else str(chunk)
    )

    # Fallback for empty chunks
    if not chunk_text.strip():
        return {
            "chunk_text": chunk_text,
            "classification": IntentClassification.INVALID,
            "intent_type": None,
            "action": IntentAction.REJECT,
            "metadata": {"confidence": 0.0, "reason": "Empty chunk"},
        }

    # If no LLM config provided, use fallback logic
    if not llm_config:
        return _fallback_classify(chunk_text)

    try:
        # Create LLM prompt for classification
        prompt = _create_classification_prompt(chunk_text)

        # Get LLM response
        response = LLMFactory.generate_with_config(llm_config, prompt)

        # Parse the response
        result = _parse_classification_response(response, chunk_text)

        if result:
            return result
        else:
            # Fallback if LLM parsing fails
            logger.warning(
                f"LLM classification parsing failed, using fallback for: {chunk_text}"
            )
            return _fallback_classify(chunk_text)

    except Exception as e:
        logger.error(
            f"LLM classification failed: {e}, using fallback for: {chunk_text}"
        )
        return _fallback_classify(chunk_text)


def _create_classification_prompt(chunk_text: str) -> str:
    """Create a prompt for LLM-based chunk classification."""
    return f"""You are an intent chunk classifier. Given a chunk of user input, determine if it should be:

1. HANDLED as a single intent (atomic)
2. SPLIT into multiple intents (composite)
3. CLARIFIED with the user (ambiguous)
4. REJECTED as invalid

Chunk to classify: "{chunk_text}"

Return your response as a JSON object with this exact format:
{{
  "classification": "Atomic|Composite|Ambiguous|Invalid",
  "intent_type": "string or null",
  "action": "handle|split|clarify|reject",
  "confidence": 0.0-1.0,
  "reason": "explanation of your decision"
}}

Examples:
- "Book a flight to NYC" → {{"classification": "Atomic", "intent_type": "BookFlightIntent", "action": "handle", "confidence": 0.95, "reason": "Single clear booking intent"}}
- "Cancel my flight and update my email" → {{"classification": "Composite", "intent_type": null, "action": "split", "confidence": 0.9, "reason": "Two distinct intents separated by conjunction"}}
- "Book something" → {{"classification": "Ambiguous", "intent_type": null, "action": "clarify", "confidence": 0.4, "reason": "Insufficient details to determine what to book"}}
- "" → {{"classification": "Invalid", "intent_type": null, "action": "reject", "confidence": 0.0, "reason": "Empty input"}}

Your response:"""


def _parse_classification_response(response: str, chunk_text: str) -> ClassifierOutput:
    """Parse the LLM response into a classification result."""
    try:
        # Use the new utility to extract JSON
        parsed = extract_json_from_text(response)
        if parsed:
            # Validate required fields
            if all(
                key in parsed
                for key in ["classification", "action", "confidence", "reason"]
            ):
                return {
                    "chunk_text": chunk_text,
                    "classification": IntentClassification(parsed["classification"]),
                    "intent_type": parsed.get("intent_type"),
                    "action": IntentAction(parsed["action"]),
                    "metadata": {
                        "confidence": float(parsed["confidence"]),
                        "reason": str(parsed["reason"]),
                    },
                }
        # If JSON parsing fails, try manual parsing
        return _manual_parse_classification(response, chunk_text)
    except (KeyError, ValueError) as e:
        logger.error(f"Failed to parse LLM classification response: {e}")
        return _manual_parse_classification(response, chunk_text)


def _manual_parse_classification(response: str, chunk_text: str) -> ClassifierOutput:
    """Fallback manual parsing when JSON parsing fails."""
    # Use the new utility to extract key-value pairs
    pairs = extract_key_value_pairs(response)
    classification = pairs.get("classification")
    action = pairs.get("action")
    confidence = pairs.get("confidence")
    reason = pairs.get("reason")
    intent_type = pairs.get("intent_type")
    if classification and action and confidence and reason:
        return {
            "chunk_text": chunk_text,
            "classification": IntentClassification(classification),
            "intent_type": intent_type,
            "action": IntentAction(action),
            "metadata": {"confidence": float(confidence), "reason": str(reason)},
        }
    response_lower = response.lower()

    # Look for classification keywords
    if "atomic" in response_lower or "single" in response_lower:
        return {
            "chunk_text": chunk_text,
            "classification": IntentClassification.ATOMIC,
            "intent_type": "ExampleIntentType",
            "action": IntentAction.HANDLE,
            "metadata": {"confidence": 0.7, "reason": "Manually parsed as atomic"},
        }
    elif "composite" in response_lower or "split" in response_lower:
        return {
            "chunk_text": chunk_text,
            "classification": IntentClassification.COMPOSITE,
            "intent_type": None,
            "action": IntentAction.SPLIT,
            "metadata": {"confidence": 0.7, "reason": "Manually parsed as composite"},
        }
    elif "ambiguous" in response_lower or "clarify" in response_lower:
        return {
            "chunk_text": chunk_text,
            "classification": IntentClassification.AMBIGUOUS,
            "intent_type": None,
            "action": IntentAction.CLARIFY,
            "metadata": {"confidence": 0.5, "reason": "Manually parsed as ambiguous"},
        }
    else:
        return {
            "chunk_text": chunk_text,
            "classification": IntentClassification.INVALID,
            "intent_type": None,
            "action": IntentAction.REJECT,
            "metadata": {"confidence": 0.3, "reason": "Manually parsed as invalid"},
        }


def _fallback_classify(chunk_text: str) -> ClassifierOutput:
    """Fallback rule-based classification when LLM is not available."""
    # Simple fallback logic - much more conservative than before
    if len(chunk_text.split()) < 2:
        return {
            "chunk_text": chunk_text,
            "classification": IntentClassification.AMBIGUOUS,
            "intent_type": None,
            "action": IntentAction.CLARIFY,
            "metadata": {"confidence": 0.4, "reason": "Too short to classify"},
        }

    # Check for single conjunctions that likely indicate multiple intents
    single_conjunctions = [r"\band\b", r"\bplus\b", r"\balso\b"]
    for pattern in single_conjunctions:
        if re.search(pattern, chunk_text, re.IGNORECASE):
            # Check if the parts around the conjunction look like separate actions
            parts = re.split(pattern, chunk_text, flags=re.IGNORECASE)
            if len(parts) == 2:
                part1, part2 = parts[0].strip(), parts[1].strip()
                # If both parts have action verbs, likely composite
                action_verbs = [
                    "cancel",
                    "book",
                    "update",
                    "get",
                    "show",
                    "calculate",
                    "greet",
                ]
                if any(verb in part1.lower() for verb in action_verbs) and any(
                    verb in part2.lower() for verb in action_verbs
                ):
                    return {
                        "chunk_text": chunk_text,
                        "classification": IntentClassification.COMPOSITE,
                        "intent_type": None,
                        "action": IntentAction.SPLIT,
                        "metadata": {
                            "confidence": 0.8,
                            "reason": f"Detected multi-intent pattern with conjunction: {pattern}",
                        },
                    }

    # Default to atomic
    return {
        "chunk_text": chunk_text,
        "classification": IntentClassification.ATOMIC,
        "intent_type": "ExampleIntentType",
        "action": IntentAction.HANDLE,
        "metadata": {"confidence": 0.9, "reason": "Single clear intent detected"},
    }
