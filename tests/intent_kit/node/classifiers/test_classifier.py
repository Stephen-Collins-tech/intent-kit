"""
Tests for classifier node module.
"""

from unittest.mock import patch, MagicMock
from typing import cast
from intent_kit.nodes.classifiers.node import ClassifierNode
from intent_kit.nodes.enums import NodeType
from intent_kit.nodes.types import ExecutionResult
from intent_kit.types import (
    LLMResponse,
    Model,
    InputTokens,
    OutputTokens,
    Cost,
    Provider,
    Duration,
)
from intent_kit.context import Context
from intent_kit.nodes.base_node import TreeNode


class TestClassifierNode:
    """Test cases for ClassifierNode."""

    def test_init(self):
        """Test ClassifierNode initialization."""
        mock_children = [cast(TreeNode, MagicMock()), cast(TreeNode, MagicMock())]

        node = ClassifierNode(
            name="test_classifier",
            children=mock_children,
            description="Test classifier",
        )

        assert node.name == "test_classifier"
        assert node.children == mock_children
        assert node.description == "Test classifier"

    def test_node_type(self):
        """Test node_type property."""
        mock_children = [cast(TreeNode, MagicMock())]

        node = ClassifierNode(name="test_classifier", children=mock_children)

        assert node.node_type == NodeType.CLASSIFIER

    @patch("intent_kit.services.ai.ollama_client.OllamaClient.generate")
    def test_execute_success(self, mock_generate):
        """Test successful execution with classifier routing."""
        mock_child = cast(TreeNode, MagicMock())
        mock_child.name = "test_child"
        mock_children = [mock_child]

        # Mock the LLM response for classification
        from intent_kit.types import (
            LLMResponse,
            Model,
            InputTokens,
            OutputTokens,
            Cost,
            Provider,
            Duration,
        )

        mock_response = LLMResponse(
            output={"choice": 1},
            model=Model("llama2"),
            input_tokens=InputTokens(10),
            output_tokens=OutputTokens(5),
            cost=Cost(0.001),
            provider=Provider("ollama"),
            duration=Duration(0.1),
        )
        mock_generate.return_value = mock_response

        # Mock child execution result
        mock_child_result = MagicMock()
        mock_child_result.output = "child output"
        mock_child_result.cost = 0.2
        mock_child_result.input_tokens = 20
        mock_child_result.output_tokens = 15
        mock_child.execute.return_value = mock_child_result

        node = ClassifierNode(
            name="test_classifier",
            children=mock_children,
            llm_config={"provider": "ollama", "model": "llama2"},
        )

        context = Context()
        result = node.execute("test input", context)

        assert result.success is True
        assert result.output == "child output"
        assert result.node_name == "test_classifier"
        assert result.node_type == NodeType.CLASSIFIER
        assert result.input == "test input"
        assert result.params is not None
        assert result.params["chosen_child"] == "test_child"

    @patch("intent_kit.services.ai.ollama_client.OllamaClient.generate")
    def test_execute_no_routing(self, mock_generate):
        """Test execution when classifier cannot route input."""
        mock_children = [cast(TreeNode, MagicMock())]

        # Mock the LLM response for no routing
        from intent_kit.types import (
            LLMResponse,
            Model,
            InputTokens,
            OutputTokens,
            Cost,
            Provider,
            Duration,
        )

        mock_response = LLMResponse(
            output={"choice": 0},
            model=Model("llama2"),
            input_tokens=InputTokens(10),
            output_tokens=OutputTokens(5),
            cost=Cost(0.001),
            provider=Provider("ollama"),
            duration=Duration(0.1),
        )
        mock_generate.return_value = mock_response

        node = ClassifierNode(
            name="test_classifier",
            children=mock_children,
            llm_config={"provider": "ollama", "model": "llama2"},
        )

        context = Context()
        result = node.execute("test input", context)

        assert result.success is True
        assert result.output is None
        assert result.params is not None
        assert result.params["chosen_child"] is None

    @patch("intent_kit.services.ai.ollama_client.OllamaClient.generate")
    def test_execute_with_remediation_success(self, mock_generate):
        """Test execution with successful remediation."""
        mock_children = [cast(TreeNode, MagicMock())]

        # Mock the LLM response for no routing
        from intent_kit.types import (
            LLMResponse,
            Model,
            InputTokens,
            OutputTokens,
            Cost,
            Provider,
            Duration,
        )

        mock_response = LLMResponse(
            output={"choice": 0},
            model=Model("llama2"),
            input_tokens=InputTokens(10),
            output_tokens=OutputTokens(5),
            cost=Cost(0.001),
            provider=Provider("ollama"),
            duration=Duration(0.1),
        )
        mock_generate.return_value = mock_response

        node = ClassifierNode(
            name="test_classifier",
            children=mock_children,
            llm_config={"provider": "ollama", "model": "llama2"},
        )

        context = Context()
        result = node.execute("test input", context)

        assert result.success is True
        assert result.output == "remediated output"

    @patch("intent_kit.services.ai.ollama_client.OllamaClient.generate")
    def test_execute_with_remediation_failure(self, mock_generate):
        """Test execution with failed remediation."""
        mock_children = [cast(TreeNode, MagicMock())]

        # Mock the LLM response for no routing
        from intent_kit.types import (
            LLMResponse,
            Model,
            InputTokens,
            OutputTokens,
            Cost,
            Provider,
            Duration,
        )

        mock_response = LLMResponse(
            output={"choice": 0},
            model=Model("llama2"),
            input_tokens=InputTokens(10),
            output_tokens=OutputTokens(5),
            cost=Cost(0.001),
            provider=Provider("ollama"),
            duration=Duration(0.1),
        )
        mock_generate.return_value = mock_response

        # Mock remediation strategy that fails
        mock_strategy = MagicMock()
        mock_strategy.name = "test_strategy"
        mock_strategy.execute.return_value = None  # Strategy fails

        node = ClassifierNode(
            name="test_classifier",
            children=mock_children,
            llm_config={"provider": "ollama", "model": "llama2"},
        )

        context = Context()
        result = node.execute("test input", context)

        assert result.success is True
        assert result.output is None
        assert result.params is not None
        assert result.params["chosen_child"] is None

    @patch("intent_kit.services.ai.ollama_client.OllamaClient.generate")
    def test_execute_with_string_remediation_strategy(self, mock_generate):
        """Test execution with string-based remediation strategy."""
        mock_children = [cast(TreeNode, MagicMock())]

        # Mock the LLM response for no routing
        from intent_kit.types import (
            LLMResponse,
            Model,
            InputTokens,
            OutputTokens,
            Cost,
            Provider,
            Duration,
        )

        mock_response = LLMResponse(
            output={"choice": 0},
            model=Model("llama2"),
            input_tokens=InputTokens(10),
            output_tokens=OutputTokens(5),
            cost=Cost(0.001),
            provider=Provider("ollama"),
            duration=Duration(0.1),
        )
        mock_generate.return_value = mock_response

        # Mock remediation strategy from registry
        mock_strategy = MagicMock()
        mock_strategy.name = "registry_strategy"
        mock_strategy.execute.return_value = ExecutionResult(
            success=True,
            node_name="test_classifier",
            node_path=["test_classifier"],
            node_type=NodeType.CLASSIFIER,
            input="test input",
            output="registry output",
            error=None,
            params={},
            children_results=[],
        )

        node = ClassifierNode(
            name="test_classifier",
            children=mock_children,
            llm_config={"provider": "ollama", "model": "llama2"},
        )

        context = Context()
        result = node.execute("test input", context)

        assert result.success is True
        assert result.output == "registry output"

    @patch("intent_kit.services.ai.ollama_client.OllamaClient.generate")
    def test_execute_with_invalid_remediation_strategy(self, mock_generate):
        """Test execution with invalid remediation strategy type."""
        mock_children = [cast(TreeNode, MagicMock())]

        # Mock the LLM response for no routing
        from intent_kit.types import (
            LLMResponse,
            Model,
            InputTokens,
            OutputTokens,
            Cost,
            Provider,
            Duration,
        )

        mock_response = LLMResponse(
            output={"choice": 0},
            model=Model("llama2"),
            input_tokens=InputTokens(10),
            output_tokens=OutputTokens(5),
            cost=Cost(0.001),
            provider=Provider("ollama"),
            duration=Duration(0.1),
        )
        mock_generate.return_value = mock_response

        node = ClassifierNode(
            name="test_classifier",
            children=mock_children,
            llm_config={"provider": "ollama", "model": "llama2"},
        )

        context = Context()
        result = node.execute("test input", context)

        assert result.success is True
        assert result.output is None

    @patch("intent_kit.services.ai.ollama_client.OllamaClient.generate")
    def test_execute_with_missing_registry_strategy(self, mock_generate):
        """Test execution with missing registry strategy."""
        mock_children = [cast(TreeNode, MagicMock())]

        # Mock the LLM response for no routing
        from intent_kit.types import (
            LLMResponse,
            Model,
            InputTokens,
            OutputTokens,
            Cost,
            Provider,
            Duration,
        )

        mock_response = LLMResponse(
            output={"choice": 0},
            model=Model("llama2"),
            input_tokens=InputTokens(10),
            output_tokens=OutputTokens(5),
            cost=Cost(0.001),
            provider=Provider("ollama"),
            duration=Duration(0.1),
        )
        mock_generate.return_value = mock_response

        node = ClassifierNode(
            name="test_classifier",
            children=mock_children,
            llm_config={"provider": "ollama", "model": "llama2"},
        )

        context = Context()
        result = node.execute("test input", context)

        assert result.success is True
        assert result.output is None

    @patch("intent_kit.services.ai.ollama_client.OllamaClient.generate")
    def test_execute_with_remediation_exception(self, mock_generate):
        """Test execution with remediation strategy exception."""
        mock_children = [cast(TreeNode, MagicMock())]

        # Mock the LLM response for no routing
        from intent_kit.types import (
            LLMResponse,
            Model,
            InputTokens,
            OutputTokens,
            Cost,
            Provider,
            Duration,
        )

        mock_response = LLMResponse(
            output={"choice": 0},
            model=Model("llama2"),
            input_tokens=InputTokens(10),
            output_tokens=OutputTokens(5),
            cost=Cost(0.001),
            provider=Provider("ollama"),
            duration=Duration(0.1),
        )
        mock_generate.return_value = mock_response

        # Mock remediation strategy that raises exception
        mock_strategy = MagicMock()
        mock_strategy.name = "test_strategy"
        mock_strategy.execute.side_effect = Exception("Strategy error")

        node = ClassifierNode(
            name="test_classifier",
            children=mock_children,
            llm_config={"provider": "ollama", "model": "llama2"},
        )

        context = Context()
        result = node.execute("test input", context)

        assert result.success is True
        assert result.output is None

    @patch("intent_kit.services.ai.ollama_client.OllamaClient.generate")
    def test_execute_with_context_dict(self, mock_generate):
        """Test execution with context dictionary."""
        mock_child = cast(TreeNode, MagicMock())
        mock_child.name = "test_child"
        mock_children = [mock_child]

        # Mock the LLM response for classification
        mock_response = LLMResponse(
            output={"choice": 1},
            model=Model("llama2"),
            input_tokens=InputTokens(10),
            output_tokens=OutputTokens(5),
            cost=Cost(0.001),
            provider=Provider("ollama"),
            duration=Duration(0.1),
        )
        mock_generate.return_value = mock_response

        # Mock child execution result
        mock_child_result = MagicMock()
        mock_child_result.output = "child output"
        mock_child_result.cost = 0.2
        mock_child_result.input_tokens = 20
        mock_child_result.output_tokens = 15
        mock_child.execute.return_value = mock_child_result

        node = ClassifierNode(
            name="test_classifier",
            children=mock_children,
            llm_config={"provider": "ollama", "model": "llama2"},
        )

        context = Context()
        context.set("user_id", "123", modified_by="test")
        result = node.execute("test input", context)

        assert result.success is True
        assert result.output == "child output"
        assert result.node_name == "test_classifier"
        assert result.node_type == NodeType.CLASSIFIER
        assert result.input == "test input"
        assert result.params is not None
        assert result.params["chosen_child"] == "test_child"

    @patch("intent_kit.services.ai.ollama_client.OllamaClient.generate")
    def test_execute_without_context(self, mock_generate):
        """Test execute method without context."""
        # Create a mock child with proper setup
        mock_child = cast(TreeNode, MagicMock())
        mock_child.name = "test_child"
        mock_child_result = MagicMock()
        mock_child_result.output = "child output"
        mock_child_result.cost = 0.2
        mock_child_result.input_tokens = 20
        mock_child_result.output_tokens = 15
        mock_child.execute.return_value = mock_child_result

        # Mock the LLM response for classification
        from intent_kit.types import (
            LLMResponse,
            Model,
            InputTokens,
            OutputTokens,
            Cost,
            Provider,
            Duration,
        )

        mock_response = LLMResponse(
            output={"choice": 1},
            model=Model("llama2"),
            input_tokens=InputTokens(10),
            output_tokens=OutputTokens(5),
            cost=Cost(0.001),
            provider=Provider("ollama"),
            duration=Duration(0.1),
        )
        mock_generate.return_value = mock_response

        classifier_node = ClassifierNode(
            name="test_classifier",
            children=[mock_child],
            llm_config={"provider": "ollama", "model": "llama2"},
        )

        result = classifier_node.execute("test input")

        assert result.success is True
        assert result.output == "child output"
        assert result.node_name == "test_classifier"
        assert result.node_type == NodeType.CLASSIFIER
        assert result.input == "test input"
        assert result.params is not None
        assert result.params["chosen_child"] == "test_child"
