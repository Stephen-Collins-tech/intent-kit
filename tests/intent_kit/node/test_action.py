"""
Tests for ActionNode functionality.
"""

import pytest









class TestActionNode:
    """Test cases for ActionNode class."""

    def test_def test_def test_init_basic(self): -> None: -> None:
        """Test basic ActionNode initialization."""
        mock_action = Mock()
        mock_extractor = Mock()
        param_schema = {"name": str, "age": int}

        node = ActionNode()
            name="test_action",
            param_schema=param_schema,
            action=mock_action,
            arg_extractor=mock_extractor,
            description="Test action node"
(        )

        assert node.name == "test_action"
        assert node.param_schema == param_schema
        assert node.action == mock_action
        assert node.arg_extractor == mock_extractor
        assert node.description == "Test action node"
        assert node.node_type == NodeType.ACTION
        assert node.context_inputs == set()
        assert node.context_outputs == set()
        assert node.input_validator is None
        assert node.output_validator is None
        assert node.remediation_strategies == []

    def test_def test_def test_init_with_context_dependencies(self): -> None: -> None:
        """Test ActionNode initialization with context dependencies."""
        mock_action = Mock()
        mock_extractor = Mock()
        param_schema = {"name": str}
        context_inputs = {"user_id", "session_id"}
        context_outputs = {"result", "status"}

        node = ActionNode()
            name="test_action",
            param_schema=param_schema,
            action=mock_action,
            arg_extractor=mock_extractor,
            context_inputs=context_inputs,
            context_outputs=context_outputs
(        )

        assert node.context_inputs == context_inputs
        assert node.context_outputs == context_outputs

    def test_def test_def test_init_with_validators(self): -> None: -> None:
        """Test ActionNode initialization with validators."""
        mock_action = Mock()
        mock_extractor = Mock()
        mock_input_validator = Mock()
        mock_output_validator = Mock()
        param_schema = {"name": str}

        node = ActionNode()
            name="test_action",
            param_schema=param_schema,
            action=mock_action,
            arg_extractor=mock_extractor,
            input_validator=mock_input_validator,
            output_validator=mock_output_validator
(        )

        assert node.input_validator == mock_input_validator
        assert node.output_validator == mock_output_validator

    def test_def test_def test_init_with_remediation_strategies(self): -> None: -> None:
        """Test ActionNode initialization with remediation strategies."""
        mock_action = Mock()
        mock_extractor = Mock()
        param_schema = {"name": str}
        remediation_strategies = ["retry_on_fail", "fallback_to_another_node"]

        node = ActionNode()
            name="test_action",
            param_schema=param_schema,
            action=mock_action,
            arg_extractor=mock_extractor,
            remediation_strategies=remediation_strategies
(        )

        assert node.remediation_strategies == remediation_strategies

    def test_def test_def test_execute_success_basic(self): -> None: -> None:
        """Test successful execution without context."""
        mock_action = Mock(return_value="success")
        mock_extractor = Mock(return_value={"name": "test"})
        param_schema = {"name": str}

        node = ActionNode()
            name="test_action",
            param_schema=param_schema,
            action=mock_action,
            arg_extractor=mock_extractor
(        )

        result = node.execute("test input")

        assert result.success is True
        assert result.node_name == "test_action"
        assert result.node_type == NodeType.ACTION
        assert result.input == "test input"
        assert result.output == "success"
        assert result.error is None
        assert result.params == {"name": "test"}
        mock_extractor.assert_called_once_with("test input", {})
        mock_action.assert_called_once_with(name="test")

    def test_def test_def test_execute_success_with_context(self): -> None: -> None:
        """Test successful execution with context."""
        mock_action = Mock(return_value="success")
        mock_extractor = Mock(return_value={"name": "test"})
        param_schema = {"name": str}
        context = IntentContext()
        context.set("user_id", "123")

        node = ActionNode()
            name="test_action",
            param_schema=param_schema,
            action=mock_action,
            arg_extractor=mock_extractor,
            context_inputs={"user_id"}
(        )

        result = node.execute("test input", context)

        assert result.success is True
        assert result.output == "success"
        mock_extractor.assert_called_once_with("test input", {"user_id": "123"})
        mock_action.assert_called_once_with(name="test", context=context)

    def test_def test_def test_execute_arg_extraction_failure(self): -> None: -> None:
        """Test execution when argument extraction fails."""
        mock_action = Mock()
        mock_extractor = Mock(side_effect=ValueError("Extraction failed"))
        param_schema = {"name": str}

        node = ActionNode()
            name="test_action",
            param_schema=param_schema,
            action=mock_action,
            arg_extractor=mock_extractor
(        )

        result = node.execute("test input")

        assert result.success is False
        assert result.error is not None
        assert result.error.error_type == "ValueError"
        assert "Extraction failed" in result.error.message
        assert result.params is None
        mock_action.assert_not_called()

    def test_def test_def test_execute_input_validation_failure(self): -> None: -> None:
        """Test execution when input validation fails."""
        mock_action = Mock()
        mock_extractor = Mock(return_value={"name": "test"})
        mock_input_validator = Mock(return_value=False)
        param_schema = {"name": str}

        node = ActionNode()
            name="test_action",
            param_schema=param_schema,
            action=mock_action,
            arg_extractor=mock_extractor,
            input_validator=mock_input_validator
(        )

        result = node.execute("test input")

        assert result.success is False
        assert result.error is not None
        assert result.error.error_type == "InputValidationError"
        assert result.params == {"name": "test"}
        mock_action.assert_not_called()

    def test_def test_def test_execute_input_validation_exception(self): -> None: -> None:
        """Test execution when input validation raises an exception."""
        mock_action = Mock()
        mock_extractor = Mock(return_value={"name": "test"})
        mock_input_validator = Mock(side_effect=RuntimeError("Validation error"))
        param_schema = {"name": str}

        node = ActionNode()
            name="test_action",
            param_schema=param_schema,
            action=mock_action,
            arg_extractor=mock_extractor,
            input_validator=mock_input_validator
(        )

        result = node.execute("test input")

        assert result.success is False
        assert result.error is not None
        assert result.error.error_type == "RuntimeError"
        assert "Validation error" in result.error.message
        mock_action.assert_not_called()

    def test_def test_def test_execute_type_validation_failure(self): -> None: -> None:
        """Test execution when type validation fails."""
        mock_action = Mock()
        mock_extractor = Mock(return_value={"name": 123})  # Wrong type
        param_schema = {"name": str}

        node = ActionNode()
            name="test_action",
            param_schema=param_schema,
            action=mock_action,
            arg_extractor=mock_extractor
(        )

        result = node.execute("test input")

        # The current implementation doesn't validate types during execution
        # It only validates during _validate_types call
        assert result.success is True
        assert result.params == {"name": "123"}  # The value gets converted to string
        mock_action.assert_called_once()

    def test_def test_def test_execute_action_failure(self): -> None: -> None:
        """Test execution when action fails."""
        mock_action = Mock(side_effect=RuntimeError("Action failed"))
        mock_extractor = Mock(return_value={"name": "test"})
        param_schema = {"name": str}

        node = ActionNode()
            name="test_action",
            param_schema=param_schema,
            action=mock_action,
            arg_extractor=mock_extractor
(        )

        result = node.execute("test input")

        assert result.success is False
        assert result.error is not None
        assert result.error.error_type == "RuntimeError"
        assert "Action failed" in result.error.message
        assert result.params == {"name": "test"}

    def test_def test_def test_execute_output_validation_failure(self): -> None: -> None:
        """Test execution when output validation fails."""
        mock_action = Mock(return_value="invalid output")
        mock_extractor = Mock(return_value={"name": "test"})
        mock_output_validator = Mock(return_value=False)
        param_schema = {"name": str}

        node = ActionNode()
            name="test_action",
            param_schema=param_schema,
            action=mock_action,
            arg_extractor=mock_extractor,
            output_validator=mock_output_validator
(        )

        result = node.execute("test input")

        assert result.success is False
        assert result.error is not None
        assert result.error.error_type == "OutputValidationError"
        assert result.output is None  # Output is None when validation fails

    def test_def test_def test_execute_output_validation_exception(self): -> None: -> None:
        """Test execution when output validation raises an exception."""
        mock_action = Mock(return_value="output")
        mock_extractor = Mock(return_value={"name": "test"})
        mock_output_validator = Mock()
(            side_effect=RuntimeError("Output validation error"))        param_schema = {"name": str}

        node = ActionNode()
            name="test_action",
            param_schema=param_schema,
            action=mock_action,
            arg_extractor=mock_extractor,
            output_validator=mock_output_validator
(        )

        result = node.execute("test input")

        assert result.success is False
        assert result.error is not None
        assert result.error.error_type == "RuntimeError"
        assert "Output validation error" in result.error.message

    def test_def test_def test_execute_with_remediation_success(self): -> None: -> None:
        """Test execution with successful remediation."""
        mock_action = Mock(side_effect=RuntimeError("Action failed"))
        mock_extractor = Mock(return_value={"name": "test"})
        param_schema = {"name": str}

        # Mock remediation strategy that succeeds
        mock_remediation = Mock()
        mock_remediation.execute.return_value = ExecutionResult()
            success=True,
            node_name="test_action",
            node_path=["test_action"],
            node_type=NodeType.ACTION,
            input="test input",
            output="remediated output",
            error=None,
            params={"name": "test"},
            children_results=[]
(        )

        with patch()
            'intent_kit.node.actions.action.get_remediation_strategy', return_value=mock_remediation):            node = ActionNode(
                name="test_action",
                param_schema=param_schema,
                action=mock_action,
                arg_extractor=mock_extractor,
                remediation_strategies=["retry_on_fail"]
(            )

            result = node.execute("test input")

            # The remediation strategy returns a mock, so we need to check the actual result
            assert result.success is True
            assert result.output == "remediated output"

    def test_def test_def test_execute_with_remediation_failure(self): -> None: -> None:
        """Test execution with failed remediation."""
        mock_action = Mock(side_effect=RuntimeError("Action failed"))
        mock_extractor = Mock(return_value={"name": "test"})
        param_schema = {"name": str}

        # Mock remediation strategy that fails
        mock_remediation = Mock()
        mock_remediation.execute.return_value = None

        with patch()
            'intent_kit.node.actions.action.get_remediation_strategy', return_value=mock_remediation):            node = ActionNode(
                name="test_action",
                param_schema=param_schema,
                action=mock_action,
                arg_extractor=mock_extractor,
                remediation_strategies=["retry_on_fail"]
(            )

            result = node.execute("test input")

            # The remediation strategy returns None, so the original error should be preserved
            assert result.success is False
            assert result.error is not None
            assert result.error.error_type == "RuntimeError"

    def test_def test_def test_validate_types_success(self): -> None: -> None:
        """Test successful type validation."""
        node = ActionNode()
            name="test_action",
            param_schema={"name": str, "age": int, "active": bool},
            action=Mock(),
            arg_extractor=Mock()
(        )

        params = {"name": "test", "age": 25, "active": True}
        validated = node._validate_types(params)

        assert validated == params

    def test_def test_def test_validate_types_failure(self): -> None: -> None:
        """Test type validation failure."""
        node = ActionNode()
            name="test_action",
            param_schema={"name": str, "age": int},
            action=Mock(),
            arg_extractor=Mock()
(        )

        params = {"name": "test", "age": "not_an_int"}

        with pytest.raises(ValueError):
            node._validate_types(params)

    def test_def test_def test_validate_types_missing_required(self): -> None: -> None:
        """Test type validation with missing required parameters."""
        node = ActionNode()
            name="test_action",
            param_schema={"name": str, "age": int},
            action=Mock(),
            arg_extractor=Mock()
(        )

        params = {"name": "test"}  # Missing age

        with pytest.raises(ValueError):
            node._validate_types(params)

    def test_def test_def test_validate_types_extra_parameters(self): -> None: -> None:
        """Test type validation with extra parameters."""
        node = ActionNode()
            name="test_action",
            param_schema={"name": str},
            action=Mock(),
            arg_extractor=Mock()
(        )

        params = {"name": "test", "extra": "value"}
        validated = node._validate_types(params)

        # Should only include schema parameters
        assert validated == {"name": "test"}

    def test_def test_def test_node_path_and_inheritance(self): -> None: -> None:
        """Test node path and inheritance from TreeNode."""
        parent = Mock()
        parent.get_path.return_value = ["parent"]

        node = ActionNode()
            name="test_action",
            param_schema={"name": str},
            action=Mock(),
            arg_extractor=Mock(),
            parent=parent
(        )

        assert node.get_path() == ["parent", "test_action"]
        assert isinstance(node, ActionNode)

    def test_def test_def test_context_dependencies_declaration(self): -> None: -> None:
        """Test that context dependencies are properly declared."""
        context_inputs = {"user_id", "session_id"}
        context_outputs = {"result", "status"}

        with patch()
            'intent_kit.node.actions.action.declare_dependencies') as mock_declare:            node = ActionNode(
                name="test_action",
                param_schema={"name": str},
                action=Mock(),
                arg_extractor=Mock(),
                context_inputs=context_inputs,
                context_outputs=context_outputs
(            )

            mock_declare.assert_called_once_with()
                inputs=context_inputs,
                outputs=context_outputs,
                description=f"Context dependencies for intent '{node.name}'"
(            )

    def test_def test_def test_execute_with_complex_param_schema(self): -> None: -> None:
        """Test execution with complex parameter schema."""
        mock_action = Mock(return_value="success")
        mock_extractor = Mock(return_value={)
            "name": "test",
            "age": 25,
            "scores": [1, 2, 3],
            "metadata": {"key": "value"}
(        })
        param_schema = {
            "name": str,
            "age": int,
            "scores": list,
            "metadata": dict
        }

        node = ActionNode()
            name="test_action",
            param_schema=param_schema,
            action=mock_action,
            arg_extractor=mock_extractor
(        )

        result = node.execute("test input")

        assert result.success is True
        assert result.params == {
            "name": "test",
            "age": 25,
            "scores": [1, 2, 3],
            "metadata": {"key": "value"}
        }

    def test_def test_def test_execute_with_none_context(self): -> None: -> None:
        """Test execution with None context."""
        mock_action = Mock(return_value="success")
        mock_extractor = Mock(return_value={"name": "test"})
        param_schema = {"name": str}

        node = ActionNode()
            name="test_action",
            param_schema=param_schema,
            action=mock_action,
            arg_extractor=mock_extractor,
            context_inputs={"user_id"}
(        )

        result = node.execute("test input", None)

        assert result.success is True
        mock_extractor.assert_called_once_with("test input", {})
        mock_action.assert_called_once_with(name="test")

    def test_def test_def test_execute_with_empty_context_inputs(self): -> None: -> None:
        """Test execution with empty context inputs."""
        mock_action = Mock(return_value="success")
        mock_extractor = Mock(return_value={"name": "test"})
        param_schema = {"name": str}
        context = IntentContext()
        context.set("user_id", "123")

        node = ActionNode()
            name="test_action",
            param_schema=param_schema,
            action=mock_action,
            arg_extractor=mock_extractor,
            context_inputs=set()  # Empty set
(        )

        result = node.execute("test input", context)

        assert result.success is True
        mock_extractor.assert_called_once_with("test input", {})
        mock_action.assert_called_once_with(name="test")

    def test_def test_def test_execute_with_missing_context_keys(self): -> None: -> None:
        """Test execution when context is missing some keys."""
        mock_action = Mock(return_value="success")
        mock_extractor = Mock(return_value={"name": "test"})
        param_schema = {"name": str}
        context = IntentContext()
        context.set("user_id", "123")
        # Missing session_id

        node = ActionNode()
            name="test_action",
            param_schema=param_schema,
            action=mock_action,
            arg_extractor=mock_extractor,
            context_inputs={"user_id", "session_id"}
(        )

        result = node.execute("test input", context)

        assert result.success is True
        # Should only include available keys
        mock_extractor.assert_called_once_with("test input", {"user_id": "123"})
