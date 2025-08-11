"""
Tests for the type validation utility.
"""

import pytest
import enum
from dataclasses import dataclass
from typing import Optional

from intent_kit.utils.type_validator import (
    validate_type,
    validate_dict,
    TypeValidationError,
    validate_int,
    validate_str,
    validate_bool,
    validate_list,
    resolve_type,
    TYPE_MAP,
)


class TestRole(enum.Enum):
    """Test role enumeration."""

    ADMIN = "admin"
    USER = "user"


@dataclass
class TestAddress:
    """Test address dataclass."""

    street: str
    city: str
    zip_code: str


@dataclass
class TestUser:
    """Test user dataclass."""

    id: int
    name: str
    email: str
    role: TestRole
    is_active: bool = True
    address: Optional[TestAddress] = None


class TestTypeValidator:
    """Test the type validation utility."""

    def test_validate_int(self):
        """Test integer validation."""
        assert validate_int("42") == 42
        assert validate_int(42) == 42

        with pytest.raises(TypeValidationError):
            validate_int("not a number")

    def test_validate_str(self):
        """Test string validation."""
        assert validate_str(123) == "123"
        assert validate_str("hello") == "hello"
        assert validate_str(None) == "None"  # None gets converted to string

        # Test that string values that are already strings are returned as-is
        assert validate_str("multiplication") == "multiplication"
        assert validate_str("") == ""
        assert validate_str("123") == "123"

    def test_validate_float(self):
        """Test float validation."""
        assert validate_type(42, float) == 42.0
        assert validate_type("3.14", float) == 3.14
        assert validate_type(3.14, float) == 3.14
        assert validate_type(0, float) == 0.0

        with pytest.raises(TypeValidationError):
            validate_type("not a number", float)

    def test_validate_bool(self):
        """Test boolean validation."""
        assert validate_bool("true") == True
        assert validate_bool("True") == True
        assert validate_bool("false") == False
        assert validate_bool("False") == False
        assert validate_bool(1) == True
        assert validate_bool(0) == False

        with pytest.raises(TypeValidationError):
            validate_bool("maybe")

    def test_validate_list(self):
        """Test list validation."""
        assert validate_list(["a", "b", "c"], str) == ["a", "b", "c"]
        assert validate_list(["1", "2", "3"], int) == [1, 2, 3]

        with pytest.raises(TypeValidationError):
            validate_list("not a list", str)

    def test_validate_complex_dataclass(self):
        """Test complex dataclass validation."""
        user_data = {
            "id": "123",
            "name": "John Doe",
            "email": "john@example.com",
            "role": "admin",
            "is_active": "true",
            "address": {
                "street": "123 Main St",
                "city": "Anytown",
                "zip_code": "12345",
            },
        }

        user = validate_type(user_data, TestUser)
        assert user.id == 123
        assert user.name == "John Doe"
        assert user.role == TestRole.ADMIN
        assert user.is_active == True
        assert user.address is not None
        assert user.address.street == "123 Main St"

    def test_validate_dict_schema(self):
        """Test dictionary schema validation."""
        schema = {"name": str, "age": int, "scores": list[int]}

        data = {"name": "Alice", "age": "25", "scores": ["95", "87", "92"]}

        validated = validate_dict(data, schema)
        assert validated["name"] == "Alice"
        assert validated["age"] == 25
        assert validated["scores"] == [95, 87, 92]

    def test_missing_required_field(self):
        """Test missing required field error."""
        with pytest.raises(TypeValidationError) as exc_info:
            validate_type({"name": "Bob"}, TestUser)

        assert "Missing required field(s)" in str(exc_info.value)
        assert "email" in str(exc_info.value)
        assert "id" in str(exc_info.value)

    def test_invalid_enum_value(self):
        """Test invalid enum value error."""
        user_data = {
            "id": 1,
            "name": "Bob",
            "email": "bob@example.com",
            "role": "invalid_role",
        }

        with pytest.raises(TypeValidationError) as exc_info:
            validate_type(user_data, TestUser)

        assert "Cannot coerce" in str(exc_info.value)
        assert "TestRole" in str(exc_info.value)

    def test_extra_field_error(self):
        """Test extra field error."""
        user_data = {
            "id": 1,
            "name": "Bob",
            "email": "bob@example.com",
            "role": "user",
            "extra_field": "value",
        }

        with pytest.raises(TypeValidationError) as exc_info:
            validate_type(user_data, TestUser)

        assert "Unexpected fields" in str(exc_info.value)
        assert "extra_field" in str(exc_info.value)

    def test_optional_field_handling(self):
        """Test optional field handling."""
        user_data = {
            "id": 1,
            "name": "Bob",
            "email": "bob@example.com",
            "role": "user",
            # address is optional, so it's OK to omit
        }

        user = validate_type(user_data, TestUser)
        assert user.address is None

    def test_none_value_handling(self):
        """Test None value handling."""
        # None should be valid for Optional types
        user_data = {
            "id": 1,
            "name": "Bob",
            "email": "bob@example.com",
            "role": "user",
            "address": None,
        }

        user = validate_type(user_data, TestUser)
        assert user.address is None

    def test_union_type_handling(self):
        """Test Union type handling."""
        # Test Union[int, str]
        assert validate_type("42", Optional[int]) == 42
        assert validate_type(None, Optional[int]) is None

        with pytest.raises(TypeValidationError):
            validate_type("not a number", Optional[int])

    def test_literal_type_handling(self):
        """Test Literal type handling."""
        from typing import Literal

        assert validate_type("admin", Literal["admin", "user"]) == "admin"
        assert validate_type("user", Literal["admin", "user"]) == "user"

        with pytest.raises(TypeValidationError):
            validate_type("invalid", Literal["admin", "user"])

    def test_error_context(self):
        """Test that errors include context information."""
        try:
            validate_type("not a number", int)
        except TypeValidationError as e:
            assert e.value == "not a number"
            assert e.expected_type == int
            assert "Expected int" in str(e)


class TestResolveType:
    """Test the resolve_type function and TYPE_MAP."""

    def test_resolve_type_with_actual_types(self):
        """Test resolve_type with actual Python types."""
        assert resolve_type(str) == str
        assert resolve_type(int) == int
        assert resolve_type(float) == float
        assert resolve_type(bool) == bool
        assert resolve_type(list) == list
        assert resolve_type(dict) == dict

    def test_resolve_type_with_string_names(self):
        """Test resolve_type with string type names."""
        assert resolve_type("str") == str
        assert resolve_type("int") == int
        assert resolve_type("float") == float
        assert resolve_type("bool") == bool
        assert resolve_type("list") == list
        assert resolve_type("dict") == dict

    def test_resolve_type_with_unknown_type(self):
        """Test resolve_type with unknown type name."""
        with pytest.raises(ValueError, match="Unknown type name: unknown_type"):
            resolve_type("unknown_type")

    def test_resolve_type_with_invalid_input(self):
        """Test resolve_type with invalid input."""
        with pytest.raises(ValueError, match="Invalid type specification"):
            resolve_type(42)

    def test_type_map_contents(self):
        """Test that TYPE_MAP contains expected mappings."""
        expected_types = [
            "str",
            "int",
            "float",
            "bool",
            "list",
            "dict",
            "tuple",
            "set",
            "frozenset",
        ]
        for type_name in expected_types:
            assert type_name in TYPE_MAP
            # Check that the mapped type is the correct built-in type
            if type_name == "str":
                assert TYPE_MAP[type_name] is str
            elif type_name == "int":
                assert TYPE_MAP[type_name] is int
            elif type_name == "float":
                assert TYPE_MAP[type_name] is float
            elif type_name == "bool":
                assert TYPE_MAP[type_name] is bool
            elif type_name == "list":
                assert TYPE_MAP[type_name] is list
            elif type_name == "dict":
                assert TYPE_MAP[type_name] is dict
            elif type_name == "tuple":
                assert TYPE_MAP[type_name] is tuple
            elif type_name == "set":
                assert TYPE_MAP[type_name] is set
            elif type_name == "frozenset":
                assert TYPE_MAP[type_name] is frozenset
