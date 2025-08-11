"""
Tests for ActionNode functionality.
"""

from typing import Dict, Any, Optional
from unittest.mock import patch

from intent_kit.nodes.actions import ActionNode
from intent_kit.nodes.enums import NodeType
from intent_kit.context import Context


class TestActionNode:
    """Test the ActionNode class."""

    def test_action_node_initialization(self):
        """Test ActionNode initialization with basic parameters."""

        # Arrange
        def mock_action(name: str, age: int) -> str:
            return f"Hello {name}, you are {age} years old"

        param_schema = {"name": str, "age": int}
        llm_config = {"provider": "ollama", "model": "llama2"}

        # Act
        action_node = ActionNode(
            name="greet_user",
            param_schema=param_schema,
            action=mock_action,
            description="Greet a user with their name and age",
            llm_config=llm_config,
        )

        # Assert
        assert action_node.name == "greet_user"
        assert action_node.param_schema == param_schema
        assert action_node.action == mock_action
        assert action_node.description == "Greet a user with their name and age"
        assert action_node.node_type == NodeType.ACTION
        assert action_node.input_validator is None
        assert action_node.output_validator is None

    @patch("intent_kit.services.ai.ollama_client.OllamaClient.generate")
    def test_action_node_successful_execution(self, mock_generate):
        """Test successful execution of an ActionNode."""

        # Arrange
        def mock_action(name: str, age: int) -> str:
            return f"Hello {name}, you are {age} years old"

        param_schema = {"name": str, "age": int}
        llm_config = {"provider": "ollama", "model": "llama2"}

        # Mock the LLM response for parameter extraction
        from intent_kit.types import (
            LLMResponse,
            Model,
            InputTokens,
            OutputTokens,
            Cost,
            Provider,
            Duration,
        )

        mock_response = LLMResponse(
            output={"name": "Bob", "age": 25},
            model=Model("llama2"),
            input_tokens=InputTokens(10),
            output_tokens=OutputTokens(5),
            cost=Cost(0.001),
            provider=Provider("ollama"),
            duration=Duration(0.1),
        )
        mock_generate.return_value = mock_response

        action_node = ActionNode(
            name="greet_user",
            param_schema=param_schema,
            action=mock_action,
            llm_config=llm_config,
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
        # Note: params are handled internally by the executor
        assert result.children_results == []

    @patch("intent_kit.services.ai.ollama_client.OllamaClient.generate")
    def test_action_node_parameter_validation(self, mock_generate):
        """Test ActionNode parameter type validation and conversion."""

        # Arrange
        def mock_action(name: str, age: int, is_active: bool) -> str:
            return f"User {name} (age: {age}, active: {is_active})"

        param_schema = {"name": str, "age": int, "is_active": bool}
        llm_config = {"provider": "ollama", "model": "llama2"}

        # Mock the LLM response for parameter extraction
        from intent_kit.types import (
            LLMResponse,
            Model,
            InputTokens,
            OutputTokens,
            Cost,
            Provider,
            Duration,
        )

        mock_response = LLMResponse(
            output={"name": "Charlie", "age": 30, "is_active": True},
            model=Model("llama2"),
            input_tokens=InputTokens(15),
            output_tokens=OutputTokens(8),
            cost=Cost(0.002),
            provider=Provider("ollama"),
            duration=Duration(0.15),
        )
        mock_generate.return_value = mock_response

        action_node = ActionNode(
            name="create_user",
            param_schema=param_schema,
            action=mock_action,
            llm_config=llm_config,
        )

        # Act
        result = action_node.execute("Create user Charlie, age 30, active true")

        # Assert
        assert result.success is True
        # Note: params are handled internally by the executor
        assert result.output == "User Charlie (age: 30, active: True)"

    @patch("intent_kit.services.ai.ollama_client.OllamaClient.generate")
    def test_action_node_error_handling(self, mock_generate):
        """Test ActionNode error handling during execution."""

        # Arrange
        def mock_action(name: str) -> str:
            raise ValueError("Invalid name provided")

        param_schema = {"name": str}
        llm_config = {"provider": "ollama", "model": "llama2"}

        # Mock the LLM response for parameter extraction
        from intent_kit.types import (
            LLMResponse,
            Model,
            InputTokens,
            OutputTokens,
            Cost,
            Provider,
            Duration,
        )

        mock_response = LLMResponse(
            output={"name": "InvalidName"},
            model=Model("llama2"),
            input_tokens=InputTokens(5),
            output_tokens=OutputTokens(3),
            cost=Cost(0.0005),
            provider=Provider("ollama"),
            duration=Duration(0.05),
        )
        mock_generate.return_value = mock_response

        action_node = ActionNode(
            name="process_user",
            param_schema=param_schema,
            action=mock_action,
            llm_config=llm_config,
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
        assert result.error.error_type == "ActionExecutionError"
        assert "Action execution failed" in result.error.message

    @patch("intent_kit.services.ai.ollama_client.OllamaClient.generate")
    def test_action_node_with_context_integration(self, mock_generate):
        """Test ActionNode with context inputs and outputs."""

        # Arrange

        def mock_action(name: str, context: Optional[Context] = None) -> Dict[str, Any]:
            # Simulate updating context with output
            return {
                "response": f"Processed message for user {name}",
                "message_count": 1,
                "last_processed": "2024-01-01",
            }

        param_schema = {"name": str}
        llm_config = {"provider": "ollama", "model": "llama2"}

        # Mock the LLM response for parameter extraction
        from intent_kit.types import (
            LLMResponse,
            Model,
            InputTokens,
            OutputTokens,
            Cost,
            Provider,
            Duration,
        )

        mock_response = LLMResponse(
            output={"name": "user123"},
            model=Model("llama2"),
            input_tokens=InputTokens(8),
            output_tokens=OutputTokens(4),
            cost=Cost(0.001),
            provider=Provider("ollama"),
            duration=Duration(0.08),
        )
        mock_generate.return_value = mock_response

        action_node = ActionNode(
            name="process_message",
            param_schema=param_schema,
            action=mock_action,
            llm_config=llm_config,
        )

        # Create context with input
        context = Context(session_id="test_session")
        context.set("name", "user123", modified_by="test")

        # Act
        result = action_node.execute(
            "Process this message for user123", context=context
        )

        # Assert
        assert result.success is True
        assert result.node_name == "process_message"
        assert result.node_type == NodeType.ACTION
        assert result.input == "Process this message for user123"
        assert result.output is not None
        assert "response" in result.output
        assert "message_count" in result.output
        assert "last_processed" in result.output

    @patch("intent_kit.services.ai.ollama_client.OllamaClient.generate")
    def test_action_node_with_validators(self, mock_generate):
        """Test ActionNode with input and output validators."""

        # Arrange
        def mock_action(name: str, age: int) -> str:
            return f"Hello {name}, you are {age} years old"

        def input_validator(params: Dict[str, Any]) -> bool:
            return "name" in params and "age" in params and params["age"] >= 18

        def output_validator(result: str) -> bool:
            return len(result) > 0 and "Hello" in result

        param_schema = {"name": str, "age": int}
        llm_config = {"provider": "ollama", "model": "llama2"}

        # Mock the LLM response for parameter extraction
        from intent_kit.types import (
            LLMResponse,
            Model,
            InputTokens,
            OutputTokens,
            Cost,
            Provider,
            Duration,
        )

        mock_response = LLMResponse(
            output={"name": "David", "age": 35},
            model=Model("llama2"),
            input_tokens=InputTokens(12),
            output_tokens=OutputTokens(6),
            cost=Cost(0.0015),
            provider=Provider("ollama"),
            duration=Duration(0.12),
        )
        mock_generate.return_value = mock_response

        from intent_kit.strategies import (
            create_input_validator,
            create_output_validator,
        )

        action_node = ActionNode(
            name="greet_adult",
            param_schema=param_schema,
            action=mock_action,
            input_validator=create_input_validator(input_validator),
            output_validator=create_output_validator(output_validator),
            llm_config=llm_config,
        )

        # Act - Valid case
        result = action_node.execute("Greet David who is 35 years old")

        # Assert - Should succeed
        assert result.success is True
        assert result.output == "Hello David, you are 35 years old"

        # Act - Invalid case (underage)
        # Mock different response for underage case
        mock_response_underage = LLMResponse(
            output={"name": "Child", "age": 15},
            model=Model("llama2"),
            input_tokens=InputTokens(10),
            output_tokens=OutputTokens(5),
            cost=Cost(0.001),
            provider=Provider("ollama"),
            duration=Duration(0.1),
        )
        mock_generate.return_value = mock_response_underage

        result = action_node.execute("Greet child who is 15 years old")

        # Assert - Should fail due to input validation
        assert result.success is False
        assert result.error is not None
        assert "validation" in result.error.message.lower()

    @patch("intent_kit.services.ai.ollama_client.OllamaClient.generate")
    def test_action_node_with_string_type_names(self, mock_generate):
        """Test action node with string type names in param_schema."""
        # Mock the LLM response for parameter extraction
        from intent_kit.types import (
            LLMResponse,
            Model,
            InputTokens,
            OutputTokens,
            Cost,
            Provider,
            Duration,
        )

        mock_response = LLMResponse(
            output={"name": "John"},
            model=Model("llama2"),
            input_tokens=InputTokens(10),
            output_tokens=OutputTokens(5),
            cost=Cost(0.001),
            provider=Provider("ollama"),
            duration=Duration(0.1),
        )
        mock_generate.return_value = mock_response

        # Create action node with string type names
        node = ActionNode(
            name="test_action",
            action=lambda name: f"Hello {name}!",
            param_schema={"name": "str"},
            llm_config={"provider": "ollama", "model": "llama2"},
        )

        # Test that the node can be created and executed
        result = node.execute("My name is John")
        assert result.success
        assert result.output == "Hello John!"

        # Test with mixed type specifications
        mock_response2 = LLMResponse(
            output={"name": "Alice", "age": 25},
            model=Model("llama2"),
            input_tokens=InputTokens(10),
            output_tokens=OutputTokens(5),
            cost=Cost(0.001),
            provider=Provider("ollama"),
            duration=Duration(0.1),
        )
        mock_generate.return_value = mock_response2

        node2 = ActionNode(
            name="test_action2",
            action=lambda name, age: f"Hello {name}, you are {age} years old!",
            param_schema={"name": "str", "age": "int"},
            llm_config={"provider": "ollama", "model": "llama2"},
        )

        result2 = node2.execute("My name is Alice and I am 25 years old")
        assert result2.success
        assert result2.output is not None
        assert "Alice" in result2.output
        assert "25" in result2.output
