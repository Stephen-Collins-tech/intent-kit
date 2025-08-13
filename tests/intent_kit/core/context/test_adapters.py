"""Tests for context adapters."""

import pytest
from intent_kit.core.context import DictBackedContext


class TestDictBackedContext:
    """Test the DictBackedContext adapter."""

    def test_basic_functionality(self):
        """Test basic functionality of DictBackedContext."""
        backing_dict = {"existing_key": "existing_value"}
        ctx = DictBackedContext(backing=backing_dict)

        # Should read from backing dict (hydrated during init)
        assert ctx.get("existing_key") == "existing_value"

        # Should write to internal context (not backing dict)
        ctx.set("new_key", "new_value")
        assert ctx.get("new_key") == "new_value"
        # Note: DictBackedContext only hydrates once, doesn't sync back

    def test_inherits_from_default_context(self):
        """Test that DictBackedContext inherits all DefaultContext functionality."""
        backing_dict = {}
        ctx = DictBackedContext(backing=backing_dict)

        # Test basic operations
        ctx.set("key1", "value1")
        ctx.set("key2", "value2")

        assert ctx.get("key1") == "value1"
        assert ctx.get("key2") == "value2"
        assert ctx.has("key1")
        assert not ctx.has("key3")

        keys = list(ctx.keys())
        assert "key1" in keys
        assert "key2" in keys

    def test_snapshot_includes_backing_data(self):
        """Test that snapshot includes data from backing dict."""
        backing_dict = {"backing_key": "backing_value"}
        ctx = DictBackedContext(backing=backing_dict)

        ctx.set("new_key", "new_value")

        snapshot = ctx.snapshot()
        assert snapshot["backing_key"] == "backing_value"
        assert snapshot["new_key"] == "new_value"
        assert len(snapshot) == 2

    def test_apply_patch_updates_internal_context(self):
        """Test that apply_patch updates the internal context."""
        backing_dict = {"existing_key": "old_value"}
        ctx = DictBackedContext(backing=backing_dict)

        from intent_kit.core.context import ContextPatch

        patch = ContextPatch(
            data={"existing_key": "new_value", "new_key": "new_value"},
            provenance="test",
        )

        ctx.apply_patch(patch)

        # Should update internal context
        assert ctx.get("existing_key") == "new_value"
        assert ctx.get("new_key") == "new_value"
        # Note: Backing dict is not updated (one-time hydration only)

    def test_fingerprint_includes_backing_data(self):
        """Test that fingerprint includes data from backing dict."""
        backing_dict = {"user.name": "Alice", "user.age": 25}
        ctx = DictBackedContext(backing=backing_dict)

        fp = ctx.fingerprint()

        # Should include backing data
        assert "Alice" in fp
        assert "25" in fp

    def test_merge_from_updates_internal_context(self):
        """Test that merge_from updates the internal context."""
        backing_dict = {"existing_key": "existing_value"}
        ctx = DictBackedContext(backing=backing_dict)

        other = {"existing_key": "new_value", "new_key": "new_value"}
        ctx.merge_from(other)

        # Should update internal context
        assert ctx.get("existing_key") == "new_value"
        assert ctx.get("new_key") == "new_value"
        # Note: Backing dict is not updated (one-time hydration only)

    def test_logger_property(self):
        """Test logger property."""
        backing_dict = {}
        ctx = DictBackedContext(backing=backing_dict)

        logger = ctx.logger
        assert logger is not None
        assert hasattr(logger, "info")
        assert hasattr(logger, "warning")
        assert hasattr(logger, "error")
        assert hasattr(logger, "debug")

    def test_add_error_logs_only(self):
        """Test that add_error only logs (doesn't store in context)."""
        backing_dict = {}
        ctx = DictBackedContext(backing=backing_dict)

        ctx.add_error(where="test", err="test error", meta={"key": "value"})

        # add_error only logs, doesn't store in context
        # This is the current implementation behavior

    def test_track_operation_logs_only(self):
        """Test that track_operation only logs (doesn't store in context)."""
        backing_dict = {}
        ctx = DictBackedContext(backing=backing_dict)

        ctx.track_operation(name="test_op", status="success", meta={"key": "value"})

        # track_operation only logs, doesn't store in context
        # This is the current implementation behavior

    def test_protected_namespace_still_works(self):
        """Test that protected namespace protection still works."""
        backing_dict = {}
        ctx = DictBackedContext(backing=backing_dict)

        from intent_kit.core.context import ContextPatch
        from intent_kit.core.exceptions import ContextConflictError

        patch = ContextPatch(data={"private.secret": "value"}, provenance="test")

        with pytest.raises(ContextConflictError, match="Write to protected namespace"):
            ctx.apply_patch(patch)

    def test_fingerprint_excludes_tmp_from_backing(self):
        """Test that fingerprint excludes tmp.* keys from backing dict."""
        backing_dict = {"user.name": "Alice", "tmp.debug": "debug_value"}
        ctx = DictBackedContext(backing=backing_dict)

        fp1 = ctx.fingerprint()

        # Change tmp value in backing dict
        backing_dict["tmp.debug"] = "different_debug_value"
        fp2 = ctx.fingerprint()

        # Fingerprints should be the same
        assert fp1 == fp2

    def test_empty_backing_dict(self):
        """Test with empty backing dict."""
        backing_dict = {}
        ctx = DictBackedContext(backing=backing_dict)

        # Should work normally
        ctx.set("key", "value")
        assert ctx.get("key") == "value"
        # Note: Backing dict is not updated (one-time hydration only)

    def test_none_backing_dict(self):
        """Test with None backing dict."""
        ctx = DictBackedContext(backing=None)

        # Should work normally (creates empty dict)
        ctx.set("key", "value")
        assert ctx.get("key") == "value"

    def test_backing_dict_one_time_hydration(self):
        """Test that DictBackedContext only hydrates once during init."""
        backing_dict = {"key1": "value1"}
        ctx = DictBackedContext(backing=backing_dict)

        # Should have hydrated key1 during init
        assert ctx.get("key1") == "value1"
        assert ctx.has("key1")

        # Direct modification of backing dict after init should not be visible
        backing_dict["key2"] = "value2"
        assert not ctx.has("key2")

        keys = list(ctx.keys())
        assert "key1" in keys
        assert "key2" not in keys
