"""Tests for context merge policies."""

import pytest
from intent_kit.core.context.policies import apply_merge
from intent_kit.core.exceptions import ContextConflictError


class TestMergePolicies:
    """Test the various merge policies."""

    def test_last_write_wins_basic(self):
        """Test last_write_wins policy with basic values."""
        result = apply_merge(
            policy="last_write_wins",
            existing="old_value",
            incoming="new_value",
            key="test_key",
        )
        assert result == "new_value"

    def test_first_write_wins_basic(self):
        """Test first_write_wins policy with basic values."""
        result = apply_merge(
            policy="first_write_wins",
            existing="old_value",
            incoming="new_value",
            key="test_key",
        )
        assert result == "old_value"

    def test_first_write_wins_none_existing(self):
        """Test first_write_wins when existing is None."""
        result = apply_merge(
            policy="first_write_wins",
            existing=None,
            incoming="new_value",
            key="test_key",
        )
        assert result == "new_value"

    def test_append_list_basic(self):
        """Test append_list policy with lists."""
        result = apply_merge(
            policy="append_list",
            existing=["item1", "item2"],
            incoming=["item3", "item4"],
            key="test_key",
        )
        assert result == ["item1", "item2", "item3", "item4"]

    def test_append_list_none_existing(self):
        """Test append_list when existing is None."""
        result = apply_merge(
            policy="append_list",
            existing=None,
            incoming=["item1", "item2"],
            key="test_key",
        )
        assert result == ["item1", "item2"]

    def test_append_list_non_list_existing(self):
        """Test append_list when existing is not a list."""
        with pytest.raises(ContextConflictError, match="append_list expects list"):
            apply_merge(
                policy="append_list",
                existing="not_a_list",
                incoming=["item1", "item2"],
                key="test_key",
            )

    def test_append_list_non_list_incoming(self):
        """Test append_list when incoming is not a list."""
        with pytest.raises(ContextConflictError, match="append_list expects list"):
            apply_merge(
                policy="append_list",
                existing=["item1", "item2"],
                incoming="not_a_list",
                key="test_key",
            )

    def test_merge_dict_basic(self):
        """Test merge_dict policy with dictionaries."""
        existing = {"key1": "value1", "key2": "value2"}
        incoming = {"key2": "new_value2", "key3": "value3"}
        result = apply_merge(
            policy="merge_dict", existing=existing, incoming=incoming, key="test_key"
        )
        expected = {"key1": "value1", "key2": "new_value2", "key3": "value3"}
        assert result == expected

    def test_merge_dict_none_existing(self):
        """Test merge_dict when existing is None."""
        incoming = {"key1": "value1", "key2": "value2"}
        result = apply_merge(
            policy="merge_dict", existing=None, incoming=incoming, key="test_key"
        )
        assert result == incoming

    def test_merge_dict_non_dict_existing(self):
        """Test merge_dict when existing is not a dict."""
        with pytest.raises(ContextConflictError, match="merge_dict expects dicts"):
            apply_merge(
                policy="merge_dict",
                existing="not_a_dict",
                incoming={"key1": "value1"},
                key="test_key",
            )

    def test_merge_dict_non_dict_incoming(self):
        """Test merge_dict when incoming is not a dict."""
        with pytest.raises(ContextConflictError, match="merge_dict expects dicts"):
            apply_merge(
                policy="merge_dict",
                existing={"key1": "value1"},
                incoming="not_a_dict",
                key="test_key",
            )

    def test_reduce_policy_not_implemented(self):
        """Test that reduce policy raises NotImplementedError."""
        with pytest.raises(
            ContextConflictError, match="Reducer not registered for key"
        ):
            apply_merge(
                policy="reduce", existing="value1", incoming="value2", key="test_key"
            )

    def test_unknown_policy(self):
        """Test that unknown policy raises error."""
        with pytest.raises(ContextConflictError, match="Unknown merge policy"):
            apply_merge(
                policy="unknown_policy",
                existing="value1",
                incoming="value2",
                key="test_key",
            )

    def test_numeric_values(self):
        """Test policies with numeric values."""
        # last_write_wins with numbers
        result = apply_merge(
            policy="last_write_wins", existing=42, incoming=100, key="test_key"
        )
        assert result == 100

        # first_write_wins with numbers
        result = apply_merge(
            policy="first_write_wins", existing=42, incoming=100, key="test_key"
        )
        assert result == 42

    def test_boolean_values(self):
        """Test policies with boolean values."""
        # last_write_wins with booleans
        result = apply_merge(
            policy="last_write_wins", existing=True, incoming=False, key="test_key"
        )
        assert not result

        # first_write_wins with booleans
        result = apply_merge(
            policy="first_write_wins", existing=True, incoming=False, key="test_key"
        )
        assert result
