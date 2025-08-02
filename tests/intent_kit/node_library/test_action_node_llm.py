"""
Tests for action_node_llm module.
"""

from intent_kit.node_library.action_node_llm import action_node_llm


class TestActionNodeLLM:
    """Test the action_node_llm module."""

    def test_action_node_llm_returns_action_node(self):
        """Test that action_node_llm returns an ActionNode instance."""
        # Act
        node = action_node_llm()

        # Assert
        assert node.name == "action_node_llm"
        assert node.description == "LLM-powered booking action"
        assert node.param_schema == {"destination": str, "date": str}
        assert node.action is not None
        assert node.arg_extractor is not None

    def test_booking_action_with_known_destinations(self):
        """Test booking_action function with known destinations."""
        node = action_node_llm()

        # Test known destinations
        test_cases = [
            ("Paris", "ASAP", "Flight booked to Paris for ASAP (Booking #1)"),
            ("Tokyo", "tomorrow", "Flight booked to Tokyo for tomorrow (Booking #2)"),
            (
                "London",
                "next week",
                "Flight booked to London for next week (Booking #3)",
            ),
            (
                "New York",
                "December 15th",
                "Flight booked to New York for December 15th (Booking #4)",
            ),
            (
                "Sydney",
                "the weekend",
                "Flight booked to Sydney for the weekend (Booking #5)",
            ),
        ]

        for destination, date, expected in test_cases:
            result = node.action(destination, date)
            assert result == expected

    def test_booking_action_with_unknown_destination(self):
        """Test booking_action function with unknown destination."""
        node = action_node_llm()

        # Test unknown destination - should use hash-based booking number
        result = node.action("Unknown City", "ASAP")
        assert "Flight booked to Unknown City for ASAP" in result
        assert "(Booking #" in result

    def test_booking_action_with_kwargs(self):
        """Test booking_action function with additional kwargs."""
        node = action_node_llm()

        result = node.action("Paris", "ASAP", extra_param="value")
        assert result == "Flight booked to Paris for ASAP (Booking #1)"

    def test_simple_extractor_with_known_destinations(self):
        """Test simple_extractor function with known destinations."""
        node = action_node_llm()

        test_cases = [
            ("I want to go to Paris", {"destination": "Paris", "date": "ASAP"}),
            ("Book a flight to Tokyo", {"destination": "Tokyo", "date": "ASAP"}),
            ("I need to travel to London", {"destination": "London", "date": "ASAP"}),
            (
                "Can you book New York for me?",
                {"destination": "New York", "date": "ASAP"},
            ),
            ("I want to visit Sydney", {"destination": "Sydney", "date": "ASAP"}),
            ("Book Berlin please", {"destination": "Berlin", "date": "ASAP"}),
            ("I need a flight to Rome", {"destination": "Rome", "date": "ASAP"}),
            ("Book Barcelona for me", {"destination": "Barcelona", "date": "ASAP"}),
            ("I want to go to Amsterdam", {"destination": "Amsterdam", "date": "ASAP"}),
            ("Book Prague please", {"destination": "Prague", "date": "ASAP"}),
        ]

        for input_text, expected in test_cases:
            result = node.arg_extractor(input_text, None)
            assert result == expected

    def test_simple_extractor_with_unknown_destination(self):
        """Test simple_extractor function with unknown destination."""
        node = action_node_llm()

        result = node.arg_extractor("I want to go to Unknown City", None)
        assert result == {"destination": "Unknown", "date": "ASAP"}

    def test_simple_extractor_with_dates(self):
        """Test simple_extractor function with various date formats."""
        node = action_node_llm()

        test_cases = [
            (
                "Book Paris for next Friday",
                {"destination": "Paris", "date": "next Friday"},
            ),
            (
                "I want to go to Tokyo tomorrow",
                {"destination": "Tokyo", "date": "tomorrow"},
            ),
            (
                "Book London for next week",
                {"destination": "London", "date": "next week"},
            ),
            (
                "I need New York for the weekend",
                {"destination": "New York", "date": "the weekend"},
            ),
            (
                "Book Sydney for next month",
                {"destination": "Sydney", "date": "next month"},
            ),
            (
                "I want Berlin on December 15th",
                {"destination": "Berlin", "date": "December 15th"},
            ),
        ]

        for input_text, expected in test_cases:
            result = node.arg_extractor(input_text, None)
            assert result == expected

    def test_simple_extractor_with_context(self):
        """Test simple_extractor function with context parameter."""
        node = action_node_llm()

        context = {"user_id": "123", "session_id": "456"}
        result = node.arg_extractor("Book Paris for tomorrow", context)
        assert result == {"destination": "Paris", "date": "tomorrow"}

    def test_simple_extractor_case_sensitive(self):
        """Test simple_extractor function is case sensitive (actual behavior)."""
        node = action_node_llm()

        test_cases = [
            ("I want to go to Paris", {"destination": "Paris", "date": "ASAP"}),
            ("Book a flight to Tokyo", {"destination": "Tokyo", "date": "ASAP"}),
            ("I need to travel to London", {"destination": "London", "date": "ASAP"}),
        ]

        for input_text, expected in test_cases:
            result = node.arg_extractor(input_text, None)
            assert result == expected

    def test_simple_extractor_case_sensitive_failure(self):
        """Test simple_extractor function fails with wrong case."""
        node = action_node_llm()

        test_cases = [
            ("I want to go to PARIS", {"destination": "Unknown", "date": "ASAP"}),
            ("Book a flight to tokyo", {"destination": "Unknown", "date": "ASAP"}),
            ("I need to travel to london", {"destination": "Unknown", "date": "ASAP"}),
        ]

        for input_text, expected in test_cases:
            result = node.arg_extractor(input_text, None)
            assert result == expected

    def test_simple_extractor_multiple_destinations_in_text(self):
        """Test simple_extractor function with multiple destinations (should pick first)."""
        node = action_node_llm()

        result = node.arg_extractor("I want to go to Paris and then Tokyo", None)
        assert result == {"destination": "Paris", "date": "ASAP"}

    def test_simple_extractor_multiple_dates_in_text(self):
        """Test simple_extractor function with multiple dates (should pick first)."""
        node = action_node_llm()

        result = node.arg_extractor(
            "I want to go to Paris tomorrow and next week", None
        )
        assert result == {"destination": "Paris", "date": "tomorrow"}

    def test_simple_extractor_no_destination_or_date(self):
        """Test simple_extractor function with no destination or date."""
        node = action_node_llm()

        result = node.arg_extractor("I want to book a flight", None)
        assert result == {"destination": "Unknown", "date": "ASAP"}

    def test_node_execution_integration(self):
        """Test the complete node execution with extraction and action."""
        node = action_node_llm()

        # Test execution with known destination and date
        result = node.execute("I want to book a flight to Paris for tomorrow")

        assert result.success is True
        assert result.node_name == "action_node_llm"
        assert result.output == "Flight booked to Paris for tomorrow (Booking #1)"
        assert result.params == {"destination": "Paris", "date": "tomorrow"}

    def test_node_execution_with_unknown_destination(self):
        """Test node execution with unknown destination."""
        node = action_node_llm()

        result = node.execute("I want to book a flight to Unknown City")

        assert result.success is True
        assert result.node_name == "action_node_llm"
        assert result.output is not None
        assert "Flight booked to Unknown for ASAP" in result.output
        assert result.params == {"destination": "Unknown", "date": "ASAP"}
