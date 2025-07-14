from typing import Optional, List, Dict, Any
from intent_kit.node.splitters import SplitterNode


def split_text_llm(
    user_input: str, debug: bool = False, context: Optional[Dict[str, Any]] = None
) -> List[str]:
    """Split user input into multiple intents using LLM."""
    from intent_kit.services.llm_factory import LLMFactory

    # Check for mock mode
    import os

    mock_mode = os.getenv("INTENT_KIT_MOCK_MODE") == "1"

    if mock_mode:
        # Mock responses for testing without API calls
        # Simple splitting based on common conjunctions
        import re

        conjunctions = [" and ", " also ", " plus ", " as well as ", " furthermore "]
        for conj in conjunctions:
            if conj in user_input.lower():
                parts = user_input.split(conj)
                return [part.strip() for part in parts if part.strip()]
        # If no conjunctions found, return as single intent
        return [user_input]

    # Configure LLM
    provider = "openai"
    api_key = os.getenv(f"{provider.upper()}_API_KEY")

    if not api_key:
        raise ValueError(f"Environment variable {provider.upper()}_API_KEY not set")

    llm_config = {"provider": provider, "model": "gpt-4.1-mini", "api_key": api_key}

    try:
        llm_client = LLMFactory.create_client(llm_config)

        prompt = f"""
Split this text into separate requests:

"{user_input}"

Return a JSON array of strings. Each string should be a complete, standalone request.

IMPORTANT: Be verbatim. Do not add extra words, change pronouns, or modify the original text. Split exactly as written.

JSON array:"""

        response = llm_client.generate(prompt, model=llm_config["model"])

        # Parse the JSON response
        import json
        import re

        # Extract JSON array from response
        json_match = re.search(r"\[.*\]", response, re.DOTALL)
        if json_match:
            result = json.loads(json_match.group())
            if isinstance(result, list):
                return [str(item).strip() for item in result if item.strip()]

    except Exception as e:
        if debug:
            print(f"LLM splitting failed: {e}")

    # If LLM fails, return the original input as a single item
    return [user_input]


def create_splitter_node_llm():
    """Create a splitter node that uses LLM for text splitting."""
    return SplitterNode(
        name="splitter_node_llm",
        splitter_function=split_text_llm,
        children=[],
        description="Split complex user inputs into multiple intents using LLM",
    )


# Create a wrapper for evaluation that returns chunks directly
class SplitterWrapper:
    """Wrapper for splitter node that returns chunks as output for evaluation."""

    def __init__(self, splitter_node):
        self.name = splitter_node.name
        self.splitter_function = splitter_node.splitter_function

    def execute(self, user_input: str, context=None):
        chunks = self.splitter_function(user_input, debug=False, context=context)
        return type("Result", (), {"success": True, "output": chunks, "error": None})()


# Export the node creation function
splitter_node_llm = SplitterWrapper(create_splitter_node_llm())
