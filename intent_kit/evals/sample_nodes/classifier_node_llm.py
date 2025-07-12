from typing import Optional, List, Dict, Any
from intent_kit.node.classifiers import ClassifierNode
from intent_kit.node.actions.action import ActionNode as HandlerNode
from intent_kit.context import IntentContext
from intent_kit.node.base import TreeNode


def extract_weather_args_llm(
    user_input: str, context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Extract weather parameters using LLM."""
    from intent_kit.services.llm_factory import LLMFactory

    # Check for mock mode
    import os

    mock_mode = os.getenv("INTENT_KIT_MOCK_MODE") == "1"

    if mock_mode:
        # Mock responses for testing without API calls
        import re

        location_patterns = [
            r"(?:in|for|at)\s+([A-Za-z\s]+?)(?:\s|$)",
            r"(?:weather|temperature|forecast)\s+(?:in|for|at)\s+([A-Za-z\s]+?)(?:\s|$)",
            r"(?:What\'s|How\'s)\s+(?:the\s+)?(?:weather|temperature)\s+(?:like\s+)?(?:in|for|at)\s+([A-Za-z\s]+?)(?:\?|$)",
            r"(?:weather|temperature)\s+(?:in|for|at)\s+([A-Za-z\s]+?)(?:\?|$)",
            r"(?:weather|temperature|forecast)\s+for\s+([A-Za-z\s]+?)(?:\?|$)",
            r"(?:weather|temperature)\s+in\s+([A-Za-z\s]+?)(?:\?|$)",
        ]

        location = "Unknown"
        for pattern in location_patterns:
            location_match = re.search(pattern, user_input, re.IGNORECASE)
            if location_match:
                location = location_match.group(1).strip()
                break

        return {"location": location}

    # Configure LLM
    provider = "openai"  # or "anthropic", "google", "ollama"
    api_key = os.getenv(f"{provider.upper()}_API_KEY")

    if not api_key:
        raise ValueError(f"Environment variable {provider.upper()}_API_KEY not set")

    llm_config = {"provider": provider, "model": "gpt-4.1-mini", "api_key": api_key}

    try:
        llm_client = LLMFactory.create_client(llm_config)

        prompt = f"""
Extract the location from this weather-related user input.

User input: "{user_input}"

Return a JSON object with this field:
- location: The specific location/city mentioned

Rules:
- Extract the exact location name (e.g., "New York", "London", "Tokyo")
- If no location is mentioned, use "Unknown"
- Be precise and extract the full location name

Examples:
- "What's the weather like in New York?" → {{"location": "New York"}}
- "How's the temperature in London?" → {{"location": "London"}}
- "Can you tell me the weather forecast for Tokyo?" → {{"location": "Tokyo"}}
- "What's the weather like today?" → {{"location": "Unknown"}}

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
            return {"location": result.get("location", "Unknown")}
    except Exception as e:
        print(f"LLM weather extraction failed: {e}")

    # Fallback to regex extraction
    import re

    location_patterns = [
        r"(?:in|for|at)\s+([A-Za-z\s]+?)(?:\s|$)",
        r"(?:weather|temperature|forecast)\s+(?:in|for|at)\s+([A-Za-z\s]+?)(?:\s|$)",
        r"(?:What\'s|How\'s)\s+(?:the\s+)?(?:weather|temperature)\s+(?:like\s+)?(?:in|for|at)\s+([A-Za-z\s]+?)(?:\?|$)",
        r"(?:weather|temperature)\s+(?:in|for|at)\s+([A-Za-z\s]+?)(?:\?|$)",
        r"(?:weather|temperature|forecast)\s+for\s+([A-Za-z\s]+?)(?:\?|$)",
        r"(?:weather|temperature)\s+in\s+([A-Za-z\s]+?)(?:\?|$)",
    ]

    location = "Unknown"
    for pattern in location_patterns:
        location_match = re.search(pattern, user_input, re.IGNORECASE)
        if location_match:
            location = location_match.group(1).strip()
            break

    return {"location": location}


def weather_handler(location: str, context: IntentContext) -> str:
    """Handle weather requests."""
    return f"Weather in {location}: Sunny with a chance of rain"


def extract_cancel_args_llm(
    user_input: str, context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Extract cancellation parameters using LLM."""
    from intent_kit.services.llm_factory import LLMFactory

    # Check for mock mode
    import os

    mock_mode = os.getenv("INTENT_KIT_MOCK_MODE") == "1"

    if mock_mode:
        # Mock responses for testing without API calls
        import re

        cancel_patterns = [
            r"cancel\s+(?:my\s+)?([^,\s]+(?:\s+[^,\s]+)*?)(?:\s|$)",
            r"cancel\s+(?:my\s+)?([^,\s]+(?:\s+[^,\s]+)*?)(?:\?|$)",
            r"(?:I\s+need\s+to\s+)?cancel\s+(?:my\s+)?([^,\s]+(?:\s+[^,\s]+)*?)(?:\s|$)",
            r"(?:cancel|cancellation)\s+(?:of\s+)?(?:my\s+)?([^,\s]+(?:\s+[^,\s]+)*?)(?:\s|$)",
        ]

        item = "reservation"
        for pattern in cancel_patterns:
            cancel_match = re.search(pattern, user_input, re.IGNORECASE)
            if cancel_match:
                item = cancel_match.group(1).strip()
                break

        return {"item": item}

    # Configure LLM
    provider = "openai"  # or "anthropic", "google", "ollama"
    api_key = os.getenv(f"{provider.upper()}_API_KEY")

    if not api_key:
        raise ValueError(f"Environment variable {provider.upper()}_API_KEY not set")

    llm_config = {"provider": provider, "model": "gpt-3.5-turbo", "api_key": api_key}

    try:
        llm_client = LLMFactory.create_client(llm_config)

        prompt = f"""
Extract what the user wants to cancel from this user input.

User input: "{user_input}"

Return a JSON object with this field:
- item: The specific item/reservation to cancel

Rules:
- Extract the exact item name (e.g., "flight reservation", "hotel booking", "restaurant reservation")
- Be precise and extract the full item description
- If no specific item is mentioned, use "reservation"

Examples:
- "I need to cancel my flight reservation" → {{"item": "flight reservation"}}
- "Cancel my hotel booking" → {{"item": "hotel booking"}}
- "I want to cancel my restaurant reservation" → {{"item": "restaurant reservation"}}
- "Please cancel my appointment" → {{"item": "appointment"}}

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
            return {"item": result.get("item", "reservation")}
    except Exception as e:
        print(f"LLM cancel extraction failed: {e}")

    # Fallback to regex extraction
    import re

    cancel_patterns = [
        r"cancel\s+(?:my\s+)?([^,\s]+(?:\s+[^,\s]+)*?)(?:\s|$)",
        r"cancel\s+(?:my\s+)?([^,\s]+(?:\s+[^,\s]+)*?)(?:\?|$)",
        r"(?:I\s+need\s+to\s+)?cancel\s+(?:my\s+)?([^,\s]+(?:\s+[^,\s]+)*?)(?:\s|$)",
        r"(?:cancel|cancellation)\s+(?:of\s+)?(?:my\s+)?([^,\s]+(?:\s+[^,\s]+)*?)(?:\s|$)",
    ]

    item = "reservation"
    for pattern in cancel_patterns:
        cancel_match = re.search(pattern, user_input, re.IGNORECASE)
        if cancel_match:
            item = cancel_match.group(1).strip()
            break

    return {"item": item}


def cancel_handler(item: str, context: IntentContext) -> str:
    """Handle cancellation requests."""
    return f"Successfully cancelled {item}"


# Create handler nodes with LLM extraction
weather_handler_node = HandlerNode(
    name="weather_handler",
    param_schema={"location": str},
    action=weather_handler,
    arg_extractor=extract_weather_args_llm,
    description="Get weather information for a location",
)

cancel_handler_node = HandlerNode(
    name="cancel_handler",
    param_schema={"item": str},
    action=cancel_handler,
    arg_extractor=extract_cancel_args_llm,
    description="Cancel reservations or bookings",
)


def intent_classifier_llm(
    user_input: str, children: List[TreeNode], context: Optional[Dict[str, Any]] = None
) -> Optional[TreeNode]:
    """Classify user intent using LLM."""
    from intent_kit.services.llm_factory import LLMFactory

    # Check for mock mode
    import os

    mock_mode = os.getenv("INTENT_KIT_MOCK_MODE") == "1"

    if mock_mode:
        # Mock responses for testing without API calls
        if "weather" in user_input.lower():
            # Return first child (weather handler)
            return children[0] if children else None
        elif "cancel" in user_input.lower():
            # Return second child (cancel handler)
            return children[1] if len(children) > 1 else None
        else:
            return children[0] if children else None  # Default to first child

    # Configure LLM
    provider = "openai"  # or "anthropic", "google", "ollama"
    api_key = os.getenv(f"{provider.upper()}_API_KEY")

    if not api_key:
        raise ValueError(f"Environment variable {provider.upper()}_API_KEY not set")

    llm_config = {"provider": provider, "model": "gpt-3.5-turbo", "api_key": api_key}

    try:
        llm_client = LLMFactory.create_client(llm_config)

        # Create descriptions of available handlers
        handler_descriptions = []
        for child in children:
            handler_descriptions.append(f"- {child.name}: {child.description}")

        prompt = f"""
Classify the user's intent and return the name of the appropriate handler.

Available handlers:
{chr(10).join(handler_descriptions)}

User input: "{user_input}"

Rules:
- If the user asks about weather, temperature, or forecast, return "weather_handler"
- If the user wants to cancel something, return "cancel_handler"
- Be precise and match the exact handler name

Return only the handler name (e.g., "weather_handler" or "cancel_handler") or "none" if no handler matches.

Handler:"""

        response = llm_client.generate(prompt, model=llm_config["model"])
        handler_name = response.strip().lower()

        # Find the matching handler
        for child in children:
            if child.name == handler_name:
                return child

        # Fallback to keyword matching
        user_input_lower = user_input.lower()
        if any(
            word in user_input_lower for word in ["weather", "temperature", "forecast"]
        ):
            return weather_handler_node
        elif any(
            word in user_input_lower for word in ["cancel", "cancellation", "refund"]
        ):
            return cancel_handler_node

    except Exception as e:
        print(f"LLM classification failed: {e}")
        # Fallback to keyword matching
        user_input_lower = user_input.lower()
        if any(
            word in user_input_lower for word in ["weather", "temperature", "forecast"]
        ):
            return weather_handler_node
        elif any(
            word in user_input_lower for word in ["cancel", "cancellation", "refund"]
        ):
            return cancel_handler_node

    return None


# Create the classifier node with LLM classification
classifier_node_llm = ClassifierNode(
    name="classifier_node_llm",
    classifier=intent_classifier_llm,
    children=[weather_handler_node, cancel_handler_node],
    description="Route user intents to appropriate handlers using LLM classification",
)
