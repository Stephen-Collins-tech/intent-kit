"""DAG ClassifierNode implementation with LLM integration."""

import time
from typing import Any, Dict, List, Optional, Callable
from intent_kit.core.types import NodeProtocol, ExecutionResult
from intent_kit.core.context import ContextProtocol
from intent_kit.utils.logger import Logger
from intent_kit.services.ai.llm_service import LLMService
from intent_kit.utils.type_coercion import validate_raw_content


class ClassifierNode(NodeProtocol):
    """Classifier node for DAG execution using LLM services."""

    def __init__(
        self,
        name: str,
        output_labels: List[str],
        description: str = "",
        llm_config: Optional[Dict[str, Any]] = None,
        classification_func: Optional[Callable[[str, Any], str]] = None,
        custom_prompt: Optional[str] = None,
        context_read: Optional[List[str]] = None,
        context_write: Optional[List[str]] = None,
    ):
        """Initialize the DAG classifier node.

        Args:
            name: Node name
            output_labels: List of possible output labels
            description: Node description
            llm_config: LLM configuration
            classification_func: Function to perform classification (overrides LLM)
            custom_prompt: Custom prompt for classification
            context_read: List of context keys to read before execution
            context_write: List of context keys to write after execution
        """
        self.name = name
        self.output_labels = output_labels
        self.description = description
        self.llm_config = llm_config or {}
        self.classification_func = classification_func
        self.custom_prompt = custom_prompt
        self.context_read = context_read or []
        self.context_write = context_write or []
        self.logger = Logger(name)

    def execute(self, user_input: str, ctx: ContextProtocol) -> ExecutionResult:
        """Execute the classifier node using LLM or custom function.

        Args:
            user_input: User input string
            ctx: Execution context

        Returns:
            ExecutionResult with classification results
        """
        try:
            # Read context values if specified
            context_data = {}
            for key in self.context_read:
                value = ctx.get(key)
                if value is not None:
                    context_data[key] = value

            # Get LLM service from context
            llm_service = ctx.get("llm_service") if hasattr(ctx, "get") else None

            # Get effective LLM config (node-specific or default from DAG)
            effective_llm_config = self.llm_config
            if not effective_llm_config and hasattr(ctx, "get"):
                # Try to get default config from DAG metadata
                metadata = ctx.get("metadata", {})
                effective_llm_config = metadata.get("default_llm_config", {})

            # Use custom classification function if provided
            if self.classification_func:
                chosen_label = self.classification_func(user_input, context_data)
            elif llm_service and effective_llm_config:
                # Use LLM for classification
                chosen_label = self._classify_with_llm(
                    user_input, ctx, llm_service, effective_llm_config
                )
            else:
                raise ValueError("No classification function or LLM service provided")

            # Validate the chosen label
            self.logger.debug(f"LLM classification result CHOSEN_LABEL: {chosen_label}")
            self.logger.debug(
                f"LLM classification result OUTPUT_LABELS: {self.output_labels}"
            )

            # Use the existing parsing logic to properly match the label
            parsed_label = self._parse_classification_response(chosen_label)
            chosen_label = parsed_label if parsed_label is not None else ""

            if chosen_label not in self.output_labels:
                self.logger.warning(
                    f"Invalid label '{chosen_label}', not in {self.output_labels}"
                )
                chosen_label = ""  # Use empty string instead of None

            # Create context patch with classification result
            context_patch: Dict[str, Any] = {"chosen_label": chosen_label}

            # Add context write operations if specified
            for key in self.context_write:
                if key == "intent.confidence":
                    context_patch[key] = chosen_label
                elif key == "classification.time":
                    context_patch[key] = time.time()
                else:
                    # For other keys, we could add more special cases as needed
                    context_patch[key] = chosen_label

            return ExecutionResult(
                data=chosen_label,  # Return the classification result in data
                # Route to clarification when classification fails
                next_edges=[chosen_label] if chosen_label else ["clarification"],
                terminate=False,  # Classifiers don't terminate
                metrics={},
                context_patch=context_patch,
            )
        except Exception as e:
            self.logger.error(f"Classification failed: {e}")
            return ExecutionResult(
                # Return error info in data
                data=f"ClassificationError: {str(e)}",
                next_edges=None,
                terminate=True,  # Terminate on error
                metrics={},
                context_patch={"error": str(e), "error_type": "ClassificationError"},
            )

    def _classify_with_llm(
        self,
        user_input: str,
        ctx: Any,
        llm_service: LLMService,
        llm_config: Dict[str, Any],
    ) -> str:
        """Classify user input using LLM services."""
        try:
            # Build prompt for classification
            prompt = self._build_classification_prompt(user_input, ctx)

            # Get model from config or use default
            model = llm_config.get("model", "gpt-3.5-turbo")

            # Get client from shared service
            llm_client = llm_service.get_client(llm_config)

            # Get raw response
            raw_response = llm_client.generate(prompt, model=model)

            # Parse the response using the validation utility
            chosen_label = validate_raw_content(raw_response.content, str)
            self.logger.debug(f"LLM classification result CHOSEN_LABEL: {chosen_label}")

            self.logger.info(f"LLM classification result: {chosen_label}")
            return chosen_label

        except Exception as e:
            self.logger.error(f"LLM classification failed: {e}")
            return ""

    def _build_classification_prompt(self, user_input: str, ctx: Any) -> str:
        """Build the classification prompt."""
        if self.custom_prompt:
            return self.custom_prompt.format(user_input=user_input)

        # Build label descriptions
        label_descriptions = []
        for label in self.output_labels:
            label_descriptions.append(f"- {label}")

        label_descriptions_text = "\n".join(label_descriptions)

        # Build context info
        context_info = ""
        if ctx and hasattr(ctx, "snapshot"):
            context_data = ctx.snapshot()
            if context_data:
                context_info = f"\nAvailable Context:\n{context_data}"

        return f"""You are a strict classification specialist. Given a user input, classify it into one of the available categories.

User Input: {user_input}

Classification Task: {self.name}
Description: {self.description}

Available Categories:
{label_descriptions_text}

{context_info}

Instructions:
- Analyze the user input carefully
- Choose the most appropriate category from the available options ONLY
- Return only the category name (exactly as listed above)
- If the input doesn't clearly match any category, return "unknown"
- If the input is ambiguous or could fit multiple categories, return "unknown"
- If the input is about topics not covered by these categories, return "unknown"
- Be strict - only classify if there's a clear, unambiguous match

Return only the category name:"""

    def _parse_classification_response(self, response: Any) -> Optional[str]:
        """Parse the LLM classification response."""
        if isinstance(response, str):
            # Clean up the response
            label = response.strip().lower()

            # Find the best match
            for output_label in self.output_labels:
                if output_label.lower() == label:
                    return output_label

            # Try partial matching
            for output_label in self.output_labels:
                if output_label.lower() in label or label in output_label.lower():
                    return output_label

            self.logger.warning(
                f"Could not match LLM response '{response}' to any label"
            )
            return None
        else:
            self.logger.warning(f"Unexpected response type: {type(response)}")
            return None

    @property
    def context_read_keys(self) -> List[str]:
        """List of context keys to read before execution."""
        return self.context_read

    @property
    def context_write_keys(self) -> List[str]:
        """List of context keys to write after execution."""
        return self.context_write
