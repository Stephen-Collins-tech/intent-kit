"""
Type validation and coercion utilities.

This module provides utilities for validating input data against type annotations
and coercing data into the expected types with clear error messages.

## Quick Start

```python
from intent_kit.utils.type_coercion import validate_type, validate_dict, validate_raw_content, TypeValidationError

# Basic validation
age = validate_type("25", int)  # Returns 25
name = validate_type(123, str)  # Returns "123"
is_active = validate_type("true", bool)  # Returns True

# Raw content validation (from LLM responses)
raw_json = '{"name": "John", "age": 30}'
user_data = validate_raw_content(raw_json, dict)  # Returns {"name": "John", "age": 30}

# Complex validation with dataclasses
@dataclass
class User:
    id: int
    name: str
    email: str
    role: str

user_data = {
    "id": "123",
    "name": "John Doe",
    "email": "john@example.com",
    "role": "admin"
}

user = validate_type(user_data, User)  # Returns User instance

# Dictionary schema validation
schema = {"name": str, "age": int, "scores": list[int]}
data = {"name": "Alice", "age": "25", "scores": ["95", "87"]}
validated = validate_dict(data, schema)  # Returns {"name": "Alice", "age": 25, "scores": [95, 87]}

# Error handling
try:
    validate_type("not a number", int)
except TypeValidationError as e:
    print(f"Validation failed: {e}")  # "Expected int, got 'not a number'"
```

## Features

- **Type Coercion**: Automatically converts compatible types (e.g., "123" → 123)
- **Raw Content Validation**: Parse and validate JSON/YAML from LLM responses
- **Complex Types**: Supports dataclasses, enums, unions, literals, and collections
- **Clear Errors**: Detailed error messages with context
- **Schema Validation**: Validate dictionaries against type schemas
- **Convenience Functions**: Quick validation for common types

## Supported Types

- **Primitives**: str, int, float, bool
- **Collections**: list, tuple, set, dict
- **Complex**: dataclasses, enums, unions, literals
- **Optional**: None values and default handling
- **Custom Classes**: Classes with __init__ methods

## Error Handling

All validation functions raise `TypeValidationError` with:
- Descriptive error message
- Original value that failed validation
- Expected type information
"""

from __future__ import annotations

import inspect
import enum
import re
import json
from dataclasses import is_dataclass, fields, MISSING
from collections.abc import Mapping as ABCMapping
from typing import (
    Any,
    Type,
    TypeVar,
    Union,
    get_args,
    get_origin,
    get_type_hints,
    Literal,
)

# Try to import yaml at module load time
try:
    import yaml

    YAML_AVAILABLE = True
except ImportError:
    yaml = None  # type: ignore
    YAML_AVAILABLE = False

T = TypeVar("T")

# Type mapping for string type names to actual types
TYPE_MAP = {
    "str": str,
    "int": int,
    "float": float,
    "bool": bool,
    "list": list,
    "dict": dict,
    "tuple": tuple,
    "set": set,
    "frozenset": frozenset,
}


def resolve_type(type_spec: Union[Type[Any], str, Any]) -> Type[Any]:
    """
    Resolve a type specification to an actual Python type.

    Args:
        type_spec: Either a Python type or a string type name

    Returns:
        The resolved Python type

    Raises:
        ValueError: If the type name is unknown
    """
    if isinstance(type_spec, type):
        return type_spec
    elif isinstance(type_spec, str):
        if type_spec in TYPE_MAP:
            return TYPE_MAP[type_spec]
        else:
            raise ValueError(f"Unknown type name: {type_spec}")
    else:
        raise ValueError(f"Invalid type specification: {type_spec}")


class TypeValidationError(ValueError):
    """Raised when data cannot be validated or coerced into the expected type."""

    def __init__(self, message: str, value: Any = None, expected_type: Any = None):
        super().__init__(message)
        self.value = value
        self.expected_type = expected_type


def validate_raw_content(raw_content: str, expected_type: Type[T]) -> T:
    """Validate raw string content against an expected type.

    This function handles parsing JSON/YAML from LLM responses and validates
    the parsed data against the expected type.

    Args:
        raw_content: The raw string content to validate
        expected_type: The expected type to validate against

    Returns:
        The validated data in the expected type

    Raises:
        TypeValidationError: If the content cannot be validated against the expected type
        ValueError: If the content cannot be parsed from the string format
    """
    if not isinstance(raw_content, str):
        raise ValueError(f"Expected string content, got {type(raw_content)}")

    # If expected type is str, return as-is
    if expected_type is str:
        return raw_content.strip()  # type: ignore[return-value]

    # Parse the raw content into structured data
    parsed_data = _parse_string_to_structured(raw_content)

    # Validate and convert to expected type
    try:
        return validate_type(parsed_data, expected_type)
    except TypeValidationError as e:
        # Provide more context about the validation failure
        raise TypeValidationError(
            f"Failed to validate content against {expected_type.__name__}: {str(e)}",
            raw_content,
            expected_type,
        )


def _parse_string_to_structured(content_str: str) -> Union[dict, list, Any]:
    """Parse a string into structured data with JSON/YAML detection.

    Args:
        content_str: The string to parse

    Returns:
        Structured data (dict, list, or wrapped in dict if parsing fails)
    """
    # Clean the string - remove common LLM artifacts
    cleaned_str = content_str.strip()

    # Remove markdown code blocks if present
    json_block_pattern = re.compile(r"```json\s*([\s\S]*?)\s*```", re.IGNORECASE)
    yaml_block_pattern = re.compile(r"```yaml\s*([\s\S]*?)\s*```", re.IGNORECASE)
    generic_block_pattern = re.compile(r"```\s*([\s\S]*?)\s*```")

    # Try to extract from JSON code block first
    match = json_block_pattern.search(cleaned_str)
    if match:
        cleaned_str = match.group(1).strip()
    else:
        # Try YAML code block
        match = yaml_block_pattern.search(cleaned_str)
        if match:
            cleaned_str = match.group(1).strip()
        else:
            # Try generic code block
            match = generic_block_pattern.search(cleaned_str)
            if match:
                cleaned_str = match.group(1).strip()

    # Try to parse as JSON first
    try:
        result = json.loads(cleaned_str)
        return result
    except (json.JSONDecodeError, ValueError):
        pass

    # Try to parse as YAML
    if YAML_AVAILABLE and yaml is not None:
        try:
            parsed = yaml.safe_load(cleaned_str)
            # Only return YAML result if it's a dict or list, otherwise wrap in dict
            if isinstance(parsed, (dict, list)):
                return parsed
            else:
                return {"raw_content": content_str}
        except (yaml.YAMLError, ValueError):
            pass

    # If parsing fails, wrap in a dict
    return {"raw_content": content_str}


def validate_type(data: Any, expected_type: Any) -> Any:
    """
    Validate and coerce data into the expected type.

    Args:
        data: The data to validate and coerce
        expected_type: The target type to coerce into

    Returns:
        The coerced data of type T

    Raises:
        TypeValidationError: If data cannot be coerced into the expected type
    """
    try:
        return _coerce_value(data, expected_type)
    except TypeValidationError:
        raise
    except Exception as e:
        raise TypeValidationError(
            f"Unexpected error during type validation: {e}", data, expected_type
        ) from e


def _coerce_value(val: Any, tp: Any) -> Any:
    """Internal function to coerce a value into a specific type."""
    origin = get_origin(tp)
    args = get_args(tp)

    # Handle NoneType
    if tp is type(None):  # noqa: E721
        if val is None:
            return None
        raise TypeValidationError(f"Expected None, got {type(val).__name__}", val, tp)

    # Handle Any/object
    if tp is Any or tp is object:
        return val

    # Handle Union/Optional
    if origin is Union:
        last_err: Exception | None = None
        for arg_type in args:
            try:
                return _coerce_value(val, arg_type)
            except TypeValidationError as e:
                last_err = e
        raise last_err or TypeValidationError(
            f"Value {val!r} does not match any type in {tp!r}", val, tp
        )

    # Handle Literal
    if origin is Literal:
        if val in args:
            return val
        raise TypeValidationError(f"Expected one of {args}, got {val!r}", val, tp)

    # Handle Enums
    if isinstance(tp, type) and issubclass(tp, enum.Enum):
        if isinstance(val, tp):
            return val
        # Try value then name
        try:
            return tp(val)  # type: ignore[call-arg]
        except Exception:
            try:
                return tp[str(val)]  # type: ignore[index]
            except Exception:
                raise TypeValidationError(
                    f"Cannot coerce {val!r} to enum {tp.__name__}", val, tp
                )

    # Handle primitives
    if tp in (str, int, float, bool):
        # If already correct primitive type, return as is (do not coerce)
        if isinstance(val, tp):
            return val
        if tp is bool:
            # Handle common truthy/falsy values
            if val in (True, False, 1, 0):
                return bool(val)
            if isinstance(val, str):
                if val.lower() in ("true", "1", "yes", "on"):
                    return True
                if val.lower() in ("false", "0", "no", "off"):
                    return False
            raise TypeValidationError(
                f"Expected bool, got {type(val).__name__}", val, tp
            )
        try:
            return tp(val)  # type: ignore[call-arg]
        except Exception:
            raise TypeValidationError(f"Expected {tp.__name__}, got {val!r}", val, tp)

    # Handle collections
    if origin in (list, tuple, set, frozenset):
        if not isinstance(val, (list, tuple, set, frozenset)):
            origin_name = origin.__name__ if origin else "collection"
            raise TypeValidationError(
                f"Expected {origin_name}, got {type(val).__name__}", val, tp
            )
        elem_type = args[0] if args else Any
        coerced = [_coerce_value(v, elem_type) for v in list(val)]
        if origin is list:
            return coerced
        if origin is tuple:
            return tuple(coerced)
        if origin is set:
            return set(coerced)
        if origin is frozenset:
            return frozenset(coerced)

    # Handle dict
    if origin is dict:
        key_type, val_type = args if args else (Any, Any)
        if not isinstance(val, ABCMapping):
            raise TypeValidationError(
                f"Expected dict, got {type(val).__name__}", val, tp
            )
        return {
            _coerce_value(k, key_type): _coerce_value(v, val_type)
            for k, v in val.items()
        }

    # Handle dataclasses
    if is_dataclass(tp) and isinstance(tp, type):
        if not isinstance(val, ABCMapping):
            raise TypeValidationError(
                f"Expected object (mapping) for {tp.__name__}", val, tp
            )
        type_hints = get_type_hints(tp)
        out_kwargs: dict[str, Any] = {}
        required_names = set()

        for field in fields(tp):
            field_type = type_hints.get(field.name, field.type)
            if (
                field.default is MISSING
                and getattr(field, "default_factory", MISSING) is MISSING
            ):
                required_names.add(field.name)
            if field.name in val:
                out_kwargs[field.name] = _coerce_value(val[field.name], field_type)

        missing = required_names - set(out_kwargs)
        if missing:
            raise TypeValidationError(
                f"Missing required field(s) for {tp.__name__}: {sorted(missing)}",
                val,
                tp,
            )

        # Check for extra keys
        extra = set(val.keys()) - {f.name for f in fields(tp)}
        if extra:
            raise TypeValidationError(
                f"Unexpected fields for {tp.__name__}: {sorted(extra)}", val, tp
            )

        return tp(**out_kwargs)  # type: ignore[misc]

    # Handle plain classes
    if inspect.isclass(tp) and isinstance(tp, type):
        # Special handling for dict type
        if tp is dict:
            if isinstance(val, ABCMapping):
                return dict(val)  # Convert to dict directly
            else:
                raise TypeValidationError(
                    f"Expected dict, got {type(val).__name__}", val, tp
                )

        if not isinstance(val, ABCMapping):
            raise TypeValidationError(
                f"Expected object (mapping) for {tp.__name__}", val, tp
            )
        sig = inspect.signature(tp.__init__)
        params = list(sig.parameters.values())[1:]  # skip self
        anno = get_type_hints(tp.__init__)
        kwargs: dict[str, Any] = {}

        for param in params:
            if param.kind not in (param.POSITIONAL_OR_KEYWORD, param.KEYWORD_ONLY):
                raise TypeValidationError(
                    f"Unsupported parameter kind: {param.kind} on {tp.__name__}.__init__",
                    val,
                    tp,
                )
            if param.name in val:
                target_type = anno.get(param.name, Any)
                kwargs[param.name] = _coerce_value(val[param.name], target_type)
            else:
                if param.default is inspect._empty:
                    raise TypeValidationError(
                        f"Missing required param '{param.name}' for {tp.__name__}",
                        val,
                        tp,
                    )

        extra = set(val.keys()) - {p.name for p in params}
        if extra:
            raise TypeValidationError(
                f"Unexpected fields for {tp.__name__}: {sorted(extra)}", val, tp
            )

        return tp(**kwargs)

    # Fallback: try callable cast
    if callable(tp):
        try:
            return tp(val)  # type: ignore[call-arg]
        except Exception:
            pass

    raise TypeValidationError(f"Don't know how to coerce into {tp!r}", val, tp)


def validate_dict(data: dict[str, Any], schema: dict[str, Any]) -> dict[str, Any]:
    """
    Validate a dictionary against a schema of expected types.

    Args:
        data: The dictionary to validate
        schema: Dictionary mapping field names to expected types

    Returns:
        The validated dictionary with coerced values

    Raises:
        TypeValidationError: If validation fails
    """
    result = {}
    for field_name, field_type in schema.items():
        if field_name not in data:
            raise TypeValidationError(
                f"Missing required field '{field_name}'", data, schema
            )
        result[field_name] = validate_type(data[field_name], field_type)

    # Check for extra fields
    extra_fields = set(data.keys()) - set(schema.keys())
    if extra_fields:
        raise TypeValidationError(
            f"Unexpected fields: {sorted(extra_fields)}", data, schema
        )

    return result


# Convenience functions for common validations
def validate_int(value: Any) -> int:
    """Validate and coerce to int."""
    return validate_type(value, int)


def validate_str(value: Any) -> str:
    """Validate and coerce to str."""
    return validate_type(value, str)


def validate_bool(value: Any) -> bool:
    """Validate and coerce to bool."""
    return validate_type(value, bool)


def validate_list(value: Any, element_type: Any = Any) -> list[Any]:
    """Validate and coerce to list with optional element type validation."""
    return validate_type(value, list[element_type])


def validate_dict_simple(
    value: Any, key_type: Any = Any, value_type: Any = Any
) -> dict[Any, Any]:
    """Validate and coerce to dict with optional key/value type validation."""
    return validate_type(value, dict[key_type, value_type])
