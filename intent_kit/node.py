from typing import Any, Callable, List, Optional, Dict, Union, Type, Set
from abc import ABC, abstractmethod
from dataclasses import dataclass
import uuid
try:
    from typing import TypedDict
except ImportError:
    from typing_extensions import TypedDict

from intent_kit.utils.logger import Logger
from intent_kit.context import IntentContext
from intent_kit.context.dependencies import ContextDependencies, declare_dependencies
from intent_kit.exceptions import NodeExecutionError, NodeInputValidationError, NodeOutputValidationError


class Node:
    """Base class for all nodes with UUID identification and optional user-defined names."""

    def __init__(self, name: Optional[str] = None, parent: Optional["Node"] = None):
        """
        Initialize a node with optional user-defined name.

        Args:
            name: Optional user-defined name for the node. If None, uses UUID.
            parent: Parent node in the tree structure
        """
        self.node_id = str(uuid.uuid4())
        self._user_name = name
        self.parent = parent

    @property
    def name(self) -> str:
        """Get the node name, using user-defined name if available, otherwise UUID."""
        return self._user_name if self._user_name is not None else self.node_id

    @name.setter
    def name(self, value: str):
        """Set the user-defined name for the node."""
        self._user_name = value

    @property
    def has_user_name(self) -> bool:
        """Check if the node has a user-defined name."""
        return self._user_name is not None

    def get_path(self) -> List[str]:
        """Get the path from root to this node as a list of node names."""
        path = []
        node = self
        while node:
            path.append(node.name)
            node = node.parent
        return list(reversed(path))

    def get_path_string(self) -> str:
        """Get the path as a dot-separated string."""
        return ".".join(self.get_path())

    def get_uuid_path(self) -> List[str]:
        """Get the path from root to this node using UUIDs."""
        path = []
        node = self
        while node:
            path.append(node.node_id)
            node = node.parent
        return list(reversed(path))

    def get_uuid_path_string(self) -> str:
        """Get the UUID path as a dot-separated string."""
        return ".".join(self.get_uuid_path())


class TaxonomyNode(Node, ABC):
    """Base class for all nodes in the intent taxonomy tree."""

    def __init__(self, *, name: Optional[str] = None, description: str, children: List["TaxonomyNode"] = [], parent: Optional["TaxonomyNode"] = None):
        super().__init__(name=name, parent=parent)
        self.logger = Logger(name or "unnamed_node")
        self.description = description
        self.children: List["TaxonomyNode"] = children

        # Set parent reference for all children
        for child in self.children:
            child.parent = self

    @abstractmethod
    def execute(self, user_input: str, context: Optional[IntentContext] = None) -> Dict[str, Any]:
        """Execute the node with the given user input and optional context."""
        pass


class ClassifierNode(TaxonomyNode):
    """Intermediate node that uses a classifier to select child nodes."""

    def __init__(
        self,
        name: Optional[str],
        classifier: Callable[[str, List["TaxonomyNode"], Optional[Dict[str, Any]]], Optional["TaxonomyNode"]],
        children: List["TaxonomyNode"],
        description: str = "",
        parent: Optional["TaxonomyNode"] = None
    ):
        super().__init__(name=name, description=description, children=children, parent=parent)
        self.classifier = classifier

    def execute(self, user_input: str, context: Optional[IntentContext] = None) -> Dict[str, Any]:
        """Execute the node with the given user input and optional context."""
        # Prepare context information for the classifier
        context_dict = None
        if context:
            # Get all available context fields
            context_dict = {}
            for key in context.keys():
                context_dict[key] = context.get(key)

        chosen = self.classifier(user_input, self.children, context_dict)
        if not chosen:
            self.logger.error(
                f"Classifier at '{self.name}' (Path: {'.'.join(self.get_path())}) could not route input.")
            return {
                "intent": None,
                "params": None,
                "output": None,
                "error": f"Classifier at '{self.name}' could not route input."
            }
        self.logger.debug(
            f"Classifier at '{self.name}' routed input to '{chosen.name}'.")
        return chosen.execute(user_input, context)


class IntentNode(TaxonomyNode):
    """Leaf node representing an executable intent with argument extraction and validation."""

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
        parent: Optional["TaxonomyNode"] = None
    ):
        super().__init__(name=name, description=description, children=[], parent=parent)
        self.param_schema = param_schema
        self.handler = handler
        self.arg_extractor = arg_extractor
        self.context_inputs = context_inputs or set()
        self.context_outputs = context_outputs or set()
        self.input_validator = input_validator
        self.output_validator = output_validator

        # Create context dependencies
        self.context_dependencies = declare_dependencies(
            inputs=self.context_inputs,
            outputs=self.context_outputs,
            description=f"Context dependencies for intent '{self.name}'"
        )

    def execute(self, user_input: str, context: Optional[IntentContext] = None) -> Dict[str, Any]:
        """
        Execute the intent with the given user input and optional context.
        Context is always passed as the final parameter to the handler.

        Returns:
            Dict containing:
                - success: Boolean indicating if execution was successful
                - params: Extracted and validated parameters
                - output: Result of handler execution
                - error: Error message if any
        """
        # Step 1: Argument Extraction
        try:
            # Prepare context information for the arg extractor
            context_dict: Optional[Dict[str, Any]] = None
            if context:
                # Get only the context fields this intent needs
                context_dict = {}
                for key in self.context_inputs:
                    if context.has(key):
                        context_dict[key] = context.get(key)

            extracted_params = self.arg_extractor(
                user_input, context_dict or {})
        except Exception as e:
            original_error = e
            self.logger.error(
                f"Argument extraction failed for intent '{self.name}' (Path: {'.'.join(self.get_path())}): {type(original_error).__name__}: {str(original_error)}")
            raise NodeExecutionError(
                node_name=self.name,
                taxonomy_name="unknown",  # Will be set by caller
                error_message=f"Argument extraction failed: {type(original_error).__name__}: {str(original_error)}",
                params=None,
                node_id=self.node_id,
                node_path=self.get_path()
            ) from e

        # Step 2: Input Validation
        if self.input_validator:
            try:
                if not self.input_validator(extracted_params):
                    self.logger.error(
                        f"Input validation failed for intent '{self.name}' (Path: {'.'.join(self.get_path())})")
                    raise NodeInputValidationError(
                        node_name=self.name,
                        taxonomy_name="unknown",  # Will be set by caller
                        validation_error="Input validation failed",
                        input_data=extracted_params,
                        node_id=self.node_id,
                        node_path=self.get_path()
                    )
            except (NodeInputValidationError, NodeOutputValidationError):
                # Re-raise validation errors as-is
                raise
            except Exception as e:
                original_error = e
                self.logger.error(
                    f"Input validation error for intent '{self.name}' (Path: {'.'.join(self.get_path())}): {type(original_error).__name__}: {str(original_error)}")
                raise NodeInputValidationError(
                    node_name=self.name,
                    taxonomy_name="unknown",  # Will be set by caller
                    validation_error=f"Input validation error: {type(original_error).__name__}: {str(original_error)}",
                    input_data=extracted_params,
                    node_id=self.node_id,
                    node_path=self.get_path()
                ) from e

        # Step 3: Type Validation
        try:
            validated_params = self._validate_types(extracted_params)
        except (NodeInputValidationError, NodeOutputValidationError):
            # Re-raise validation errors as-is
            raise
        except Exception as e:
            original_error = e
            self.logger.error(
                f"Type validation error for intent '{self.name}' (Path: {'.'.join(self.get_path())}): {type(original_error).__name__}: {str(original_error)}")
            raise NodeInputValidationError(
                node_name=self.name,
                taxonomy_name="unknown",  # Will be set by caller
                validation_error=f"Type validation error: {type(original_error).__name__}: {str(original_error)}",
                input_data=extracted_params,
                node_id=self.node_id,
                node_path=self.get_path()
            ) from e

        # Step 4: Handler Execution with context as final parameter
        try:
            if context is not None:
                # Always pass context as the final parameter
                output = self.handler(**validated_params, context=context)
            else:
                # No context provided, call handler normally
                output = self.handler(**validated_params)
        except NodeExecutionError:
            # Re-raise NodeExecutionError as-is
            raise
        except Exception as e:
            original_error = e
            self.logger.error(
                f"Handler execution error for intent '{self.name}' (Path: {'.'.join(self.get_path())}): {type(original_error).__name__}: {str(original_error)}")
            raise NodeExecutionError(
                node_name=self.name,
                taxonomy_name="unknown",  # Will be set by caller
                error_message=f"Handler execution failed: {type(original_error).__name__}: {str(original_error)}",
                params=validated_params,
                node_id=self.node_id,
                node_path=self.get_path()
            ) from e

        # Step 5: Output Validation
        if self.output_validator:
            try:
                if not self.output_validator(output):
                    self.logger.error(
                        f"Output validation failed for intent '{self.name}' (Path: {'.'.join(self.get_path())})")
                    raise NodeOutputValidationError(
                        node_name=self.name,
                        taxonomy_name="unknown",  # Will be set by caller
                        validation_error="Output validation failed",
                        output_data=output,
                        node_id=self.node_id,
                        node_path=self.get_path()
                    )
            except (NodeInputValidationError, NodeOutputValidationError):
                # Re-raise validation errors as-is
                raise
            except Exception as e:
                original_error = e
                self.logger.error(
                    f"Output validation error for intent '{self.name}' (Path: {'.'.join(self.get_path())}): {type(original_error).__name__}: {str(original_error)}")
                raise NodeOutputValidationError(
                    node_name=self.name,
                    taxonomy_name="unknown",  # Will be set by caller
                    validation_error=f"Output validation error: {type(original_error).__name__}: {str(original_error)}",
                    output_data=output,
                    node_id=self.node_id,
                    node_path=self.get_path()
                ) from e

        return {
            "success": True,
            "params": validated_params,
            "output": output,
            "error": None
        }

    def _validate_types(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Validate that extracted parameters match the expected types."""
        validated_params = {}

        for param_name, expected_type in self.param_schema.items():
            if param_name not in params:
                self.logger.error(
                    f"Missing required parameter '{param_name}' for intent '{self.name}' (Path: {'.'.join(self.get_path())})")
                raise NodeInputValidationError(
                    node_name=self.name,
                    taxonomy_name="unknown",  # Will be set by caller
                    validation_error=f"Missing required parameter '{param_name}'",
                    input_data=params,
                    node_id=self.node_id,
                    node_path=self.get_path()
                )

            param_value = params[param_name]

            # Handle type validation
            if expected_type == str:
                if not isinstance(param_value, str):
                    self.logger.error(
                        f"Parameter '{param_name}' must be a string, got {type(param_value).__name__} for intent '{self.name}' (Path: {'.'.join(self.get_path())})")
                    raise NodeInputValidationError(
                        node_name=self.name,
                        taxonomy_name="unknown",  # Will be set by caller
                        validation_error=f"Parameter '{param_name}' must be a string, got {type(param_value).__name__}",
                        input_data=params,
                        node_id=self.node_id,
                        node_path=self.get_path()
                    )
            elif expected_type == int:
                try:
                    param_value = int(param_value)
                except (ValueError, TypeError) as e:
                    original_error = e
                    self.logger.error(
                        f"Parameter '{param_name}' must be an integer, got {type(param_value).__name__} for intent '{self.name}' (Path: {'.'.join(self.get_path())}): {type(original_error).__name__}: {str(original_error)}")
                    raise NodeInputValidationError(
                        node_name=self.name,
                        taxonomy_name="unknown",  # Will be set by caller
                        validation_error=f"Parameter '{param_name}' must be an integer, got {type(param_value).__name__}: {type(original_error).__name__}: {str(original_error)}",
                        input_data=params,
                        node_id=self.node_id,
                        node_path=self.get_path()
                    ) from e
            elif expected_type == float:
                try:
                    param_value = float(param_value)
                except (ValueError, TypeError) as e:
                    original_error = e
                    self.logger.error(
                        f"Parameter '{param_name}' must be a number, got {type(param_value).__name__} for intent '{self.name}' (Path: {'.'.join(self.get_path())}): {type(original_error).__name__}: {str(original_error)}")
                    raise NodeInputValidationError(
                        node_name=self.name,
                        taxonomy_name="unknown",  # Will be set by caller
                        validation_error=f"Parameter '{param_name}' must be a number, got {type(param_value).__name__}: {type(original_error).__name__}: {str(original_error)}",
                        input_data=params,
                        node_id=self.node_id,
                        node_path=self.get_path()
                    ) from e
            elif expected_type == bool:
                if isinstance(param_value, str):
                    param_value = param_value.lower() in ('true', '1', 'yes', 'on')
                elif not isinstance(param_value, bool):
                    self.logger.error(
                        f"Parameter '{param_name}' must be a boolean, got {type(param_value).__name__} for intent '{self.name}' (Path: {'.'.join(self.get_path())})")
                    raise NodeInputValidationError(
                        node_name=self.name,
                        taxonomy_name="unknown",  # Will be set by caller
                        validation_error=f"Parameter '{param_name}' must be a boolean, got {type(param_value).__name__}",
                        input_data=params,
                        node_id=self.node_id,
                        node_path=self.get_path()
                    )

            validated_params[param_name] = param_value

        return validated_params
