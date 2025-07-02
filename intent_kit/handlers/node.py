from typing import Any, Callable, Dict, Optional, Set, Type
from intent_kit.node.base import TreeNode
from intent_kit.node.enums import NodeType
from intent_kit.context import IntentContext
from intent_kit.context.dependencies import declare_dependencies
from intent_kit.node.types import ExecutionResult, ExecutionError


class HandlerNode(TreeNode):
    """Leaf node representing an executable handler with argument extraction and validation."""

    def __init__(
        self,
        name: Optional[str],
        param_schema: Dict[str, Type],
        handler: Callable[..., Any],
        arg_extractor: Callable[[str, Optional[Dict[str, Any]]], Dict[str, Any]],
        context_inputs: Optional[Set[str]] = None,
        context_outputs: Optional[Set[str]] = None,
        input_validator: Optional[Callable[[Dict[str, Any]], bool]] = None,
        output_validator: Optional[Callable[[Any], bool]] = None,
        description: str = "",
        parent: Optional["TreeNode"] = None
    ):
        super().__init__(name=name, description=description, children=[], parent=parent)
        self.param_schema = param_schema
        self.handler = handler
        self.arg_extractor = arg_extractor
        self.context_inputs = context_inputs or set()
        self.context_outputs = context_outputs or set()
        self.input_validator = input_validator
        self.output_validator = output_validator
        self.context_dependencies = declare_dependencies(
            inputs=self.context_inputs,
            outputs=self.context_outputs,
            description=f"Context dependencies for intent '{self.name}'"
        )

    @property
    def node_type(self) -> NodeType:
        """Get the type of this node."""
        return NodeType.HANDLER

    def execute(self, user_input: str, context: Optional[IntentContext] = None) -> ExecutionResult:
        try:
            context_dict: Optional[Dict[str, Any]] = None
            if context:
                context_dict = {key: context.get(
                    key) for key in self.context_inputs if context.has(key)}
            extracted_params = self.arg_extractor(
                user_input, context_dict or {})
        except Exception as e:
            self.logger.error(
                f"Argument extraction failed for intent '{self.name}' (Path: {'.'.join(self.get_path())}): {type(e).__name__}: {str(e)}")
            return ExecutionResult(
                success=False,
                node_name=self.name,
                node_path=self.get_path(),
                node_type=NodeType.HANDLER,
                input=user_input,
                output=None,
                error=ExecutionError(
                    error_type=type(e).__name__,
                    message=str(e),
                    node_name=self.name,
                    node_path=self.get_path()
                ),
                params=None,
                children_results=[]
            )
        if self.input_validator:
            try:
                if not self.input_validator(extracted_params):
                    self.logger.error(
                        f"Input validation failed for intent '{self.name}' (Path: {'.'.join(self.get_path())})")
                    return ExecutionResult(
                        success=False,
                        node_name=self.name,
                        node_path=self.get_path(),
                        node_type=NodeType.HANDLER,
                        input=user_input,
                        output=None,
                        error=ExecutionError(
                            error_type="InputValidationError",
                            message="Input validation failed",
                            node_name=self.name,
                            node_path=self.get_path()
                        ),
                        params=extracted_params,
                        children_results=[]
                    )
            except Exception as e:
                self.logger.error(
                    f"Input validation error for intent '{self.name}' (Path: {'.'.join(self.get_path())}): {type(e).__name__}: {str(e)}")
                return ExecutionResult(
                    success=False,
                    node_name=self.name,
                    node_path=self.get_path(),
                    node_type=NodeType.HANDLER,
                    input=user_input,
                    output=None,
                    error=ExecutionError(
                        error_type=type(e).__name__,
                        message=str(e),
                        node_name=self.name,
                        node_path=self.get_path()
                    ),
                    params=extracted_params,
                    children_results=[]
                )
        try:
            validated_params = self._validate_types(extracted_params)
        except Exception as e:
            self.logger.error(
                f"Type validation error for intent '{self.name}' (Path: {'.'.join(self.get_path())}): {type(e).__name__}: {str(e)}")
            return ExecutionResult(
                success=False,
                node_name=self.name,
                node_path=self.get_path(),
                node_type=NodeType.HANDLER,
                input=user_input,
                output=None,
                error=ExecutionError(
                    error_type=type(e).__name__,
                    message=str(e),
                    node_name=self.name,
                    node_path=self.get_path()
                ),
                params=extracted_params,
                children_results=[]
            )
        try:
            if context is not None:
                output = self.handler(**validated_params, context=context)
            else:
                output = self.handler(**validated_params)
        except Exception as e:
            self.logger.error(
                f"Handler execution error for intent '{self.name}' (Path: {'.'.join(self.get_path())}): {type(e).__name__}: {str(e)}")
            return ExecutionResult(
                success=False,
                node_name=self.name,
                node_path=self.get_path(),
                node_type=NodeType.HANDLER,
                input=user_input,
                output=None,
                error=ExecutionError(
                    error_type=type(e).__name__,
                    message=str(e),
                    node_name=self.name,
                    node_path=self.get_path()
                ),
                params=validated_params,
                children_results=[]
            )
        if self.output_validator:
            try:
                if not self.output_validator(output):
                    self.logger.error(
                        f"Output validation failed for intent '{self.name}' (Path: {'.'.join(self.get_path())})")
                    return ExecutionResult(
                        success=False,
                        node_name=self.name,
                        node_path=self.get_path(),
                        node_type=NodeType.HANDLER,
                        input=user_input,
                        output=output,
                        error=ExecutionError(
                            error_type="OutputValidationError",
                            message="Output validation failed",
                            node_name=self.name,
                            node_path=self.get_path()
                        ),
                        params=validated_params,
                        children_results=[]
                    )
            except Exception as e:
                self.logger.error(
                    f"Output validation error for intent '{self.name}' (Path: {'.'.join(self.get_path())}): {type(e).__name__}: {str(e)}")
                return ExecutionResult(
                    success=False,
                    node_name=self.name,
                    node_path=self.get_path(),
                    node_type=NodeType.HANDLER,
                    input=user_input,
                    output=output,
                    error=ExecutionError(
                        error_type=type(e).__name__,
                        message=str(e),
                        node_name=self.name,
                        node_path=self.get_path()
                    ),
                    params=validated_params,
                    children_results=[]
                )
        return ExecutionResult(
            success=True,
            node_name=self.name,
            node_path=self.get_path(),
            node_type=NodeType.HANDLER,
            input=user_input,
            output=output,
            error=None,
            params=validated_params,
            children_results=[]
        )

    def _validate_types(self, params: Dict[str, Any]) -> Dict[str, Any]:
        validated_params = {}
        for param_name, expected_type in self.param_schema.items():
            if param_name not in params:
                self.logger.error(
                    f"Missing required parameter '{param_name}' for intent '{self.name}' (Path: {'.'.join(self.get_path())})")
                raise Exception(f"Missing required parameter '{param_name}'")
            param_value = params[param_name]
            if expected_type == str:
                if not isinstance(param_value, str):
                    self.logger.error(
                        f"Parameter '{param_name}' must be a string, got {type(param_value).__name__} for intent '{self.name}' (Path: {'.'.join(self.get_path())})")
                    raise Exception(
                        f"Parameter '{param_name}' must be a string, got {type(param_value).__name__}")
            elif expected_type == int:
                try:
                    param_value = int(param_value)
                except (ValueError, TypeError) as e:
                    self.logger.error(
                        f"Parameter '{param_name}' must be an integer, got {type(param_value).__name__} for intent '{self.name}' (Path: {'.'.join(self.get_path())}): {type(e).__name__}: {str(e)}")
                    raise Exception(
                        f"Parameter '{param_name}' must be an integer, got {type(param_value).__name__}: {type(e).__name__}: {str(e)}")
            elif expected_type == float:
                try:
                    param_value = float(param_value)
                except (ValueError, TypeError) as e:
                    self.logger.error(
                        f"Parameter '{param_name}' must be a number, got {type(param_value).__name__} for intent '{self.name}' (Path: {'.'.join(self.get_path())}): {type(e).__name__}: {str(e)}")
                    raise Exception(
                        f"Parameter '{param_name}' must be a number, got {type(param_value).__name__}: {type(e).__name__}: {str(e)}")
            elif expected_type == bool:
                if isinstance(param_value, str):
                    param_value = param_value.lower() in ('true', '1', 'yes', 'on')
                elif not isinstance(param_value, bool):
                    self.logger.error(
                        f"Parameter '{param_name}' must be a boolean, got {type(param_value).__name__} for intent '{self.name}' (Path: {'.'.join(self.get_path())})")
                    raise Exception(
                        f"Parameter '{param_name}' must be a boolean, got {type(param_value).__name__}")
            validated_params[param_name] = param_value
        return validated_params
