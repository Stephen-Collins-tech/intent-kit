import pytest
from intent_kit.node import IntentNode, ClassifierNode, TreeNode
from intent_kit.tree import TreeBuilder
from intent_kit.classifiers.keyword import keyword_classifier


# Test fixtures


def extract_test_args(user_input: str, context=None) -> dict:
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


def test_tree_node_creation():
    """Test that TreeNode ABC cannot be instantiated directly."""
    import pytest
    with pytest.raises(TypeError):
        # type: ignore pylint: disable-next=abstract-class-instantiated
        TreeNode(  # type: ignore # pylint: disable-next=abstract-class-instantiated
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


def test_execute_tree_success(sample_tree):
    """Test successful tree execution."""
    result = sample_tree.execute(user_input="Test value")
    # The root classifier node should have routed to the Test intent
    assert result.success is True
    assert len(result.children_results) == 1

    # The child result should be the actual intent execution
    child_result = result.children_results[0]
    assert child_result.node_name == "Test"
    assert child_result.params == {"param": "value"}
    assert child_result.output == "Test with value"
    assert child_result.error is None


def test_execute_tree_no_match(sample_tree):
    """Test tree execution with no matching intent."""
    result = sample_tree.execute(user_input="Unknown value")
    # The root classifier should fail to route
    assert result.success is False
    assert result.error is not None and "could not route input" in result.error.message


def test_execute_tree_handler_error(sample_tree):
    """Test tree execution with handler error."""
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

    # The root classifier should route to the error intent, which should fail
    result = error_tree.execute(user_input="Error value")
    assert result.success is True  # Classifier succeeded
    assert len(result.children_results) == 1

    # The child result should contain the error
    child_result = result.children_results[0]
    assert child_result.node_name == "Error"
    assert child_result.success is False
    assert child_result.error is not None and "Test error" in child_result.error.message


def test_intent_node_execution():
    """Test direct intent node execution."""
    def test_handler(name: str, age: int) -> str:
        return f"Hello {name}, you are {age} years old"

    def extract_person_args(user_input: str, context=None) -> dict:
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
    assert result.success is True
    assert result.params == {"name": "John", "age": 30}
    assert result.output == "Hello John, you are 30 years old"
    assert result.error is None
    assert result.input == "John 30"

    # Test validation failure - now returns ExecutionResult with error
    result = intent.execute("")
    assert result.success is False
    assert result.error is not None and "validation failed" in result.error.message


def test_type_validation():
    """Test type validation in intent execution."""
    def test_handler(count: int, active: bool) -> str:
        return f"Count: {count}, Active: {active}"

    def extract_args(user_input: str, context=None) -> dict:
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
    assert result.success is True
    assert result.params == {"count": 10, "active": True}
    assert result.input == "10 true"

    # Test invalid type - now returns ExecutionResult with error
    result = intent.execute("invalid true")
    assert result.success is False
    assert result.error is not None and "must be an integer" in result.error.message
