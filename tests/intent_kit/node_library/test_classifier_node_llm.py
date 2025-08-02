"""
Tests for classifier_node_llm module.
"""

from intent_kit.node_library.classifier_node_llm import classifier_node_llm
from intent_kit.context import IntentContext


class TestClassifierNodeLLM:
    """Test the classifier_node_llm module."""

    def test_classifier_node_llm_returns_classifier_node(self):
        """Test that classifier_node_llm returns a ClassifierNode instance."""
        # Act
        node = classifier_node_llm()

        # Assert
        assert node.name == "classifier_node_llm"
        assert (
            node.description
            == "LLM-powered intent classifier for weather and cancellation"
        )
        assert node.classifier is not None
        assert len(node.children) == 2
        assert node.children[0].name == "weather_node"
        assert node.children[1].name == "cancellation_node"

    def test_simple_classifier_with_cancellation_keywords(self):
        """Test simple_classifier function with cancellation keywords."""
        node = classifier_node_llm()

        cancellation_inputs = [
            "I want to cancel my flight",
            "Please cancel my reservation",
            "Cancel the booking",
            "I need to cancel my appointment",
            "Cancel a restaurant reservation",
        ]

        for input_text in cancellation_inputs:
            result = node.classifier(input_text, node.children, None)
            assert result[0] == node.children[1]  # Should return cancellation child
            assert result[1] is None

    def test_simple_classifier_with_weather_keywords(self):
        """Test simple_classifier function with weather keywords."""
        node = classifier_node_llm()

        weather_inputs = [
            "What's the weather like today?",
            "Tell me the temperature",
            "What's the forecast?",
            "What's the weather like in Paris?",
            "How's the weather today?",
        ]

        for input_text in weather_inputs:
            result = node.classifier(input_text, node.children, None)
            assert result[0] == node.children[0]  # Should return weather child
            assert result[1] is None

    def test_simple_classifier_with_mixed_keywords(self):
        """Test simple_classifier function with both weather and cancellation keywords."""
        node = classifier_node_llm()

        # When both keywords are present, cancellation should take precedence
        mixed_inputs = [
            "Cancel my flight and check the weather",
            "What's the weather like? Also cancel my appointment",
        ]

        for input_text in mixed_inputs:
            result = node.classifier(input_text, node.children, None)
            assert result[0] == node.children[1]  # Should return cancellation child
            assert result[1] is None

    def test_simple_classifier_with_no_keywords(self):
        """Test simple_classifier function with no keywords (defaults to first child)."""
        node = classifier_node_llm()

        neutral_inputs = [
            "Hello",
            "How are you?",
            "What can you help me with?",
            "I need assistance",
        ]

        for input_text in neutral_inputs:
            result = node.classifier(input_text, node.children, None)
            assert result[0] == node.children[0]  # Should return first child (weather)
            assert result[1] is None

    def test_simple_classifier_with_no_children(self):
        """Test simple_classifier function with no children."""
        node = classifier_node_llm()

        result = node.classifier("Hello", [], None)
        assert result[0] is None
        assert result[1] is None

    def test_simple_classifier_with_single_child(self):
        """Test simple_classifier function with single child."""
        node = classifier_node_llm()

        result = node.classifier("Hello", [node.children[0]], None)
        assert result[0] == node.children[0]
        assert result[1] is None

    def test_simple_classifier_case_insensitive(self):
        """Test simple_classifier function is case insensitive."""
        node = classifier_node_llm()

        test_cases = [
            ("CANCEL my flight", node.children[1]),  # Cancellation
            ("cancel my appointment", node.children[1]),  # Cancellation
            ("WEATHER today", node.children[0]),  # Weather
            ("weather forecast", node.children[0]),  # Weather
        ]

        for input_text, expected_child in test_cases:
            result = node.classifier(input_text, node.children, None)
            assert result[0] == expected_child
            assert result[1] is None

    def test_simple_classifier_with_context(self):
        """Test simple_classifier function with context parameter."""
        node = classifier_node_llm()

        context = {"user_id": "123", "session_id": "456"}
        result = node.classifier("Cancel my flight", node.children, context)
        assert result[0] == node.children[1]
        assert result[1] is None

    def test_mock_weather_node_initialization(self):
        """Test MockWeatherNode initialization."""
        node = classifier_node_llm()
        weather_node = node.children[0]

        assert weather_node.name == "weather_node"
        assert weather_node.description == "Mock weather node"

    def test_mock_weather_node_execution_with_known_locations(self):
        """Test MockWeatherNode execution with known locations."""
        node = classifier_node_llm()
        weather_node = node.children[0]

        test_cases = [
            (
                "What's the weather in New York?",
                "Weather in New York: Sunny with a chance of rain",
            ),
            (
                "Tell me about the weather in London",
                "Weather in London: Sunny with a chance of rain",
            ),
            (
                "How's the weather in Tokyo?",
                "Weather in Tokyo: Sunny with a chance of rain",
            ),
            ("Weather in Paris", "Weather in Paris: Sunny with a chance of rain"),
            ("Sydney weather", "Weather in Sydney: Sunny with a chance of rain"),
            (
                "Berlin weather forecast",
                "Weather in Berlin: Sunny with a chance of rain",
            ),
            (
                "What's the weather like in Rome?",
                "Weather in Rome: Sunny with a chance of rain",
            ),
            ("Barcelona weather", "Weather in Barcelona: Sunny with a chance of rain"),
            (
                "Amsterdam weather today",
                "Weather in Amsterdam: Sunny with a chance of rain",
            ),
            (
                "Prague weather forecast",
                "Weather in Prague: Sunny with a chance of rain",
            ),
        ]

        for input_text, expected_output in test_cases:
            result = weather_node.execute(input_text)
            assert result.success is True
            assert result.node_name == "weather_node"
            assert result.output == expected_output
            assert result.error is None

    def test_mock_weather_node_execution_with_unknown_location(self):
        """Test MockWeatherNode execution with unknown location."""
        node = classifier_node_llm()
        weather_node = node.children[0]

        result = weather_node.execute("What's the weather like?")
        assert result.success is True
        assert result.node_name == "weather_node"
        assert result.output == "Weather in Unknown: Sunny with a chance of rain"
        assert result.error is None

    def test_mock_weather_node_execution_with_context(self):
        """Test MockWeatherNode execution with context."""
        node = classifier_node_llm()
        weather_node = node.children[0]

        context = IntentContext(session_id="test_session")
        context.set("user_id", "123", modified_by="test")
        result = weather_node.execute("What's the weather in Paris?", context)
        assert result.success is True
        assert result.output == "Weather in Paris: Sunny with a chance of rain"

    def test_mock_cancellation_node_initialization(self):
        """Test MockCancellationNode initialization."""
        node = classifier_node_llm()
        cancellation_node = node.children[1]

        assert cancellation_node.name == "cancellation_node"
        assert cancellation_node.description == "Mock cancellation node"

    def test_mock_cancellation_node_execution_with_known_item_types(self):
        """Test MockCancellationNode execution with known item types."""
        node = classifier_node_llm()
        cancellation_node = node.children[1]

        test_cases = [
            (
                "Cancel my flight reservation",
                "Successfully cancelled flight reservation",
            ),
            (
                "I want to cancel my hotel booking",
                "Successfully cancelled hotel booking",
            ),
            (
                "Cancel my restaurant reservation",
                "Successfully cancelled restaurant reservation",
            ),
            ("I need to cancel my appointment", "Successfully cancelled appointment"),
            ("Cancel my subscription", "Successfully cancelled subscription"),
            ("I want to cancel my order", "Successfully cancelled order"),
        ]

        for input_text, expected_output in test_cases:
            result = cancellation_node.execute(input_text)
            assert result.success is True
            assert result.node_name == "cancellation_node"
            assert result.output == expected_output
            assert result.error is None

    def test_mock_cancellation_node_execution_with_unknown_item_type(self):
        """Test MockCancellationNode execution with unknown item type."""
        node = classifier_node_llm()
        cancellation_node = node.children[1]

        result = cancellation_node.execute("I want to cancel something")
        assert result.success is True
        assert result.node_name == "cancellation_node"
        assert (
            result.output == "Successfully cancelled appointment"
        )  # Default item type
        assert result.error is None

    def test_mock_cancellation_node_execution_with_context(self):
        """Test MockCancellationNode execution with context."""
        node = classifier_node_llm()
        cancellation_node = node.children[1]

        context = IntentContext(session_id="test_session")
        context.set("user_id", "123", modified_by="test")
        result = cancellation_node.execute("Cancel my flight reservation", context)
        assert result.success is True
        assert result.output == "Successfully cancelled flight reservation"

    def test_node_execution_integration_weather(self):
        """Test complete node execution for weather intent."""
        node = classifier_node_llm()

        result = node.execute("What's the weather like in Paris?")

        assert result.success is True
        assert result.node_name == "classifier_node_llm"
        assert result.children_results is not None
        assert len(result.children_results) == 1
        assert result.children_results[0].node_name == "weather_node"
        assert result.children_results[0].output is not None
        assert (
            "Weather in Paris: Sunny with a chance of rain"
            in result.children_results[0].output
        )

    def test_node_execution_integration_cancellation(self):
        """Test complete node execution for cancellation intent."""
        node = classifier_node_llm()

        result = node.execute("I want to cancel my flight reservation")

        assert result.success is True
        assert result.node_name == "classifier_node_llm"
        assert result.children_results is not None
        assert len(result.children_results) == 1
        assert result.children_results[0].node_name == "cancellation_node"
        assert result.children_results[0].output is not None
        assert (
            "Successfully cancelled flight reservation"
            in result.children_results[0].output
        )
