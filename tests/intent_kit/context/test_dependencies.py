from intent_kit.context.dependencies import (
    declare_dependencies,
    validate_context_dependencies,
    merge_dependencies,
    analyze_action_dependencies,
    create_dependency_graph,
    detect_circular_dependencies,
)
from intent_kit.context import IntentContext


def test_declare_dependencies():
    deps = declare_dependencies({"a", "b"}, {"c"}, "desc")
    assert deps.inputs == {"a", "b"}
    assert deps.outputs == {"c"}
    assert deps.description == "desc"


def test_validate_context_dependencies_all_present():
    deps = declare_dependencies({"a", "b"}, {"c"})
    ctx = IntentContext()
    ctx.set("a", 1, "test")
    ctx.set("b", 2, "test")
    result = validate_context_dependencies(deps, ctx)
    assert result["valid"] is True
    assert result["missing_inputs"] == set()
    assert result["available_inputs"] == {"a", "b"}


def test_validate_context_dependencies_missing_strict():
    deps = declare_dependencies({"a", "b"}, {"c"})
    ctx = IntentContext()
    ctx.set("a", 1, "test")
    result = validate_context_dependencies(deps, ctx, strict=True)
    assert result["valid"] is False
    assert result["missing_inputs"] == {"b"}
    assert result["available_inputs"] == {"a"}
    assert result["warnings"]


def test_validate_context_dependencies_missing_non_strict():
    deps = declare_dependencies({"a", "b"}, {"c"})
    ctx = IntentContext()
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
