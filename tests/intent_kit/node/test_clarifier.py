"""
Tests for the ClarifierNode class.
"""







class TestClarifierNode:
    """Test cases for ClarifierNode."""

    def test_def test_def test_clarifier_node_creation(self): -> None: -> None:
        """Test that ClarifierNode can be created with basic parameters."""
        node = ClarifierNode()
            name="test_clarifier",
            clarification_prompt="Please provide more details about {input}",
            description="Test clarifier node",
(        )

        assert node.name == "test_clarifier"
        assert node.clarification_prompt == "Please provide more details about {input}"
        assert node.description == "Test clarifier node"
        assert node.expected_response_format is None
        assert node.max_clarification_attempts == 3

    def test_def test_def test_clarifier_node_with_optional_params(self): -> None: -> None:
        """Test that ClarifierNode can be created with all optional parameters."""
        node = ClarifierNode()
            name="test_clarifier",
            clarification_prompt="Please clarify: {input}",
            expected_response_format="Please provide: [specific details]",
            max_clarification_attempts=5,
            description="Test clarifier with all params",
(        )

        assert node.name == "test_clarifier"
        assert node.clarification_prompt == "Please clarify: {input}"
        assert node.expected_response_format == "Please provide: [specific details]"
        assert node.max_clarification_attempts == 5
        assert node.description == "Test clarifier with all params"

    def test_def test_def test_clarifier_node_type(self): -> None: -> None:
        """Test that ClarifierNode returns the correct node type."""
        node = ClarifierNode(name="test_clarifier", clarification_prompt="Test prompt")

        assert node.node_type == NodeType.CLARIFY

    def test_def test_def test_clarifier_node_execute_basic(self): -> None: -> None:
        """Test basic execution of ClarifierNode."""
        node = ClarifierNode()
            name="test_clarifier",
            clarification_prompt="Please provide more details about {input}",
(        )

        result = node.execute("book something")

        assert isinstance(result, ExecutionResult)
        assert result.success is False  # Clarification requests are not "successful"
        assert result.node_name == "test_clarifier"
        assert result.node_type == NodeType.CLARIFY
        assert result.input == "book something"
        assert result.output is not None
        assert result.output["requires_clarification"] is True
        assert ()
            "Please provide more details about book something"
            in result.output["clarification_message"]
(        )
        assert result.error is not None
        assert result.error.error_type == "ClarificationNeeded"

    def test_def test_def test_clarifier_node_execute_with_context(self): -> None: -> None:
        """Test ClarifierNode execution with context."""
        node = ClarifierNode()
            name="test_clarifier", clarification_prompt="Please clarify: {input}"
(        )

        context = IntentContext()
        result = node.execute("ambiguous input", context=context)

        assert result.success is False
        assert result.node_type == NodeType.CLARIFY

        # Check that clarification context was stored
        clarification_context = context.get("clarification_context")
        assert clarification_context is not None
        assert clarification_context["original_input"] == "ambiguous input"
        assert clarification_context["attempts"] == 0
        assert clarification_context["max_attempts"] == 3

    def test_def test_def test_clarifier_node_with_expected_format(self): -> None: -> None:
        """Test ClarifierNode with expected response format."""
        node = ClarifierNode()
            name="test_clarifier",
            clarification_prompt="What would you like to book?",
            expected_response_format="Please specify: [type] [date] [time]",
(        )

        result = node.execute("book")

        assert result.output["clarification_message"] == ()
            "What would you like to book?\n\n"
"Please provide your response in the following format: Please specify: [type] [date]
            [time]"
(        )

    def test_def test_def test_clarifier_node_with_placeholder_replacement(self): -> None: -> None:
        """Test that placeholders in clarification prompt are replaced."""
        node = ClarifierNode()
            name="test_clarifier",
clarification_prompt="Your input '{input}' is unclear. Please provide more details.",
(        )

        result = node.execute("book flight")

        expected_message = ()
            "Your input 'book flight' is unclear. Please provide more details."
(        )
        assert result.output["clarification_message"] == expected_message

    def test_def test_def test_clarifier_node_without_placeholder(self): -> None: -> None:
        """Test ClarifierNode with prompt that doesn't contain placeholder."""'
        node = ClarifierNode()
            name="test_clarifier",
            clarification_prompt="Please provide more information.",
(        )

        result = node.execute("ambiguous")

        assert ()
            result.output["clarification_message"] == "Please provide more information."
(        )

    def test_def test_def test_clarifier_node_handle_clarification_response_success(self): -> None: -> None:
        """Test handling clarification response successfully."""
        node = ClarifierNode()
            name="test_clarifier", clarification_prompt="Please clarify"
(        )

        context = IntentContext()
        context.set()
            "clarification_context",
            {"original_input": "book", "attempts": 0, "max_attempts": 3},
(        )

        response = node.handle_clarification_response("book a flight to Paris", context)

        assert response["success"] is True
        assert response["clarified_input"] == "book a flight to Paris"
        assert response["original_input"] == "book"
        assert response["attempts"] == 1

    def test_def test_def test_clarifier_node_handle_clarification_response_max_attempts(self): -> None: -> None:
        """Test handling clarification response when max attempts exceeded."""
        node = ClarifierNode()
            name="test_clarifier",
            clarification_prompt="Please clarify",
            max_clarification_attempts=2,
(        )

        context = IntentContext()
        context.set()
            "clarification_context",
            {
                "original_input": "book",
                "attempts": 2,  # Already at max
                "max_attempts": 2,
            },
(        )

        response = node.handle_clarification_response("book a flight", context)

        assert response["success"] is False
        assert response["error"] == "Maximum clarification attempts exceeded"
        assert response["attempts"] == 3

    def test_def test_def test_clarifier_node_handle_clarification_response_no_context(self): -> None: -> None:
        """Test handling clarification response without context."""
        node = ClarifierNode()
            name="test_clarifier", clarification_prompt="Please clarify"
(        )

        response = node.handle_clarification_response("clarified input")

        assert response["success"] is True
        assert response["clarified_input"] == "clarified input"
        assert response["attempts"] == 1

    def test_def test_def test_clarifier_node_path_and_uuid(self): -> None: -> None:
        """Test that ClarifierNode has proper path and UUID functionality."""
        parent = ClarifierNode(name="parent", clarification_prompt="Parent prompt")

        child = ClarifierNode()
            name="child", clarification_prompt="Child prompt", parent=parent
(        )

        assert child.get_path() == ["parent", "child"]
        assert child.get_path_string() == "parent.child"
        assert len(child.get_uuid_path()) == 2
        assert child.has_name is True

    def test_def test_def test_clarifier_node_children_handling(self): -> None: -> None:
        """Test that ClarifierNode properly handles children (should be empty)."""
        node = ClarifierNode(name="test_clarifier", clarification_prompt="Test prompt")

        # Clarifier nodes should be leaf nodes with no children
        assert len(node.children) == 0

    def test_def test_def test_clarifier_node_execution_result_structure(self): -> None: -> None:
        """Test that ClarifierNode execution returns properly structured result."""
        node = ClarifierNode()
            name="test_clarifier", clarification_prompt="Please clarify: {input}"
(        )

        result = node.execute("unclear input")

        # Check result structure
        assert hasattr(result, "success")
        assert hasattr(result, "node_name")
        assert hasattr(result, "node_path")
        assert hasattr(result, "node_type")
        assert hasattr(result, "input")
        assert hasattr(result, "output")
        assert hasattr(result, "error")
        assert hasattr(result, "params")
        assert hasattr(result, "children_results")

        # Check specific values
        assert result.success is False
        assert result.node_name == "test_clarifier"
        assert result.node_type == NodeType.CLARIFY
        assert result.input == "unclear input"
        assert isinstance(result.output, dict)
        assert isinstance(result.error, ExecutionError)
        assert isinstance(result.children_results, list)
        assert len(result.children_results) == 0

    def test_def test_def test_clarifier_node_error_structure(self): -> None: -> None:
        """Test that ClarifierNode error has proper structure."""
        node = ClarifierNode()
            name="test_clarifier", clarification_prompt="Please clarify"
(        )

        result = node.execute("test input")

        error = result.error
        assert error.error_type == "ClarificationNeeded"
        assert "test input" in error.message
        assert error.node_name == "test_clarifier"
        assert isinstance(error.node_path, list)
        assert error.input_data is not None
        assert "original_input" in error.input_data
        assert error.params is not None
        assert "clarification_prompt" in error.params
