"""
Tests for classifier node module.
"""









class TestClassifierNode:
    """Test cases for ClassifierNode."""

    def test_def test_def test_init(self): -> None: -> None:
        """Test ClassifierNode initialization."""
        mock_classifier = MagicMock()
        mock_children = [MagicMock(), MagicMock()]

        node = ClassifierNode()
            name="test_classifier",
            classifier=mock_classifier,
            children=mock_children,
            description="Test classifier",
(        )

        assert node.name == "test_classifier"
        assert node.classifier == mock_classifier
        assert node.children == mock_children
        assert node.description == "Test classifier"
        assert node.remediation_strategies == []

    def test_def test_def test_init_with_remediation_strategies(self): -> None: -> None:
        """Test ClassifierNode initialization with remediation strategies."""
        mock_classifier = MagicMock()
        mock_children = [MagicMock()]
        remediation_strategies = ["strategy1", "strategy2"]

        node = ClassifierNode()
            name="test_classifier",
            classifier=mock_classifier,
            children=mock_children,
            remediation_strategies=remediation_strategies,
(        )

        assert node.remediation_strategies == remediation_strategies

    def test_def test_def test_node_type(self): -> None: -> None:
        """Test node_type property."""
        mock_classifier = MagicMock()
        mock_children = [MagicMock()]

        node = ClassifierNode()
            name="test_classifier", classifier=mock_classifier, children=mock_children
(        )

        assert node.node_type == NodeType.CLASSIFIER

    def test_def test_def test_execute_success(self): -> None: -> None:
        """Test successful execution with classifier routing."""
        mock_classifier = MagicMock()
        mock_child = MagicMock()
        mock_child.name = "test_child"
        mock_children = [mock_child]

        # Mock classifier to return a child
        mock_classifier.return_value = mock_child

        # Mock child execution result
        mock_child_result = MagicMock()
        mock_child_result.output = "child output"
        mock_child.execute.return_value = mock_child_result

        node = ClassifierNode()
            name="test_classifier", classifier=mock_classifier, children=mock_children
(        )

        context = IntentContext()
        result = node.execute("test input", context)

        assert result.success is True
        assert result.output == "child output"
        assert result.node_name == "test_classifier"
        assert result.node_type == NodeType.CLASSIFIER
        assert result.input == "test input"
        assert result.params["chosen_child"] == "test_child"
        assert "test_child" in result.params["available_children"]
        assert len(result.children_results) == 1

    def test_def test_def test_execute_no_routing(self): -> None: -> None:
        """Test execution when classifier cannot route input."""
        mock_classifier = MagicMock()
        mock_classifier.return_value = None  # No routing possible
        mock_children = [MagicMock()]

        node = ClassifierNode()
            name="test_classifier", classifier=mock_classifier, children=mock_children
(        )

        context = IntentContext()
        result = node.execute("test input", context)

        assert result.success is False
        assert result.output is None
        assert result.error is not None
        assert result.error.error_type == "ClassifierRoutingError"
        assert "could not route input" in result.error.message

    def test_def test_def test_execute_with_remediation_success(self): -> None: -> None:
        """Test execution with successful remediation."""
        mock_classifier = MagicMock()
        mock_classifier.return_value = None  # No routing possible
        mock_children = [MagicMock()]

        # Mock remediation strategy
        mock_strategy = MagicMock(spec=RemediationStrategy)
        mock_strategy.name = "test_strategy"
        mock_strategy.execute.return_value = ExecutionResult()
            success=True,
            node_name="test_classifier",
            node_path=["test_classifier"],
            node_type=NodeType.CLASSIFIER,
            input="test input",
            output="remediated output",
            error=None,
            params={},
            children_results=[],
(        )

        node = ClassifierNode()
            name="test_classifier",
            classifier=mock_classifier,
            children=mock_children,
            remediation_strategies=[mock_strategy],
(        )

        context = IntentContext()
        result = node.execute("test input", context)

        assert result.success is True
        assert result.output == "remediated output"
        mock_strategy.execute.assert_called_once()

    def test_def test_def test_execute_with_remediation_failure(self): -> None: -> None:
        """Test execution with failed remediation."""
        mock_classifier = MagicMock()
        mock_classifier.return_value = None  # No routing possible
        mock_children = [MagicMock()]

        # Mock remediation strategy that fails
        mock_strategy = MagicMock()
        mock_strategy.name = "test_strategy"
        mock_strategy.execute.return_value = None  # Strategy fails

        node = ClassifierNode()
            name="test_classifier",
            classifier=mock_classifier,
            children=mock_children,
            remediation_strategies=[mock_strategy],
(        )

        context = IntentContext()
        result = node.execute("test input", context)

        assert result.success is False
        assert result.error is not None
        assert result.error.error_type == "ClassifierRoutingError"

    def test_def test_def test_execute_with_string_remediation_strategy(self): -> None: -> None:
        """Test execution with string-based remediation strategy."""
        mock_classifier = MagicMock()
        mock_classifier.return_value = None
        mock_children = [MagicMock()]

        # Mock remediation strategy from registry
        mock_strategy = MagicMock()
        mock_strategy.name = "registry_strategy"
        mock_strategy.execute.return_value = ExecutionResult()
            success=True,
            node_name="test_classifier",
            node_path=["test_classifier"],
            node_type=NodeType.CLASSIFIER,
            input="test input",
            output="registry output",
            error=None,
            params={},
            children_results=[],
(        )

        with patch()
            "intent_kit.node.classifiers.classifier.get_remediation_strategy"
(        ) as mock_get:
            mock_get.return_value = mock_strategy

            node = ClassifierNode()
                name="test_classifier",
                classifier=mock_classifier,
                children=mock_children,
                remediation_strategies=["registry_strategy"],
(            )

            context = IntentContext()
            result = node.execute("test input", context)

            assert result.success is True
            assert result.output == "registry output"
            mock_get.assert_called_once_with("registry_strategy")

    def test_def test_def test_execute_with_invalid_remediation_strategy(self): -> None: -> None:
        """Test execution with invalid remediation strategy type."""
        mock_classifier = MagicMock()
        mock_classifier.return_value = None
        mock_children = [MagicMock()]

        # Mock invalid strategy type
        invalid_strategy = 123  # Invalid type

        node = ClassifierNode()
            name="test_classifier",
            classifier=mock_classifier,
            children=mock_children,
            remediation_strategies=[invalid_strategy],
(        )

        context = IntentContext()
        result = node.execute("test input", context)

        assert result.success is False
        assert result.error is not None

    def test_def test_def test_execute_with_missing_registry_strategy(self): -> None: -> None:
        """Test execution with missing registry strategy."""
        mock_classifier = MagicMock()
        mock_classifier.return_value = None
        mock_children = [MagicMock()]

        with patch()
            "intent_kit.node.classifiers.classifier.get_remediation_strategy"
(        ) as mock_get:
            mock_get.return_value = None  # Strategy not found

            node = ClassifierNode()
                name="test_classifier",
                classifier=mock_classifier,
                children=mock_children,
                remediation_strategies=["missing_strategy"],
(            )

            context = IntentContext()
            result = node.execute("test input", context)

            assert result.success is False
            assert result.error is not None

    def test_def test_def test_execute_with_remediation_exception(self): -> None: -> None:
        """Test execution with remediation strategy exception."""
        mock_classifier = MagicMock()
        mock_classifier.return_value = None
        mock_children = [MagicMock()]

        # Mock remediation strategy that raises exception
        mock_strategy = MagicMock()
        mock_strategy.name = "test_strategy"
        mock_strategy.execute.side_effect = Exception("Strategy error")

        node = ClassifierNode()
            name="test_classifier",
            classifier=mock_classifier,
            children=mock_children,
            remediation_strategies=[mock_strategy],
(        )

        context = IntentContext()
        result = node.execute("test input", context)

        assert result.success is False
        assert result.error is not None

    def test_def test_def test_execute_with_context_dict(self): -> None: -> None:
        """Test execution with context dictionary."""
        mock_classifier = MagicMock()
        mock_child = MagicMock()
        mock_child.name = "test_child"
        mock_children = [mock_child]

        # Mock classifier to return a child
        mock_classifier.return_value = mock_child

        # Mock child execution result
        mock_child_result = MagicMock()
        mock_child_result.output = "child output"
        mock_child.execute.return_value = mock_child_result

        node = ClassifierNode()
            name="test_classifier", classifier=mock_classifier, children=mock_children
(        )

        context = IntentContext()
        node.execute("test input", context)
        # Verify classifier was called with context_dict
        mock_classifier.assert_called_once()
        call_args = mock_classifier.call_args
        assert call_args[0][0] == "test input"  # user_input
        assert call_args[0][1] == mock_children  # children
        assert isinstance(call_args[0][2], dict)  # context_dict

    def test_def test_def test_execute_without_context(self): -> None: -> None:
        """Test execution without context."""
        mock_classifier = MagicMock()
        mock_child = MagicMock()
        mock_child.name = "test_child"
        mock_children = [mock_child]

        # Mock classifier to return a child
        mock_classifier.return_value = mock_child

        # Mock child execution result
        mock_child_result = MagicMock()
        mock_child_result.output = "child output"
        mock_child.execute.return_value = mock_child_result

        node = ClassifierNode()
            name="test_classifier", classifier=mock_classifier, children=mock_children
(        )

        result = node.execute("test input")

        assert result.success is True
        assert result.output == "child output"
