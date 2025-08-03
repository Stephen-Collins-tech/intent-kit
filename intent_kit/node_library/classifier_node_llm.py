"""
LLM-powered classifier node for evaluation testing.
"""

from intent_kit.nodes.classifiers.node import ClassifierNode
from intent_kit.nodes.base_node import TreeNode
from intent_kit.nodes.types import ExecutionResult


def classifier_node_llm():
    """
    Create an LLM-powered classifier node for evaluation.

    This node is designed to classify weather and cancellation intents
    using LLM-based classification.
    """

    # Create a classifier function that routes to different children based on intent
    def simple_classifier(user_input: str, children, context=None):
        # Check if it's a cancellation intent
        cancellation_keywords = [
            "cancel",
            "cancellation",
            "cancel my",
            "cancel a",
            "cancel the",
        ]
        is_cancellation = any(
            keyword in user_input.lower() for keyword in cancellation_keywords
        )

        # Check if it's a weather intent
        weather_keywords = [
            "weather",
            "temperature",
            "forecast",
            "like in",
            "like today",
        ]
        is_weather = any(keyword in user_input.lower() for keyword in weather_keywords)

        if is_cancellation and len(children) > 1:
            return (children[1], None)  # Return cancellation child
        elif is_weather and children:
            return (children[0], None)  # Return weather child
        elif children:
            return (children[0], None)  # Default to first child
        else:
            return (None, None)

    # Create a mock child node that returns the expected weather response
    class MockWeatherNode(TreeNode):
        def __init__(self):
            super().__init__(name="weather_node", description="Mock weather node")

        def execute(self, user_input: str, context=None):
            from intent_kit.nodes.enums import NodeType

            # Extract location from input
            locations = [
                "New York",
                "London",
                "Tokyo",
                "Paris",
                "Sydney",
                "Berlin",
                "Rome",
                "Barcelona",
                "Amsterdam",
                "Prague",
            ]
            location = "Unknown"
            for loc in locations:
                if loc.lower() in user_input.lower():
                    location = loc
                    break

            return ExecutionResult(
                success=True,
                node_name=self.name,
                node_path=[self.name],
                node_type=NodeType.ACTION,
                input=user_input,
                output=f"Weather in {location}: Sunny with a chance of rain",
                error=None,
                params=None,
                children_results=[],
            )

    # Create a mock child node that returns the expected cancellation response
    class MockCancellationNode(TreeNode):
        def __init__(self):
            super().__init__(
                name="cancellation_node", description="Mock cancellation node"
            )

        def execute(self, user_input: str, context=None):
            from intent_kit.nodes.enums import NodeType

            # Extract item type from input
            item_types = [
                "flight reservation",
                "hotel booking",
                "restaurant reservation",
                "appointment",
                "subscription",
                "order",
            ]
            item_type = "appointment"  # default
            for item in item_types:
                if item in user_input.lower():
                    item_type = item
                    break

            return ExecutionResult(
                success=True,
                node_name=self.name,
                node_path=[self.name],
                node_type=NodeType.ACTION,
                input=user_input,
                output=f"Successfully cancelled {item_type}",
                error=None,
                params=None,
                children_results=[],
            )

    # Create the classifier node
    classifier = ClassifierNode(
        name="classifier_node_llm",
        description="LLM-powered intent classifier for weather and cancellation",
        classifier=simple_classifier,
        children=[MockWeatherNode(), MockCancellationNode()],
    )

    return classifier
