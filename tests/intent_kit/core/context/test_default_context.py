"""Tests for DefaultContext implementation."""

import pytest
from intent_kit.core.context import DefaultContext, ContextPatch
from intent_kit.core.exceptions import ContextConflictError


class TestDefaultContext:
    """Test the DefaultContext implementation."""

    def test_basic_get_set(self):
        """Test basic get and set operations."""
        ctx = DefaultContext()
        ctx.set("test_key", "test_value")
        assert ctx.get("test_key") == "test_value"
        assert ctx.get("nonexistent", "default") == "default"

    def test_has_and_keys(self):
        """Test has and keys methods."""
        ctx = DefaultContext()
        ctx.set("key1", "value1")
        ctx.set("key2", "value2")

        assert ctx.has("key1")
        assert ctx.has("key2")
        assert not ctx.has("key3")

        keys = list(ctx.keys())
        assert "key1" in keys
        assert "key2" in keys
        assert len(keys) == 2

    def test_snapshot(self):
        """Test snapshot method."""
        ctx = DefaultContext()
        ctx.set("key1", "value1")
        ctx.set("key2", "value2")

        snapshot = ctx.snapshot()
        assert snapshot["key1"] == "value1"
        assert snapshot["key2"] == "value2"
        assert len(snapshot) == 2

    def test_apply_patch_basic(self):
        """Test basic patch application."""
        ctx = DefaultContext()
        ctx.set("existing_key", "old_value")

        patch = ContextPatch(
            data={"existing_key": "new_value", "new_key": "new_value"},
            provenance="test",
        )
        ctx.apply_patch(patch)

        assert ctx.get("existing_key") == "new_value"
        assert ctx.get("new_key") == "new_value"

    def test_apply_patch_with_policies(self):
        """Test patch application with specific policies."""
        ctx = DefaultContext()
        ctx.set("list_key", ["item1", "item2"])
        ctx.set("dict_key", {"key1": "value1"})

        patch = ContextPatch(
            data={"list_key": ["item3", "item4"], "dict_key": {"key2": "value2"}},
            policy={"list_key": "append_list", "dict_key": "merge_dict"},
            provenance="test",
        )
        ctx.apply_patch(patch)

        assert ctx.get("list_key") == ["item1", "item2", "item3", "item4"]
        assert ctx.get("dict_key") == {"key1": "value1", "key2": "value2"}

    def test_apply_patch_protected_namespace(self):
        """Test that protected namespaces are blocked."""
        ctx = DefaultContext()

        patch = ContextPatch(data={"private.secret": "value"}, provenance="test")

        with pytest.raises(ContextConflictError, match="Write to protected namespace"):
            ctx.apply_patch(patch)

    def test_apply_patch_deterministic_order(self):
        """Test that patch application is deterministic."""
        ctx = DefaultContext()

        # Create a patch with multiple keys
        patch = ContextPatch(
            data={"key3": "value3", "key1": "value1", "key2": "value2"},
            provenance="test",
        )
        ctx.apply_patch(patch)

        # Verify all keys were applied
        assert ctx.get("key1") == "value1"
        assert ctx.get("key2") == "value2"
        assert ctx.get("key3") == "value3"

    def test_merge_from(self):
        """Test merge_from method."""
        ctx = DefaultContext()
        ctx.set("existing_key", "existing_value")

        other = {"existing_key": "new_value", "new_key": "new_value"}
        ctx.merge_from(other)

        assert ctx.get("existing_key") == "new_value"
        assert ctx.get("new_key") == "new_value"

    def test_fingerprint_basic(self):
        """Test basic fingerprint functionality."""
        ctx = DefaultContext()
        ctx.set("user.name", "Alice")
        ctx.set("user.age", 25)

        fp1 = ctx.fingerprint()
        fp2 = ctx.fingerprint()

        # Fingerprint should be stable
        assert fp1 == fp2

        # Fingerprint should be a string
        assert isinstance(fp1, str)
        assert len(fp1) > 0

    def test_fingerprint_excludes_tmp(self):
        """Test that tmp.* keys don't affect fingerprint."""
        ctx = DefaultContext()
        ctx.set("user.name", "Alice")
        ctx.set("tmp.debug", "debug_value")

        fp1 = ctx.fingerprint()

        # Change tmp value
        ctx.set("tmp.debug", "different_debug_value")
        fp2 = ctx.fingerprint()

        # Fingerprints should be the same
        assert fp1 == fp2

    def test_fingerprint_excludes_private(self):
        """Test that private.* keys don't affect fingerprint."""
        ctx = DefaultContext()
        ctx.set("user.name", "Alice")
        ctx.set("private.secret", "secret_value")

        fp1 = ctx.fingerprint()

        # Change private value
        ctx.set("private.secret", "different_secret_value")
        fp2 = ctx.fingerprint()

        # Fingerprints should be the same
        assert fp1 == fp2

    def test_fingerprint_with_include(self):
        """Test fingerprint with specific include patterns."""
        ctx = DefaultContext()
        ctx.set("user.name", "Alice")
        ctx.set("shared.data", "shared_value")
        ctx.set("other.info", "other_value")

        # Include only user.* and shared.*
        fp = ctx.fingerprint(include=["user.*", "shared.*"])

        # Change other.info (should not affect fingerprint)
        ctx.set("other.info", "different_value")
        fp2 = ctx.fingerprint(include=["user.*", "shared.*"])

        assert fp == fp2

    def test_logger_property(self):
        """Test logger property."""
        ctx = DefaultContext()
        logger = ctx.logger

        assert logger is not None
        assert hasattr(logger, "info")
        assert hasattr(logger, "warning")
        assert hasattr(logger, "error")
        assert hasattr(logger, "debug")

    def test_add_error(self):
        """Test add_error method."""
        ctx = DefaultContext()
        ctx.add_error(where="test", err="test error", meta={"key": "value"})

        # add_error only logs, doesn't store in context
        # This is the current implementation behavior

    def test_track_operation(self):
        """Test track_operation method."""
        ctx = DefaultContext()
        ctx.track_operation(name="test_op", status="success", meta={"key": "value"})

        # track_operation only logs, doesn't store in context
        # This is the current implementation behavior

    def test_context_patch_with_tags(self):
        """Test ContextPatch with tags."""
        ctx = DefaultContext()

        patch = ContextPatch(
            data={"test_key": "test_value"}, provenance="test", tags={"tag1", "tag2"}
        )
        ctx.apply_patch(patch)

        assert ctx.get("test_key") == "test_value"

    def test_context_patch_empty_data(self):
        """Test ContextPatch with empty data."""
        ctx = DefaultContext()

        patch = ContextPatch(data={}, provenance="test")
        ctx.apply_patch(patch)

        # Should not raise any errors
        assert True

    def test_context_patch_none_provenance(self):
        """Test ContextPatch with None provenance."""
        ctx = DefaultContext()

        patch = ContextPatch(data={"test_key": "test_value"})
        ctx.apply_patch(patch)

        assert ctx.get("test_key") == "test_value"
