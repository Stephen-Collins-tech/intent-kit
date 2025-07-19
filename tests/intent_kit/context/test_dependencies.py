"""
Tests for context dependencies functionality.
"""






    ContextDependencies,
    declare_dependencies,
    validate_context_dependencies,
    merge_dependencies,
    analyze_action_dependencies,
    create_dependency_graph,
    detect_circular_dependencies,
()



class TestContextDependencies:
    """Test cases for ContextDependencies dataclass."""

    def test_def test_def test_init_basic(self): -> None: -> None:
        """Test basic ContextDependencies initialization."""
        inputs = {"user_id", "session_id"}
        outputs = {"result", "status"}
        description = "Test dependencies"

        deps = ContextDependencies()
            inputs=inputs,
            outputs=outputs,
            description=description
(        )

        assert deps.inputs == inputs
        assert deps.outputs == outputs
        assert deps.description == description

    def test_def test_def test_init_empty(self): -> None: -> None:
        """Test ContextDependencies initialization with empty sets."""
        deps = ContextDependencies(inputs=set(), outputs=set())

        assert deps.inputs == set()
        assert deps.outputs == set()
        assert deps.description == ""

    def test_def test_def test_equality(self): -> None: -> None:
        """Test ContextDependencies equality."""
        deps1 = ContextDependencies()
            inputs={"a", "b"},
            outputs={"c"},
            description="Test"
(        )
        deps2 = ContextDependencies()
            inputs={"a", "b"},
            outputs={"c"},
            description="Test"
(        )

        assert deps1 == deps2

    def test_def test_def test_inequality(self): -> None: -> None:
        """Test ContextDependencies inequality."""
        deps1 = ContextDependencies(inputs={"a"}, outputs={"b"})
        deps2 = ContextDependencies(inputs={"a"}, outputs={"c"})

        assert deps1 != deps2


class TestDeclareDependencies:
    """Test cases for declare_dependencies function."""

    def test_def test_def test_declare_dependencies_basic(self): -> None: -> None:
        """Test basic dependency declaration."""
        inputs = {"user_id", "session_id"}
        outputs = {"result"}
        description = "Test dependencies"

        deps = declare_dependencies(inputs, outputs, description)

        assert deps.inputs == inputs
        assert deps.outputs == outputs
        assert deps.description == description

    def test_def test_def test_declare_dependencies_empty(self): -> None: -> None:
        """Test dependency declaration with empty sets."""
        deps = declare_dependencies(set(), set())

        assert deps.inputs == set()
        assert deps.outputs == set()
        assert deps.description == ""

    def test_def test_def test_declare_dependencies_no_description(self): -> None: -> None:
        """Test dependency declaration without description."""
        inputs = {"user_id"}
        outputs = {"result"}

        deps = declare_dependencies(inputs, outputs)

        assert deps.inputs == inputs
        assert deps.outputs == outputs
        assert deps.description == ""


class TestValidateContextDependencies:
    """Test cases for validate_context_dependencies function."""

    def test_def test_def test_validate_dependencies_all_available(self): -> None: -> None:
        """Test validation when all inputs are available."""
        deps = ContextDependencies()
            inputs={"user_id", "session_id"},
            outputs={"result"}
(        )
        context = IntentContext()
        context.set("user_id", "123")
        context.set("session_id", "456")

        result = validate_context_dependencies(deps, context)

        assert result["valid"] is True
        assert result["missing_inputs"] == set()
        assert result["available_inputs"] == {"user_id", "session_id"}
        assert result["warnings"] == []

    def test_def test_def test_validate_dependencies_some_missing(self): -> None: -> None:
        """Test validation when some inputs are missing."""
        deps = ContextDependencies()
            inputs={"user_id", "session_id", "missing_field"},
            outputs={"result"}
(        )
        context = IntentContext()
        context.set("user_id", "123")
        context.set("session_id", "456")

        result = validate_context_dependencies(deps, context)

        assert result["valid"] is True  # Not strict
        assert result["missing_inputs"] == {"missing_field"}
        assert result["available_inputs"] == {"user_id", "session_id"}
        assert len(result["warnings"]) == 1
        assert "Optional context inputs not available" in result["warnings"][0]

    def test_def test_def test_validate_dependencies_strict_mode(self): -> None: -> None:
        """Test validation in strict mode."""
        deps = ContextDependencies()
            inputs={"user_id", "missing_field"},
            outputs={"result"}
(        )
        context = IntentContext()
        context.set("user_id", "123")

        result = validate_context_dependencies(deps, context, strict=True)

        assert result["valid"] is False
        assert result["missing_inputs"] == {"missing_field"}
        assert result["available_inputs"] == {"user_id"}
        assert len(result["warnings"]) == 1
        assert "Missing required context inputs" in result["warnings"][0]

    def test_def test_def test_validate_dependencies_no_inputs(self): -> None: -> None:
        """Test validation with no inputs."""
        deps = ContextDependencies(inputs=set(), outputs={"result"})
        context = IntentContext()

        result = validate_context_dependencies(deps, context)

        assert result["valid"] is True
        assert result["missing_inputs"] == set()
        assert result["available_inputs"] == set()
        assert result["warnings"] == []

    def test_def test_def test_validate_dependencies_empty_context(self): -> None: -> None:
        """Test validation with empty context."""
        deps = ContextDependencies()
            inputs={"user_id", "session_id"},
            outputs={"result"}
(        )
        context = IntentContext()

        result = validate_context_dependencies(deps, context)

        assert result["valid"] is True  # Not strict
        assert result["missing_inputs"] == {"user_id", "session_id"}
        assert result["available_inputs"] == set()
        assert len(result["warnings"]) == 1


class TestMergeDependencies:
    """Test cases for merge_dependencies function."""

    def test_def test_def test_merge_dependencies_basic(self): -> None: -> None:
        """Test basic dependency merging."""
        deps1 = ContextDependencies()
            inputs={"a", "b"},
            outputs={"c"},
            description="First"
(        )
        deps2 = ContextDependencies()
            inputs={"b", "d"},
            outputs={"e"},
            description="Second"
(        )

        merged = merge_dependencies(deps1, deps2)

        assert merged.inputs == {"a", "b", "d"}
        assert merged.outputs == {"c", "e"}
        assert merged.description == "First; Second"

    def test_def test_def test_merge_dependencies_outputs_removed_from_inputs(self): -> None: -> None:
        """Test that outputs are removed from inputs when merging."""
        deps1 = ContextDependencies()
            inputs={"a", "b"},
            outputs={"b"},  # b is both input and output
            description="Test"
(        )
        deps2 = ContextDependencies()
            inputs={"c", "d"},
            outputs={"d"},  # d is both input and output
            description="Test2"
(        )

        merged = merge_dependencies(deps1, deps2)

        # b and d should be removed from inputs since they're outputs
        assert merged.inputs == {"a", "c"}
        assert merged.outputs == {"b", "d"}

    def test_def test_def test_merge_dependencies_empty(self): -> None: -> None:
        """Test merging with empty dependencies."""
        merged = merge_dependencies()

        assert merged.inputs == set()
        assert merged.outputs == set()
        assert merged.description == "Empty dependencies"

    def test_def test_def test_merge_dependencies_single(self): -> None: -> None:
        """Test merging with single dependency."""
        deps = ContextDependencies()
            inputs={"a"},
            outputs={"b"},
            description="Single"
(        )

        merged = merge_dependencies(deps)

        assert merged.inputs == {"a"}
        assert merged.outputs == {"b"}
        assert merged.description == "Single"

    def test_def test_def test_merge_dependencies_no_descriptions(self): -> None: -> None:
        """Test merging dependencies without descriptions."""
        deps1 = ContextDependencies(inputs={"a"}, outputs={"b"})
        deps2 = ContextDependencies(inputs={"c"}, outputs={"d"})

        merged = merge_dependencies(deps1, deps2)

        assert merged.inputs == {"a", "c"}
        assert merged.outputs == {"b", "d"}
        assert merged.description == ""


class TestAnalyzeActionDependencies:
    """Test cases for analyze_action_dependencies function."""

    def test_def test_def test_analyze_action_dependencies_not_callable(self): -> None: -> None:
        """Test analysis of non-callable object."""
        result = analyze_action_dependencies("not_callable")

        assert result is None

    def test_def test_def test_analyze_action_dependencies_with_explicit_deps(self): -> None: -> None:
        """Test analysis of action with explicit dependencies."""
        mock_action = Mock()
        mock_deps = ContextDependencies()
            inputs={"user_id"},
            outputs={"result"}
(        )
        mock_action.context_dependencies = mock_deps

        result = analyze_action_dependencies(mock_action)

        assert result == mock_deps

    def test_def test_def test_analyze_action_dependencies_with_annotations(self): -> None: -> None:
        """Test analysis of action with dependency annotations."""
        # Create a mock that doesn't have context_dependencies attribute
        mock_action = Mock()
        mock_action.__annotations__ = {
            "context_inputs": set,
            "context_outputs": set
        }
        # Set the attributes directly on the mock
        mock_action.context_inputs = {"user_id"}
        mock_action.context_outputs = {"result"}
        # Ensure it doesn't have context_dependencies attribute
        del mock_action.context_dependencies

        result = analyze_action_dependencies(mock_action)

        # The function should return a ContextDependencies object
        assert result is not None
        assert result.inputs == {"user_id"}
        assert result.outputs == {"result"}

    def test_def test_def test_analyze_action_dependencies_no_analysis(self): -> None: -> None:
        """Test analysis when no analysis is possible."""
        def simple_function():
            pass

        result = analyze_action_dependencies(simple_function)

        assert result is None

    def test_def test_def test_analyze_action_dependencies_with_docstring(self): -> None: -> None:
        """Test analysis of action with docstring hints."""
        def action_with_doc():
            """This action reads from context and writes to context."""
            pass

        result = analyze_action_dependencies(action_with_doc)

        # Should return None since docstring analysis is not implemented
        assert result is None


class TestCreateDependencyGraph:
    """Test cases for create_dependency_graph function."""

    def test_def test_def test_create_dependency_graph_basic(self): -> None: -> None:
        """Test basic dependency graph creation."""
        nodes = {
            "node1": ContextDependencies(inputs={"a"}, outputs={"b"}),
            "node2": ContextDependencies(inputs={"b"}, outputs={"c"}),
            "node3": ContextDependencies(inputs={"c"}, outputs={"d"}),
        }

        graph = create_dependency_graph(nodes)

        assert graph["node1"] == {"node2"}  # node2 depends on node1's output'
        assert graph["node2"] == {"node3"}  # node3 depends on node2's output'
        assert graph["node3"] == set()      # node3 has no dependents

    def test_def test_def test_create_dependency_graph_no_dependencies(self): -> None: -> None:
        """Test dependency graph with no dependencies."""
        nodes = {
            "node1": ContextDependencies(inputs={"a"}, outputs={"b"}),
            "node2": ContextDependencies(inputs={"c"}, outputs={"d"}),
        }

        graph = create_dependency_graph(nodes)

        assert graph["node1"] == set()
        assert graph["node2"] == set()

    def test_def test_def test_create_dependency_graph_circular(self): -> None: -> None:
        """Test dependency graph with circular dependencies."""
        nodes = {
            "node1": ContextDependencies(inputs={"b"}, outputs={"a"}),
            "node2": ContextDependencies(inputs={"a"}, outputs={"b"}),
        }

        graph = create_dependency_graph(nodes)

        assert graph["node1"] == {"node2"}
        assert graph["node2"] == {"node1"}

    def test_def test_def test_create_dependency_graph_empty(self): -> None: -> None:
        """Test dependency graph creation with empty nodes."""
        graph = create_dependency_graph({})

        assert graph == {}

    def test_def test_def test_create_dependency_graph_single_node(self): -> None: -> None:
        """Test dependency graph creation with single node."""
        nodes = {
            "node1": ContextDependencies(inputs={"a"}, outputs={"b"}),
        }

        graph = create_dependency_graph(nodes)

        assert graph["node1"] == set()


class TestDetectCircularDependencies:
    """Test cases for detect_circular_dependencies function."""

    def test_def test_def test_detect_circular_dependencies_none(self): -> None: -> None:
        """Test detection when no circular dependencies exist."""
        graph = {
            "node1": {"node2"},
            "node2": {"node3"},
            "node3": set(),
        }

        result = detect_circular_dependencies(graph)

        assert result is None

    def test_def test_def test_detect_circular_dependencies_simple(self): -> None: -> None:
        """Test detection of simple circular dependency."""
        graph = {
            "node1": {"node2"},
            "node2": {"node1"},
        }

        result = detect_circular_dependencies(graph)

        assert result is not None
        assert len(result) >= 2
        assert "node1" in result
        assert "node2" in result

    def test_def test_def test_detect_circular_dependencies_complex(self): -> None: -> None:
        """Test detection of complex circular dependency."""
        graph = {
            "node1": {"node2"},
            "node2": {"node3"},
            "node3": {"node1"},
        }

        result = detect_circular_dependencies(graph)

        assert result is not None
        assert len(result) >= 3
        assert "node1" in result
        assert "node2" in result
        assert "node3" in result

    def test_def test_def test_detect_circular_dependencies_self_loop(self): -> None: -> None:
        """Test detection of self-loop dependency."""
        graph = {
            "node1": {"node1"},
        }

        result = detect_circular_dependencies(graph)

        assert result is not None
        assert len(result) >= 1
        assert "node1" in result

    def test_def test_def test_detect_circular_dependencies_empty(self): -> None: -> None:
        """Test detection with empty graph."""
        result = detect_circular_dependencies({})

        assert result is None

    def test_def test_def test_detect_circular_dependencies_single_node(self): -> None: -> None:
        """Test detection with single node."""
        graph = {
            "node1": set(),
        }

        result = detect_circular_dependencies(graph)

        assert result is None


class TestContextAwareAction:
    """Test cases for ContextAwareAction protocol."""

    def test_def test_def test_context_aware_action_protocol(self): -> None: -> None:
        """Test that a class can implement ContextAwareAction protocol."""
        class TestAction:
            def __init__def __init__def __init__(self): -> None: -> None:
                self.context_dependencies = ContextDependencies()
                    inputs={"user_id"},
                    outputs={"result"}
(                )

            def __call__(self, context, **kwargs) -> None:
                return "result"

        action = TestAction()

        # Should not raise any errors
        assert action.context_dependencies.inputs == {"user_id"}
        assert action.context_dependencies.outputs == {"result"}
        assert callable(action)


class TestIntegration:
    """Integration tests for dependencies functionality."""

    def test_def test_def test_full_workflow(self): -> None: -> None:
        """Test full dependency workflow."""
        # Create dependencies
        deps1 = declare_dependencies()
            inputs={"user_id"},
            outputs={"user_info"},
            description="Get user info"
(        )
        deps2 = declare_dependencies()
            inputs={"user_info"},
            outputs={"result"},
            description="Process user info"
(        )

        # Merge dependencies
        merged = merge_dependencies(deps1, deps2)

        # Create context
        context = IntentContext()
        context.set("user_id", "123")

        # Validate dependencies
        validation = validate_context_dependencies(merged, context)

        assert validation["valid"] is True
        assert validation["missing_inputs"] == set()
        assert validation["available_inputs"] == {"user_id"}

        # Create dependency graph
        nodes = {
            "get_user": deps1,
            "process_user": deps2,
        }
        graph = create_dependency_graph(nodes)

        # Check for circular dependencies
        circular = detect_circular_dependencies(graph)

        assert circular is None
        assert graph["get_user"] == {"process_user"}
        assert graph["process_user"] == set()

    def test_def test_def test_circular_dependency_workflow(self): -> None: -> None:
        """Test workflow with circular dependencies."""
        deps1 = declare_dependencies()
            inputs={"b"},
            outputs={"a"}
(        )
        deps2 = declare_dependencies()
            inputs={"a"},
            outputs={"b"}
(        )

        nodes = {
            "node1": deps1,
            "node2": deps2,
        }
        graph = create_dependency_graph(nodes)

        circular = detect_circular_dependencies(graph)

        assert circular is not None
        assert len(circular) >= 2
