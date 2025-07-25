import pytest
from intent_kit.builders import (
    ActionBuilder,
    ClassifierBuilder,
    SplitterBuilder,
    IntentGraphBuilder,
)
from intent_kit.node.actions import ActionNode
from intent_kit.node.classifiers import ClassifierNode
from intent_kit.node.splitters import SplitterNode
from intent_kit.graph import IntentGraph


def test_action_builder_basic():
    def greet(name: str) -> str:
        return f"Hello {name}!"

    node = (
        ActionBuilder("greet")
        .with_action(greet)
        .with_param_schema({"name": str})
        .with_description("Greet the user")
        .build()
    )
    assert isinstance(node, ActionNode)
    assert node.name == "greet"
    assert node.description == "Greet the user"
    assert node.param_schema == {"name": str}


def test_action_builder_missing_action():
    builder = ActionBuilder("fail")
    builder.with_param_schema({"name": str})
    with pytest.raises(ValueError):
        builder.build()


def test_classifier_builder_basic():
    def dummy_classifier(user_input, children, context=None):
        return children[0]

    child1 = (
        ActionBuilder("greet")
        .with_action(lambda n: f"Hi {n}")
        .with_param_schema({"name": str})
        .build()
    )
    child2 = (
        ActionBuilder("calc")
        .with_action(lambda a, b: a + b)
        .with_param_schema({"a": int, "b": int})
        .build()
    )

    node = (
        ClassifierBuilder("root")
        .with_classifier(dummy_classifier)
        .with_children([child1, child2])
        .with_description("Root classifier")
        .build()
    )
    assert isinstance(node, ClassifierNode)
    assert node.name == "root"
    assert node.description == "Root classifier"
    assert node.children == [child1, child2]


def test_classifier_builder_missing_children():
    builder = ClassifierBuilder("fail")
    with pytest.raises(ValueError):
        builder.build()


def test_splitter_builder_basic():
    def splitter_func(user_input, debug=False):
        return [user_input]

    child = (
        ActionBuilder("greet")
        .with_action(lambda n: f"Hi {n}")
        .with_param_schema({"name": str})
        .build()
    )
    node = (
        SplitterBuilder("splitter")
        .with_splitter(splitter_func)
        .with_children([child])
        .with_description("Test splitter")
        .build()
    )
    assert isinstance(node, SplitterNode)
    assert node.name == "splitter"
    assert node.description == "Test splitter"
    assert node.children == [child]


def test_splitter_builder_missing_splitter():
    child = (
        ActionBuilder("greet")
        .with_action(lambda n: f"Hi {n}")
        .with_param_schema({"name": str})
        .build()
    )
    builder = SplitterBuilder("fail").with_children([child])
    with pytest.raises(ValueError):
        builder.build()


def test_intent_graph_builder_full():
    # Build nodes
    greet = (
        ActionBuilder("greet")
        .with_action(lambda n: f"Hi {n}")
        .with_param_schema({"name": str})
        .build()
    )
    calc = (
        ActionBuilder("calc")
        .with_action(lambda a, b: a + b)
        .with_param_schema({"a": int, "b": int})
        .build()
    )
    classifier = ClassifierBuilder("root").with_children([greet, calc]).build()
    # Build graph
    graph = IntentGraphBuilder().root(classifier).build()
    assert isinstance(graph, IntentGraph)
    assert graph.root_nodes[0] == classifier


def test_intent_graph_builder_with_llm_config():
    """Test that IntentGraphBuilder correctly passes llm_config to IntentGraph."""
    greet = (
        ActionBuilder("greet")
        .with_action(lambda n: f"Hi {n}")
        .with_param_schema({"name": str})
        .build()
    )
    classifier = ClassifierBuilder("root").with_children([greet]).build()

    llm_config = {"provider": "openai", "model": "gpt-4"}
    graph = (
        IntentGraphBuilder()
        .root(classifier)
        .with_default_llm_config(llm_config)
        .build()
    )

    assert isinstance(graph, IntentGraph)
    assert graph.llm_config == llm_config
    assert graph.root_nodes[0] == classifier
