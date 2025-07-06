import unittest

from intent_kit.builder import handler, IntentGraphBuilder
from intent_kit.classifiers import ClassifierNode
from intent_kit.classifiers.fuzzy import fuzzy_classifier
from intent_kit.context import IntentContext


class TestIntentGraphEndToEnd(unittest.TestCase):
    """End-to-end tests that exercise IntentGraphBuilder with the new classifiers."""

    def setUp(self):
        # Greet intent
        greet_handler = handler(
            name="greet",
            description="Greet the user",
            handler_func=lambda name, context=None: f"Hello {name}!",
            param_schema={"name": str},
        )
        # Add fuzzy keywords with common typos
        setattr(greet_handler, "fuzzy_keywords", ["hello", "helo", "hi", "greet"])

        # Calculate intent (very simple – doubles the provided number)
        calc_handler = handler(
            name="calculate",
            description="Double a number for demo purposes",
            handler_func=lambda a, context=None: a * 2,
            param_schema={"a": int},
        )
        setattr(calc_handler, "fuzzy_keywords", ["calculate", "calc", "compute", "math"])

        # Wrapper to lower the similarity threshold for demo stability
        def fuzzy_low_threshold(user_input: str, children, context=None):
            return fuzzy_classifier(user_input, children, context, threshold=0.5)

        root_classifier = ClassifierNode(
            name="root",
            classifier=fuzzy_low_threshold,
            children=[greet_handler, calc_handler],
            description="Fuzzy top-level classifier",
        )

        # Build the graph with the fluent builder
        self.graph = IntentGraphBuilder().root(root_classifier).build()

    def test_greet_flow_typo(self):
        """Typo-tolerant greeting should still route correctly."""
        ctx = IntentContext(session_id="s1")
        result = self.graph.route("Helo Alice", context=ctx)
        self.assertTrue(result.success)
        self.assertEqual(result.output, "Hello Alice!")

    def test_calculate_flow(self):
        """Numeric calculation via fuzzy keyword."""
        ctx = IntentContext(session_id="s2")
        result = self.graph.route("calc 7", context=ctx)
        self.assertTrue(result.success)
        # Expect double of 7 => 14
        self.assertEqual(result.output, 14)


if __name__ == "__main__":
    unittest.main()