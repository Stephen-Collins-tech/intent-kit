"""
Tests for intent_kit.builder module.
"""

import pytest
from unittest.mock import Mock
from typing import Dict, Any

from intent_kit.builder import (
    IntentGraphBuilder,
    handler,
    llm_classifier,
    llm_splitter_node,
    rule_splitter_node,
    create_intent_graph,
)
from intent_kit.node import TreeNode
from intent_kit.handlers import HandlerNode
from intent_kit.classifiers import ClassifierNode
from intent_kit.splitters import SplitterNode
from intent_kit.graph import IntentGraph


class MockTreeNode(TreeNode):
    """Mock TreeNode for testing."""

    def __init__(self, name: str, description: str = ""):
        super().__init__(name=name, description=description)
        self.parent = None
        self.executed = False

    def execute(self, user_input: str, context=None):
        """Mock execute method."""
        self.executed = True
        from intent_kit.node.types import ExecutionResult
        from intent_kit.node.enums import NodeType

        return ExecutionResult(
            success=True,
            node_name=self.name,
            node_path=[self.name],
            node_type=NodeType.UNKNOWN,
            input=user_input,
            output=f"Mock output for {user_input}",
            error=None,
            params={},
            children_results=[],
        )


class TestIntentGraphBuilder:
    """Test the IntentGraphBuilder class."""

    def test_builder_initialization(self):
        """Test IntentGraphBuilder initialization."""
        builder = IntentGraphBuilder()

        assert builder._root_node is None
        assert builder._splitter is None
        assert builder._debug_context is False
        assert builder._context_trace is False

    def test_root_method(self):
        """Test setting the root node."""
        builder = IntentGraphBuilder()
        root_node = MockTreeNode("root", "Root node")

        result = builder.root(root_node)

        assert result is builder  # Method chaining
        assert builder._root_node == root_node

    def test_splitter_method(self):
        """Test setting a custom splitter function."""
        builder = IntentGraphBuilder()

        def splitter_func(x):
            return []

        result = builder.splitter(splitter_func)

        assert result is builder  # Method chaining
        assert builder._splitter == splitter_func

    def test_debug_context_method(self):
        """Test enabling/disabling debug context."""
        builder = IntentGraphBuilder()

        # Enable debug context
        result = builder.debug_context(True)
        assert result is builder
        assert builder._debug_context is True

        # Disable debug context
        result = builder.debug_context(False)
        assert result is builder
        assert builder._debug_context is False

        # Default to True
        result = builder.debug_context()
        assert result is builder
        assert builder._debug_context is True

    def test_context_trace_method(self):
        """Test enabling/disabling context tracing."""
        builder = IntentGraphBuilder()

        # Enable context tracing
        result = builder.context_trace(True)
        assert result is builder
        assert builder._context_trace is True

        # Disable context tracing
        result = builder.context_trace(False)
        assert result is builder
        assert builder._context_trace is False

        # Default to True
        result = builder.context_trace()
        assert result is builder
        assert builder._context_trace is True

    def test_build_with_root_node(self):
        """Test building IntentGraph with root node."""
        builder = IntentGraphBuilder()
        root_node = MockTreeNode("root", "Root node")

        builder.root(root_node)
        graph = builder.build()

        assert isinstance(graph, IntentGraph)
        assert len(graph.root_nodes) == 1
        assert graph.root_nodes[0] == root_node

    def test_build_with_root_node_and_splitter(self):
        """Test building IntentGraph with root node and splitter."""
        builder = IntentGraphBuilder()
        root_node = MockTreeNode("root", "Root node")

        def splitter_func(x):
            return []

        builder.root(root_node).splitter(splitter_func)
        graph = builder.build()

        assert isinstance(graph, IntentGraph)
        assert len(graph.root_nodes) == 1
        assert graph.root_nodes[0] == root_node

    def test_build_without_root_node(self):
        """Test building IntentGraph without root node raises error."""
        builder = IntentGraphBuilder()

        with pytest.raises(ValueError, match="No root node set"):
            builder.build()

    def test_build_with_debug_options(self):
        """Test building IntentGraph with debug options."""
        builder = IntentGraphBuilder()
        root_node = MockTreeNode("root", "Root node")

        builder.root(root_node).debug_context(True).context_trace(True)
        graph = builder.build()

        assert isinstance(graph, IntentGraph)
        assert len(graph.root_nodes) == 1
        assert graph.root_nodes[0] == root_node

    def test_method_chaining(self):
        """Test method chaining functionality."""
        builder = IntentGraphBuilder()
        root_node = MockTreeNode("root", "Root node")

        def splitter_func(x):
            return []

        result = (
            builder.root(root_node)
            .splitter(splitter_func)
            .debug_context(True)
            .context_trace(True)
            .build()
        )

        assert isinstance(result, IntentGraph)
        assert len(result.root_nodes) == 1
        assert result.root_nodes[0] == root_node


class TestHandler:
    """Test the handler function."""

    def test_handler_basic_creation(self):
        """Test basic handler creation."""

        def handler_func(name: str) -> str:
            return f"Hello {name}!"

        handler_node = handler(
            name="greet",
            description="Greet the user",
            handler_func=handler_func,
            param_schema={"name": str},
        )

        assert isinstance(handler_node, HandlerNode)
        assert handler_node.name == "greet"
        assert handler_node.description == "Greet the user"
        assert handler_node.param_schema == {"name": str}

    def test_handler_with_llm_config(self):
        """Test handler creation with LLM config."""

        def handler_func(name: str, age: int) -> str:
            return f"Hello {name}, you are {age} years old!"

        llm_config = {"provider": "openai", "model": "gpt-4"}

        handler_node = handler(
            name="greet",
            description="Greet the user",
            handler_func=handler_func,
            param_schema={"name": str, "age": int},
            llm_config=llm_config,
        )

        assert isinstance(handler_node, HandlerNode)
        assert handler_node.name == "greet"
        assert handler_node.param_schema == {"name": str, "age": int}

    def test_handler_with_custom_extraction_prompt(self):
        """Test handler creation with custom extraction prompt."""

        def handler_func(name: str) -> str:
            return f"Hello {name}!"

        llm_config = {"provider": "openai", "model": "gpt-4"}
        extraction_prompt = "Custom prompt: {user_input}\n{param_descriptions}"

        handler_node = handler(
            name="greet",
            description="Greet the user",
            handler_func=handler_func,
            param_schema={"name": str},
            llm_config=llm_config,
            extraction_prompt=extraction_prompt,
        )

        assert isinstance(handler_node, HandlerNode)

    def test_handler_with_context_inputs_outputs(self):
        """Test handler creation with context inputs and outputs."""

        def handler_func(name: str) -> str:
            return f"Hello {name}!"

        handler_node = handler(
            name="greet",
            description="Greet the user",
            handler_func=handler_func,
            param_schema={"name": str},
            context_inputs={"user_id", "session"},
            context_outputs={"greeting_count"},
        )

        assert isinstance(handler_node, HandlerNode)
        assert handler_node.context_inputs == {"user_id", "session"}
        assert handler_node.context_outputs == {"greeting_count"}

    def test_handler_with_validators(self):
        """Test handler creation with input and output validators."""

        def handler_func(name: str) -> str:
            return f"Hello {name}!"

        def input_validator(params: Dict[str, Any]) -> bool:
            return "name" in params and len(params["name"]) > 0

        def output_validator(output: Any) -> bool:
            return isinstance(output, str) and "Hello" in output

        handler_node = handler(
            name="greet",
            description="Greet the user",
            handler_func=handler_func,
            param_schema={"name": str},
            input_validator=input_validator,
            output_validator=output_validator,
        )

        assert isinstance(handler_node, HandlerNode)
        assert handler_node.input_validator == input_validator
        assert handler_node.output_validator == output_validator

    def test_handler_with_remediation_strategies(self):
        """Test handler creation with remediation strategies."""

        def handler_func(name: str) -> str:
            return f"Hello {name}!"

        handler_node = handler(
            name="greet",
            description="Greet the user",
            handler_func=handler_func,
            param_schema={"name": str},
            remediation_strategies=["retry", "fallback"],
        )

        assert isinstance(handler_node, HandlerNode)
        assert handler_node.remediation_strategies == ["retry", "fallback"]

    def test_handler_simple_arg_extractor_string_param(self):
        """Test simple argument extractor with string parameter."""

        def handler_func(name: str) -> str:
            return f"Hello {name}!"

        handler_node = handler(
            name="greet",
            description="Greet the user",
            handler_func=handler_func,
            param_schema={"name": str},
        )

        # Test the argument extractor
        extracted = handler_node.arg_extractor("Hello John")
        assert extracted["name"] == "John"

    def test_handler_simple_arg_extractor_numeric_param(self):
        """Test simple argument extractor with numeric parameter."""

        def handler_func(age: int) -> str:
            return f"You are {age} years old!"

        handler_node = handler(
            name="age",
            description="Get age",
            handler_func=handler_func,
            param_schema={"age": int},
        )

        # Test the argument extractor
        extracted = handler_node.arg_extractor("I am 25 years old")
        assert extracted["age"] == 25

    def test_handler_simple_arg_extractor_multiple_params(self):
        """Test simple argument extractor with multiple parameters."""

        def handler_func(name: str, age: int) -> str:
            return f"Hello {name}, you are {age} years old!"

        handler_node = handler(
            name="greet",
            description="Greet the user",
            handler_func=handler_func,
            param_schema={"name": str, "age": int},
        )

        # Test the argument extractor
        extracted = handler_node.arg_extractor("Hello John, I am 25 years old")
        assert extracted["name"] == "old"  # Last word in text
        assert extracted["age"] == 25

    def test_handler_simple_arg_extractor_default_values(self):
        """Test simple argument extractor with default values."""

        def handler_func(a: int, b: int) -> int:
            return a + b

        handler_node = handler(
            name="add",
            description="Add two numbers",
            handler_func=handler_func,
            param_schema={"a": int, "b": int},
        )

        # Test with no numbers in text
        extracted = handler_node.arg_extractor("add some numbers")
        assert extracted["a"] == 10  # Default for "a"
        assert extracted["b"] == 5  # Default for "b"

    def test_handler_simple_arg_extractor_boolean_param(self):
        """Test simple argument extractor with boolean parameter."""

        def handler_func(enabled: bool) -> str:
            return f"Feature is {'enabled' if enabled else 'disabled'}"

        handler_node = handler(
            name="feature",
            description="Check feature status",
            handler_func=handler_func,
            param_schema={"enabled": bool},
        )

        # Test the argument extractor
        extracted = handler_node.arg_extractor("check feature status")
        assert extracted["enabled"] is True  # Default for bool


class TestLLMClassifier:
    """Test the llm_classifier function."""

    def test_llm_classifier_basic_creation(self):
        """Test basic LLM classifier creation."""
        children = [
            MockTreeNode("greet", "Greet the user"),
            MockTreeNode("calc", "Calculate something"),
        ]

        llm_config = {"provider": "openai", "model": "gpt-4"}

        classifier_node = llm_classifier(
            name="root", children=children, llm_config=llm_config
        )

        assert isinstance(classifier_node, ClassifierNode)
        assert classifier_node.name == "root"
        assert classifier_node.children == children
        assert all(child.parent == classifier_node for child in children)

    def test_llm_classifier_with_custom_prompt(self):
        """Test LLM classifier creation with custom prompt."""
        children = [
            MockTreeNode("greet", "Greet the user"),
            MockTreeNode("calc", "Calculate something"),
        ]

        llm_config = {"provider": "openai", "model": "gpt-4"}
        classification_prompt = "Custom prompt: {user_input}\n{node_descriptions}"

        classifier_node = llm_classifier(
            name="root",
            children=children,
            llm_config=llm_config,
            classification_prompt=classification_prompt,
        )

        assert isinstance(classifier_node, ClassifierNode)

    def test_llm_classifier_with_description(self):
        """Test LLM classifier creation with description."""
        children = [
            MockTreeNode("greet", "Greet the user"),
            MockTreeNode("calc", "Calculate something"),
        ]

        llm_config = {"provider": "openai", "model": "gpt-4"}

        classifier_node = llm_classifier(
            name="root",
            children=children,
            llm_config=llm_config,
            description="Root classifier",
        )

        assert isinstance(classifier_node, ClassifierNode)
        assert classifier_node.description == "Root classifier"

    def test_llm_classifier_with_remediation_strategies(self):
        """Test LLM classifier creation with remediation strategies."""
        children = [
            MockTreeNode("greet", "Greet the user"),
            MockTreeNode("calc", "Calculate something"),
        ]

        llm_config = {"provider": "openai", "model": "gpt-4"}

        classifier_node = llm_classifier(
            name="root",
            children=children,
            llm_config=llm_config,
            remediation_strategies=["retry", "fallback"],
        )

        assert isinstance(classifier_node, ClassifierNode)
        assert classifier_node.remediation_strategies == ["retry", "fallback"]

    def test_llm_classifier_without_children(self):
        """Test LLM classifier creation without children raises error."""
        llm_config = {"provider": "openai", "model": "gpt-4"}

        with pytest.raises(ValueError, match="requires at least one child node"):
            llm_classifier(name="root", children=[], llm_config=llm_config)

    def test_llm_classifier_children_without_descriptions(self):
        """Test LLM classifier with children that have no descriptions."""
        children = [
            MockTreeNode("greet", ""),  # No description
            MockTreeNode("calc", "Calculate something"),
        ]

        llm_config = {"provider": "openai", "model": "gpt-4"}

        classifier_node = llm_classifier(
            name="root", children=children, llm_config=llm_config
        )

        assert isinstance(classifier_node, ClassifierNode)
        # Should use name as fallback for description


class TestLLMSplitterNode:
    """Test the llm_splitter_node function."""

    def test_llm_splitter_node_basic_creation(self):
        """Test basic LLM splitter node creation."""
        children = [
            MockTreeNode("classifier", "Main classifier"),
        ]

        llm_config = {"provider": "openai", "model": "gpt-4", "llm_client": Mock()}

        splitter_node = llm_splitter_node(
            name="multi_intent_splitter", children=children, llm_config=llm_config
        )

        assert isinstance(splitter_node, SplitterNode)
        assert splitter_node.name == "multi_intent_splitter"
        assert splitter_node.children == children
        assert all(child.parent == splitter_node for child in children)

    def test_llm_splitter_node_with_description(self):
        """Test LLM splitter node creation with description."""
        children = [
            MockTreeNode("classifier", "Main classifier"),
        ]

        llm_config = {"provider": "openai", "model": "gpt-4", "llm_client": Mock()}

        splitter_node = llm_splitter_node(
            name="multi_intent_splitter",
            children=children,
            llm_config=llm_config,
            description="Split multi-intent inputs",
        )

        assert isinstance(splitter_node, SplitterNode)
        assert splitter_node.description == "Split multi-intent inputs"


class TestRuleSplitterNode:
    """Test the rule_splitter_node function."""

    def test_rule_splitter_node_basic_creation(self):
        """Test basic rule splitter node creation."""
        children = [
            MockTreeNode("classifier", "Main classifier"),
        ]

        splitter_node = rule_splitter_node(
            name="rule_based_splitter", children=children
        )

        assert isinstance(splitter_node, SplitterNode)
        assert splitter_node.name == "rule_based_splitter"
        assert splitter_node.children == children
        assert all(child.parent == splitter_node for child in children)

    def test_rule_splitter_node_with_description(self):
        """Test rule splitter node creation with description."""
        children = [
            MockTreeNode("classifier", "Main classifier"),
        ]

        splitter_node = rule_splitter_node(
            name="rule_based_splitter",
            children=children,
            description="Rule-based multi-intent splitter",
        )

        assert isinstance(splitter_node, SplitterNode)
        assert splitter_node.description == "Rule-based multi-intent splitter"


class TestCreateIntentGraph:
    """Test the create_intent_graph function."""

    def test_create_intent_graph(self):
        """Test creating an IntentGraph with a root node."""
        root_node = MockTreeNode("root", "Root node")

        graph = create_intent_graph(root_node)

        assert isinstance(graph, IntentGraph)
        assert len(graph.root_nodes) == 1
        assert graph.root_nodes[0] == root_node


class TestBuilderIntegration:
    """Integration tests for the builder module."""

    def test_complete_workflow(self):
        """Test a complete workflow using the builder."""

        # Create handler nodes
        def greet_handler(name: str) -> str:
            return f"Hello {name}!"

        def calc_handler(a: int, b: int) -> int:
            return a + b

        greet_node = handler(
            name="greet",
            description="Greet the user",
            handler_func=greet_handler,
            param_schema={"name": str},
        )

        calc_node = handler(
            name="calc",
            description="Calculate sum",
            handler_func=calc_handler,
            param_schema={"a": int, "b": int},
        )

        # Create classifier
        llm_config = {"provider": "openai", "model": "gpt-4"}
        classifier_node = llm_classifier(
            name="root", children=[greet_node, calc_node], llm_config=llm_config
        )

        # Create graph
        graph = create_intent_graph(classifier_node)

        assert isinstance(graph, IntentGraph)
        assert len(graph.root_nodes) == 1
        assert graph.root_nodes[0] == classifier_node

    def test_builder_with_all_options(self):
        """Test builder with all available options."""
        root_node = MockTreeNode("root", "Root node")

        def splitter_func(x):
            return []

        graph = (
            IntentGraphBuilder()
            .root(root_node)
            .splitter(splitter_func)
            .debug_context(True)
            .context_trace(True)
            .build()
        )

        assert isinstance(graph, IntentGraph)
        assert len(graph.root_nodes) == 1
        assert graph.root_nodes[0] == root_node

    def test_handler_with_all_options(self):
        """Test handler with all available options."""

        def handler_func(name: str, age: int) -> str:
            return f"Hello {name}, you are {age} years old!"

        def input_validator(params: Dict[str, Any]) -> bool:
            return "name" in params

        def output_validator(output: Any) -> bool:
            return isinstance(output, str)

        llm_config = {"provider": "openai", "model": "gpt-4"}
        extraction_prompt = "Custom extraction: {user_input}\n{param_descriptions}"

        handler_node = handler(
            name="greet",
            description="Greet the user",
            handler_func=handler_func,
            param_schema={"name": str, "age": int},
            llm_config=llm_config,
            extraction_prompt=extraction_prompt,
            context_inputs={"user_id"},
            context_outputs={"greeting_count"},
            input_validator=input_validator,
            output_validator=output_validator,
            remediation_strategies=["retry", "fallback"],
        )

        assert isinstance(handler_node, HandlerNode)
        assert handler_node.name == "greet"
        assert handler_node.param_schema == {"name": str, "age": int}
        assert handler_node.context_inputs == {"user_id"}
        assert handler_node.context_outputs == {"greeting_count"}
        assert handler_node.input_validator == input_validator
        assert handler_node.output_validator == output_validator
        assert handler_node.remediation_strategies == ["retry", "fallback"]
