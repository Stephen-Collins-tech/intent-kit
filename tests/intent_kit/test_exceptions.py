"""
Tests for intent_kit.exceptions module.
"""


from intent_kit.exceptions import (
    NodeError,
    NodeExecutionError,
    NodeValidationError,
    NodeInputValidationError,
    NodeOutputValidationError,
    NodeNotFoundError,
    NodeArgumentExtractionError,
)


class TestNodeError:
    """Test the base NodeError exception."""

    def test_node_error_inheritance(self):
        """Test that NodeError inherits from Exception."""
        error = NodeError("test message")
        assert isinstance(error, Exception)
        assert isinstance(error, NodeError)
        assert str(error) == "test message"


class TestNodeExecutionError:
    """Test the NodeExecutionError exception."""

    def test_node_execution_error_basic(self):
        """Test basic NodeExecutionError creation."""
        error = NodeExecutionError("test_node", "test error")
        
        assert error.node_name == "test_node"
        assert error.error_message == "test error"
        assert error.params == {}
        assert error.node_id is None
        assert error.node_path == []
        assert "Node 'test_node' (path: unknown) failed: test error" in str(error)

    def test_node_execution_error_with_params(self):
        """Test NodeExecutionError with parameters."""
        params = {"param1": "value1", "param2": 42}
        error = NodeExecutionError("test_node", "test error", params=params)
        
        assert error.params == params

    def test_node_execution_error_with_node_id(self):
        """Test NodeExecutionError with node_id."""
        error = NodeExecutionError("test_node", "test error", node_id="uuid-123")
        
        assert error.node_id == "uuid-123"

    def test_node_execution_error_with_node_path(self):
        """Test NodeExecutionError with node_path."""
        node_path = ["root", "child1", "child2"]
        error = NodeExecutionError("test_node", "test error", node_path=node_path)
        
        assert error.node_path == node_path
        assert "Node 'test_node' (path: root -> child1 -> child2) failed: test error" in str(error)

    def test_node_execution_error_with_all_params(self):
        """Test NodeExecutionError with all parameters."""
        params = {"param1": "value1"}
        node_path = ["root", "child"]
        error = NodeExecutionError(
            "test_node", 
            "test error", 
            params=params,
            node_id="uuid-123",
            node_path=node_path
        )
        
        assert error.node_name == "test_node"
        assert error.error_message == "test error"
        assert error.params == params
        assert error.node_id == "uuid-123"
        assert error.node_path == node_path

    def test_node_execution_error_inheritance(self):
        """Test that NodeExecutionError inherits from NodeError."""
        error = NodeExecutionError("test_node", "test error")
        assert isinstance(error, NodeError)
        assert isinstance(error, NodeExecutionError)


class TestNodeValidationError:
    """Test the NodeValidationError exception."""

    def test_node_validation_error_inheritance(self):
        """Test that NodeValidationError inherits from NodeError."""
        error = NodeValidationError("test message")
        assert isinstance(error, NodeError)
        assert isinstance(error, NodeValidationError)
        assert str(error) == "test message"


class TestNodeInputValidationError:
    """Test the NodeInputValidationError exception."""

    def test_node_input_validation_error_basic(self):
        """Test basic NodeInputValidationError creation."""
        error = NodeInputValidationError("test_node", "validation failed")
        
        assert error.node_name == "test_node"
        assert error.validation_error == "validation failed"
        assert error.input_data == {}
        assert error.node_id is None
        assert error.node_path == []
        assert "Node 'test_node' (path: unknown) input validation failed: validation failed" in str(error)

    def test_node_input_validation_error_with_input_data(self):
        """Test NodeInputValidationError with input_data."""
        input_data = {"input1": "value1", "input2": 42}
        error = NodeInputValidationError("test_node", "validation failed", input_data=input_data)
        
        assert error.input_data == input_data

    def test_node_input_validation_error_with_node_id(self):
        """Test NodeInputValidationError with node_id."""
        error = NodeInputValidationError("test_node", "validation failed", node_id="uuid-123")
        
        assert error.node_id == "uuid-123"

    def test_node_input_validation_error_with_node_path(self):
        """Test NodeInputValidationError with node_path."""
        node_path = ["root", "child1", "child2"]
        error = NodeInputValidationError("test_node", "validation failed", node_path=node_path)
        
        assert error.node_path == node_path
        assert "Node 'test_node' (path: root -> child1 -> child2) input validation failed: validation failed" in str(error)

    def test_node_input_validation_error_with_all_params(self):
        """Test NodeInputValidationError with all parameters."""
        input_data = {"input1": "value1"}
        node_path = ["root", "child"]
        error = NodeInputValidationError(
            "test_node", 
            "validation failed", 
            input_data=input_data,
            node_id="uuid-123",
            node_path=node_path
        )
        
        assert error.node_name == "test_node"
        assert error.validation_error == "validation failed"
        assert error.input_data == input_data
        assert error.node_id == "uuid-123"
        assert error.node_path == node_path

    def test_node_input_validation_error_inheritance(self):
        """Test that NodeInputValidationError inherits from NodeValidationError."""
        error = NodeInputValidationError("test_node", "validation failed")
        assert isinstance(error, NodeValidationError)
        assert isinstance(error, NodeInputValidationError)


class TestNodeOutputValidationError:
    """Test the NodeOutputValidationError exception."""

    def test_node_output_validation_error_basic(self):
        """Test basic NodeOutputValidationError creation."""
        error = NodeOutputValidationError("test_node", "validation failed")
        
        assert error.node_name == "test_node"
        assert error.validation_error == "validation failed"
        assert error.output_data is None
        assert error.node_id is None
        assert error.node_path == []
        assert "Node 'test_node' (path: unknown) output validation failed: validation failed" in str(error)

    def test_node_output_validation_error_with_output_data(self):
        """Test NodeOutputValidationError with output_data."""
        output_data = {"output1": "value1", "output2": 42}
        error = NodeOutputValidationError("test_node", "validation failed", output_data=output_data)
        
        assert error.output_data == output_data

    def test_node_output_validation_error_with_node_id(self):
        """Test NodeOutputValidationError with node_id."""
        error = NodeOutputValidationError("test_node", "validation failed", node_id="uuid-123")
        
        assert error.node_id == "uuid-123"

    def test_node_output_validation_error_with_node_path(self):
        """Test NodeOutputValidationError with node_path."""
        node_path = ["root", "child1", "child2"]
        error = NodeOutputValidationError("test_node", "validation failed", node_path=node_path)
        
        assert error.node_path == node_path
        assert "Node 'test_node' (path: root -> child1 -> child2) output validation failed: validation failed" in str(error)

    def test_node_output_validation_error_with_all_params(self):
        """Test NodeOutputValidationError with all parameters."""
        output_data = {"output1": "value1"}
        node_path = ["root", "child"]
        error = NodeOutputValidationError(
            "test_node", 
            "validation failed", 
            output_data=output_data,
            node_id="uuid-123",
            node_path=node_path
        )
        
        assert error.node_name == "test_node"
        assert error.validation_error == "validation failed"
        assert error.output_data == output_data
        assert error.node_id == "uuid-123"
        assert error.node_path == node_path

    def test_node_output_validation_error_inheritance(self):
        """Test that NodeOutputValidationError inherits from NodeValidationError."""
        error = NodeOutputValidationError("test_node", "validation failed")
        assert isinstance(error, NodeValidationError)
        assert isinstance(error, NodeOutputValidationError)


class TestNodeNotFoundError:
    """Test the NodeNotFoundError exception."""

    def test_node_not_found_error_basic(self):
        """Test basic NodeNotFoundError creation."""
        error = NodeNotFoundError("missing_node")
        
        assert error.node_name == "missing_node"
        assert error.available_nodes == []
        assert str(error) == "Node 'missing_node' not found"

    def test_node_not_found_error_with_available_nodes(self):
        """Test NodeNotFoundError with available_nodes."""
        available_nodes = ["node1", "node2", "node3"]
        error = NodeNotFoundError("missing_node", available_nodes=available_nodes)
        
        assert error.node_name == "missing_node"
        assert error.available_nodes == available_nodes

    def test_node_not_found_error_inheritance(self):
        """Test that NodeNotFoundError inherits from NodeError."""
        error = NodeNotFoundError("missing_node")
        assert isinstance(error, NodeError)
        assert isinstance(error, NodeNotFoundError)


class TestNodeArgumentExtractionError:
    """Test the NodeArgumentExtractionError exception."""

    def test_node_argument_extraction_error_basic(self):
        """Test basic NodeArgumentExtractionError creation."""
        error = NodeArgumentExtractionError("test_node", "extraction failed")
        
        assert error.node_name == "test_node"
        assert error.error_message == "extraction failed"
        assert error.user_input is None
        assert str(error) == "Node 'test_node' argument extraction failed: extraction failed"

    def test_node_argument_extraction_error_with_user_input(self):
        """Test NodeArgumentExtractionError with user_input."""
        user_input = "user provided input"
        error = NodeArgumentExtractionError("test_node", "extraction failed", user_input=user_input)
        
        assert error.user_input == user_input

    def test_node_argument_extraction_error_inheritance(self):
        """Test that NodeArgumentExtractionError inherits from NodeError."""
        error = NodeArgumentExtractionError("test_node", "extraction failed")
        assert isinstance(error, NodeError)
        assert isinstance(error, NodeArgumentExtractionError)


class TestExceptionIntegration:
    """Test exception integration and edge cases."""

    def test_exception_message_formatting_with_empty_path(self):
        """Test exception message formatting with empty node_path."""
        error = NodeExecutionError("test_node", "test error", node_path=[])
        assert "Node 'test_node' (path: unknown) failed: test error" in str(error)

    def test_exception_message_formatting_with_none_path(self):
        """Test exception message formatting with None node_path."""
        error = NodeExecutionError("test_node", "test error", node_path=None)
        assert "Node 'test_node' (path: unknown) failed: test error" in str(error)

    def test_exception_message_formatting_with_single_path(self):
        """Test exception message formatting with single element path."""
        error = NodeExecutionError("test_node", "test error", node_path=["root"])
        assert "Node 'test_node' (path: root) failed: test error" in str(error)

    def test_exception_with_complex_data(self):
        """Test exceptions with complex data structures."""
        complex_params = {
            "nested": {"key": "value"},
            "list": [1, 2, 3],
            "tuple": (1, 2, 3)
        }
        error = NodeExecutionError("test_node", "test error", params=complex_params)
        assert error.params == complex_params

    def test_exception_with_special_characters(self):
        """Test exceptions with special characters in names and messages."""
        error = NodeExecutionError("test-node_123", "error with 'quotes' and \"double quotes\"")
        assert error.node_name == "test-node_123"
        assert "error with 'quotes' and \"double quotes\"" in error.error_message