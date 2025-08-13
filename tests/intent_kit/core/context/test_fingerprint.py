"""Tests for fingerprint functionality."""

from intent_kit.core.context.fingerprint import canonical_fingerprint


class TestFingerprint:
    """Test the fingerprint functionality."""

    def test_canonical_fingerprint_basic(self):
        """Test basic fingerprint generation."""
        data = {"key1": "value1", "key2": "value2"}
        fp = canonical_fingerprint(data)

        assert isinstance(fp, str)
        assert len(fp) > 0
        assert '"key1":"value1"' in fp
        assert '"key2":"value2"' in fp

    def test_canonical_fingerprint_stable_order(self):
        """Test that fingerprint is stable regardless of key order."""
        data1 = {"key1": "value1", "key2": "value2"}
        data2 = {"key2": "value2", "key1": "value1"}

        fp1 = canonical_fingerprint(data1)
        fp2 = canonical_fingerprint(data2)

        assert fp1 == fp2

    def test_canonical_fingerprint_empty(self):
        """Test fingerprint with empty data."""
        data = {}
        fp = canonical_fingerprint(data)

        assert fp == "{}"

    def test_canonical_fingerprint_nested(self):
        """Test fingerprint with nested data structures."""
        data = {
            "user": {"name": "Alice", "age": 25},
            "settings": {"theme": "dark", "notifications": True},
        }

        fp = canonical_fingerprint(data)

        assert isinstance(fp, str)
        assert len(fp) > 0
        assert '"user"' in fp
        assert '"name":"Alice"' in fp
        assert '"age":25' in fp

    def test_canonical_fingerprint_lists(self):
        """Test fingerprint with lists."""
        data = {"items": ["item1", "item2", "item3"], "counts": [1, 2, 3]}

        fp = canonical_fingerprint(data)

        assert isinstance(fp, str)
        assert len(fp) > 0
        assert '"items"' in fp
        assert '"item1"' in fp
        assert '"counts"' in fp
        assert "1" in fp  # Numbers are not quoted in JSON

    def test_canonical_fingerprint_mixed_types(self):
        """Test fingerprint with mixed data types."""
        data = {
            "string": "hello",
            "number": 42,
            "boolean": True,
            "null": None,
            "float": 3.14,
        }

        fp = canonical_fingerprint(data)

        assert isinstance(fp, str)
        assert len(fp) > 0
        assert '"string":"hello"' in fp
        assert '"number":42' in fp
        assert '"boolean":true' in fp
        assert '"null":null' in fp
        assert '"float":3.14' in fp

    def test_canonical_fingerprint_unicode(self):
        """Test fingerprint with unicode characters."""
        data = {"name": "José", "message": "Hello, 世界!"}

        fp = canonical_fingerprint(data)

        assert isinstance(fp, str)
        assert len(fp) > 0
        # Unicode characters are escaped in JSON
        assert '"name":"Jos\\u00e9"' in fp
        assert '"message":"Hello, \\u4e16\\u754c!"' in fp

    def test_canonical_fingerprint_special_chars(self):
        """Test fingerprint with special characters."""
        data = {
            "path": "/path/to/file",
            "url": "https://example.com?param=value",
            "json": '{"nested": "value"}',
        }

        fp = canonical_fingerprint(data)

        assert isinstance(fp, str)
        assert len(fp) > 0
        assert '"path":"/path/to/file"' in fp
        assert '"url":"https://example.com?param=value"' in fp
        assert '"json":"{\\"nested\\": \\"value\\"}"' in fp

    def test_canonical_fingerprint_deterministic(self):
        """Test that fingerprint is deterministic for same input."""
        data = {"key": "value"}

        fp1 = canonical_fingerprint(data)
        fp2 = canonical_fingerprint(data)
        fp3 = canonical_fingerprint(data)

        assert fp1 == fp2 == fp3

    def test_canonical_fingerprint_different_inputs(self):
        """Test that different inputs produce different fingerprints."""
        data1 = {"key": "value1"}
        data2 = {"key": "value2"}
        data3 = {"different_key": "value1"}

        fp1 = canonical_fingerprint(data1)
        fp2 = canonical_fingerprint(data2)
        fp3 = canonical_fingerprint(data3)

        assert fp1 != fp2
        assert fp1 != fp3
        assert fp2 != fp3

    def test_canonical_fingerprint_large_data(self):
        """Test fingerprint with larger data structures."""
        data = {
            "users": [
                {"id": 1, "name": "Alice", "active": True},
                {"id": 2, "name": "Bob", "active": False},
                {"id": 3, "name": "Charlie", "active": True},
            ],
            "settings": {
                "theme": "dark",
                "language": "en",
                "timezone": "UTC",
                "notifications": {"email": True, "push": False, "sms": True},
            },
            "metadata": {
                "version": "1.0.0",
                "created": "2023-01-01T00:00:00Z",
                "tags": ["production", "stable"],
            },
        }

        fp = canonical_fingerprint(data)

        assert isinstance(fp, str)
        assert len(fp) > 0
        # Should contain key elements from the data
        assert '"users"' in fp
        assert '"settings"' in fp
        assert '"metadata"' in fp
        assert '"Alice"' in fp
        assert '"Bob"' in fp
        assert '"Charlie"' in fp
