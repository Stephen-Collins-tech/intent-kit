"""DAG ExtractorNode implementation for parameter extraction."""

from typing import Any, Dict, Optional, Union, Type, List
from intent_kit.core.types import NodeProtocol, ExecutionResult
from intent_kit.core.context import ContextProtocol
from intent_kit.utils.logger import Logger
from intent_kit.utils.type_coercion import (
    validate_type,
    resolve_type,
    TypeValidationError,
    validate_raw_content,
)


class ExtractorNode(NodeProtocol):
    """Parameter extraction node for DAG execution using LLM services."""

    def __init__(
        self,
        name: str,
        param_schema: Dict[str, Union[Type[Any], str]],
        description: str = "",
        llm_config: Optional[Dict[str, Any]] = None,
        custom_prompt: Optional[str] = None,
        output_key: str = "extracted_params",
        context_read: Optional[List[str]] = None,
        context_write: Optional[List[str]] = None,
    ):
        """Initialize the DAG extractor node.

        Args:
            name: Node name
            param_schema: Parameter schema for extraction
            description: Node description
            llm_config: LLM configuration
            custom_prompt: Custom prompt for parameter extraction
            output_key: Key to store extracted parameters in context
            context_read: List of context keys to read before execution
            context_write: List of context keys to write after execution
        """
        self.name = name
        self.param_schema = param_schema
        self.description = description
        self.llm_config = llm_config or {}
        self.custom_prompt = custom_prompt
        self.output_key = output_key
        self.context_read = context_read or []
        self.context_write = context_write or []
        self.logger = Logger(name)

    def execute(self, user_input: str, ctx: ContextProtocol) -> ExecutionResult:
        """Execute parameter extraction using LLM.

        Args:
            user_input: User input string
            ctx: Execution context

        Returns:
            ExecutionResult with extracted parameters
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

            if not llm_service or not effective_llm_config:
                raise ValueError(
                    "LLM service and config required for parameter extraction"
                )

            # Build prompt for parameter extraction (pass context data for potential use)
            prompt = self._build_prompt(user_input, ctx)

            # Get model from config or use default
            model = effective_llm_config.get("model")
            if not model:
                raise ValueError("LLM model required for parameter extraction")

            # Get client from shared service
            llm_client = llm_service.get_client(effective_llm_config)

            # Generate raw response using LLM
            raw_response = llm_client.generate(prompt, model=model)

            # Parse and validate the extracted parameters using the validation utility
            validated_params = validate_raw_content(raw_response.content, dict)

            # Ensure all required parameters are present with defaults if missing
            validated_params = self._ensure_all_parameters_present(validated_params)

            # Build metrics
            metrics = {}
            if raw_response.input_tokens:
                metrics["input_tokens"] = raw_response.input_tokens
            if raw_response.output_tokens:
                metrics["output_tokens"] = raw_response.output_tokens
            if raw_response.cost:
                metrics["cost"] = raw_response.cost
            if raw_response.duration:
                metrics["duration"] = raw_response.duration

            # Create context patch with extraction results
            context_patch = {
                self.output_key: validated_params,
                "extraction_success": True,
            }

            # Add context write operations if specified
            for key in self.context_write:
                if key == "extraction.confidence":
                    # Could be calculated based on validation
                    context_patch[key] = True
                elif key == "extraction.time":
                    import time

                    context_patch[key] = time.time()
                else:
                    # For other keys, we could add more special cases as needed
                    context_patch[key] = validated_params

            return ExecutionResult(
                data=validated_params,
                next_edges=["success"],  # Continue to next node
                terminate=False,
                metrics=metrics,
                context_patch=context_patch,
            )

        except Exception as e:
            self.logger.error(f"Parameter extraction failed: {e}")
            return ExecutionResult(
                data=None,
                next_edges=None,
                terminate=True,  # Terminate on extraction failure
                metrics={},
                context_patch={
                    "error": str(e),
                    "error_type": "ExtractionError",
                    "extraction_success": False,
                },
            )

    def _build_prompt(self, user_input: str, ctx: Any) -> str:
        """Build the parameter extraction prompt."""
        if self.custom_prompt:
            return self.custom_prompt.format(user_input=user_input)

        # Build parameter descriptions
        param_descriptions = []
        for param_name, param_type in self.param_schema.items():
            if isinstance(param_type, str):
                type_name = param_type
            elif hasattr(param_type, "__name__"):
                type_name = param_type.__name__
            else:
                type_name = str(param_type)

            param_descriptions.append(f"- {param_name} ({type_name})")

        param_descriptions_text = "\n".join(param_descriptions)

        # Build context info
        context_info = ""
        if ctx and hasattr(ctx, "snapshot"):
            context_data = ctx.snapshot()
            if context_data:
                context_info = f"\nAvailable Context:\n{context_data}"

        return f"""You are a parameter extraction specialist. Given a user input, extract the required parameters.

User Input: {user_input}

Extraction Task: {self.name}
Description: {self.description}

Required Parameters:
{param_descriptions_text}

{context_info}

Instructions:
- Extract the required parameters from the user input
- Consider the available context information to help with extraction
- Return the parameters as a JSON object
- If a parameter is not explicitly mentioned, infer it from context or use a sensible default:
  * For names: use "user" or "there" if no specific name is mentioned
  * For numbers: use 0 or 1 as appropriate
  * For strings: use empty string "" if no value is found
  * For booleans: use false if not specified
- Always return ALL required parameters, never omit them
- Be specific and accurate in your extraction

Return only the JSON object with the extracted parameters:"""

    def _parse_response(self, response: Any) -> Dict[str, Any]:
        """Parse the LLM response to extract parameters."""
        if isinstance(response, dict):
            return response
        elif isinstance(response, str):
            # Try to extract JSON from string response
            import json

            try:
                # Find JSON-like content in the response
                start = response.find("{")
                end = response.rfind("}") + 1
                if start != -1 and end != 0:
                    json_str = response[start:end]
                    return json.loads(json_str)
                else:
                    # Fallback: try to parse the entire response
                    return json.loads(response)
            except json.JSONDecodeError:
                self.logger.warning(f"Failed to parse JSON from response: {response}")
                return {}
        else:
            self.logger.warning(f"Unexpected response type: {type(response)}")
            return {}

    def _validate_and_cast_data(self, parsed_data: Any) -> Dict[str, Any]:
        """Validate and cast the parsed data to the expected types."""
        if not isinstance(parsed_data, dict):
            raise TypeValidationError(
                f"Expected dict, got {type(parsed_data)}", parsed_data, dict
            )

        validated_data = {}
        for param_name, param_type in self.param_schema.items():
            if param_name in parsed_data:
                try:
                    resolved_type = resolve_type(param_type)
                    validated_data[param_name] = validate_type(
                        parsed_data[param_name], resolved_type
                    )
                except TypeValidationError as e:
                    self.logger.warning(
                        f"Parameter validation failed for {param_name}: {e}"
                    )
                    validated_data[param_name] = parsed_data[param_name]
            else:
                validated_data[param_name] = None

        return validated_data

    def _ensure_all_parameters_present(
        self, extracted_params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Ensures all required parameters are present in the extracted_params dictionary,
        adding them with default values if they are missing.
        """
        result_params = extracted_params.copy()

        # Ensure all required parameters are present, even if extracted_params was empty
        for param_name, param_type in self.param_schema.items():
            if param_name not in result_params:
                # Provide sensible defaults based on parameter type
                if isinstance(param_type, str):
                    if param_type == "str":
                        result_params[param_name] = ""
                    elif param_type == "int":
                        result_params[param_name] = 0
                    elif param_type == "float":
                        result_params[param_name] = 0.0
                    elif param_type == "bool":
                        result_params[param_name] = False
                    else:
                        result_params[param_name] = ""
                else:
                    # For complex types, try to provide a reasonable default
                    if param_type is str:
                        result_params[param_name] = ""
                    elif param_type is int:
                        result_params[param_name] = 0
                    elif param_type is float:
                        result_params[param_name] = 0.0
                    elif param_type is bool:
                        result_params[param_name] = False
                    else:
                        result_params[param_name] = ""

        return result_params

    @property
    def context_read_keys(self) -> List[str]:
        """List of context keys to read before execution."""
        return self.context_read

    @property
    def context_write_keys(self) -> List[str]:
        """List of context keys to write after execution."""
        return self.context_write
