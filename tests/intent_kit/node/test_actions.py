"""
Tests for ActionNode functionality.
"""

from typing import Dict, Any, Optional

from intent_kit.node.actions import ActionNode
from intent_kit.node.enums import NodeType
from intent_kit.context import IntentContext


class TestActionNode:
    """Test the ActionNode class."""

    def test_action_node_initialization(self):
        """Test ActionNode initialization with basic parameters."""

        # Arrange
        def mock_action(name: str, age: int) -> str:
            return f"Hello {name}, you are {age} years old"

        def mock_arg_extractor(
            user_input: str, context: Optional[Dict[str, Any]] = None
        ) -> Dict[str, Any]:
            return {"name": "Alice", "age": 30}

        param_schema = {"name": str, "age": int}

        # Act
        action_node = ActionNode(
            name="greet_user",
            param_schema=param_schema,
            action=mock_action,
            arg_extractor=mock_arg_extractor,
            description="Greet a user with their name and age",
        )

        # Assert
        assert action_node.name == "greet_user"
        assert action_node.param_schema == param_schema
        assert action_node.action == mock_action
        assert action_node.arg_extractor == mock_arg_extractor
        assert action_node.description == "Greet a user with their name and age"
        assert action_node.node_type == NodeType.ACTION
        assert action_node.context_inputs == set()
        assert action_node.context_outputs == set()
        assert action_node.input_validator is None
        assert action_node.output_validator is None
        assert action_node.remediation_strategies == []

    def test_action_node_successful_execution(self):
        """Test successful execution of an ActionNode."""

        # Arrange
        def mock_action(name: str, age: int) -> str:
            return f"Hello {name}, you are {age} years old"

        def mock_arg_extractor(
            user_input: str, context: Optional[Dict[str, Any]] = None
        ) -> Dict[str, Any]:
            return {"name": "Bob", "age": 25}

        param_schema = {"name": str, "age": int}
        action_node = ActionNode(
            name="greet_user",
            param_schema=param_schema,
            action=mock_action,
            arg_extractor=mock_arg_extractor,
        )

        # Act
        result = action_node.execute("Hello, my name is Bob and I am 25 years old")

        # Assert
        assert result.success is True
        assert result.node_name == "greet_user"
        assert result.node_type == NodeType.ACTION
        assert result.input == "Hello, my name is Bob and I am 25 years old"
        assert result.output == "Hello Bob, you are 25 years old"
        assert result.error is None
        assert result.params == {"name": "Bob", "age": 25}
        assert result.children_results == []

    def test_action_node_parameter_validation(self):
        """Test ActionNode parameter type validation and conversion."""

        # Arrange
        def mock_action(name: str, age: int, is_active: bool) -> str:
            return f"User {name} (age: {age}, active: {is_active})"

        def mock_arg_extractor(
            user_input: str, context: Optional[Dict[str, Any]] = None
        ) -> Dict[str, Any]:
            return {
                "name": "Charlie",
                "age": "30",  # String that should be converted to int
                "is_active": "true",  # String that should be converted to bool
            }

        param_schema = {"name": str, "age": int, "is_active": bool}
        action_node = ActionNode(
            name="create_user",
            param_schema=param_schema,
            action=mock_action,
            arg_extractor=mock_arg_extractor,
        )

        # Act
        result = action_node.execute("Create user Charlie, age 30, active true")

        # Assert
        assert result.success is True
        assert result.params == {"name": "Charlie", "age": 30, "is_active": True}
        assert result.output == "User Charlie (age: 30, active: True)"

    def test_action_node_error_handling(self):
        """Test ActionNode error handling during execution."""

        # Arrange
        def mock_action(name: str) -> str:
            raise ValueError("Invalid name provided")

        def mock_arg_extractor(
            user_input: str, context: Optional[Dict[str, Any]] = None
        ) -> Dict[str, Any]:
            return {"name": "invalid_name"}

        param_schema = {"name": str}
        action_node = ActionNode(
            name="process_user",
            param_schema=param_schema,
            action=mock_action,
            arg_extractor=mock_arg_extractor,
        )

        # Act
        result = action_node.execute("Process user with invalid name")

        # Assert
        assert result.success is False
        assert result.node_name == "process_user"
        assert result.node_type == NodeType.ACTION
        assert result.input == "Process user with invalid name"
        assert result.output is None
        assert result.error is not None
        assert result.error.error_type == "ValueError"
        assert "Invalid name provided" in result.error.message
        assert result.params == {"name": "invalid_name"}

    def test_action_node_with_context_integration(self):
        """Test ActionNode with context inputs and outputs."""

        # Arrange
        def mock_action(
            user_id: str, message: str, context: IntentContext
        ) -> Dict[str, Any]:
            # Simulate updating context with output
            return {
                "response": f"Processed message for user {user_id}: {message}",
                "message_count": 1,
                "last_processed": "2024-01-01",
            }

        def mock_arg_extractor(
            user_input: str, context: Optional[Dict[str, Any]] = None
        ) -> Dict[str, Any]:
            return {
                "user_id": context.get("user_id") if context else "default_user",
                "message": "Hello world",
            }

        param_schema = {"user_id": str, "message": str}
        action_node = ActionNode(
            name="process_message",
            param_schema=param_schema,
            action=mock_action,
            arg_extractor=mock_arg_extractor,
            context_inputs={"user_id"},
            context_outputs={"message_count", "last_processed"},
        )

        # Create context with input
        context = IntentContext(session_id="test_session")
        context.set("user_id", "user123", modified_by="test")

        # Act
        result = action_node.execute("Process this message", context=context)

        # Assert
        assert result.success is True
        assert result.node_name == "process_message"
        assert (
            result.output["response"]
            == "Processed message for user user123: Hello world"
        )
        assert result.output["message_count"] == 1
        assert result.output["last_processed"] == "2024-01-01"

        # Check that context was updated with outputs
        assert context.get("message_count") == 1
        assert context.get("last_processed") == "2024-01-01"

    def test_action_node_with_validators(self):
        """Test ActionNode with input and output validators."""

        # Arrange
        def mock_action(name: str, age: int) -> str:
            return f"Hello {name}, you are {age} years old"

        def mock_arg_extractor(
            user_input: str, context: Optional[Dict[str, Any]] = None
        ) -> Dict[str, Any]:
            return {"name": "David", "age": 35}

        def input_validator(params: Dict[str, Any]) -> bool:
            return "name" in params and "age" in params and params["age"] >= 18

        def output_validator(result: str) -> bool:
            return len(result) > 0 and "Hello" in result

        param_schema = {"name": str, "age": int}
        action_node = ActionNode(
            name="greet_adult",
            param_schema=param_schema,
            action=mock_action,
            arg_extractor=mock_arg_extractor,
            input_validator=input_validator,
            output_validator=output_validator,
        )

        # Act - Valid case
        result = action_node.execute("Greet David who is 35 years old")

        # Assert - Should succeed
        assert result.success is True
        assert result.output == "Hello David, you are 35 years old"

        # Test with invalid input (underage)
        def mock_arg_extractor_invalid(
            user_input: str, context: Optional[Dict[str, Any]] = None
        ) -> Dict[str, Any]:
            return {"name": "Young", "age": 15}

        action_node.arg_extractor = mock_arg_extractor_invalid
        result_invalid = action_node.execute("Greet Young who is 15 years old")

        # Assert - Should fail due to input validation
        assert result_invalid.success is False
        assert result_invalid.error.error_type == "InputValidationError"
        assert "Input validation failed" in result_invalid.error.message
