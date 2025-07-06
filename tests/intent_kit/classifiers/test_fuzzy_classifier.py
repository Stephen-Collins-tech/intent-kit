import unittest

from intent_kit.classifiers.fuzzy import fuzzy_classifier
from intent_kit.builder import handler


class TestFuzzyClassifier(unittest.TestCase):
    """Tests for the typo-tolerant fuzzy_classifier."""

    def setUp(self):
        self.greet_handler = handler(
            name="Greet",
            description="Say hello",
            handler_func=lambda name: f"Hello {name}!",
            param_schema={"name": str},
        )
        # Custom fuzzy keywords (intentionally lower-cased for clarity)
        setattr(self.greet_handler, "fuzzy_keywords", ["hello", "hi", "greetings"])

        self.calc_handler = handler(
            name="Calculate",
            description="Do math",
            handler_func=lambda a, b: a + b,
            param_schema={"a": int, "b": int},
        )
        setattr(self.calc_handler, "fuzzy_keywords", ["calculate", "compute", "math"])

        self.children = [self.greet_handler, self.calc_handler]

    def test_exact_match(self):
        chosen = fuzzy_classifier("hello there", self.children)
        self.assertIsNotNone(chosen)
        self.assertEqual(getattr(chosen, "name", None), "Greet")

    def test_typo_tolerant_match(self):
        # Intentional typo in the keyword "calculate"
        chosen = fuzzy_classifier("calclate 2+2", self.children)
        self.assertIsNotNone(chosen)
        self.assertEqual(getattr(chosen, "name", None), "Calculate")

    def test_no_match_below_threshold(self):
        # Use a very high threshold so nothing matches
        chosen = fuzzy_classifier("random text", self.children, threshold=0.95)
        self.assertIsNone(chosen)


if __name__ == "__main__":
    unittest.main()