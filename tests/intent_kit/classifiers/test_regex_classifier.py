import unittest

from intent_kit.classifiers.regex import regex_classifier
from intent_kit.builder import handler


class TestRegexClassifier(unittest.TestCase):
    """Tests for the regex_classifier helper."""

    def setUp(self):
        # Minimal handler nodes for testing
        self.greet_handler = handler(
            name="Greet",
            description="Say hello",
            handler_func=lambda name: f"Hello {name}!",
            param_schema={"name": str},
        )
        # Attach regex patterns for greeting
        setattr(self.greet_handler, "regex_patterns", [r"\bhello\b", r"\bhi\b", r"\bgreet\b"])

        self.calc_handler = handler(
            name="Calculate",
            description="Do math",
            handler_func=lambda a, b: a + b,
            param_schema={"a": int, "b": int},
        )
        # Regex patterns for calculation intents
        setattr(self.calc_handler, "regex_patterns", [r"\bcalculate\b", r"\bcalc\b", r"\bcompute\b"])

        self.children = [self.greet_handler, self.calc_handler]

    def test_match_with_explicit_patterns(self):
        """Input matching custom regex patterns should return the correct node."""
        chosen = regex_classifier("hi there", self.children)
        self.assertIsNotNone(chosen)
        self.assertEqual(chosen.name, "Greet")

    def test_match_with_fallback_name(self):
        """When no patterns provided, fallback to matching the node name (case-insensitive)."""
        weather_handler = handler(
            name="Weather",
            description="Weather info",
            handler_func=lambda location: f"Weather in {location}",
            param_schema={"location": str},
        )
        # Note: no regex_patterns attribute set
        children = self.children + [weather_handler]
        chosen = regex_classifier("Tell me the weather please", children)
        self.assertIsNotNone(chosen)
        self.assertEqual(chosen.name, "Weather")

    def test_no_match_returns_none(self):
        chosen = regex_classifier("unrelated input", self.children)
        self.assertIsNone(chosen)


if __name__ == "__main__":
    unittest.main()