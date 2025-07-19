"""
Integration tests for Clarifier nodes with graph builder and intent graph.
"""

from unittest.mock import patch
from intent_kit.builders import IntentGraphBuilder
from intent_kit.node.actions import ClarifierNode
from intent_kit.node.enums import NodeType
from intent_kit.context import IntentContext


class TestClarifierIntegration:
    """Integration tests for Clarifier nodes."""

    def test_graph_builder_with_clarifier_node(self):
        """Test that graph builder can create graphs with Clarifier nodes."""

        # Create a simple function registry
        def dummy_action(user_input: str) -> str:
            return f"Processed: {user_input}"

        function_registry = {"dummy_action": dummy_action}

        # Create JSON graph specification with clarifier node
        json_graph = {
            "root": "clarifier_node",
            "intents": {
                "clarifier_node": {
                    "type": "clarifier",
                    "name": "booking_clarifier",
                    "description": "Clarifies booking requests",
                    "clarification_prompt": "Please provide more details about your booking request: {input}",
                    "expected_response_format": "Please specify: [type] [date] [time] [destination]",
                    "max_clarification_attempts": 3,
                }
            },
        }

        # Build the graph
        builder = IntentGraphBuilder()
        graph = builder.with_json(json_graph).with_functions(function_registry).build()

        # Verify the graph was created
        assert graph is not None
        assert len(graph.root_nodes) == 1

        # Verify the clarifier node was created correctly
        clarifier_node = graph.root_nodes[0]
        assert isinstance(clarifier_node, ClarifierNode)
        assert clarifier_node.name == "booking_clarifier"
        assert clarifier_node.node_type == NodeType.CLARIFY
        assert (
            clarifier_node.clarification_prompt
            == "Please provide more details about your booking request: {input}"
        )
        assert (
            clarifier_node.expected_response_format
            == "Please specify: [type] [date] [time] [destination]"
        )
        assert clarifier_node.max_clarification_attempts == 3

    def test_graph_builder_validation_with_clarifier(self):
        """Test that graph builder validation works with Clarifier nodes."""
        json_graph = {
            "root": "clarifier_node",
            "intents": {
                "clarifier_node": {
                    "type": "clarifier",
                    "name": "test_clarifier",
                    "clarification_prompt": "Please clarify: {input}",
                }
            },
        }

        builder = IntentGraphBuilder()
        validation_result = builder.with_json(json_graph).validate_json_graph()

        assert validation_result["valid"] is True
        assert validation_result["node_count"] == 1
        assert len(validation_result["errors"]) == 0

    def test_graph_builder_validation_missing_clarification_prompt(self):
        """Test that validation fails when clarification_prompt is missing."""
        json_graph = {
            "root": "clarifier_node",
            "intents": {
                "clarifier_node": {
                    "type": "clarifier",
                    "name": "test_clarifier",
                    # Missing clarification_prompt
                }
            },
        }

        builder = IntentGraphBuilder()
        validation_result = builder.with_json(json_graph).validate_json_graph()

        assert validation_result["valid"] is False
        assert len(validation_result["errors"]) > 0
        assert any(
            "missing 'clarification_prompt' field" in error
            for error in validation_result["errors"]
        )

    def test_intent_graph_with_clarifier_node(self):
        """Test that IntentGraph can handle Clarifier nodes in routing."""
        # Create a clarifier node
        clarifier_node = ClarifierNode(
            name="booking_clarifier",
            clarification_prompt="Please provide more details about your booking: {input}",
            expected_response_format="Please specify: [type] [date] [time]",
        )

        # Create a simple action node
        def book_action(user_input: str) -> str:
            return f"Booked: {user_input}"

        from intent_kit.utils.node_factory import action

        action_node = action(
            name="book_action",
            description="Books items",
            action_func=book_action,
            param_schema={},
        )

        # Create graph with both nodes
        from intent_kit.graph import IntentGraph

        graph = IntentGraph(root_nodes=[clarifier_node, action_node])

        # Mock the classifier to return CLARIFY action
        with patch(
            "intent_kit.graph.intent_graph.classify_intent_chunk"
        ) as mock_classify:
            mock_classify.return_value = {"action": "clarify"}

            # Route input through the graph
            result = graph.route("book something", debug=True)

            # Verify that the clarifier node was executed
            assert result.success is False
            assert len(result.children_results) == 1

            clarifier_result = result.children_results[0]
            assert clarifier_result.node_type == NodeType.CLARIFY
            assert clarifier_result.node_name == "booking_clarifier"
            assert clarifier_result.output["requires_clarification"] is True
            assert (
                "Please provide more details about your booking: book something"
                in clarifier_result.output["clarification_message"]
            )

    def test_clarifier_node_factory_function(self):
        """Test the clarifier factory function."""
        from intent_kit.utils.node_factory import clarifier

        node = clarifier(
            name="test_clarifier",
            clarification_prompt="Please clarify: {input}",
            expected_response_format="Please provide: [details]",
            max_clarification_attempts=5,
            description="Test clarifier",
        )

        assert isinstance(node, ClarifierNode)
        assert node.name == "test_clarifier"
        assert node.clarification_prompt == "Please clarify: {input}"
        assert node.expected_response_format == "Please provide: [details]"
        assert node.max_clarification_attempts == 5
        assert node.description == "Test clarifier"

    def test_clarifier_node_with_context_integration(self):
        """Test Clarifier node with context integration."""
        clarifier_node = ClarifierNode(
            name="test_clarifier", clarification_prompt="Please clarify: {input}"
        )

        context = IntentContext()

        # Execute clarifier node
        clarifier_node.execute("ambiguous input", context=context)

        # Verify context was updated
        clarification_context = context.get("clarification_context")
        assert clarification_context is not None
        assert clarification_context["original_input"] == "ambiguous input"
        assert clarification_context["attempts"] == 0

        # Handle clarification response
        response = clarifier_node.handle_clarification_response(
            "clarified input", context
        )

        assert response["success"] is True
        assert response["clarified_input"] == "clarified input"
        assert response["attempts"] == 1

        # Verify context was updated again
        updated_context = context.get("clarification_context")
        assert updated_context["attempts"] == 1
        assert updated_context["last_response"] == "clarified input"

    def test_clarifier_node_max_attempts_integration(self):
        """Test Clarifier node max attempts integration."""
        clarifier_node = ClarifierNode(
            name="test_clarifier",
            clarification_prompt="Please clarify",
            max_clarification_attempts=2,
        )

        context = IntentContext()
        context.set(
            "clarification_context",
            {
                "original_input": "ambiguous",
                "attempts": 2,  # Already at max
                "max_attempts": 2,
            },
        )

        # Try to handle another clarification response
        response = clarifier_node.handle_clarification_response(
            "another attempt", context
        )

        assert response["success"] is False
        assert response["error"] == "Maximum clarification attempts exceeded"
        assert response["attempts"] == 3

    def test_clarifier_node_placeholder_replacement_integration(self):
        """Test Clarifier node placeholder replacement in integration."""
        clarifier_node = ClarifierNode(
            name="test_clarifier",
            clarification_prompt="Your input '{input}' needs clarification. Please provide more details.",
        )

        result = clarifier_node.execute("book flight")

        expected_message = (
            "Your input 'book flight' needs clarification. Please provide more details."
        )
        assert result.output["clarification_message"] == expected_message

    def test_clarifier_node_with_expected_format_integration(self):
        """Test Clarifier node with expected format in integration."""
        clarifier_node = ClarifierNode(
            name="test_clarifier",
            clarification_prompt="What would you like to book?",
            expected_response_format="Please specify: [type] [date] [time]",
        )

        result = clarifier_node.execute("book")

        expected_message = (
            "What would you like to book?\n\n"
            "Please provide your response in the following format: Please specify: [type] [date] [time]"
        )
        assert result.output["clarification_message"] == expected_message
