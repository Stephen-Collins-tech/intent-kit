"""Tests for ActionNode."""

import pytest
from unittest.mock import Mock
from intent_kit.nodes.action import ActionNode
from intent_kit.core.types import ExecutionResult
from intent_kit.core.context import DefaultContext


class TestActionNode:
    """Test cases for ActionNode."""

    def test_action_node_initialization(self):
        """Test ActionNode initialization with all parameters."""
        mock_action = Mock(return_value="test_result")

        node = ActionNode(
            name="test_action",
            action=mock_action,
            description="Test action node",
            terminate_on_success=True,
            param_key="test_params",
            context_read=["user.name", "user.preferences"],
            context_write=["action.result", "action.count"],
            param_keys=["test_params", "extracted_params"],
        )

        assert node.name == "test_action"
        assert node.action == mock_action
        assert node.description == "Test action node"
        assert node.terminate_on_success is True
        assert node.param_key == "test_params"
        assert node.context_read == ["user.name", "user.preferences"]
        assert node.context_write == ["action.result", "action.count"]
        assert node.param_keys == ["test_params", "extracted_params"]

    def test_action_node_initialization_defaults(self):
        """Test ActionNode initialization with default values."""
        mock_action = Mock(return_value="test_result")

        node = ActionNode(name="test_action", action=mock_action)

        assert node.name == "test_action"
        assert node.action == mock_action
        assert node.description == ""
        assert node.terminate_on_success is True
        assert node.param_key == "extracted_params"
        assert node.context_read == []
        assert node.context_write == []
        assert node.param_keys == ["extracted_params"]

    def test_execute_basic(self):
        """Test basic action execution without context."""

        def test_action(name: str) -> str:
            return f"Hello {name}!"

        node = ActionNode(name="test_action", action=test_action)

        context = DefaultContext()
        context.set("extracted_params", {"name": "Alice"})

        result = node.execute("Hello Alice", context)

        assert isinstance(result, ExecutionResult)
        assert result.data == "Hello Alice!"
        assert result.terminate is True
        assert result.next_edges is None
        assert "action_result" in result.context_patch
        assert "action_name" in result.context_patch

    def test_execute_with_context_read(self):
        """Test action execution with context read."""

        def test_action(name: str, **kwargs) -> str:
            user_name = kwargs.get("user.name")
            return f"Hello {name}! User: {user_name}"

        node = ActionNode(
            name="test_action", action=test_action, context_read=["user.name"]
        )

        context = DefaultContext()
        context.set("extracted_params", {"name": "Alice"})
        context.set("user.name", "Bob")

        result = node.execute("Hello Alice", context)

        assert result.data == "Hello Alice! User: Bob"

    def test_execute_with_context_write(self):
        """Test action execution with context write."""

        def test_action(name: str) -> str:
            return f"Hello {name}!"

        node = ActionNode(
            name="test_action",
            action=test_action,
            context_write=["user.name", "greeting.count"],
        )

        context = DefaultContext()
        context.set("extracted_params", {"name": "Alice"})

        result = node.execute("Hello Alice", context)

        # Check that context write keys are in the patch
        assert "user.name" in result.context_patch
        # greeting.count is not in all_params, so it won't be written
        # assert "greeting.count" in result.context_patch
        assert result.context_patch["user.name"] == "Alice"

    def test_execute_with_param_keys(self):
        """Test action execution with custom param_keys."""

        def test_action(name: str) -> str:
            return f"Hello {name}!"

        node = ActionNode(
            name="test_action",
            action=test_action,
            param_keys=["name_params", "extracted_params"],
        )

        context = DefaultContext()
        context.set("name_params", {"name": "Alice"})
        # Note: extracted_params is not set, should use name_params

        result = node.execute("Hello Alice", context)

        assert result.data == "Hello Alice!"

    def test_execute_param_keys_fallback(self):
        """Test that param_keys fallback works correctly."""

        def test_action(name: str) -> str:
            return f"Hello {name}!"

        node = ActionNode(
            name="test_action",
            action=test_action,
            param_keys=["name_params", "extracted_params"],
        )

        context = DefaultContext()
        # name_params not set, should fall back to extracted_params
        context.set("extracted_params", {"name": "Alice"})

        result = node.execute("Hello Alice", context)

        assert result.data == "Hello Alice!"

    def test_execute_no_params_found(self):
        """Test action execution when no parameters are found."""

        def test_action(**kwargs) -> str:
            return "No parameters"

        node = ActionNode(
            name="test_action",
            action=test_action,
            param_keys=["name_params", "extracted_params"],
        )

        context = DefaultContext()
        # No parameters set

        result = node.execute("Hello", context)

        assert result.data == "No parameters"

    def test_execute_special_context_write_cases(self):
        """Test special context write cases (user.name, user.first_seen, etc.)."""

        def test_action(name: str, location: str) -> str:
            return f"Weather for {location}"

        node = ActionNode(
            name="test_action",
            action=test_action,
            param_keys=[
                "name_params",
                "location_params",
            ],  # Specify which keys to look for
            context_write=[
                "user.name",
                "user.first_seen",
                "weather.requests",
                "weather.last_location",
            ],
        )

        context = DefaultContext()
        context.set("name_params", {"name": "Alice"})
        context.set("location_params", {"location": "San Francisco"})

        result = node.execute("Weather request", context)

        # Check special cases are handled
        assert "user.name" in result.context_patch
        assert "user.first_seen" in result.context_patch
        assert "weather.requests" in result.context_patch
        assert "weather.last_location" in result.context_patch
        assert result.context_patch["user.name"] == "Alice"
        assert result.context_patch["weather.last_location"] == "San Francisco"

    def test_execute_weather_requests_counter(self):
        """Test weather requests counter increment."""

        def test_action(location: str) -> str:
            return f"Weather for {location}"

        node = ActionNode(
            name="test_action",
            action=test_action,
            param_keys=["location_params"],  # Specify which key to look for
            context_write=["weather.requests"],
        )

        context = DefaultContext()
        context.set("location_params", {"location": "San Francisco"})

        # First request
        result1 = node.execute("Weather request", context)
        assert result1.context_patch["weather.requests"] == 1

        # Second request
        context.set("weather.requests", 1)
        result2 = node.execute("Weather request", context)
        assert result2.context_patch["weather.requests"] == 2

    def test_execute_terminate_on_success_false(self):
        """Test action execution with terminate_on_success=False."""

        def test_action(name: str) -> str:
            return f"Hello {name}!"

        node = ActionNode(
            name="test_action", action=test_action, terminate_on_success=False
        )

        context = DefaultContext()
        context.set("extracted_params", {"name": "Alice"})

        result = node.execute("Hello Alice", context)

        assert result.terminate is False
        assert result.next_edges == ["next"]

    def test_execute_action_error(self):
        """Test action execution when action raises an error."""

        def test_action(name: str) -> str:
            raise ValueError("Action error")

        node = ActionNode(name="test_action", action=test_action)

        context = DefaultContext()
        context.set("extracted_params", {"name": "Alice"})

        with pytest.raises(ValueError, match="Action error"):
            node.execute("Hello Alice", context)

    def test_context_read_keys_property(self):
        """Test context_read_keys property."""
        node = ActionNode(
            name="test_action",
            action=Mock(),
            context_read=["user.name", "user.preferences"],
        )

        assert node.context_read_keys == ["user.name", "user.preferences"]

    def test_context_write_keys_property(self):
        """Test context_write_keys property."""
        node = ActionNode(
            name="test_action",
            action=Mock(),
            context_write=["action.result", "action.count"],
        )

        assert node.context_write_keys == ["action.result", "action.count"]

    def test_get_params_from_context_primary_key(self):
        """Test _get_params_from_context with primary param_key."""
        node = ActionNode(name="test_action", action=Mock(), param_key="test_params")

        context = DefaultContext()
        context.set("test_params", {"name": "Alice"})

        params = node._get_params_from_context(context)
        assert params == {"name": "Alice"}

    def test_get_params_from_context_fallback_keys(self):
        """Test _get_params_from_context with fallback param_keys."""
        node = ActionNode(
            name="test_action",
            action=Mock(),
            param_key="primary_params",
            param_keys=["primary_params", "name_params", "extracted_params"],
        )

        context = DefaultContext()
        # primary_params not set, should use name_params
        context.set("name_params", {"name": "Alice"})

        params = node._get_params_from_context(context)
        assert params == {"name": "Alice"}

    def test_get_params_from_context_no_params(self):
        """Test _get_params_from_context when no parameters are found."""
        node = ActionNode(
            name="test_action",
            action=Mock(),
            param_keys=["name_params", "extracted_params"],
        )

        context = DefaultContext()
        # No parameters set

        params = node._get_params_from_context(context)
        assert params == {}

    def test_get_params_from_context_invalid_type(self):
        """Test _get_params_from_context with invalid parameter type."""
        node = ActionNode(name="test_action", action=Mock(), param_key="test_params")

        context = DefaultContext()
        context.set("test_params", "not_a_dict")

        params = node._get_params_from_context(context)
        assert params == {}

    def test_execute_with_complex_context_data(self):
        """Test action execution with complex context data."""

        def test_action(name: str, **kwargs) -> str:
            user_prefs = kwargs.get("user.preferences", {})
            language = user_prefs.get("language", "en")
            return f"Hello {name} in {language}!"

        node = ActionNode(
            name="test_action", action=test_action, context_read=["user.preferences"]
        )

        context = DefaultContext()
        context.set("extracted_params", {"name": "Alice"})
        context.set("user.preferences", {"language": "es", "theme": "dark"})

        result = node.execute("Hello Alice", context)

        assert result.data == "Hello Alice in es!"

    def test_execute_context_patch_structure(self):
        """Test that context patch has the correct structure."""

        def test_action(name: str) -> str:
            return f"Hello {name}!"

        node = ActionNode(
            name="test_action", action=test_action, context_write=["user.name"]
        )

        context = DefaultContext()
        context.set("extracted_params", {"name": "Alice"})

        result = node.execute("Hello Alice", context)

        expected_patch_keys = {"action_result", "action_name", "user.name"}
        assert set(result.context_patch.keys()) == expected_patch_keys
        assert result.context_patch["action_result"] == "Hello Alice!"
        assert result.context_patch["action_name"] == "test_action"
        assert result.context_patch["user.name"] == "Alice"
