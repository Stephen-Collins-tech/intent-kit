import pytest
from intent_kit.builders import (
    ActionBuilder,
    ClassifierBuilder,
    IntentGraphBuilder,
)
from intent_kit.node.actions import ActionNode
from intent_kit.node.classifiers import ClassifierNode
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
