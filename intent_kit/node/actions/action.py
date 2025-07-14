"""
Action node implementation.

This module provides the ActionNode class which is a leaf node representing
an executable action with argument extraction and validation.
"""

from typing import Any, Callable, Dict, Optional, Set, Type, List, Union
from ..base import TreeNode
from ..enums import NodeType
from ..types import ExecutionResult, ExecutionError
from intent_kit.context import IntentContext
from intent_kit.context.dependencies import declare_dependencies
from .remediation import (
    get_remediation_strategy,
    RemediationStrategy,
)


class ActionNode(TreeNode):
    """Leaf node representing an executable action with argument extraction and validation."""

    def __init__(
        self,
        name: Optional[str],
        param_schema: Dict[str, Type],
        action: Callable[..., Any],
        arg_extractor: Callable[[str, Optional[Dict[str, Any]]], Dict[str, Any]],
        context_inputs: Optional[Set[str]] = None,
        context_outputs: Optional[Set[str]] = None,
        input_validator: Optional[Callable[[Dict[str, Any]], bool]] = None,
        output_validator: Optional[Callable[[Any], bool]] = None,
        description: str = "",
        parent: Optional["TreeNode"] = None,
        remediation_strategies: Optional[List[Union[str, RemediationStrategy]]] = None,
    ):
        super().__init__(name=name, description=description, children=[], parent=parent)
        self.param_schema = param_schema
        self.action = action
        self.arg_extractor = arg_extractor
        self.context_inputs = context_inputs or set()
        self.context_outputs = context_outputs or set()
        self.input_validator = input_validator
        self.output_validator = output_validator
        self.context_dependencies = declare_dependencies(
            inputs=self.context_inputs,
            outputs=self.context_outputs,
            description=f"Context dependencies for intent '{self.name}'",
        )

        # Store remediation strategies
        self.remediation_strategies = remediation_strategies or []

    @property
    def node_type(self) -> NodeType:
        """Get the type of this node."""
        return NodeType.ACTION

    def execute(
        self, user_input: str, context: Optional[IntentContext] = None
    ) -> ExecutionResult:
        try:
            context_dict: Optional[Dict[str, Any]] = None
            if context:
                context_dict = {
                    key: context.get(key)
                    for key in self.context_inputs
                    if context.has(key)
                }
            extracted_params = self.arg_extractor(user_input, context_dict or {})
        except Exception as e:
            self.logger.error(
                f"Argument extraction failed for intent '{self.name}' (Path: {'.'.join(self.get_path())}): {type(e).__name__}: {str(e)}"
            )
            return ExecutionResult(
                success=False,
                node_name=self.name,
                node_path=self.get_path(),
                node_type=NodeType.ACTION,
                input=user_input,
                output=None,
                error=ExecutionError(
                    error_type=type(e).__name__,
                    message=str(e),
                    node_name=self.name,
                    node_path=self.get_path(),
                ),
                params=None,
                children_results=[],
            )
        if self.input_validator:
            try:
                if not self.input_validator(extracted_params):
                    self.logger.error(
                        f"Input validation failed for intent '{self.name}' (Path: {'.'.join(self.get_path())})"
                    )
                    return ExecutionResult(
                        success=False,
                        node_name=self.name,
                        node_path=self.get_path(),
                        node_type=NodeType.ACTION,
                        input=user_input,
                        output=None,
                        error=ExecutionError(
                            error_type="InputValidationError",
                            message="Input validation failed",
                            node_name=self.name,
                            node_path=self.get_path(),
                        ),
                        params=extracted_params,
                        children_results=[],
                    )
            except Exception as e:
                self.logger.error(
                    f"Input validation error for intent '{self.name}' (Path: {'.'.join(self.get_path())}): {type(e).__name__}: {str(e)}"
                )
                return ExecutionResult(
                    success=False,
                    node_name=self.name,
                    node_path=self.get_path(),
                    node_type=NodeType.ACTION,
                    input=user_input,
                    output=None,
                    error=ExecutionError(
                        error_type=type(e).__name__,
                        message=str(e),
                        node_name=self.name,
                        node_path=self.get_path(),
                    ),
                    params=extracted_params,
                    children_results=[],
                )
        try:
            validated_params = self._validate_types(extracted_params)
        except Exception as e:
            self.logger.error(
                f"Type validation error for intent '{self.name}' (Path: {'.'.join(self.get_path())}): {type(e).__name__}: {str(e)}"
            )
            return ExecutionResult(
                success=False,
                node_name=self.name,
                node_path=self.get_path(),
                node_type=NodeType.ACTION,
                input=user_input,
                output=None,
                error=ExecutionError(
                    error_type=type(e).__name__,
                    message=str(e),
                    node_name=self.name,
                    node_path=self.get_path(),
                ),
                params=extracted_params,
                children_results=[],
            )
        try:
            if context is not None:
                output = self.action(**validated_params, context=context)
            else:
                output = self.action(**validated_params)
        except Exception as e:
            self.logger.error(
                f"Action execution error for intent '{self.name}' (Path: {'.'.join(self.get_path())}): {type(e).__name__}: {str(e)}"
            )

            # Try remediation strategies
            error = ExecutionError(
                error_type=type(e).__name__,
                message=str(e),
                node_name=self.name,
                node_path=self.get_path(),
            )

            remediation_result = self._execute_remediation_strategies(
                user_input=user_input,
                context=context,
                original_error=error,
                validated_params=validated_params,
            )

            if remediation_result:
                return remediation_result

            # If no remediation succeeded, return the original error
            return ExecutionResult(
                success=False,
                node_name=self.name,
                node_path=self.get_path(),
                node_type=NodeType.ACTION,
                input=user_input,
                output=None,
                error=error,
                params=validated_params,
                children_results=[],
            )
        if self.output_validator:
            try:
                if not self.output_validator(output):
                    self.logger.error(
                        f"Output validation failed for intent '{self.name}' (Path: {'.'.join(self.get_path())})"
                    )
                    return ExecutionResult(
                        success=False,
                        node_name=self.name,
                        node_path=self.get_path(),
                        node_type=NodeType.ACTION,
                        input=user_input,
                        output=None,
                        error=ExecutionError(
                            error_type="OutputValidationError",
                            message="Output validation failed",
                            node_name=self.name,
                            node_path=self.get_path(),
                        ),
                        params=validated_params,
                        children_results=[],
                    )
            except Exception as e:
                self.logger.error(
                    f"Output validation error for intent '{self.name}' (Path: {'.'.join(self.get_path())}): {type(e).__name__}: {str(e)}"
                )
                return ExecutionResult(
                    success=False,
                    node_name=self.name,
                    node_path=self.get_path(),
                    node_type=NodeType.ACTION,
                    input=user_input,
                    output=None,
                    error=ExecutionError(
                        error_type=type(e).__name__,
                        message=str(e),
                        node_name=self.name,
                        node_path=self.get_path(),
                    ),
                    params=validated_params,
                    children_results=[],
                )

        # Update context with outputs
        if context is not None:
            for key in self.context_outputs:
                if hasattr(output, key):
                    context.set(key, getattr(output, key), self.name)
                elif isinstance(output, dict) and key in output:
                    context.set(key, output[key], self.name)

        return ExecutionResult(
            success=True,
            node_name=self.name,
            node_path=self.get_path(),
            node_type=NodeType.ACTION,
            input=user_input,
            output=output,
            error=None,
            params=validated_params,
            children_results=[],
        )

    def _execute_remediation_strategies(
        self,
        user_input: str,
        context: Optional[IntentContext] = None,
        original_error: Optional[ExecutionError] = None,
        validated_params: Optional[Dict[str, Any]] = None,
    ) -> Optional[ExecutionResult]:
        """Execute remediation strategies in order until one succeeds."""
        for strategy in self.remediation_strategies:
            try:
                if isinstance(strategy, str):
                    strategy_instance = get_remediation_strategy(strategy)
                else:
                    strategy_instance = strategy

                if strategy_instance:
                    remediation_result = strategy_instance.execute(
                        node_name=self.name or "unknown",
                        user_input=user_input,
                        context=context,
                        original_error=original_error,
                        handler_func=self.action,
                        validated_params=validated_params,
                    )
                    if remediation_result and remediation_result.success:
                        self.logger.info(
                            f"Remediation strategy '{strategy_instance.__class__.__name__}' succeeded for intent '{self.name}'"
                        )
                        return remediation_result
            except Exception as e:
                self.logger.error(
                    f"Remediation strategy execution failed for intent '{self.name}': {type(e).__name__}: {str(e)}"
                )

        return None

    def _validate_types(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and convert parameter types according to the schema."""
        validated_params: Dict[str, Any] = {}
        for param_name, param_type in self.param_schema.items():
            if param_name not in params:
                raise ValueError(f"Missing required parameter: {param_name}")

            param_value = params[param_name]
            try:
                if param_type is str:
                    validated_params[param_name] = str(param_value)
                elif param_type is int:
                    validated_params[param_name] = int(param_value)
                elif param_type is float:
                    validated_params[param_name] = float(param_value)
                elif param_type is bool:
                    if isinstance(param_value, str):
                        validated_params[param_name] = param_value.lower() in (
                            "true",
                            "1",
                            "yes",
                            "on",
                        )
                    else:
                        validated_params[param_name] = bool(param_value)
                else:
                    validated_params[param_name] = param_value
            except (ValueError, TypeError) as e:
                raise ValueError(
                    f"Invalid type for parameter '{param_name}': expected {param_type.__name__}, got {type(param_value).__name__}"
                ) from e

        return validated_params
