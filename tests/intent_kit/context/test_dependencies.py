from intent_kit.context.dependencies import (
    declare_dependencies,
    validate_context_dependencies,
    merge_dependencies,
    analyze_action_dependencies,
    create_dependency_graph,
    detect_circular_dependencies,
    ContextDependencies,
)
from intent_kit.context import Context


def test_declare_dependencies():
    deps = declare_dependencies({"a", "b"}, {"c"}, "desc")
    assert deps.inputs == {"a", "b"}
    assert deps.outputs == {"c"}
    assert deps.description == "desc"


def test_validate_context_dependencies_all_present():
    deps = declare_dependencies({"a", "b"}, {"c"})
    ctx = Context()
    ctx.set("a", 1, "test")
    ctx.set("b", 2, "test")
    result = validate_context_dependencies(deps, ctx)
    assert result["valid"] is True
    assert result["missing_inputs"] == set()
    assert result["available_inputs"] == {"a", "b"}


def test_validate_context_dependencies_missing_strict():
    deps = declare_dependencies({"a", "b"}, {"c"})
    ctx = Context()
    ctx.set("a", 1, "test")
    result = validate_context_dependencies(deps, ctx, strict=True)
    assert result["valid"] is False
    assert result["missing_inputs"] == {"b"}
    assert result["available_inputs"] == {"a"}
    assert result["warnings"]


def test_validate_context_dependencies_missing_non_strict():
    deps = declare_dependencies({"a", "b"}, {"c"})
    ctx = Context()
    ctx.set("a", 1, "test")
    result = validate_context_dependencies(deps, ctx, strict=False)
    assert result["valid"] is True
    assert result["missing_inputs"] == {"b"}
    assert result["available_inputs"] == {"a"}
    assert result["warnings"]


def test_merge_dependencies():
    d1 = declare_dependencies({"a", "b"}, {"c"}, "d1")
    d2 = declare_dependencies({"b", "d"}, {"e"}, "d2")
    merged = merge_dependencies(d1, d2)
    assert merged.inputs == {"a", "b", "d"} - {"c", "e"}
    assert merged.outputs == {"c", "e"}
    assert "d1" in merged.description and "d2" in merged.description


def test_analyze_action_dependencies_explicit():
    class Dummy:
        context_dependencies = declare_dependencies({"a"}, {"b"}, "desc")

    deps = analyze_action_dependencies(Dummy())
    assert deps is not None
    assert deps.inputs == {"a"}
    assert deps.outputs == {"b"}


def test_analyze_action_dependencies_none():
    def dummy():
        pass

    assert analyze_action_dependencies(dummy) is None


def test_create_dependency_graph():
    nodes = {
        "A": declare_dependencies({"x"}, {"y"}),
        "B": declare_dependencies({"y"}, {"z"}),
        "C": declare_dependencies({"z"}, {"w"}),
    }
    graph = create_dependency_graph(nodes)
    assert graph["A"] == {"B"}
    assert graph["B"] == {"C"}
    assert graph["C"] == set()


def test_detect_circular_dependencies_none():
    graph = {"A": {"B"}, "B": {"C"}, "C": set()}
    assert detect_circular_dependencies(graph) is None


def test_detect_circular_dependencies_cycle():
    graph = {"A": {"B"}, "B": {"C"}, "C": {"A"}}
    cycle = detect_circular_dependencies(graph)
    assert cycle is not None
    assert set(cycle) == {"A", "B", "C"}


# Tests for ContextAwareAction protocol methods
class MockContextAwareAction:
    """Mock implementation of ContextAwareAction protocol for testing."""

    def __init__(self, inputs=None, outputs=None, description=""):
        self._deps = ContextDependencies(
            inputs=inputs or set(), outputs=outputs or set(), description=description
        )

    @property
    def context_dependencies(self) -> ContextDependencies:
        """Return the context dependencies for this action."""
        return self._deps

    def __call__(self, context: Context, **kwargs):
        """Execute the action with context access."""
        # Mock implementation that reads from context and writes back
        result = {}
        for key in self._deps.inputs:
            if context.has(key):
                result[key] = context.get(key)

        # Write outputs to context
        for key in self._deps.outputs:
            context.set(key, f"processed_{key}", modified_by="mock_action")

        return result


def test_context_aware_action_context_dependencies():
    """Test the context_dependencies property of ContextAwareAction."""
    action = MockContextAwareAction(
        inputs={"user_id", "preferences"}, outputs={"result"}, description="Test action"
    )

    deps = action.context_dependencies
    assert isinstance(deps, ContextDependencies)
    assert deps.inputs == {"user_id", "preferences"}
    assert deps.outputs == {"result"}
    assert deps.description == "Test action"


def test_context_aware_action_call():
    """Test the __call__ method of ContextAwareAction."""
    action = MockContextAwareAction(
        inputs={"user_id", "name"}, outputs={"processed_result"}
    )

    context = Context()
    context.set("user_id", "123", modified_by="test")
    context.set("name", "John", modified_by="test")

    result = action(context, extra_param="value")

    # Check that inputs were read
    assert result["user_id"] == "123"
    assert result["name"] == "John"

    # Check that outputs were written to context
    assert context.get("processed_result") == "processed_processed_result"


def test_context_aware_action_call_with_missing_inputs():
    """Test ContextAwareAction.__call__ with missing context inputs."""
    action = MockContextAwareAction(
        inputs={"user_id", "missing_field"}, outputs={"result"}
    )

    context = Context()
    context.set("user_id", "123", modified_by="test")

    result = action(context)

    # Should still work, just with None for missing field
    assert result["user_id"] == "123"
    assert "missing_field" not in result or result["missing_field"] is None


def test_context_aware_action_call_empty_dependencies():
    """Test ContextAwareAction.__call__ with empty dependencies."""
    action = MockContextAwareAction()

    context = Context()
    result = action(context)

    assert result == {}
    # No outputs should be written
    assert len(context.keys()) == 0


def test_context_aware_action_protocol_compliance():
    """Test that MockContextAwareAction properly implements the protocol."""
    action = MockContextAwareAction()

    # Should have the required property
    assert hasattr(action, "context_dependencies")
    assert isinstance(action.context_dependencies, ContextDependencies)

    # Should be callable with context
    context = Context()
    result = action(context)
    assert isinstance(result, dict)
