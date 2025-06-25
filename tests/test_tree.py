import pytest
from intent_kit.node import IntentNode, ClassifierNode, TaxonomyNode
from intent_kit.tree import TreeBuilder
from intent_kit.classifiers import keyword_classifier
from intent_kit.engine import execute_taxonomy

# Test fixtures


def extract_test_args(user_input: str) -> dict:
    """Simple argument extractor for testing."""
    words = user_input.split()
    return {"param": words[-1] if words else "default"}


def validate_test_args(params: dict) -> bool:
    """Simple validator for testing."""
    return bool(params.get("param"))


@pytest.fixture
def sample_handlers():
    def handle_test(param: str) -> str:
        return f"Test with {param}"
    return {"test": handle_test}


@pytest.fixture
def sample_tree(sample_handlers):
    return TreeBuilder.classifier_node(
        name="Root",
        classifier=keyword_classifier,
        children=[
            TreeBuilder.intent_node(
                name="Test",
                param_schema={"param": str},
                handler=sample_handlers["test"],
                arg_extractor=extract_test_args,
                input_validator=validate_test_args,
                description="Test intent"
            ),
        ],
        description="Test root"
    )


def test_taxonomy_node_creation():
    """Test that TaxonomyNode ABC cannot be instantiated directly."""
    import pytest
    with pytest.raises(TypeError):
        # type: ignore pylint: disable-next=abstract-class-instantiated
        TaxonomyNode(  # type: ignore # pylint: disable-next=abstract-class-instantiated
            name="test",
            description="test description"
        )


def test_intent_creation(sample_handlers):
    """Test intent node creation."""
    intent = TreeBuilder.intent_node(
        name="Test",
        param_schema={"param": str},
        handler=sample_handlers["test"],
        arg_extractor=extract_test_args,
        input_validator=validate_test_args
    )
    assert isinstance(intent, IntentNode)
    assert intent.name == "Test"
    assert intent.param_schema == {"param": str}
    assert intent.handler == sample_handlers["test"]
    assert intent.arg_extractor == extract_test_args


def test_classifier_node_creation():
    """Test classifier node creation."""
    node = TreeBuilder.classifier_node(
        name="Test",
        classifier=keyword_classifier,
        children=[],
        description="Test classifier"
    )
    assert isinstance(node, ClassifierNode)
    assert node.name == "Test"
    assert node.classifier == keyword_classifier
    assert node.children == []


def test_execute_taxonomy_success(sample_tree):
    """Test successful taxonomy execution."""
    result = execute_taxonomy(user_input="Test value", node=sample_tree)
    assert result["intent"] == "Test"
    assert result["params"] == {"param": "value"}
    assert result["output"] == "Test with value"
    assert result["error"] is None


def test_execute_taxonomy_no_match(sample_tree):
    """Test taxonomy execution with no matching intent."""
    result = execute_taxonomy(user_input="Unknown value", node=sample_tree)
    assert result["intent"] is None
    assert result["params"] is None
    assert result["output"] is None
    assert "could not route input" in result["error"]


def test_execute_taxonomy_handler_error(sample_tree):
    """Test taxonomy execution with handler error."""
    def error_handler(param: str) -> str:
        raise ValueError("Test error")

    error_tree = TreeBuilder.classifier_node(
        name="Root",
        classifier=keyword_classifier,
        children=[
            TreeBuilder.intent_node(
                name="Error",
                param_schema={"param": str},
                handler=error_handler,
                arg_extractor=extract_test_args,
                input_validator=validate_test_args,
                description="Error intent"
            ),
        ],
        description="Error test root"
    )

    result = execute_taxonomy(user_input="Error value", node=error_tree)
    assert result["intent"] == "Error"
    assert result["params"] == {"param": "value"}
    assert result["output"] is None
    assert "Test error" in result["error"]


def test_intent_node_execution():
    """Test direct intent node execution."""
    def test_handler(name: str, age: int) -> str:
        return f"Hello {name}, you are {age} years old"

    def extract_person_args(user_input: str) -> dict:
        words = user_input.split()
        if len(words) >= 2:
            return {"name": words[0], "age": words[1]}
        elif len(words) == 1:
            return {"name": words[0], "age": ""}
        else:
            return {"name": "", "age": ""}

    def validate_person_args(params: dict) -> bool:
        return bool(params.get("name") and params.get("age"))

    intent = IntentNode(
        name="GreetPerson",
        param_schema={"name": str, "age": int},
        handler=test_handler,
        arg_extractor=extract_person_args,
        input_validator=validate_person_args
    )

    # Test successful execution
    result = intent.execute("John 30")
    assert result["success"] is True
    assert result["params"] == {"name": "John", "age": 30}
    assert result["output"] == "Hello John, you are 30 years old"
    assert result["error"] is None

    # Test validation failure
    result = intent.execute("")
    assert result["success"] is False
    assert "validation failed" in result["error"]


def test_type_validation():
    """Test type validation in intent execution."""
    def test_handler(count: int, active: bool) -> str:
        return f"Count: {count}, Active: {active}"

    def extract_args(user_input: str) -> dict:
        words = user_input.split()
        return {
            "count": words[0] if words else "5",
            "active": words[1] if len(words) > 1 else "true"
        }

    intent = IntentNode(
        name="TestTypes",
        param_schema={"count": int, "active": bool},
        handler=test_handler,
        arg_extractor=extract_args
    )

    # Test successful type conversion
    result = intent.execute("10 true")
    assert result["success"] is True
    assert result["params"] == {"count": 10, "active": True}

    # Test invalid type
    result = intent.execute("invalid true")
    assert result["success"] is False
    assert "must be an integer" in result["error"]
