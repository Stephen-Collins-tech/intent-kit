#!/usr/bin/env python3
"""
Minimal Example: Custom LLM Client Demo (real HTTP, no mock)

This shows how to implement a real custom LLM client (mirroring OpenAIClient structure)
and use it in an intent graph for both classification and parameter extraction.
"""
import re
import os





logger = Logger(__name__)

# Safe import of openai
try:


    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    logger.warning(
        "OpenAI package not found. Please install it with: pip install openai"
    )


class ExampleLLMClient(BaseLLMClient):
    """Custom LLM client that uses OpenAI API for real LLM responses."""

    def __init__def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4.1-nano"): -> None:
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
                        "content": "You are a helpful assistant that extracts parameters and classifies intents accurately.",
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
            logger.error(f"OpenAI API call failed: {e}")
            # Fallback to simple rule-based extraction
            return self._fallback_extraction(prompt)

    def _fallback_extraction(self, prompt: str) -> str:
        """Fallback extraction when OpenAI API fails."""
        # Extract user input from the prompt
        user_input_match = re.search(r"User Input: (.+?)(?:\n|$)", prompt)
        if not user_input_match:
            return ""

        user_input = user_input_match.group(1).strip()

        # Extract parameter names from the prompt
        param_names = []
        param_match = re.search(
            r"Required Parameters:\n(.*?)(?:\n\n|$)", prompt, re.DOTALL
        )
        if param_match:
            param_lines = param_match.group(1).strip().split("\n")
            for line in param_lines:
                if line.strip().startswith("- "):
                    param_name = line.strip()[2:].split(":")[0].strip()
                    param_names.append(param_name)

        # Simple extraction rules
        extracted_params = []

        for param_name in param_names:
            if param_name == "name":
                # Extract name from common patterns
                name_match = re.search(
                    r"(
                        ?:my name is|i'm|i am|call me|hello,? i'm|hi,? i'm)\s+([a-zA-Z]+)",                    user_input.lower(),
                )
                if name_match:
                    extracted_params.append(f"name: {name_match.group(1).title()}")
                else:
                    # Try to find a name-like word
                    words = user_input.split()
                    for word in words:
                        if word[0].isupper() and len(word) > 2:
                            extracted_params.append(f"name: {word}")
                            break
                    else:
                        extracted_params.append("name: User")

            elif param_name in ["a", "b"]:
                # Extract numbers for calculations
                numbers = re.findall(r"\d+(?:\.\d+)?", user_input)
                if param_name == "a" and len(numbers) > 0:
                    extracted_params.append(f"a: {numbers[0]}")
                elif param_name == "b" and len(numbers) > 1:
                    extracted_params.append(f"b: {numbers[1]}")
                elif param_name == "b" and len(numbers) == 1:
                    # For "Add 2 and 3", extract the second number
                    add_match = re.search(
                        r"add\s+(\d+)\s+and\s+(\d+)", user_input.lower()
                    )
                    if add_match:
                        if param_name == "a":
                            extracted_params.append(f"a: {add_match.group(1)}")
                        elif param_name == "b":
                            extracted_params.append(f"b: {add_match.group(2)}")

        return "\n".join(extracted_params)


# Simple actions


def greet_action(name: str, **_) -> str:
    return f"Hello {name}!"


def calc_action(a: float, b: float, **_) -> str:
    return f"Sum: {a + b}"


def main() -> None:
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
    print("Using model: gpt-3.5-turbo-0125")
    print()

    # Build intent graph using ExampleLLMClient for both extraction and classification
    try:
        example_client = ExampleLLMClient(api_key=api_key, model="gpt-4.1-nano")
        actions = [
            action(
                name="greet",
                description="Greet the user",
                action_func=greet_action,
                param_schema={"name": str},
                llm_config=example_client,
            ),
            action(
                name="calc",
                description="Add two numbers",
                action_func=calc_action,
                param_schema={"a": float, "b": float},
                llm_config=example_client,
            ),
        ]
        # Custom prompt for name-based classification
        classification_prompt = (
            "You are an intent classifier. Given a user input, select the most appropriate intent from the available options.\n"
            "User Input: {user_input}\n\n"
            "Available Intents (names):\n{node_descriptions}\n\n"
            "Instructions:\n"
            "- Analyze the user input carefully\n"
            "- Select the intent name (
                not a number) that best matches the user's request\n"            "- For 'greet' intent: Choose this for greetings, introductions, name sharing, or any social interaction\n"
            "- For 'calc' intent: Choose this for mathematical operations, calculations, adding numbers\n"
            "- Return only the name of the intent (e.g., greet, calc)\n"
            "- If no intent matches, return 'none'\n\n"
            "Examples:\n"
            "- 'My name is Alice' → greet\n"
            "- 'Hello, I'm Bob' → greet\n"
            "- 'Add 2 and 3' → calc\n"
            "- 'Calculate 10 plus 5' → calc\n\n"
            "Your choice (intent name only):"
        )
        classifier = llm_classifier(
            name="root",
            children=actions,
            llm_config=example_client,
            description="Classify user intent",
            classification_prompt=classification_prompt,
        )
        graph = IntentGraphBuilder().root(classifier).build()

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
