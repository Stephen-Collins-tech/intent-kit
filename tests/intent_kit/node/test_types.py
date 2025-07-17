"""
Tests for node types and data structures.
"""

import pytest
from unittest.mock import Mock
from typing import Dict, Any, List, Optional

from intent_kit.node.types import ExecutionError, ExecutionResult
from intent_kit.node.enums import NodeType


class TestExecutionError:
    """Test the ExecutionError class."""

    def test_init_basic(self):
        """Test basic initialization."""
        error = ExecutionError(
            error_type="TestError",
            message="Test error message",
            node_name="test_node",
            node_path=["root", "test_node"]
        )
        
        assert error.error_type == "TestError"
        assert error.message == "Test error message"
        assert error.node_name == "test_node"
        assert error.node_path == ["root", "test_node"]
        assert error.node_id is None
        assert error.input_data is None
        assert error.output_data is None
        assert error.params is None
        assert error.original_exception is None

    def test_init_with_optional_fields(self):
        """Test initialization with all optional fields."""
        original_exception = ValueError("Test exception")
        error = ExecutionError(
            error_type="TestError",
            message="Test error message",
            node_name="test_node",
            node_path=["root", "test_node"],
            node_id="test-id-123",
            input_data={"input": "data"},
            output_data={"output": "data"},
            params={"param": "value"},
            original_exception=original_exception
        )
        
        assert error.node_id == "test-id-123"
        assert error.input_data == {"input": "data"}
        assert error.output_data == {"output": "data"}
        assert error.params == {"param": "value"}
        assert error.original_exception == original_exception

    def test_from_exception_basic(self):
        """Test creating ExecutionError from basic exception."""
        exception = ValueError("Test exception")
        error = ExecutionError.from_exception(
            exception=exception,
            node_name="test_node",
            node_path=["root", "test_node"]
        )
        
        assert error.error_type == "ValueError"
        assert error.message == "Test exception"
        assert error.node_name == "test_node"
        assert error.node_path == ["root", "test_node"]
        assert error.node_id is None
        assert error.original_exception == exception

    def test_from_exception_with_validation_error(self):
        """Test creating ExecutionError from exception with validation_error attribute."""
        class ValidationException(Exception):
            def __init__(self, message, validation_error, input_data):
                super().__init__(message)
                self.validation_error = validation_error
                self.input_data = input_data
        
        exception = ValidationException(
            "Test exception",
            "Validation failed",
            {"input": "data"}
        )
        
        error = ExecutionError.from_exception(
            exception=exception,
            node_name="test_node",
            node_path=["root", "test_node"],
            node_id="test-id"
        )
        
        assert error.error_type == "ValidationException"
        assert error.message == "Validation failed"
        assert error.node_name == "test_node"
        assert error.node_path == ["root", "test_node"]
        assert error.node_id == "test-id"
        assert error.input_data == {"input": "data"}
        assert error.params == {"input": "data"}

    def test_from_exception_with_error_message(self):
        """Test creating ExecutionError from exception with error_message attribute."""
        class CustomException(Exception):
            def __init__(self, message, error_message, params):
                super().__init__(message)
                self.error_message = error_message
                self.params = params
        
        exception = CustomException(
            "Test exception",
            "Custom error message",
            {"param": "value"}
        )
        
        error = ExecutionError.from_exception(
            exception=exception,
            node_name="test_node",
            node_path=["root", "test_node"]
        )
        
        assert error.error_type == "CustomException"
        assert error.message == "Custom error message"
        assert error.params == {"param": "value"}

    def test_to_dict(self):
        """Test converting ExecutionError to dictionary."""
        error = ExecutionError(
            error_type="TestError",
            message="Test error message",
            node_name="test_node",
            node_path=["root", "test_node"],
            node_id="test-id",
            input_data={"input": "data"},
            output_data={"output": "data"},
            params={"param": "value"}
        )
        
        result = error.to_dict()
        
        expected = {
            "error_type": "TestError",
            "message": "Test error message",
            "node_name": "test_node",
            "node_path": ["root", "test_node"],
            "node_id": "test-id",
            "input_data": {"input": "data"},
            "output_data": {"output": "data"},
            "params": {"param": "value"}
        }
        
        assert result == expected

    def test_to_dict_with_none_values(self):
        """Test to_dict with None values."""
        error = ExecutionError(
            error_type="TestError",
            message="Test error message",
            node_name="test_node",
            node_path=["root", "test_node"]
        )
        
        result = error.to_dict()
        
        expected = {
            "error_type": "TestError",
            "message": "Test error message",
            "node_name": "test_node",
            "node_path": ["root", "test_node"],
            "node_id": None,
            "input_data": None,
            "output_data": None,
            "params": None
        }
        
        assert result == expected


class TestExecutionResult:
    """Test the ExecutionResult class."""

    def test_init_success(self):
        """Test initialization for successful execution."""
        result = ExecutionResult(
            success=True,
            node_name="test_node",
            node_path=["root", "test_node"],
            node_type=NodeType.ACTION,
            input="test input",
            output="test output",
            error=None,
            params={"param": "value"},
            children_results=[]
        )
        
        assert result.success is True
        assert result.node_name == "test_node"
        assert result.node_path == ["root", "test_node"]
        assert result.node_type == NodeType.ACTION
        assert result.input == "test input"
        assert result.output == "test output"
        assert result.error is None
        assert result.params == {"param": "value"}
        assert result.children_results == []
        assert result.visualization_html is None

    def test_init_failure(self):
        """Test initialization for failed execution."""
        error = ExecutionError(
            error_type="TestError",
            message="Test error",
            node_name="test_node",
            node_path=["root", "test_node"]
        )
        
        result = ExecutionResult(
            success=False,
            node_name="test_node",
            node_path=["root", "test_node"],
            node_type=NodeType.CLASSIFIER,
            input="test input",
            output=None,
            error=error,
            params={"param": "value"},
            children_results=[]
        )
        
        assert result.success is False
        assert result.error == error
        assert result.output is None

    def test_init_with_visualization(self):
        """Test initialization with visualization HTML."""
        result = ExecutionResult(
            success=True,
            node_name="test_node",
            node_path=["root", "test_node"],
            node_type=NodeType.SPLITTER,
            input="test input",
            output="test output",
            error=None,
            params={},
            children_results=[],
            visualization_html="<div>Test visualization</div>"
        )
        
        assert result.visualization_html == "<div>Test visualization</div>"

    def test_init_with_children_results(self):
        """Test initialization with children results."""
        child_result = ExecutionResult(
            success=True,
            node_name="child_node",
            node_path=["root", "test_node", "child_node"],
            node_type=NodeType.ACTION,
            input="child input",
            output="child output",
            error=None,
            params={},
            children_results=[]
        )
        
        result = ExecutionResult(
            success=True,
            node_name="test_node",
            node_path=["root", "test_node"],
            node_type=NodeType.CLASSIFIER,
            input="test input",
            output="test output",
            error=None,
            params={},
            children_results=[child_result]
        )
        
        assert len(result.children_results) == 1
        assert result.children_results[0] == child_result

    def test_init_with_complex_output(self):
        """Test initialization with complex output data."""
        complex_output = {
            "result": "success",
            "data": [1, 2, 3],
            "metadata": {"key": "value"}
        }
        
        result = ExecutionResult(
            success=True,
            node_name="test_node",
            node_path=["root", "test_node"],
            node_type=NodeType.ACTION,
            input="test input",
            output=complex_output,
            error=None,
            params={},
            children_results=[]
        )
        
        assert result.output == complex_output

    def test_init_with_none_values(self):
        """Test initialization with None values."""
        result = ExecutionResult(
            success=True,
            node_name="test_node",
            node_path=["root", "test_node"],
            node_type=NodeType.UNKNOWN,
            input="test input",
            output=None,
            error=None,
            params=None,
            children_results=[]
        )
        
        assert result.output is None
        assert result.error is None
        assert result.params is None
        assert result.visualization_html is None

    def test_different_node_types(self):
        """Test initialization with different node types."""
        node_types = [
            NodeType.UNKNOWN,
            NodeType.ACTION,
            NodeType.CLASSIFIER,
            NodeType.SPLITTER,
            NodeType.CLARIFY,
            NodeType.GRAPH,
            NodeType.UNHANDLED_CHUNK
        ]
        
        for node_type in node_types:
            result = ExecutionResult(
                success=True,
                node_name="test_node",
                node_path=["root", "test_node"],
                node_type=node_type,
                input="test input",
                output="test output",
                error=None,
                params={},
                children_results=[]
            )
            
            assert result.node_type == node_type

    def test_complex_tree_structure(self):
        """Test creating a complex tree of execution results."""
        # Create leaf nodes
        leaf1 = ExecutionResult(
            success=True,
            node_name="leaf1",
            node_path=["root", "parent", "leaf1"],
            node_type=NodeType.ACTION,
            input="leaf1 input",
            output="leaf1 output",
            error=None,
            params={},
            children_results=[]
        )
        
        leaf2 = ExecutionResult(
            success=True,
            node_name="leaf2",
            node_path=["root", "parent", "leaf2"],
            node_type=NodeType.ACTION,
            input="leaf2 input",
            output="leaf2 output",
            error=None,
            params={},
            children_results=[]
        )
        
        # Create parent node
        parent = ExecutionResult(
            success=True,
            node_name="parent",
            node_path=["root", "parent"],
            node_type=NodeType.CLASSIFIER,
            input="parent input",
            output="parent output",
            error=None,
            params={},
            children_results=[leaf1, leaf2]
        )
        
        # Create root node
        root = ExecutionResult(
            success=True,
            node_name="root",
            node_path=["root"],
            node_type=NodeType.GRAPH,
            input="root input",
            output="root output",
            error=None,
            params={},
            children_results=[parent]
        )
        
        assert len(root.children_results) == 1
        assert len(root.children_results[0].children_results) == 2
        assert root.children_results[0].node_name == "parent"
        assert root.children_results[0].children_results[0].node_name == "leaf1"
        assert root.children_results[0].children_results[1].node_name == "leaf2"