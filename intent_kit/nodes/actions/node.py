"""
Action node implementation.

This module provides the ActionNode class which is a leaf node
that executes actions with argument extraction and validation.
"""

import re
import json
from typing import Any, Callable, Dict, List, Optional, Type, Union
from ..base_node import TreeNode
from ..enums import NodeType
from ..types import ExecutionResult, ExecutionError
from intent_kit.context import Context
from intent_kit.strategies import InputValidator, OutputValidator
from intent_kit.extraction import ArgumentSchema
from intent_kit.utils.type_validator import (
    validate_type,
    TypeValidationError,
    resolve_type,
)


class ActionNode(TreeNode):
    """Leaf node representing an executable action with argument extraction and validation."""

    def __init__(
        self,
        name: str,
        action: Callable[..., Any],
        param_schema: Optional[Dict[str, Union[Type[Any], str]]] = None,
        description: str = "",
        context: Optional[Context] = None,
        input_validator: Optional[InputValidator] = None,
        output_validator: Optional[OutputValidator] = None,
        llm_config: Optional[Dict[str, Any]] = None,
        parent: Optional["TreeNode"] = None,
        children: Optional[List["TreeNode"]] = None,
        custom_prompt: Optional[str] = None,
        prompt_template: Optional[str] = None,
        arg_schema: Optional[ArgumentSchema] = None,
    ):
        super().__init__(
            name=name,
            description=description,
            children=children or [],
            parent=parent,
            llm_config=llm_config,
        )
        self.action = action
        self.param_schema = param_schema or {}
        self._llm_config = llm_config or {}

        # Use new Context class
        self.context = context or Context()

        # Use new validator classes
        self.input_validator = input_validator
        self.output_validator = output_validator

        # New extraction system
        self.arg_schema = arg_schema or self._build_arg_schema()

        # Prompt configuration
        self.custom_prompt = custom_prompt
        self.prompt_template = prompt_template or self._get_default_prompt_template()

    def _build_arg_schema(self) -> ArgumentSchema:
        """Build argument schema from param_schema."""
        schema: ArgumentSchema = {"type": "object", "properties": {}, "required": []}

        for param_name, param_type in self.param_schema.items():
            # Handle both string type names and actual Python types
            if isinstance(param_type, str):
                type_name = param_type
            elif hasattr(param_type, "__name__"):
                type_name = param_type.__name__
            else:
                type_name = str(param_type)

            schema["properties"][param_name] = {
                "type": type_name,
                "description": f"Parameter {param_name}",
            }
            schema["required"].append(param_name)

        return schema

    def _get_default_prompt_template(self) -> str:
        """Get the default action prompt template."""
        return """You are an action executor. Given a user input, extract the required parameters and execute the action.

User Input: {user_input}

Action: {action_name}
Description: {action_description}

Required Parameters:
{param_descriptions}

{context_info}

Instructions:
- Extract the required parameters from the user input
- Consider the available context information to help with extraction
- Return the parameters as a JSON object
- If a parameter is not found, use a reasonable default or null
- Be specific and accurate in your extraction

Return only the JSON object with the extracted parameters:"""

    def _build_prompt(self, user_input: str, context: Optional[Context] = None) -> str:
        """Build the action prompt."""
        # Build parameter descriptions
        param_descriptions = []
        for param_name, param_type in self.param_schema.items():
            # Handle both string type names and actual Python types
            if isinstance(param_type, str):
                type_name = param_type
            elif hasattr(param_type, "__name__"):
                type_name = param_type.__name__
            else:
                type_name = str(param_type)

            param_descriptions.append(
                f"- {param_name} ({type_name}): Parameter {param_name}"
            )

        # Build context info
        context_info = ""
        if context:
            context_dict = context.export_to_dict()
            if context_dict:
                context_info = "\n\nContext Information:\n"
                for key, value in context_dict.items():
                    context_info += f"- {key}: {value}\n"

        return self.prompt_template.format(
            user_input=user_input,
            action_name=self.name,
            action_description=self.description,
            param_descriptions="\n".join(param_descriptions),
            context_info=context_info,
        )

    def _parse_response(self, response: Any) -> Dict[str, Any]:
        """Parse the LLM response to extract parameters."""
        try:
            # Clean up the response
            self.logger.debug_structured(
                {
                    "response": response,
                    "response_type": type(response).__name__,
                },
                "Action Response _parse_response",
            )

            if isinstance(response, dict):
                # Check if response has raw_content field (LLM client wrapper)
                if "raw_content" in response:
                    raw_content = response["raw_content"]
                    if isinstance(raw_content, dict):
                        return raw_content
                    elif isinstance(raw_content, str):
                        return self._extract_key_value_pairs(raw_content)

                # Direct dict response
                return response

            elif isinstance(response, str):
                # Try to extract JSON from the response
                return self._extract_key_value_pairs(response)
            else:
                self.logger.warning(f"Unexpected response type: {type(response)}")
                return {}

        except Exception as e:
            self.logger.error(f"Error parsing response: {e}")
            return {}

    def _extract_key_value_pairs(self, text: str) -> Dict[str, Any]:
        """Extract key-value pairs from text using regex patterns."""
        # Try to find JSON object
        json_match = re.search(r"\{[^{}]*\}", text)
        if json_match:
            try:
                return json.loads(json_match.group())
            except json.JSONDecodeError:
                pass

        # Fallback to regex extraction
        result = {}
        # Pattern for key: value or "key": value
        pattern = r'["\']?(\w+)["\']?\s*:\s*["\']?([^"\',\s]+)["\']?'
        matches = re.findall(pattern, text)

        for key, value in matches:
            # Try to convert to appropriate type
            if value.lower() in ("true", "false"):
                result[key] = value.lower() == "true"
            elif value.isdigit():
                result[key] = int(value)
            elif value.replace(".", "").isdigit():
                result[key] = float(value)
            else:
                result[key] = value

        return result

    def _validate_and_cast_data(self, parsed_data: Any) -> Dict[str, Any]:
        """Validate and cast the parsed data to the expected types."""
        if not isinstance(parsed_data, dict):
            raise TypeValidationError(
                f"Expected dict, got {type(parsed_data)}", parsed_data, dict
            )

        validated_data = {}
        self.logger.debug_structured(
            {"parsed_data": parsed_data, "param_schema": self.param_schema},
            "ActionNode _validate_and_cast_data",
        )
        for param_name, param_type in self.param_schema.items():
            self.logger.debug(
                f"Validating parameter: {param_name} with type: {param_type}"
            )
            if param_name in parsed_data:
                try:
                    # Resolve the type if it's a string
                    resolved_type = resolve_type(param_type)
                    self.logger.debug_structured(
                        {
                            "param_name": param_name,
                            "param_type": param_type,
                            "resolved_type": resolved_type,
                            "parsed_data": parsed_data[param_name],
                        },
                        "ActionNode _validate_and_cast_data BEFORE VALIDATION",
                    )
                    validated_data[param_name] = validate_type(
                        parsed_data[param_name], resolved_type
                    )
                except TypeValidationError as e:
                    self.logger.warning(
                        f"Parameter validation failed for {param_name}: {e}"
                    )
                    # Use the original value if validation fails
                    validated_data[param_name] = parsed_data[param_name]
            else:
                # Parameter not found, use None as default
                validated_data[param_name] = None

        # Apply operation normalization for calculate actions
        validated_data = self._normalize_operation(validated_data)

        return validated_data

    def _normalize_operation(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize operation parameter for calculate actions."""
        self.logger.debug(f"Normalizing operation params: {params}")

        if "operation" in params and isinstance(params["operation"], str):
            operation = params["operation"].lower()
            self.logger.debug(f"Processing operation: '{operation}'")

            # Map various operation formats to standard symbols
            operation_map = {
                "+": "+",
                "add": "+",
                "addition": "+",
                "plus": "+",
                "-": "-",
                "subtract": "-",
                "subtraction": "-",
                "minus": "-",
                "*": "*",
                "multiply": "*",
                "multiplication": "*",
                "times": "*",
                "/": "/",
                "divide": "/",
                "division": "/",
                "divided by": "/",
            }

            if operation in operation_map:
                params["operation"] = operation_map[operation]
                self.logger.debug(
                    f"Normalized operation '{operation}' to '{params['operation']}'"
                )
            else:
                self.logger.warning(f"Unknown operation: '{operation}'")
        else:
            self.logger.warning(
                f"No operation found in params or not a string: {params.get('operation', 'NOT_FOUND')}"
            )

        return params

    def _execute_action_with_llm(
        self, user_input: str, context: Optional[Context] = None
    ) -> ExecutionResult:
        """Execute the action using LLM for parameter extraction."""
        try:
            # Build prompt
            prompt = self.custom_prompt or self._build_prompt(user_input, context)

            # Generate response using LLM
            if self.llm_client:
                # Get model from config or use default
                model = self._llm_config.get("model", "default")
                llm_response = self.llm_client.generate(
                    prompt, model=model, expected_type=dict
                )

                # Parse the response
                parsed_data = self._parse_response(llm_response.output)

                # Validate and cast the data
                validated_params = self._validate_and_cast_data(parsed_data)

                # Apply input validation if available
                if self.input_validator:
                    if not self.input_validator.validate(validated_params):
                        return ExecutionResult(
                            success=False,
                            node_name=self.name,
                            node_path=[self.name],
                            node_type=NodeType.ACTION,
                            input=user_input,
                            output=None,
                            error=ExecutionError(
                                error_type="InputValidationError",
                                message="Input validation failed",
                                node_name=self.name,
                                node_path=[self.name],
                                original_exception=None,
                            ),
                            children_results=[],
                        )

                # Execute the action
                action_result = self.action(**validated_params)

                # Apply output validation if available
                if self.output_validator:
                    if not self.output_validator.validate(action_result):
                        return ExecutionResult(
                            success=False,
                            node_name=self.name,
                            node_path=[self.name],
                            node_type=NodeType.ACTION,
                            input=user_input,
                            output=None,
                            error=ExecutionError(
                                error_type="OutputValidationError",
                                message="Output validation failed",
                                node_name=self.name,
                                node_path=[self.name],
                                original_exception=None,
                            ),
                            children_results=[],
                        )

                return ExecutionResult(
                    success=True,
                    node_name=self.name,
                    node_path=[self.name],
                    node_type=NodeType.ACTION,
                    input=user_input,
                    output=action_result,
                    input_tokens=llm_response.input_tokens,
                    output_tokens=llm_response.output_tokens,
                    cost=llm_response.cost,
                    provider=llm_response.provider,
                    model=llm_response.model,
                    params=validated_params,
                    children_results=[],
                    duration=llm_response.duration,
                )
            else:
                raise ValueError("No LLM client available for parameter extraction")

        except Exception as e:
            self.logger.error(f"Action execution failed: {e}")
            return ExecutionResult(
                success=False,
                node_name=self.name,
                node_path=[self.name],
                node_type=NodeType.ACTION,
                input=user_input,
                output=None,
                error=ExecutionError(
                    error_type="ActionExecutionError",
                    message=f"Action execution failed: {e}",
                    node_name=self.name,
                    node_path=[self.name],
                    original_exception=e,
                ),
                children_results=[],
            )

    @staticmethod
    def from_json(
        node_spec: Dict[str, Any],
        function_registry: Dict[str, Callable],
        llm_config: Optional[Dict[str, Any]] = None,
    ) -> "ActionNode":
        """
        Create an ActionNode from JSON spec.
        Supports function names (resolved via function_registry) or full callable objects (for stateful actions).
        """
        # Extract common node information (same logic as base class)
        node_id = node_spec.get("id") or node_spec.get("name")
        if not node_id:
            raise ValueError(f"Node spec must have 'id' or 'name': {node_spec}")

        name = node_spec.get("name", node_id)
        description = node_spec.get("description", "")
        node_llm_config = node_spec.get("llm_config", {})

        # Merge LLM configs
        if llm_config:
            node_llm_config = {**llm_config, **node_llm_config}

        # Resolve action (function or stateful callable)
        action = node_spec.get("function")
        action_obj = None
        if action is None:
            raise ValueError(f"Action node '{name}' must have a 'function' field")
        elif isinstance(action, str):
            if action not in function_registry:
                raise ValueError(f"Function '{action}' not found in function registry")
            action_obj = function_registry[action]
        elif callable(action):
            action_obj = action
        else:
            raise ValueError(
                f"Invalid action specification for node '{name}': {action}"
            )

        # Get custom prompt from node spec
        custom_prompt = node_spec.get("custom_prompt")
        prompt_template = node_spec.get("prompt_template")

        # Create the node
        node = ActionNode(
            name=name,
            description=description,
            action=action_obj,
            param_schema=node_spec.get("param_schema", {}),
            llm_config=node_llm_config,
            custom_prompt=custom_prompt,
            prompt_template=prompt_template,
        )

        return node

    @property
    def node_type(self) -> NodeType:
        """Get the node type."""
        return NodeType.ACTION

    def execute(
        self, user_input: str, context: Optional[Context] = None
    ) -> ExecutionResult:
        """Execute the action node."""
        try:
            # Execute the action using LLM for parameter extraction
            return self._execute_action_with_llm(user_input, context)
        except Exception as e:
            self.logger.error(f"Action execution failed: {e}")
            return ExecutionResult(
                success=False,
                node_name=self.name,
                node_path=[self.name],
                node_type=NodeType.ACTION,
                input=user_input,
                output=None,
                error=ExecutionError(
                    error_type="ActionExecutionError",
                    message=f"Action execution failed: {e}",
                    node_name=self.name,
                    node_path=[self.name],
                    original_exception=e,
                ),
                children_results=[],
            )
