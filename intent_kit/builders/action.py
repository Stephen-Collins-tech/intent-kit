"""
Action builder for creating action nodes with fluent interface.

This module provides a builder class for creating ActionNode instances
with a more readable and type-safe approach.
"""

from typing import Any, Callable, Dict, Type, Set, List, Optional, Union
from intent_kit.node.actions import ActionNode
from intent_kit.node.actions import RemediationStrategy
from intent_kit.utils.param_extraction import create_arg_extractor
from intent_kit.utils.node_factory import create_action_node
from .base import Builder


class ActionBuilder(Builder):
    """Builder for creating action nodes with fluent interface."""

    def __init__(self, name: str):
        """Initialize the action builder.

        Args:
            name: Name of the action node
        """
        super().__init__(name)
        self.action_func: Optional[Callable[..., Any]] = None
        self.param_schema: Dict[str, Type] = {}
        self.llm_config: Optional[Dict[str, Any]] = None
        self.extraction_prompt: Optional[str] = None
        self.context_inputs: Optional[Set[str]] = None
        self.context_outputs: Optional[Set[str]] = None
        self.input_validator: Optional[Callable[[Dict[str, Any]], bool]] = None
        self.output_validator: Optional[Callable[[Any], bool]] = None
        self.remediation_strategies: Optional[List[Union[str, RemediationStrategy]]] = (
            None
        )

    def with_action(self, action_func: Callable[..., Any]) -> "ActionBuilder":
        """Set the action function.

        Args:
            action_func: Function to execute when this action is triggered

        Returns:
            Self for method chaining
        """
        self.action_func = action_func
        return self

    def with_param_schema(self, param_schema: Dict[str, Type]) -> "ActionBuilder":
        """Set the parameter schema.

        Args:
            param_schema: Dictionary mapping parameter names to their types

        Returns:
            Self for method chaining
        """
        self.param_schema = param_schema
        return self

    def with_llm_config(self, llm_config: Dict[str, Any]) -> "ActionBuilder":
        """Set the LLM configuration for argument extraction.

        Args:
            llm_config: LLM configuration dictionary

        Returns:
            Self for method chaining
        """
        self.llm_config = llm_config
        return self

    def with_extraction_prompt(self, extraction_prompt: str) -> "ActionBuilder":
        """Set a custom extraction prompt.

        Args:
            extraction_prompt: Custom prompt for LLM argument extraction

        Returns:
            Self for method chaining
        """
        self.extraction_prompt = extraction_prompt
        return self

    def with_context_inputs(self, context_inputs: Set[str]) -> "ActionBuilder":
        """Set context inputs for the action.

        Args:
            context_inputs: Set of context keys this action reads from

        Returns:
            Self for method chaining
        """
        self.context_inputs = context_inputs
        return self

    def with_context_outputs(self, context_outputs: Set[str]) -> "ActionBuilder":
        """Set context outputs for the action.

        Args:
            context_outputs: Set of context keys this action writes to

        Returns:
            Self for method chaining
        """
        self.context_outputs = context_outputs
        return self

    def with_input_validator(
        self, input_validator: Callable[[Dict[str, Any]], bool]
    ) -> "ActionBuilder":
        """Set the input validator function.

        Args:
            input_validator: Function to validate extracted parameters

        Returns:
            Self for method chaining
        """
        self.input_validator = input_validator
        return self

    def with_output_validator(
        self, output_validator: Callable[[Any], bool]
    ) -> "ActionBuilder":
        """Set the output validator function.

        Args:
            output_validator: Function to validate action output

        Returns:
            Self for method chaining
        """
        self.output_validator = output_validator
        return self

    def with_remediation_strategies(
        self, strategies: List[Union[str, RemediationStrategy]]
    ) -> "ActionBuilder":
        """Set remediation strategies.

        Args:
            strategies: List of remediation strategies (strings or strategy objects)

        Returns:
            Self for method chaining
        """
        self.remediation_strategies = strategies
        return self

    def build(self) -> ActionNode:
        """Build and return the ActionNode instance.

        Returns:
            Configured ActionNode instance

        Raises:
            ValueError: If required fields are missing
        """
        # Validate required fields using base class method
        self._validate_required_fields(
            [
                ("action function", self.action_func, "with_action"),
                ("parameter schema", self.param_schema, "with_param_schema"),
            ]
        )

        # Create argument extractor
        arg_extractor = create_arg_extractor(
            param_schema=self.param_schema,
            llm_config=self.llm_config,
            extraction_prompt=self.extraction_prompt,
            node_name=self.name,
        )

        # Type assertion since validation ensures these are not None
        assert self.action_func is not None
        assert self.param_schema is not None
        action_func = self.action_func
        param_schema = self.param_schema

        return create_action_node(
            name=self.name,
            description=self.description,
            action_func=action_func,
            param_schema=param_schema,
            arg_extractor=arg_extractor,
            context_inputs=self.context_inputs,
            context_outputs=self.context_outputs,
            input_validator=self.input_validator,
            output_validator=self.output_validator,
            remediation_strategies=self.remediation_strategies,
        )
