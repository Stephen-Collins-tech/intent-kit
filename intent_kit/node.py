from typing import Any, Callable, List, Optional, Dict, Union, Type
from abc import ABC, abstractmethod
from dataclasses import dataclass
try:
    from typing import TypedDict
except ImportError:
    from typing_extensions import TypedDict

from intent_kit.utils.logger import Logger


class TaxonomyNode(ABC):
    """Base class for all nodes in the intent taxonomy tree."""

    def __init__(self, *, name: str, description: str, children: List["TaxonomyNode"] = []):
        self.name = name
        self.logger = Logger(name)
        self.description = description
        self.children: List["TaxonomyNode"] = children

    @abstractmethod
    def execute(self, user_input: str) -> Dict[str, Any]:
        """Execute the node with the given user input."""
        pass


class ClassifierNode(TaxonomyNode):
    """Intermediate node that uses a classifier to select child nodes."""

    def __init__(
        self,
        name: str,
        classifier: Callable[[str, List["TaxonomyNode"]], Optional["TaxonomyNode"]],
        children: List["TaxonomyNode"],
        description: str = ""
    ):
        super().__init__(name=name, description=description, children=children)
        self.classifier = classifier

    def execute(self, user_input: str) -> Dict[str, Any]:
        """Execute the node with the given user input."""
        chosen = self.classifier(user_input, self.children)
        if not chosen:
            self.logger.error(
                f"Classifier at '{self.name}' could not route input.")
            return {
                "intent": None,
                "params": None,
                "output": None,
                "error": f"Classifier at '{self.name}' could not route input."
            }
        self.logger.debug(
            f"Classifier at '{self.name}' routed input to '{chosen.name}'.")
        return chosen.execute(user_input)


class IntentNode(TaxonomyNode):
    """Leaf node representing an executable intent with argument extraction and validation."""

    def __init__(
        self,
        name: str,
        param_schema: Dict[str, Type],
        handler: Callable[..., Any],
        arg_extractor: Callable[[str], Dict[str, Any]],
        input_validator: Optional[Callable[[Dict[str, Any]], bool]] = None,
        output_validator: Optional[Callable[[Any], bool]] = None,
        description: str = ""
    ):
        super().__init__(name=name, description=description, children=[])
        self.param_schema = param_schema
        self.handler = handler
        self.arg_extractor = arg_extractor
        self.input_validator = input_validator
        self.output_validator = output_validator

    def execute(self, user_input: str) -> Dict[str, Any]:
        """
        Execute the intent with the given user input.

        Returns:
            Dict containing:
                - success: Boolean indicating if execution was successful
                - params: Extracted and validated parameters
                - output: Result of handler execution
                - error: Error message if any
        """
        try:
            # Step 1: Argument Extraction
            extracted_params = self.arg_extractor(user_input)

            # Step 2: Input Validation
            if self.input_validator:
                if not self.input_validator(extracted_params):
                    self.logger.error(
                        f"Input validation failed for intent '{self.name}'.")
                    return {
                        "success": False,
                        "params": extracted_params,
                        "output": None,
                        "error": f"Input validation failed for intent '{self.name}'"
                    }

            # Step 3: Type Validation
            validated_params = self._validate_types(extracted_params)
            if not validated_params["success"]:
                return validated_params

            # Step 4: Handler Execution
            try:
                output = self.handler(**validated_params["params"])
            except Exception as e:
                self.logger.error(
                    f"Execution error in intent '{self.name}': {str(e)}")
                return {
                    "success": False,
                    "params": validated_params["params"],
                    "output": None,
                    "error": f"Execution error in intent '{self.name}': {str(e)}"
                }

            # Step 5: Output Validation
            if self.output_validator:
                if not self.output_validator(output):
                    self.logger.error(
                        f"Output validation failed for intent '{self.name}'.")
                    return {
                        "success": False,
                        "params": validated_params["params"],
                        "output": output,
                        "error": f"Output validation failed for intent '{self.name}'"
                    }

            return {
                "success": True,
                "params": validated_params["params"],
                "output": output,
                "error": None
            }

        except Exception as e:
            self.logger.error(
                f"Execution error in intent '{self.name}': {str(e)}")
            return {
                "success": False,
                "params": None,
                "output": None,
                "error": f"Execution error in intent '{self.name}': {str(e)}"
            }

    def _validate_types(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Validate that extracted parameters match the expected types."""
        validated_params = {}

        for param_name, expected_type in self.param_schema.items():
            if param_name not in params:
                self.logger.error(
                    f"Missing required parameter '{param_name}' for intent '{self.name}'.")
                return {
                    "success": False,
                    "params": None,
                    "error": f"Missing required parameter '{param_name}' for intent '{self.name}'"
                }

            param_value = params[param_name]

            # Handle type validation
            if expected_type == str:
                if not isinstance(param_value, str):
                    self.logger.error(
                        f"Parameter '{param_name}' must be a string, got {type(param_value).__name__}")
                    return {
                        "success": False,
                        "params": None,
                        "error": f"Parameter '{param_name}' must be a string, got {type(param_value).__name__}"
                    }
            elif expected_type == int:
                try:
                    param_value = int(param_value)
                except (ValueError, TypeError):
                    self.logger.error(
                        f"Parameter '{param_name}' must be an integer, got {type(param_value).__name__}")
                    return {
                        "success": False,
                        "params": None,
                        "error": f"Parameter '{param_name}' must be an integer, got {type(param_value).__name__}"
                    }
            elif expected_type == float:
                try:
                    param_value = float(param_value)
                except (ValueError, TypeError):
                    self.logger.error(
                        f"Parameter '{param_name}' must be a number, got {type(param_value).__name__}")
                    return {
                        "success": False,
                        "params": None,
                        "error": f"Parameter '{param_name}' must be a number, got {type(param_value).__name__}"
                    }
            elif expected_type == bool:
                if isinstance(param_value, str):
                    param_value = param_value.lower() in ('true', '1', 'yes', 'on')
                elif not isinstance(param_value, bool):
                    self.logger.error(
                        f"Parameter '{param_name}' must be a boolean, got {type(param_value).__name__}")
                    return {
                        "success": False,
                        "params": None,
                        "error": f"Parameter '{param_name}' must be a boolean, got {type(param_value).__name__}"
                    }

            validated_params[param_name] = param_value

        return {
            "success": True,
            "params": validated_params,
            "error": None
        }
