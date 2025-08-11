"""
Tests for the Context system.
"""

import pytest
from intent_kit.context import Context
from intent_kit.context.dependencies import (
    declare_dependencies,
    validate_context_dependencies,
    merge_dependencies,
)


class TestIntentContext:
    """Test the Context class."""

    def test_context_creation(self):
        """Test creating a new context."""
        context = Context(session_id="test_123")
        assert context.session_id == "test_123"
        assert len(context.keys()) == 0
        assert len(context.get_history()) == 0

    def test_context_auto_session_id(self):
        """Test that context gets auto-generated session ID if none provided."""
        context = Context()
        assert context.session_id is not None
        assert len(context.session_id) > 0

    def test_context_set_get(self):
        """Test setting and getting values from context."""
        context = Context(session_id="test_123")

        # Set a value
        context.set("test_key", "test_value", modified_by="test")

        # Get the value
        value = context.get("test_key")
        assert value == "test_value"

        # Check history - now includes both set and get operations
        history = context.get_history()
        assert len(history) == 2  # One for set, one for get
        assert history[0].action == "set"
        assert history[0].key == "test_key"
        assert history[0].value == "test_value"
        assert history[0].modified_by == "test"
        assert history[1].action == "get"
        assert history[1].key == "test_key"
        assert history[1].value == "test_value"
        # get operations don't have modified_by
        assert history[1].modified_by is None

    def test_context_default_value(self):
        """Test getting default value when key doesn't exist."""
        context = Context()
        value = context.get("nonexistent", default="default_value")
        assert value == "default_value"

    def test_context_has_key(self):
        """Test checking if key exists."""
        context = Context()
        assert not context.has("test_key")

        context.set("test_key", "value")
        assert context.has("test_key")

    def test_context_delete(self):
        """Test deleting a key."""
        context = Context()
        context.set("test_key", "value")
        assert context.has("test_key")

        deleted = context.delete("test_key", modified_by="test")
        assert deleted is True
        assert not context.has("test_key")

        # Try to delete non-existent key
        deleted = context.delete("nonexistent")
        assert deleted is False

    def test_context_keys(self):
        """Test getting all keys."""
        context = Context()
        context.set("key1", "value1")
        context.set("key2", "value2")

        keys = context.keys()
        assert "key1" in keys
        assert "key2" in keys
        assert len(keys) == 2

    def test_context_clear(self):
        """Test clearing all fields."""
        context = Context()
        context.set("key1", "value1")
        context.set("key2", "value2")

        assert len(context.keys()) == 2

        context.clear(modified_by="test")
        assert len(context.keys()) == 0

        # Check history
        history = context.get_history()
        assert len(history) == 3  # 2 sets + 1 clear
        assert history[-1].action == "clear"

    def test_context_get_field_metadata(self):
        """Test getting field metadata."""
        context = Context()
        context.set("test_key", "test_value", modified_by="test")

        metadata = context.get_field_metadata("test_key")
        assert metadata is not None
        assert metadata["value"] == "test_value"
        assert metadata["modified_by"] == "test"
        assert "created_at" in metadata
        assert "last_modified" in metadata

    def test_context_get_history_filtered(self):
        """Test getting filtered history."""
        context = Context()
        context.set("key1", "value1")
        context.set("key2", "value2")
        context.set("key1", "value1_updated")

        # Get history for specific key
        key1_history = context.get_history(key="key1")
        assert len(key1_history) == 2

        # Get limited history
        limited_history = context.get_history(limit=2)
        assert len(limited_history) == 2

    def test_context_thread_safety(self):
        """Test that context operations are thread-safe."""
        import threading
        import time

        context = Context()
        results = []

        def worker(thread_id):
            for i in range(10):
                context.set(
                    f"thread_{thread_id}_key_{i}",
                    f"value_{i}",
                    modified_by=f"thread_{thread_id}",
                )
                # Small delay to increase chance of race conditions
                time.sleep(0.001)
                value = context.get(f"thread_{thread_id}_key_{i}")
                results.append((thread_id, i, value))

        # Start multiple threads
        threads = []
        for i in range(3):
            t = threading.Thread(target=worker, args=(i,))
            threads.append(t)
            t.start()

        # Wait for all threads to complete
        for t in threads:
            t.join()

        # Verify all operations completed successfully
        assert len(results) == 30  # 3 threads * 10 operations each

        # Verify all values are correct
        for thread_id, i, value in results:
            assert value == f"value_{i}"

    def test_add_error(self):
        """Test adding errors to the context."""
        context = Context(session_id="test_123")

        # Add an error
        context.add_error(
            node_name="test_node",
            user_input="test input",
            error_message="Test error message",
            error_type="ValueError",
            params={"param1": "value1"},
        )

        # Check that error was added
        errors = context.get_errors()
        assert len(errors) == 1

        error = errors[0]
        assert error.node_name == "test_node"
        assert error.user_input == "test input"
        assert error.error_message == "Test error message"
        assert error.error_type == "ValueError"
        assert error.params == {"param1": "value1"}
        assert error.session_id == "test_123"
        assert error.stack_trace is not None

    def test_get_errors_filtered_by_node(self):
        """Test getting errors filtered by node name."""
        context = Context()

        # Add errors from different nodes
        context.add_error("node1", "input1", "error1", "TypeError")
        context.add_error("node2", "input2", "error2", "ValueError")
        context.add_error("node1", "input3", "error3", "RuntimeError")

        # Get all errors
        all_errors = context.get_errors()
        assert len(all_errors) == 3

        # Get errors for specific node
        node1_errors = context.get_errors(node_name="node1")
        assert len(node1_errors) == 2
        assert all(error.node_name == "node1" for error in node1_errors)

        # Get errors for non-existent node
        node3_errors = context.get_errors(node_name="node3")
        assert len(node3_errors) == 0

    def test_get_errors_with_limit(self):
        """Test getting errors with a limit."""
        context = Context()

        # Add multiple errors
        for i in range(5):
            context.add_error(f"node{i}", f"input{i}", f"error{i}", "TypeError")

        # Get all errors
        all_errors = context.get_errors()
        assert len(all_errors) == 5

        # Get limited errors
        limited_errors = context.get_errors(limit=3)
        assert len(limited_errors) == 3
        # Should return the last 3 errors
        assert limited_errors[0].node_name == "node2"
        assert limited_errors[1].node_name == "node3"
        assert limited_errors[2].node_name == "node4"

    def test_clear_errors(self):
        """Test clearing all errors from the context."""
        context = Context()

        # Add some errors
        context.add_error("node1", "input1", "error1", "TypeError")
        context.add_error("node2", "input2", "error2", "ValueError")

        # Verify errors exist
        assert len(context.get_errors()) == 2

        # Clear errors
        context.clear_errors()

        # Verify errors are cleared
        assert len(context.get_errors()) == 0

    def test_error_count(self):
        """Test getting the error count."""
        context = Context()

        # Initially no errors
        assert context.error_count() == 0

        # Add errors
        context.add_error("node1", "input1", "error1", "TypeError")
        assert context.error_count() == 1

        context.add_error("node2", "input2", "error2", "ValueError")
        assert context.error_count() == 2

        # Clear errors
        context.clear_errors()
        assert context.error_count() == 0

    def test_context_repr(self):
        """Test the string representation of the context."""
        context = Context(session_id="test_123")

        # Test empty context
        repr_str = repr(context)
        assert "Context" in repr_str
        assert "session_id=test_123" in repr_str
        assert "fields=0" in repr_str
        assert "history=0" in repr_str
        assert "errors=0" in repr_str

        # Test context with data
        context.set("key1", "value1")
        context.add_error("node1", "input1", "error1", "TypeError")

        repr_str = repr(context)
        assert "fields=1" in repr_str
        assert "history=1" in repr_str
        assert "errors=1" in repr_str

    def test_context_debug_mode(self):
        """Test context creation with debug mode enabled."""
        context = Context(session_id="test_123", debug=True)
        assert context.session_id == "test_123"
        assert context._debug is True

    def test_get_with_debug_logging(self):
        """Test get operations with debug logging enabled."""
        context = Context(debug=True)

        # Test get non-existent key with debug logging
        value = context.get("nonexistent", default="default_value")
        assert value == "default_value"

        # Test get existing key with debug logging
        context.set("test_key", "test_value")
        value = context.get("test_key")
        assert value == "test_value"

    def test_set_with_debug_logging(self):
        """Test set operations with debug logging enabled."""
        context = Context(debug=True)

        # Test creating new field with debug logging
        context.set("new_key", "new_value", modified_by="test")
        assert context.get("new_key") == "new_value"

        # Test updating existing field with debug logging
        context.set("new_key", "updated_value", modified_by="test")
        assert context.get("new_key") == "updated_value"

    def test_delete_with_debug_logging(self):
        """Test delete operations with debug logging enabled."""
        context = Context(debug=True)

        # Test deleting non-existent key with debug logging
        deleted = context.delete("nonexistent")
        assert deleted is False

        # Test deleting existing key with debug logging
        context.set("test_key", "test_value")
        deleted = context.delete("test_key")
        assert deleted is True

    def test_add_error_with_debug_logging(self):
        """Test adding errors with debug logging enabled."""
        context = Context(debug=True)

        context.add_error(
            node_name="test_node",
            user_input="test input",
            error_message="Test error message",
            error_type="ValueError",
        )

        errors = context.get_errors()
        assert len(errors) == 1
        assert errors[0].node_name == "test_node"

    def test_add_error_debug_logging_specific(self):
        """Test the specific debug logging line in add_error method."""
        context = Context(debug=True)

        # This should trigger the debug logging in add_error
        context.add_error(
            node_name="debug_test_node",
            user_input="debug test input",
            error_message="Debug test error message",
            error_type="RuntimeError",
            params={"test_param": "test_value"},
        )

        # Verify the error was added
        errors = context.get_errors()
        assert len(errors) == 1
        assert errors[0].node_name == "debug_test_node"

    def test_get_errors_with_debug_logging(self):
        """Test getting errors with debug logging enabled."""
        context = Context(debug=True)

        # Add some errors
        context.add_error("node1", "input1", "error1", "TypeError")
        context.add_error("node2", "input2", "error2", "ValueError")

        # Test getting all errors
        all_errors = context.get_errors()
        assert len(all_errors) == 2

        # Test getting filtered errors
        node1_errors = context.get_errors(node_name="node1")
        assert len(node1_errors) == 1

    def test_clear_errors_with_debug_logging(self):
        """Test clearing errors with debug logging enabled."""
        context = Context(debug=True)

        # Add some errors
        context.add_error("node1", "input1", "error1", "TypeError")
        context.add_error("node2", "input2", "error2", "ValueError")

        # Clear errors with debug logging
        context.clear_errors()
        assert len(context.get_errors()) == 0

    def test_clear_with_debug_logging(self):
        """Test clearing all fields with debug logging enabled."""
        context = Context(debug=True)

        # Add some fields
        context.set("key1", "value1")
        context.set("key2", "value2")

        # Verify fields exist before clearing
        assert len(context.keys()) == 2

        # Clear all fields with debug logging
        context.clear(modified_by="test")
        assert len(context.keys()) == 0

    def test_clear_method_coverage(self):
        """Test clear method to ensure line 230 is covered."""
        context = Context()

        # Add multiple fields to ensure the keys list is populated
        context.set("field1", "value1")
        context.set("field2", "value2")
        context.set("field3", "value3")

        # This should execute line 230: keys = list(self._fields.keys())
        context.clear()

        # Verify all fields are cleared
        assert len(context.keys()) == 0


class TestContextDependencies:
    """Test the context dependency system."""

    def test_declare_dependencies(self):
        """Test creating dependency declarations."""
        deps = declare_dependencies(
            inputs={"input1", "input2"},
            outputs={"output1"},
            description="Test dependencies",
        )

        assert deps.inputs == {"input1", "input2"}
        assert deps.outputs == {"output1"}
        assert deps.description == "Test dependencies"

    def test_validate_context_dependencies(self):
        """Test validating dependencies against context."""
        context = Context()
        context.set("input1", "value1")
        context.set("input2", "value2")

        deps = declare_dependencies(
            inputs={"input1", "input2", "missing_input"}, outputs={"output1"}
        )

        result = validate_context_dependencies(deps, context, strict=False)
        assert result["valid"] is True
        assert result["missing_inputs"] == {"missing_input"}
        assert result["available_inputs"] == {"input1", "input2"}
        assert len(result["warnings"]) == 1

    def test_validate_context_dependencies_strict(self):
        """Test strict validation of dependencies."""
        context = Context()
        context.set("input1", "value1")

        deps = declare_dependencies(
            inputs={"input1", "missing_input"}, outputs={"output1"}
        )

        result = validate_context_dependencies(deps, context, strict=True)
        assert result["valid"] is False
        assert result["missing_inputs"] == {"missing_input"}
        assert len(result["warnings"]) == 1

    def test_merge_dependencies(self):
        """Test merging multiple dependency declarations."""
        deps1 = declare_dependencies(inputs={"input1"}, outputs={"output1"})
        deps2 = declare_dependencies(inputs={"input2"}, outputs={"output2"})

        merged = merge_dependencies(deps1, deps2)
        assert merged.inputs == {"input1", "input2"}
        assert merged.outputs == {"output1", "output2"}


if __name__ == "__main__":
    pytest.main([__file__])
