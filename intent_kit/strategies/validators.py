"""
Validation classes for action nodes.

This module provides InputValidator and OutputValidator classes for handling
validation logic in a clean, separated way.
"""

from typing import Any, Dict, Callable, Optional
from abc import ABC, abstractmethod


class InputValidator(ABC):
    """Base class for input validation."""

    @abstractmethod
    def validate(self, params: Dict[str, Any]) -> bool:
        """Validate input parameters.

        Args:
            params: Parameters to validate

        Returns:
            True if validation passes, False otherwise
        """
        pass

    def __call__(self, params: Dict[str, Any]) -> bool:
        """Make the validator callable."""
        return self.validate(params)


class OutputValidator(ABC):
    """Base class for output validation."""

    @abstractmethod
    def validate(self, output: Any) -> bool:
        """Validate output.

        Args:
            output: Output to validate

        Returns:
            True if validation passes, False otherwise
        """
        pass

    def __call__(self, output: Any) -> bool:
        """Make the validator callable."""
        return self.validate(output)


class FunctionInputValidator(InputValidator):
    """Input validator that wraps a function."""

    def __init__(self, validator_func: Callable[[Dict[str, Any]], bool]):
        """Initialize with a validation function.

        Args:
            validator_func: Function that takes parameters and returns bool
        """
        self.validator_func = validator_func

    def validate(self, params: Dict[str, Any]) -> bool:
        """Validate using the wrapped function."""
        return self.validator_func(params)


class FunctionOutputValidator(OutputValidator):
    """Output validator that wraps a function."""

    def __init__(self, validator_func: Callable[[Any], bool]):
        """Initialize with a validation function.

        Args:
            validator_func: Function that takes output and returns bool
        """
        self.validator_func = validator_func

    def validate(self, output: Any) -> bool:
        """Validate using the wrapped function."""
        return self.validator_func(output)


class RequiredFieldsValidator(InputValidator):
    """Validator that checks for required fields."""

    def __init__(self, required_fields: set):
        """Initialize with required fields.

        Args:
            required_fields: Set of required field names
        """
        self.required_fields = required_fields

    def validate(self, params: Dict[str, Any]) -> bool:
        """Check that all required fields are present."""
        return all(field in params for field in self.required_fields)


class NonEmptyValidator(OutputValidator):
    """Validator that checks output is not empty."""

    def validate(self, output: Any) -> bool:
        """Check that output is not empty."""
        if output is None:
            return False
        if isinstance(output, str):
            return len(output.strip()) > 0
        if isinstance(output, (list, tuple)):
            return len(output) > 0
        if isinstance(output, dict):
            return len(output) > 0
        return True


def create_input_validator(
    validator: Optional[Callable[[Dict[str, Any]], bool]]
) -> Optional[InputValidator]:
    """Create an InputValidator from a function or return None.

    Args:
        validator: Function to wrap or None

    Returns:
        InputValidator instance or None
    """
    if validator is None:
        return None
    if isinstance(validator, InputValidator):
        return validator
    return FunctionInputValidator(validator)


def create_output_validator(
    validator: Optional[Callable[[Any], bool]]
) -> Optional[OutputValidator]:
    """Create an OutputValidator from a function or return None.

    Args:
        validator: Function to wrap or None

    Returns:
        OutputValidator instance or None
    """
    if validator is None:
        return None
    if isinstance(validator, OutputValidator):
        return validator
    return FunctionOutputValidator(validator)
