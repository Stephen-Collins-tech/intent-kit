"""
Tests for node enums.
"""




class TestNodeType:
    """Test the NodeType enum."""

    def test_def test_all_enum_values_exist(self): -> None:
        """Test that all expected enum values exist."""
        expected_values = {
            "UNKNOWN": "unknown",
            "ACTION": "action",
            "CLASSIFIER": "classifier",
            "SPLITTER": "splitter",
            "CLARIFY": "clarify",
            "GRAPH": "graph",
            "UNHANDLED_CHUNK": "unhandled_chunk",
        }

        for name, value in expected_values.items():
            assert hasattr(NodeType, name)
            assert getattr(NodeType, name).value == value

    def test_def test_enum_values_are_strings(self): -> None:
        """Test that all enum values are strings."""
        for node_type in NodeType:
            assert isinstance(node_type.value, str)

    def test_def test_enum_values_are_unique(self): -> None:
        """Test that all enum values are unique."""
        values = [node_type.value for node_type in NodeType]
        assert len(values) == len(set(values))

    def test_def test_unknown_node_type(self): -> None:
        """Test the UNKNOWN node type."""
        assert NodeType.UNKNOWN.value == "unknown"

    def test_def test_action_node_type(self): -> None:
        """Test the ACTION node type."""
        assert NodeType.ACTION.value == "action"

    def test_def test_classifier_node_type(self): -> None:
        """Test the CLASSIFIER node type."""
        assert NodeType.CLASSIFIER.value == "classifier"

    def test_def test_splitter_node_type(self): -> None:
        """Test the SPLITTER node type."""
        assert NodeType.SPLITTER.value == "splitter"

    def test_def test_clarify_node_type(self): -> None:
        """Test the CLARIFY node type."""
        assert NodeType.CLARIFY.value == "clarify"

    def test_def test_graph_node_type(self): -> None:
        """Test the GRAPH node type."""
        assert NodeType.GRAPH.value == "graph"

    def test_def test_unhandled_chunk_node_type(self): -> None:
        """Test the UNHANDLED_CHUNK node type."""
        assert NodeType.UNHANDLED_CHUNK.value == "unhandled_chunk"

    def test_def test_enum_iteration(self): -> None:
        """Test that the enum can be iterated over."""
        node_types = list(NodeType)
        assert len(node_types) == 7  # Total number of enum values

    def test_def test_enum_comparison(self): -> None:
        """Test enum comparison operations."""
        assert NodeType.ACTION == NodeType.ACTION
        assert NodeType.ACTION != NodeType.CLASSIFIER
        assert NodeType.ACTION.value == "action"

    def test_def test_enum_string_conversion(self): -> None:
        """Test string conversion of enum values."""
        assert str(NodeType.ACTION) == "NodeType.ACTION"
        assert repr(NodeType.ACTION) == "<NodeType.ACTION: 'action'>"

    def test_def test_enum_value_access(self): -> None:
        """Test accessing enum values."""
        assert NodeType.ACTION.value == "action"
        assert NodeType.CLASSIFIER.value == "classifier"
        assert NodeType.SPLITTER.value == "splitter"

    def test_def test_enum_name_access(self): -> None:
        """Test accessing enum names."""
        assert NodeType.ACTION.name == "ACTION"
        assert NodeType.CLASSIFIER.name == "CLASSIFIER"
        assert NodeType.SPLITTER.name == "SPLITTER"

    def test_def test_enum_membership(self): -> None:
        """Test enum membership operations."""
        assert NodeType.ACTION in NodeType
        assert NodeType.CLASSIFIER in NodeType
        assert NodeType.SPLITTER in NodeType

    def test_def test_enum_value_membership(self): -> None:
        """Test checking if a value belongs to the enum."""
        valid_values = [node_type.value for node_type in NodeType]
        assert "action" in valid_values
        assert "classifier" in valid_values
        assert "splitter" in valid_values
        assert "invalid_type" not in valid_values

    def test_def test_enum_from_value(self): -> None:
        """Test creating enum from value."""
        # This is a common pattern for enums
        action_node = next((nt for nt in NodeType if nt.value == "action"), None)
        assert action_node == NodeType.ACTION

    def test_def test_enum_documentation(self): -> None:
        """Test that enum has proper documentation."""
        assert NodeType.__doc__ is not None
        assert "Enumeration of valid node types" in NodeType.__doc__

    def test_def test_enum_comment_documentation(self): -> None:
        """Test that enum values have proper comment documentation."""
        # Check that the enum file has proper comments
        import inspect

        source = inspect.getsource(NodeType)
        assert "# Base node types" in source
        assert "# Specialized node types" in source
        assert "# Special types for execution results" in source
