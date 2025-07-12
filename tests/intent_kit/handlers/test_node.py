"""
Tests for intent_kit.handlers.node module.
"""

from unittest.mock import Mock, patch
from typing import Dict, Any, Optional

from intent_kit.node.handlers import HandlerNode
from intent_kit.node.enums import NodeType
from intent_kit.context import IntentContext
from intent_kit.node.types import ExecutionResult


class TestHandlerNodeInitialization:
    """Test HandlerNode initialization."""

    def test_init_basic(self):
        """Test basic HandlerNode initialization."""

        def handler_func(name: str) -> str:
            return f"Hello {name}!"

        def arg_extractor(
            user_input: str, context: Optional[Dict[str, Any]] = None
        ) -> Dict[str, Any]:
            return {"name": user_input.split()[-1]}

        handler = HandlerNode(
            name="greet",
            param_schema={"name": str},
            handler=handler_func,
            arg_extractor=arg_extractor,
            description="Greet the user",
        )

        assert handler.name == "greet"
        assert handler.description == "Greet the user"
        assert handler.node_type == NodeType.HANDLER
        assert handler.param_schema == {"name": str}
        assert handler.handler == handler_func
        assert handler.arg_extractor == arg_extractor
        assert handler.context_inputs == set()
        assert handler.context_outputs == set()
        assert handler.input_validator is None
        assert handler.output_validator is None
        assert handler.remediation_strategies == []

    def test_init_with_context_dependencies(self):
        """Test HandlerNode initialization with context dependencies."""

        def handler_func(name: str, user_id: str) -> str:
            return f"Hello {name} (ID: {user_id})!"

        def arg_extractor(
            user_input: str, context: Optional[Dict[str, Any]] = None
        ) -> Dict[str, Any]:
            return {
                "name": user_input.split()[-1],
                "user_id": context.get("user_id", "unknown") if context else "unknown",
            }

        handler = HandlerNode(
            name="greet",
            param_schema={"name": str, "user_id": str},
            handler=handler_func,
            arg_extractor=arg_extractor,
            context_inputs={"user_id"},
            context_outputs={"greeting_count"},
            description="Greet the user with context",
        )

        assert handler.context_inputs == {"user_id"}
        assert handler.context_outputs == {"greeting_count"}

    def test_init_with_validators(self):
        """Test HandlerNode initialization with validators."""

        def handler_func(age: int) -> str:
            return f"You are {age} years old"

        def arg_extractor(
            user_input: str, context: Optional[Dict[str, Any]] = None
        ) -> Dict[str, Any]:
            # Extract the number from the input
            import re

            numbers = re.findall(r"\d+", user_input)
            if numbers:
                return {"age": int(numbers[0])}
            else:
                return {"age": 0}

        def input_validator(params: Dict[str, Any]) -> bool:
            return params.get("age", 0) > 0

        def output_validator(output: Any) -> bool:
            return isinstance(output, str) and len(output) > 0

        handler = HandlerNode(
            name="age_handler",
            param_schema={"age": int},
            handler=handler_func,
            arg_extractor=arg_extractor,
            input_validator=input_validator,
            output_validator=output_validator,
        )

        assert handler.input_validator == input_validator
        assert handler.output_validator == output_validator

    def test_init_with_remediation_strategies(self):
        """Test HandlerNode initialization with remediation strategies."""

        def handler_func(name: str) -> str:
            return f"Hello {name}!"

        def arg_extractor(
            user_input: str, context: Optional[Dict[str, Any]] = None
        ) -> Dict[str, Any]:
            return {"name": user_input.split()[-1]}

        handler = HandlerNode(
            name="greet",
            param_schema={"name": str},
            handler=handler_func,
            arg_extractor=arg_extractor,
            remediation_strategies=["retry", "fallback"],
        )

        assert handler.remediation_strategies == ["retry", "fallback"]


class TestHandlerNodeExecution:
    """Test HandlerNode execution."""

    def test_execute_success(self):
        """Test successful handler execution."""

        def handler_func(name: str) -> str:
            return f"Hello {name}!"

        def arg_extractor(
            user_input: str, context: Optional[Dict[str, Any]] = None
        ) -> Dict[str, Any]:
            return {"name": user_input.split()[-1]}

        handler = HandlerNode(
            name="greet",
            param_schema={"name": str},
            handler=handler_func,
            arg_extractor=arg_extractor,
        )

        result = handler.execute("Hello John")

        assert result.success is True
        assert result.output == "Hello John!"
        assert result.node_name == "greet"
        assert result.node_type == NodeType.HANDLER
        assert result.input == "Hello John"
        assert result.error is None

    def test_execute_with_context(self):
        """Test handler execution with context."""

        def handler_func(name: str, user_id: str, context=None) -> str:
            return f"Hello {name} (ID: {user_id})!"

        def arg_extractor(
            user_input: str, context: Optional[Dict[str, Any]] = None
        ) -> Dict[str, Any]:
            return {
                "name": user_input.split()[-1],
                "user_id": context.get("user_id", "unknown") if context else "unknown",
            }

        handler = HandlerNode(
            name="greet",
            param_schema={"name": str, "user_id": str},
            handler=handler_func,
            arg_extractor=arg_extractor,
            context_inputs={"user_id"},
        )

        context = IntentContext()
        context.set("user_id", "12345")

        result = handler.execute("Hello John", context=context)

        assert result.success is True
        assert result.output == "Hello John (ID: 12345)!"

    def test_execute_arg_extraction_failure(self):
        """Test handler execution when argument extraction fails."""

        def handler_func(name: str) -> str:
            return f"Hello {name}!"

        def arg_extractor(
            user_input: str, context: Optional[Dict[str, Any]] = None
        ) -> Dict[str, Any]:
            raise ValueError("Failed to extract arguments")

        handler = HandlerNode(
            name="greet",
            param_schema={"name": str},
            handler=handler_func,
            arg_extractor=arg_extractor,
        )

        result = handler.execute("Hello John")

        assert result.success is False
        assert result.error is not None
        assert result.error.error_type == "ValueError"
        assert "Failed to extract arguments" in result.error.message
        assert result.output is None

    def test_execute_input_validation_failure(self):
        """Test handler execution when input validation fails."""

        def handler_func(age: int) -> str:
            return f"You are {age} years old"

        def arg_extractor(
            user_input: str, context: Optional[Dict[str, Any]] = None
        ) -> Dict[str, Any]:
            # Extract the number from the input
            import re

            numbers = re.findall(r"\d+", user_input)
            if numbers:
                return {"age": int(numbers[0])}
            else:
                return {"age": 0}

        def input_validator(params: Dict[str, Any]) -> bool:
            return params.get("age", 0) > 18  # Must be over 18

        handler = HandlerNode(
            name="age_handler",
            param_schema={"age": int},
            handler=handler_func,
            arg_extractor=arg_extractor,
            input_validator=input_validator,
        )

        result = handler.execute("I am 16 years old")

        assert result.success is False
        assert result.error is not None
        assert result.error.error_type == "InputValidationError"
        assert "Input validation failed" in result.error.message

    def test_execute_input_validation_exception(self):
        """Test handler execution when input validation raises an exception."""

        def handler_func(age: int) -> str:
            return f"You are {age} years old"

        def arg_extractor(
            user_input: str, context: Optional[Dict[str, Any]] = None
        ) -> Dict[str, Any]:
            # Extract the number from the input
            import re

            numbers = re.findall(r"\d+", user_input)
            if numbers:
                return {"age": int(numbers[0])}
            else:
                return {"age": 0}

        def input_validator(params: Dict[str, Any]) -> bool:
            raise ValueError("Validation error")

        handler = HandlerNode(
            name="age_handler",
            param_schema={"age": int},
            handler=handler_func,
            arg_extractor=arg_extractor,
            input_validator=input_validator,
        )

        result = handler.execute("I am 25 years old")

        assert result.success is False
        assert result.error is not None
        assert result.error.error_type == "ValueError"
        assert "Validation error" in result.error.message

    def test_execute_type_validation_failure(self):
        """Test handler execution when type validation fails."""

        def handler_func(age: int) -> str:
            return f"You are {age} years old"

        def arg_extractor(
            user_input: str, context: Optional[Dict[str, Any]] = None
        ) -> Dict[str, Any]:
            return {"age": "not a number"}  # Wrong type

        handler = HandlerNode(
            name="age_handler",
            param_schema={"age": int},
            handler=handler_func,
            arg_extractor=arg_extractor,
        )

        result = handler.execute("I am not a number years old")

        assert result.success is False
        assert result.error is not None
        assert (
            "integer" in result.error.message.lower()
            or "type" in result.error.message.lower()
        )

    def test_execute_handler_exception(self):
        """Test handler execution when the handler function raises an exception."""

        def handler_func(name: str) -> str:
            raise RuntimeError("Handler failed")

        def arg_extractor(
            user_input: str, context: Optional[Dict[str, Any]] = None
        ) -> Dict[str, Any]:
            return {"name": user_input.split()[-1]}

        handler = HandlerNode(
            name="greet",
            param_schema={"name": str},
            handler=handler_func,
            arg_extractor=arg_extractor,
        )

        result = handler.execute("Hello John")

        assert result.success is False
        assert result.error is not None
        assert result.error.error_type == "RuntimeError"
        assert "Handler failed" in result.error.message

    def test_execute_output_validation_failure(self):
        """Test handler execution when output validation fails."""

        def handler_func(name: str) -> str:
            return ""  # Empty string will fail validation

        def arg_extractor(
            user_input: str, context: Optional[Dict[str, Any]] = None
        ) -> Dict[str, Any]:
            return {"name": user_input.split()[-1]}

        def output_validator(output: Any) -> bool:
            return isinstance(output, str) and len(output) > 0

        handler = HandlerNode(
            name="greet",
            param_schema={"name": str},
            handler=handler_func,
            arg_extractor=arg_extractor,
            output_validator=output_validator,
        )

        result = handler.execute("Hello John")

        assert result.success is False
        assert result.error is not None
        assert result.error.error_type == "OutputValidationError"
        assert "Output validation failed" in result.error.message


class TestHandlerNodeTypeValidation:
    """Test HandlerNode type validation."""

    def test_validate_types_success(self):
        """Test successful type validation."""

        def handler_func(name: str, age: int, active: bool) -> str:
            return f"Hello {name}, age {age}, active: {active}"

        def arg_extractor(
            user_input: str, context: Optional[Dict[str, Any]] = None
        ) -> Dict[str, Any]:
            return {
                "name": "John",
                "age": "25",  # String that can be converted to int
                "active": "true",  # String that can be converted to bool
            }

        handler = HandlerNode(
            name="greet",
            param_schema={"name": str, "age": int, "active": bool},
            handler=handler_func,
            arg_extractor=arg_extractor,
        )

        result = handler.execute("Hello John, age 25, active true")

        assert result.success is True
        assert result.output == "Hello John, age 25, active: True"

    def test_validate_types_conversion_failure(self):
        """Test type validation when conversion fails."""

        def handler_func(age: int) -> str:
            return f"You are {age} years old"

        def arg_extractor(
            user_input: str, context: Optional[Dict[str, Any]] = None
        ) -> Dict[str, Any]:
            return {"age": "not a number"}

        handler = HandlerNode(
            name="age_handler",
            param_schema={"age": int},
            handler=handler_func,
            arg_extractor=arg_extractor,
        )

        result = handler.execute("I am not a number years old")

        assert result.success is False
        assert result.error is not None
        assert (
            "invalid literal" in result.error.message.lower()
            or "type" in result.error.message.lower()
        )


class TestHandlerNodeRemediation:
    """Test HandlerNode remediation strategies."""

    def test_execute_remediation_strategies_no_strategies(self):
        """Test remediation when no strategies are available."""

        def handler_func(name: str) -> str:
            raise RuntimeError("Handler failed")

        def arg_extractor(
            user_input: str, context: Optional[Dict[str, Any]] = None
        ) -> Dict[str, Any]:
            return {"name": user_input.split()[-1]}

        handler = HandlerNode(
            name="greet",
            param_schema={"name": str},
            handler=handler_func,
            arg_extractor=arg_extractor,
        )

        result = handler.execute("Hello John")

        assert result.success is False
        assert result.error is not None
        assert "Handler failed" in result.error.message

    @patch("intent_kit.handlers.node.get_remediation_strategy")
    def test_execute_remediation_strategies_with_strategy(self, mock_get_strategy):
        """Test remediation with available strategies."""

        def handler_func(name: str) -> str:
            raise RuntimeError("Handler failed")

        def arg_extractor(
            user_input: str, context: Optional[Dict[str, Any]] = None
        ) -> Dict[str, Any]:
            return {"name": user_input.split()[-1]}

        # Mock successful remediation
        mock_strategy = Mock()
        mock_strategy.execute.return_value = ExecutionResult(
            success=True,
            node_name="greet",
            node_path=["greet"],
            node_type=NodeType.HANDLER,
            input="Hello John",
            output="Remediated: Hello John!",
            error=None,
            params={"name": "John"},
            children_results=[],
        )
        mock_get_strategy.return_value = mock_strategy

        handler = HandlerNode(
            name="greet",
            param_schema={"name": str},
            handler=handler_func,
            arg_extractor=arg_extractor,
            remediation_strategies=["retry"],
        )

        result = handler.execute("Hello John")

        assert result.success is True
        assert result.output == "Remediated: Hello John!"
        mock_get_strategy.assert_called_once_with("retry")


class TestHandlerNodeIntegration:
    """Integration tests for HandlerNode."""

    def test_handler_with_complex_schema(self):
        """Test handler with complex parameter schema."""

        def handler_func(name: str, age: int, email: str, active: bool = True) -> str:
            status = "active" if active else "inactive"
            return f"User {name} ({email}) is {age} years old and {status}"

        def arg_extractor(
            user_input: str, context: Optional[Dict[str, Any]] = None
        ) -> Dict[str, Any]:
            # Simple extraction - in real usage this would be more sophisticated
            parts = user_input.split()
            return {
                "name": parts[1] if len(parts) > 1 else "Unknown",
                "age": int(parts[3]) if len(parts) > 3 else 0,
                "email": parts[5] if len(parts) > 5 else "unknown@example.com",
                "active": parts[7] == "active" if len(parts) > 7 else True,
            }

        handler = HandlerNode(
            name="user_handler",
            param_schema={"name": str, "age": int, "email": str, "active": bool},
            handler=handler_func,
            arg_extractor=arg_extractor,
        )

        result = handler.execute("User John age 25 email john@example.com active")

        assert result.success is True
        assert "John" in result.output if result.output is not None else False
        assert "25" in result.output if result.output is not None else False
        assert (
            "john@example.com" in result.output if result.output is not None else False
        )
        assert "active" in result.output if result.output is not None else False

    def test_handler_with_context_dependencies(self):
        """Test handler with context dependencies."""

        def handler_func(user_id: str, name: str, context=None) -> str:
            return f"User {name} (ID: {user_id}) processed"

        def arg_extractor(
            user_input: str, context: Optional[Dict[str, Any]] = None
        ) -> Dict[str, Any]:
            return {
                "user_id": context.get("user_id", "unknown") if context else "unknown",
                "name": user_input.split()[-1],
            }

        handler = HandlerNode(
            name="user_processor",
            param_schema={"user_id": str, "name": str},
            handler=handler_func,
            arg_extractor=arg_extractor,
            context_inputs={"user_id"},
            context_outputs={"processed_users"},
        )

        context = IntentContext()
        context.set("user_id", "12345")

        result = handler.execute("Process John", context=context)

        assert result.success is True
        assert "John" in result.output if result.output is not None else False
        assert "12345" in result.output if result.output is not None else False

    def test_handler_error_handling_integration(self):
        """Test comprehensive error handling integration."""

        def handler_func(age: int) -> str:
            if age < 0:
                raise ValueError("Age cannot be negative")
            return f"You are {age} years old"

        def arg_extractor(
            user_input: str, context: Optional[Dict[str, Any]] = None
        ) -> Dict[str, Any]:
            try:
                age_str = user_input.split()[-1]
                return {"age": int(age_str)}
            except (ValueError, IndexError):
                raise ValueError("Could not extract age from input")

        def input_validator(params: Dict[str, Any]) -> bool:
            age = params.get("age", 0)
            return 0 <= age <= 150

        def output_validator(output: Any) -> bool:
            return isinstance(output, str) and len(output) > 0

        handler = HandlerNode(
            name="age_handler",
            param_schema={"age": int},
            handler=handler_func,
            arg_extractor=arg_extractor,
            input_validator=input_validator,
            output_validator=output_validator,
        )

        # Test various error scenarios
        test_cases = [
            ("Invalid input", False, "Could not extract age"),
            ("Age -5", False, "Input validation failed"),  # Updated expectation
            ("Age 200", False, "Input validation failed"),
            ("Age 25", True, "You are 25 years old"),
        ]

        for user_input, expected_success, expected_content in test_cases:
            result = handler.execute(user_input)
            assert result.success == expected_success
            if expected_success:
                assert (
                    expected_content in result.output
                    if result.output is not None
                    else False
                )
            else:
                assert result.error is not None
                assert expected_content in result.error.message
