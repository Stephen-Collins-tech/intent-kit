from typing import Optional, Dict, Any
from intent_kit.node.actions.action import ActionNode
from intent_kit.context import IntentContext


def extract_booking_args_llm(
    user_input: str, context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Extract booking parameters using LLM."""
    from intent_kit.services.llm_factory import LLMFactory

    # Check for mock mode
    import os

    mock_mode = os.getenv("INTENT_KIT_MOCK_MODE") == "1"

    if mock_mode:
        # Mock responses for testing without API calls
        import re

        # Simple regex extraction for mock mode
        dest_match = re.search(
            r"(?:to|for|in)\s+([A-Za-z\s]+?)(?:\s|$)", user_input, re.IGNORECASE
        )
        destination = dest_match.group(1).strip() if dest_match else "Unknown"

        date_match = re.search(r"(?:for|on)\s+(\w+\s+\w+)", user_input, re.IGNORECASE)
        date = date_match.group(1) if date_match else "ASAP"

        return {
            "destination": destination,
            "date": date,
            "user_id": context.get("user_id", "anonymous") if context else "anonymous",
        }

    # Configure LLM (you can change this to any supported provider)
    provider = "openai"  # or "anthropic", "google", "ollama"
    api_key = os.getenv(f"{provider.upper()}_API_KEY")

    if not api_key:
        raise ValueError(f"Environment variable {provider.upper()}_API_KEY not set")

    llm_config = {"provider": provider, "model": "gpt-3.5-turbo", "api_key": api_key}

    try:
        llm_client = LLMFactory.create_client(llm_config)

        prompt = f"""
Extract booking parameters from this user input. Be precise and extract exactly what the user is asking for.

User input: "{user_input}"

Return a JSON object with these exact fields:
- destination: The destination city/location (extract the actual place name)
- date: The specific date mentioned, or "ASAP" if no date is specified

Rules:
- If the user says "book a flight to X", extract X as destination
- If the user says "travel to X", extract X as destination
- If the user says "fly to X", extract X as destination
- If the user says "go to X", extract X as destination
- For dates, extract the exact date mentioned (e.g., "next Friday", "December 15th", "tomorrow")
- If no date is mentioned, use "ASAP"
- Clean up any extra words like "for" or "to" from the date field

Examples:
- "Book a flight to Paris" → {{"destination": "Paris", "date": "ASAP"}}
- "I want to fly to Tokyo next Friday" → {{"destination": "Tokyo", "date": "next Friday"}}
- "Travel to London tomorrow" → {{"destination": "London", "date": "tomorrow"}}
- "Book a flight to Rome for the weekend" → {{"destination": "Rome", "date": "the weekend"}}

User input: {user_input}
JSON:"""

        response = llm_client.generate(prompt, model=llm_config["model"])

        # Parse the JSON response
        import json
        import re

        # Extract JSON from response
        json_match = re.search(r"\{.*\}", response, re.DOTALL)
        if json_match:
            result = json.loads(json_match.group())
            # Clean up the date field to remove extra words
            date = result.get("date", "ASAP")
            if date != "ASAP":
                # Remove common prefixes that might be extracted
                date = re.sub(r"^(for|to)\s+", "", date, flags=re.IGNORECASE)

            return {
                "destination": result.get("destination", "Unknown"),
                "date": date,
                "user_id": (
                    context.get("user_id", "anonymous") if context else "anonymous"
                ),
            }
    except Exception as e:
        print(f"LLM extraction failed: {e}")

    # Fallback to simple extraction
    import re

    dest_match = re.search(
        r"(?:to|for|in)\s+([A-Za-z\s]+?)(?:\s|$)", user_input, re.IGNORECASE
    )
    destination = dest_match.group(1).strip() if dest_match else "Unknown"

    date_match = re.search(r"(?:for|on)\s+(\w+\s+\w+)", user_input, re.IGNORECASE)
    date = date_match.group(1) if date_match else "ASAP"

    return {
        "destination": destination,
        "date": date,
        "user_id": context.get("user_id", "anonymous") if context else "anonymous",
    }


def booking_handler(destination: str, date: str, context: IntentContext) -> str:
    """Handle flight booking requests."""
    # Update context with booking info
    booking_count = context.get("booking_count", 0) + 1
    context.set("booking_count", booking_count, modified_by="booking_handler")
    context.set("last_destination", destination, modified_by="booking_handler")

    # Use the incremented count for the response
    return f"Flight booked to {destination} for {date} (Booking #{booking_count})"


# Create the handler node with LLM extraction
action_node_llm = ActionNode(
    name="action_node_llm",
    param_schema={"destination": str, "date": str},
    action=booking_handler,
    arg_extractor=extract_booking_args_llm,
    context_inputs={"user_id"},
    context_outputs={"booking_count", "last_destination"},
    description="Handle flight booking requests with LLM-powered argument extraction",
)
