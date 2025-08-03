"""
Tests for intent_kit.node_library module.
"""

from intent_kit.node_library import action_node_llm, classifier_node_llm
from intent_kit.node_library.action_node_llm import (
    action_node_llm as action_node_llm_func,
)
from intent_kit.nodes import TreeNode
from intent_kit.nodes.enums import NodeType


class TestNodeLibrary:
    """Test node library functions."""

    def test_action_node_llm_import(self):
        """Test that action_node_llm can be imported from node_library."""

        assert action_node_llm is not None
        assert callable(action_node_llm)

    def test_classifier_node_llm_import(self):
        """Test that classifier_node_llm can be imported from node_library."""

        assert classifier_node_llm is not None
        assert callable(classifier_node_llm)

    def test_action_node_llm_function(self):
        """Test the action_node_llm function."""
        node = action_node_llm_func()

        assert isinstance(node, TreeNode)
        assert node.name == "action_node_llm"
        assert node.description == "LLM-powered booking action"
        assert node.node_type == NodeType.ACTION

    def test_action_node_llm_booking_action(self):
        """Test the booking action function within action_node_llm."""
        node = action_node_llm_func()

        # Test the booking action with known destinations
        result = node.action(destination="Paris", date="ASAP")
        assert "Flight booked to Paris" in result
        assert "Booking #1" in result

        result = node.action(destination="Tokyo", date="next Friday")
        assert "Flight booked to Tokyo" in result
        assert "Booking #2" in result

        result = node.action(destination="London", date="tomorrow")
        assert "Flight booked to London" in result
        assert "Booking #3" in result

    def test_action_node_llm_unknown_destination(self):
        """Test the booking action with unknown destination."""
        node = action_node_llm_func()

        result = node.action(destination="Unknown City", date="ASAP")
        assert "Flight booked to Unknown City" in result
        # Should use hash-based booking number for unknown destinations
        assert "Booking #" in result

    def test_action_node_llm_arg_extractor(self):
        """Test the argument extractor function within action_node_llm."""
        node = action_node_llm_func()

        # Test extraction with known destinations
        result = node.arg_extractor("I want to book a flight to Paris", {})
        if isinstance(result, dict):
            assert result["destination"] == "Paris"
            assert result["date"] == "ASAP"

        result = node.arg_extractor("Book me a flight to Tokyo for next Friday", {})
        if isinstance(result, dict):
            assert result["destination"] == "Tokyo"
            assert result["date"] == "next Friday"

        result = node.arg_extractor("I need to go to London tomorrow", {})
        if isinstance(result, dict):
            assert result["destination"] == "London"
            assert result["date"] == "tomorrow"

    def test_action_node_llm_arg_extractor_unknown_destination(self):
        """Test the argument extractor with unknown destination."""
        node = action_node_llm_func()

        result = node.arg_extractor("I want to go to Mars", {})
        if isinstance(result, dict):
            assert result["destination"] == "Unknown"
            assert result["date"] == "ASAP"

    def test_action_node_llm_arg_extractor_date_extraction(self):
        """Test date extraction in the argument extractor."""
        node = action_node_llm_func()

        # Test various date patterns
        result = node.arg_extractor("Book a flight to Paris for next week", {})
        if isinstance(result, dict):
            assert result["destination"] == "Paris"
            assert result["date"] == "next week"

        result = node.arg_extractor("I want to go to Tokyo on the weekend", {})
        if isinstance(result, dict):
            assert result["destination"] == "Tokyo"
            assert result["date"] == "the weekend"

        result = node.arg_extractor("Book me a flight to London for next month", {})
        if isinstance(result, dict):
            assert result["destination"] == "London"
            assert result["date"] == "next month"

        result = node.arg_extractor("I need to go to Berlin on December 15th", {})
        if isinstance(result, dict):
            assert result["destination"] == "Berlin"
            assert result["date"] == "December 15th"

    def test_action_node_llm_param_schema(self):
        """Test that the action node has the correct parameter schema."""
        node = action_node_llm_func()

        assert node.param_schema == {"destination": str, "date": str}

    def test_action_node_llm_execution(self):
        """Test the complete execution of the action node."""
        node = action_node_llm_func()

        # Test execution with input that should extract parameters
        execution_result = node.execute(
            "I want to book a flight to Paris for next Friday"
        )

        assert execution_result.success is True
        assert execution_result.node_name == "action_node_llm"
        assert execution_result.node_type == NodeType.ACTION
        if execution_result.output:
            assert "Flight booked to Paris" in execution_result.output
            assert "next Friday" in execution_result.output

    def test_action_node_llm_multiple_destinations(self):
        """Test the action node with all supported destinations."""
        node = action_node_llm_func()

        destinations = [
            "Paris",
            "Tokyo",
            "London",
            "New York",
            "Sydney",
            "Berlin",
            "Rome",
            "Barcelona",
            "Amsterdam",
            "Prague",
        ]

        for i, destination in enumerate(destinations, 1):
            result = node.action(destination=destination, date="ASAP")
            assert f"Flight booked to {destination}" in result
            assert f"Booking #{i}" in result

    def test_action_node_llm_hash_based_booking(self):
        """Test that unknown destinations use hash-based booking numbers."""
        node = action_node_llm_func()

        # Test with an unknown destination
        result = node.action(destination="Some Random City", date="ASAP")
        assert "Flight booked to Some Random City" in result
        assert "Booking #" in result

        # The hash should be consistent for the same destination
        result1 = node.action(destination="Some Random City", date="ASAP")
        result2 = node.action(destination="Some Random City", date="ASAP")

        # Extract booking numbers and compare
        import re

        match1 = re.search(r"Booking #(\d+)", result1)
        match2 = re.search(r"Booking #(\d+)", result2)
        assert match1 is not None
        assert match2 is not None
        booking1 = match1.group(1)
        booking2 = match2.group(1)
        assert booking1 == booking2

    def test_action_node_llm_kwargs_handling(self):
        """Test that the booking action handles additional kwargs."""
        node = action_node_llm_func()

        result = node.action(
            destination="Paris", date="ASAP", airline="Air France", class_type="Economy"
        )
        assert "Flight booked to Paris" in result
        assert "Booking #" in result
        # The function should not crash with additional kwargs

    def test_action_node_llm_extractor_edge_cases(self):
        """Test the argument extractor with edge cases."""
        node = action_node_llm_func()

        # Test with empty input
        result = node.arg_extractor("", {})
        if isinstance(result, dict):
            assert result["destination"] == "Unknown"
            assert result["date"] == "ASAP"

        # Test with input that doesn't match any patterns
        result = node.arg_extractor("Just some random text", {})
        if isinstance(result, dict):
            assert result["destination"] == "Unknown"
            assert result["date"] == "ASAP"

        # Test with multiple destinations (should match first one)
        result = node.arg_extractor("I want to go to Paris and Tokyo", {})
        if isinstance(result, dict):
            assert result["destination"] == "Paris"  # First match wins
            assert result["date"] == "ASAP"

        # Test with multiple dates (should match first one)
        result = node.arg_extractor("I want to go to London tomorrow and next week", {})
        if isinstance(result, dict):
            assert result["destination"] == "London"
            assert result["date"] == "tomorrow"  # First match wins
