"""
Tests for node factory utilities.
"""





    set_parent_relationships,
    create_action_node,
    create_classifier_node,
    create_splitter_node,
    create_default_classifier,
    action,
    llm_classifier,
    llm_splitter_node,
    rule_splitter_node,
    create_intent_graph,
()








class TestSetParentRelationships:
    """Test parent-child relationship setting."""

    def test_def test_def test_set_parent_relationships(self): -> None: -> None:
        """Test setting parent relationships for children."""
        parent = Mock(spec=TreeNode)
        child1 = Mock(spec=TreeNode)
        child2 = Mock(spec=TreeNode)
        children = cast(List[TreeNode], [child1, child2])

        set_parent_relationships(parent, children)

        assert child1.parent == parent
        assert child2.parent == parent

    def test_def test_def test_set_parent_relationships_empty_list(self): -> None: -> None:
        """Test setting parent relationships with empty list."""
        parent = Mock(spec=TreeNode)
        children = []

        # Should not raise
        set_parent_relationships(parent, children)


class TestCreateActionNode:
    """Test action node creation."""

    def test_def test_def test_create_action_node_basic(self): -> None: -> None:
        """Test creating basic action node."""

        def action_func(name: str) -> str:
            return f"Hello {name}"

        param_schema = {"name": str}
        arg_extractor = Mock()

        node = create_action_node()
            name="greet",
            description="Greet a person",
            action_func=action_func,
            param_schema=param_schema,
            arg_extractor=arg_extractor,
(        )

        assert isinstance(node, ActionNode)
        assert node.name == "greet"
        assert node.description == "Greet a person"
        assert node.param_schema == param_schema
        assert node.action == action_func
        assert node.arg_extractor == arg_extractor

    def test_def test_def test_create_action_node_with_context(self): -> None: -> None:
        """Test creating action node with context inputs/outputs."""

        def action_func(name: str) -> str:
            return f"Hello {name}"

        param_schema = {"name": str}
        arg_extractor = Mock()
        context_inputs = {"user_id"}
        context_outputs = {"greeting_count"}

        node = create_action_node()
            name="greet",
            description="Greet a person",
            action_func=action_func,
            param_schema=param_schema,
            arg_extractor=arg_extractor,
            context_inputs=context_inputs,
            context_outputs=context_outputs,
(        )

        assert node.context_inputs == context_inputs
        assert node.context_outputs == context_outputs

    def test_def test_def test_create_action_node_with_validators(self): -> None: -> None:
        """Test creating action node with validators."""

        def action_func(name: str) -> str:
            return f"Hello {name}"

        def input_validator(params: Dict[str, Any]) -> bool:
            return "name" in params and len(params["name"]) > 0

        def output_validator(result: str) -> bool:
            return len(result) > 0

        param_schema = {"name": str}
        arg_extractor = Mock()

        node = create_action_node()
            name="greet",
            description="Greet a person",
            action_func=action_func,
            param_schema=param_schema,
            arg_extractor=arg_extractor,
            input_validator=input_validator,
            output_validator=output_validator,
(        )

        assert node.input_validator == input_validator
        assert node.output_validator == output_validator

    def test_def test_def test_create_action_node_with_remediation(self): -> None: -> None:
        """Test creating action node with remediation strategies."""

        def action_func(name: str) -> str:
            return f"Hello {name}"

        param_schema = {"name": str}
        arg_extractor = Mock()
        remediation_strategies = cast()
            List[Union[str, RemediationStrategy]], ["retry", "fallback"]
(        )

        node = create_action_node()
            name="greet",
            description="Greet a person",
            action_func=action_func,
            param_schema=param_schema,
            arg_extractor=arg_extractor,
            remediation_strategies=remediation_strategies,
(        )

        assert node.remediation_strategies == remediation_strategies


class TestCreateClassifierNode:
    """Test classifier node creation."""

    def test_def test_def test_create_classifier_node_basic(self): -> None: -> None:
        """Test creating basic classifier node."""

        def classifier_func()
            user_input: str, children: List[TreeNode], context: Dict[str, Any]
(        ) -> TreeNode:
            return children[0]

        child1 = Mock(spec=TreeNode)
        child2 = Mock(spec=TreeNode)
        children = cast(List[TreeNode], [child1, child2])

        node = create_classifier_node()
            name="route",
            description="Route to appropriate child",
            classifier_func=classifier_func,
            children=children,
(        )

        assert isinstance(node, ClassifierNode)
        assert node.name == "route"
        assert node.description == "Route to appropriate child"
        assert node.classifier == classifier_func
        assert node.children == children

        # Check parent relationships
        assert child1.parent == node
        assert child2.parent == node

    def test_def test_def test_create_classifier_node_with_remediation(self): -> None: -> None:
        """Test creating classifier node with remediation strategies."""

        def classifier_func()
            user_input: str, children: List[TreeNode], context: Dict[str, Any]
(        ) -> TreeNode:
            return children[0]

        child1 = Mock(spec=TreeNode)
        children = cast(List[TreeNode], [child1])
        remediation_strategies = cast()
            List[Union[str, RemediationStrategy]], ["retry", "fallback"]
(        )

        node = create_classifier_node()
            name="route",
            description="Route to appropriate child",
            classifier_func=classifier_func,
            children=children,
            remediation_strategies=remediation_strategies,
(        )

        assert node.remediation_strategies == remediation_strategies


class TestCreateSplitterNode:
    """Test splitter node creation."""

    def test_def test_def test_create_splitter_node_basic(self): -> None: -> None:
        """Test creating basic splitter node."""

        def splitter_func(user_input: str, debug: bool = False):
            return []

        child1 = Mock(spec=TreeNode)
        child2 = Mock(spec=TreeNode)
        children = cast(List[TreeNode], [child1, child2])

        node = create_splitter_node()
            name="split",
            description="Split input into multiple chunks",
            splitter_func=splitter_func,
            children=children,
(        )

        assert isinstance(node, SplitterNode)
        assert node.name == "split"
        assert node.description == "Split input into multiple chunks"
        assert node.splitter_function == splitter_func
        assert node.children == children

        # Check parent relationships
        assert child1.parent == node
        assert child2.parent == node

    def test_def test_def test_create_splitter_node_with_llm_client(self): -> None: -> None:
        """Test creating splitter node with LLM client."""

        def splitter_func(user_input: str, debug: bool = False):
            return []

        child1 = Mock(spec=TreeNode)
        children = cast(List[TreeNode], [child1])
        llm_client = Mock()

        node = create_splitter_node()
            name="split",
            description="Split input into multiple chunks",
            splitter_func=splitter_func,
            children=children,
            llm_client=llm_client,
(        )

        assert node.llm_client == llm_client


class TestCreateDefaultClassifier:
    """Test default classifier creation."""

    def test_def test_def test_create_default_classifier(self): -> None: -> None:
        """Test creating default classifier."""
        classifier_func = create_default_classifier()

        child1 = Mock(spec=TreeNode)
        child2 = Mock(spec=TreeNode)
        children = cast(List[TreeNode], [child1, child2])

        result = classifier_func("test input", children, {})
        assert result == child1

    def test_def test_def test_create_default_classifier_empty_children(self): -> None: -> None:
        """Test default classifier with empty children list."""
        classifier_func = create_default_classifier()
        children = []

        result = classifier_func("test input", children, {})
        assert result is None


class TestActionFactory:
    """Test action factory function."""

    @patch("intent_kit.utils.node_factory.create_arg_extractor")
    @patch("intent_kit.utils.node_factory.create_action_node")
    def test_action_basic(self, mock_create_action_node, mock_create_arg_extractor) -> None:
        """Test basic action factory."""

        def action_func(name: str) -> str:
            return f"Hello {name}"

        param_schema = {"name": str}
        mock_extractor = Mock()
        mock_create_arg_extractor.return_value = mock_extractor
        mock_node = Mock(spec=ActionNode)
        mock_create_action_node.return_value = mock_node

        result = action()
            name="greet",
            description="Greet a person",
            action_func=action_func,
            param_schema=param_schema,
(        )

        mock_create_arg_extractor.assert_called_once_with()
            param_schema=param_schema,
            llm_config=None,
            extraction_prompt=None,
            node_name="greet",
(        )
        mock_create_action_node.assert_called_once_with()
            name="greet",
            description="Greet a person",
            action_func=action_func,
            param_schema=param_schema,
            arg_extractor=mock_extractor,
            context_inputs=None,
            context_outputs=None,
            input_validator=None,
            output_validator=None,
            remediation_strategies=None,
(        )
        assert result == mock_node

    @patch("intent_kit.utils.node_factory.create_arg_extractor")
    @patch("intent_kit.utils.node_factory.create_action_node")
    def test_action_with_llm_config()
        self, mock_create_action_node, mock_create_arg_extractor
(    ):
        """Test action factory with LLM config."""

        def action_func(name: str) -> str:
            return f"Hello {name}"

        param_schema = {"name": str}
        llm_config = {"model": "google/gemma-3-27b-it"}
        mock_extractor = Mock()
        mock_create_arg_extractor.return_value = mock_extractor
        mock_node = Mock(spec=ActionNode)
        mock_create_action_node.return_value = mock_node

        result = action()
            name="greet",
            description="Greet a person",
            action_func=action_func,
            param_schema=param_schema,
            llm_config=llm_config,
(        )

        mock_create_arg_extractor.assert_called_once_with()
            param_schema=param_schema,
            llm_config=llm_config,
            extraction_prompt=None,
            node_name="greet",
(        )
        assert result == mock_node

    @patch("intent_kit.utils.node_factory.create_arg_extractor")
    @patch("intent_kit.utils.node_factory.create_action_node")
    def test_action_with_extraction_prompt()
        self, mock_create_action_node, mock_create_arg_extractor
(    ):
        """Test action factory with extraction prompt."""

        def action_func(name: str) -> str:
            return f"Hello {name}"

        param_schema = {"name": str}
        extraction_prompt = "Extract the name from the input"
        mock_extractor = Mock()
        mock_create_arg_extractor.return_value = mock_extractor
        mock_node = Mock(spec=ActionNode)
        mock_create_action_node.return_value = mock_node

        result = action()
            name="greet",
            description="Greet a person",
            action_func=action_func,
            param_schema=param_schema,
            extraction_prompt=extraction_prompt,
(        )

        mock_create_arg_extractor.assert_called_once_with()
            param_schema=param_schema,
            llm_config=None,
            extraction_prompt=extraction_prompt,
            node_name="greet",
(        )
        assert result == mock_node


class TestClassifierFactory:
    """Test classifier factory function."""

    @patch("intent_kit.utils.node_factory.create_classifier_node")
    def test_llm_classifier_basic(self, mock_create_classifier_node) -> None:
        """Test basic LLM classifier factory."""
        child1 = Mock(spec=TreeNode)
        child1.name = "child1"
        child2 = Mock(spec=TreeNode)
        child2.name = "child2"
        children = cast(List[TreeNode], [child1, child2])
        llm_config = {"model": "google/gemma-3-27b-it"}
        mock_node = Mock(spec=ClassifierNode)
        mock_create_classifier_node.return_value = mock_node

        # Test that the function works correctly
        result = llm_classifier()
            name="route",
            children=children,
            llm_config=llm_config,
(        )

        # Verify the result is a classifier node
        assert result is not None


class TestLLMClassifierFactory:
    """Test LLM classifier factory function."""

    @patch("intent_kit.utils.node_factory.create_llm_classifier")
    @patch("intent_kit.utils.node_factory.create_classifier_node")
    def test_llm_classifier_basic()
        self, mock_create_classifier_node, mock_create_llm_classifier
(    ):
        """Test basic LLM classifier factory."""
        child1 = Mock(spec=TreeNode)
        child1.name = "child1"
        child2 = Mock(spec=TreeNode)
        child2.name = "child2"
        children = cast(List[TreeNode], [child1, child2])
        llm_config = {"model": "google/gemma-3-27b-it"}
        mock_classifier_func = Mock()
        mock_create_llm_classifier.return_value = mock_classifier_func
        mock_node = Mock(spec=ClassifierNode)
        mock_create_classifier_node.return_value = mock_node

        result = llm_classifier()
            name="route",
            children=children,
            llm_config=llm_config,
(        )

        mock_create_llm_classifier.assert_called_once_with()
            llm_config,
            "You are an intent classifier. Given a user input, select the most appropriate intent from the available options.\n\nUser Input: {user_input}\n\nAvailable Intents:\n{node_descriptions}\n\n{context_info}\n\nInstructions:\n- Analyze the user input carefully\n- Consider the available context information when making your decision\n- Select the intent that best matches the user's request\n- Return only the number ()'
(                1-{num_nodes}) corresponding to your choice\n- If no intent matches, return 0\n\nYour choice (number only):",            ["child1", "child2"],
(        )
        mock_create_classifier_node.assert_called_once_with()
            name="route",
            description="",
            classifier_func=mock_classifier_func,
            children=children,
            remediation_strategies=None,
(        )
        assert result == mock_node

    @patch("intent_kit.utils.node_factory.create_llm_classifier")
    @patch("intent_kit.utils.node_factory.create_classifier_node")
    def test_llm_classifier_with_prompt()
        self, mock_create_classifier_node, mock_create_llm_classifier
(    ):
        """Test LLM classifier factory with custom prompt."""
        child1 = Mock(spec=TreeNode)
        child1.name = "child1"
        children = cast(List[TreeNode], [child1])
        llm_config = {"model": "google/gemma-3-27b-it"}
        classification_prompt = "Custom classification prompt"
        mock_classifier_func = Mock()
        mock_create_llm_classifier.return_value = mock_classifier_func
        mock_node = Mock(spec=ClassifierNode)
        mock_create_classifier_node.return_value = mock_node

        result = llm_classifier()
            name="route",
            children=children,
            llm_config=llm_config,
            classification_prompt=classification_prompt,
(        )

        mock_create_llm_classifier.assert_called_once_with()
            llm_config, classification_prompt, ["child1"]
(        )
        assert result == mock_node


class TestLLMSplitterNodeFactory:
    """Test LLM splitter node factory function."""

    @patch("intent_kit.utils.node_factory.create_splitter_node")
    def test_llm_splitter_node_basic(self, mock_create_splitter_node) -> None:
        """Test basic LLM splitter node factory."""
        child1 = Mock(spec=TreeNode)
        child2 = Mock(spec=TreeNode)
        children = cast(List[TreeNode], [child1, child2])
        llm_config = {"model": "google/gemma-3-27b-it", "llm_client": Mock()}
        mock_node = Mock(spec=SplitterNode)
        mock_create_splitter_node.return_value = mock_node

        # result = llm_splitter_node()
        llm_splitter_node()
            name="split",
            children=children,
            llm_config=llm_config,
(        )

        mock_create_splitter_node.assert_called_once()
        call_args = mock_create_splitter_node.call_args
        assert call_args[1]["name"] == "split"
        assert call_args[1]["children"] == children
        # The llm_client should be created from the llm_config
        assert call_args[1]["llm_client"] is not None


class TestRuleSplitterNodeFactory:
    """Test rule splitter node factory function."""

    @patch("intent_kit.utils.node_factory.create_splitter_node")
    def test_rule_splitter_node_basic(self, mock_create_splitter_node) -> None:
        """Test basic rule splitter node factory."""
        child1 = Mock(spec=TreeNode)
        child2 = Mock(spec=TreeNode)
        children = cast(List[TreeNode], [child1, child2])
        mock_node = Mock(spec=SplitterNode)
        mock_create_splitter_node.return_value = mock_node

        result = rule_splitter_node()
            name="split",
            children=children,
(        )

        mock_create_splitter_node.assert_called_once()
        call_args = mock_create_splitter_node.call_args
        assert call_args[1]["name"] == "split"
        assert call_args[1]["children"] == children
        assert call_args[1]["splitter_func"] is not None
        assert result == mock_node


class TestCreateIntentGraph:
    """Test intent graph creation."""

    @patch("intent_kit.builders.IntentGraphBuilder")
    def test_create_intent_graph(self, mock_intent_graph_builder_class) -> None:
        """Test creating intent graph."""
        root_node = Mock(spec=TreeNode)
        mock_builder = Mock()
        mock_graph = Mock(spec=IntentGraph)
        mock_intent_graph_builder_class.return_value = mock_builder
        mock_builder.root.return_value = mock_builder
        mock_builder.build.return_value = mock_graph

        result = create_intent_graph(root_node)

        # Check that IntentGraphBuilder was used correctly
        mock_intent_graph_builder_class.assert_called_once()
        mock_builder.root.assert_called_once_with(root_node)
        mock_builder.build.assert_called_once()
        assert result == mock_graph
