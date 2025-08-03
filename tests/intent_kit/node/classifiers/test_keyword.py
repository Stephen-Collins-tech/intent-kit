from intent_kit.nodes.classifiers.keyword import keyword_classifier


class DummyChild:
    def __init__(self, name):
        self.name = name


def test_keyword_classifier_match():
    children = [DummyChild("weather"), DummyChild("cancel")]
    result = keyword_classifier("Show me the weather", children)
    assert result is children[0]


def test_keyword_classifier_no_match():
    children = [DummyChild("weather"), DummyChild("cancel")]
    result = keyword_classifier("Book a flight", children)
    assert result is None


def test_keyword_classifier_case_insensitive():
    children = [DummyChild("Weather"), DummyChild("Cancel")]
    result = keyword_classifier("what's the WEATHER like?", children)
    assert result is children[0]
