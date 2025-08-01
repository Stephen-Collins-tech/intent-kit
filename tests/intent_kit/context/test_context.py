"""
Tests for the IntentContext system.
"""

import pytest
from intent_kit.context import IntentContext
from intent_kit.context.dependencies import (
    declare_dependencies,
    validate_context_dependencies,
    merge_dependencies,
)


class TestIntentContext:
    """Test the IntentContext class."""

    def test_context_creation(self):
        """Test creating a new context."""
        context = IntentContext(session_id="test_123")
        assert context.session_id == "test_123"
        assert len(context.keys()) == 0
        assert len(context.get_history()) == 0

    def test_context_auto_session_id(self):
        """Test that context gets auto-generated session ID if none provided."""
        context = IntentContext()
        assert context.session_id is not None
        assert len(context.session_id) > 0

    def test_context_set_get(self):
        """Test setting and getting values from context."""
        context = IntentContext(session_id="test_123")

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
        context = IntentContext()
        value = context.get("nonexistent", default="default_value")
        assert value == "default_value"

    def test_context_has_key(self):
        """Test checking if key exists."""
        context = IntentContext()
        assert not context.has("test_key")

        context.set("test_key", "value")
        assert context.has("test_key")

    def test_context_delete(self):
        """Test deleting a key."""
        context = IntentContext()
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
        context = IntentContext()
        context.set("key1", "value1")
        context.set("key2", "value2")

        keys = context.keys()
        assert "key1" in keys
        assert "key2" in keys
        assert len(keys) == 2

    def test_context_clear(self):
        """Test clearing all fields."""
        context = IntentContext()
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
        context = IntentContext()
        context.set("test_key", "test_value", modified_by="test")

        metadata = context.get_field_metadata("test_key")
        assert metadata is not None
        assert metadata["value"] == "test_value"
        assert metadata["modified_by"] == "test"
        assert "created_at" in metadata
        assert "last_modified" in metadata

    def test_context_get_history_filtered(self):
        """Test getting filtered history."""
        context = IntentContext()
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

        context = IntentContext()
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
        context = IntentContext()
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
        context = IntentContext()
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
