"""Tests for the DAG validation module."""

import pytest
from intent_kit.core.validation import (
    validate_dag_structure,
    _validate_ids,
    _validate_entrypoints,
    _validate_acyclic,
    _find_cycle_dfs,
    _validate_reachability,
    _validate_labels,
)
from intent_kit.core.types import IntentDAG, GraphNode
from intent_kit.core.exceptions import CycleError


class TestValidateDAGStructure:
    """Test cases for validate_dag_structure function."""

    def test_validate_dag_structure_valid(self):
        """Test validation of a valid DAG."""
        dag = IntentDAG()
        dag.nodes = {
            "node1": GraphNode(id="node1", type="classifier", config={}),
            "node2": GraphNode(id="node2", type="action", config={}),
        }
        dag.adj = {"node1": {None: {"node2"}}}
        dag.rev = {"node2": {"node1"}}
        dag.entrypoints = ["node1"]

        issues = validate_dag_structure(dag)
        assert issues == []

    def test_validate_dag_structure_with_producer_labels(self):
        """Test validation with producer labels."""
        dag = IntentDAG()
        dag.nodes = {
            "node1": GraphNode(id="node1", type="classifier", config={}),
            "node2": GraphNode(id="node2", type="action", config={}),
        }
        dag.adj = {"node1": {"success": {"node2"}}}
        dag.rev = {"node2": {"node1"}}
        dag.entrypoints = ["node1"]

        producer_labels = {"node1": {"success"}}

        issues = validate_dag_structure(dag, producer_labels)
        assert issues == []

    def test_validate_dag_structure_with_unreachable_nodes(self):
        """Test validation with unreachable nodes."""
        dag = IntentDAG()
        dag.nodes = {
            "node1": GraphNode(id="node1", type="classifier", config={}),
            "node2": GraphNode(id="node2", type="action", config={}),
            "node3": GraphNode(id="node3", type="action", config={}),  # Unreachable
        }
        dag.adj = {"node1": {None: {"node2"}}}
        dag.rev = {"node2": {"node1"}, "node3": set()}
        dag.entrypoints = ["node1"]

        issues = validate_dag_structure(dag)
        assert len(issues) == 1
        assert "Unreachable nodes: node3" in issues[0]

    def test_validate_dag_structure_with_cycle(self):
        """Test validation with cycle detection."""
        dag = IntentDAG()
        dag.nodes = {
            "node1": GraphNode(id="node1", type="classifier", config={}),
            "node2": GraphNode(id="node2", type="action", config={}),
        }
        dag.adj = {"node1": {None: {"node2"}}, "node2": {None: {"node1"}}}
        dag.rev = {"node1": {"node2"}, "node2": {"node1"}}
        dag.entrypoints = ["node1"]

        with pytest.raises(CycleError):
            validate_dag_structure(dag)

    def test_validate_dag_structure_with_label_issues(self):
        """Test validation with label validation issues."""
        dag = IntentDAG()
        dag.nodes = {
            "node1": GraphNode(id="node1", type="classifier", config={}),
            "node2": GraphNode(id="node2", type="action", config={}),
        }
        dag.adj = {"node1": {"success": {"node2"}}}
        dag.rev = {"node2": {"node1"}}
        dag.entrypoints = ["node1"]

        # Node1 can produce "failure" but has no corresponding edge
        producer_labels = {"node1": {"success", "failure"}}

        issues = validate_dag_structure(dag, producer_labels)
        assert len(issues) == 1
        assert "can produce label 'failure' but has no corresponding edge" in issues[0]


class TestValidateIDs:
    """Test cases for _validate_ids function."""

    def test_validate_ids_valid(self):
        """Test validation of valid IDs."""
        dag = IntentDAG()
        dag.nodes = {
            "node1": GraphNode(id="node1", type="classifier", config={}),
            "node2": GraphNode(id="node2", type="action", config={}),
        }
        dag.adj = {"node1": {None: {"node2"}}}
        dag.rev = {"node2": {"node1"}}
        dag.entrypoints = ["node1"]

        # Should not raise any exception
        _validate_ids(dag)

    def test_validate_ids_missing_entrypoint(self):
        """Test validation with missing entrypoint."""
        dag = IntentDAG()
        dag.nodes = {
            "node1": GraphNode(id="node1", type="classifier", config={}),
        }
        dag.adj = {}
        dag.rev = {}
        dag.entrypoints = ["nonexistent"]

        with pytest.raises(ValueError, match="Entrypoint nonexistent does not exist"):
            _validate_ids(dag)

    def test_validate_ids_missing_edge_source(self):
        """Test validation with missing edge source."""
        dag = IntentDAG()
        dag.nodes = {
            "node2": GraphNode(id="node2", type="action", config={}),
        }
        dag.adj = {"nonexistent": {None: {"node2"}}}
        dag.rev = {"node2": set()}
        dag.entrypoints = []

        with pytest.raises(ValueError, match="Edge source nonexistent does not exist"):
            _validate_ids(dag)

    def test_validate_ids_missing_edge_destination(self):
        """Test validation with missing edge destination."""
        dag = IntentDAG()
        dag.nodes = {
            "node1": GraphNode(id="node1", type="classifier", config={}),
        }
        dag.adj = {"node1": {None: {"nonexistent"}}}
        dag.rev = {}
        dag.entrypoints = []

        with pytest.raises(
            ValueError, match="Edge destination nonexistent does not exist"
        ):
            _validate_ids(dag)

    def test_validate_ids_missing_reverse_edge_destination(self):
        """Test validation with missing reverse edge destination."""
        dag = IntentDAG()
        dag.nodes = {
            "node1": GraphNode(id="node1", type="classifier", config={}),
        }
        dag.adj = {}
        dag.rev = {"nonexistent": {"node1"}}
        dag.entrypoints = []

        with pytest.raises(
            ValueError, match="Reverse edge destination nonexistent does not exist"
        ):
            _validate_ids(dag)

    def test_validate_ids_missing_reverse_edge_source(self):
        """Test validation with missing reverse edge source."""
        dag = IntentDAG()
        dag.nodes = {
            "node2": GraphNode(id="node2", type="action", config={}),
        }
        dag.adj = {}
        dag.rev = {"node2": {"nonexistent"}}
        dag.entrypoints = []

        with pytest.raises(
            ValueError, match="Reverse edge source nonexistent does not exist"
        ):
            _validate_ids(dag)


class TestValidateEntrypoints:
    """Test cases for _validate_entrypoints function."""

    def test_validate_entrypoints_valid(self):
        """Test validation of valid entrypoints."""
        dag = IntentDAG()
        dag.nodes = {
            "node1": GraphNode(id="node1", type="classifier", config={}),
        }
        dag.entrypoints = ["node1"]

        # Should not raise any exception
        _validate_entrypoints(dag)

    def test_validate_entrypoints_empty(self):
        """Test validation with empty entrypoints."""
        dag = IntentDAG()
        dag.nodes = {}
        dag.entrypoints = []

        with pytest.raises(ValueError, match="DAG must have at least one entrypoint"):
            _validate_entrypoints(dag)

    def test_validate_entrypoints_missing_node(self):
        """Test validation with missing entrypoint node."""
        dag = IntentDAG()
        dag.nodes = {
            "node1": GraphNode(id="node1", type="classifier", config={}),
        }
        dag.entrypoints = ["nonexistent"]

        with pytest.raises(ValueError, match="Entrypoint nonexistent does not exist"):
            _validate_entrypoints(dag)


class TestValidateAcyclic:
    """Test cases for _validate_acyclic function."""

    def test_validate_acyclic_valid(self):
        """Test validation of acyclic DAG."""
        dag = IntentDAG()
        dag.nodes = {
            "node1": GraphNode(id="node1", type="classifier", config={}),
            "node2": GraphNode(id="node2", type="action", config={}),
        }
        dag.adj = {"node1": {None: {"node2"}}}
        dag.rev = {"node2": {"node1"}}

        # Should not raise any exception
        _validate_acyclic(dag)

    def test_validate_acyclic_with_cycle(self):
        """Test validation with cycle detection."""
        dag = IntentDAG()
        dag.nodes = {
            "node1": GraphNode(id="node1", type="classifier", config={}),
            "node2": GraphNode(id="node2", type="action", config={}),
        }
        dag.adj = {"node1": {None: {"node2"}}, "node2": {None: {"node1"}}}
        dag.rev = {"node1": {"node2"}, "node2": {"node1"}}

        with pytest.raises(CycleError):
            _validate_acyclic(dag)

    def test_validate_acyclic_self_loop(self):
        """Test validation with self-loop."""
        dag = IntentDAG()
        dag.nodes = {
            "node1": GraphNode(id="node1", type="classifier", config={}),
        }
        dag.adj = {"node1": {None: {"node1"}}}
        dag.rev = {"node1": {"node1"}}

        with pytest.raises(CycleError):
            _validate_acyclic(dag)

    def test_validate_acyclic_complex_cycle(self):
        """Test validation with complex cycle."""
        dag = IntentDAG()
        dag.nodes = {
            "node1": GraphNode(id="node1", type="classifier", config={}),
            "node2": GraphNode(id="node2", type="action", config={}),
            "node3": GraphNode(id="node3", type="action", config={}),
        }
        dag.adj = {
            "node1": {None: {"node2"}},
            "node2": {None: {"node3"}},
            "node3": {None: {"node1"}},
        }
        dag.rev = {
            "node1": {"node3"},
            "node2": {"node1"},
            "node3": {"node2"},
        }

        with pytest.raises(CycleError):
            _validate_acyclic(dag)


class TestFindCycleDFS:
    """Test cases for _find_cycle_dfs function."""

    def test_find_cycle_dfs_simple_cycle(self):
        """Test finding a simple cycle."""
        dag = IntentDAG()
        dag.nodes = {
            "node1": GraphNode(id="node1", type="classifier", config={}),
            "node2": GraphNode(id="node2", type="action", config={}),
        }
        dag.adj = {"node1": {None: {"node2"}}, "node2": {None: {"node1"}}}
        dag.rev = {"node1": {"node2"}, "node2": {"node1"}}

        cycle = _find_cycle_dfs(dag)
        assert len(cycle) >= 2
        assert "node1" in cycle
        assert "node2" in cycle

    def test_find_cycle_dfs_self_loop(self):
        """Test finding a self-loop."""
        dag = IntentDAG()
        dag.nodes = {
            "node1": GraphNode(id="node1", type="classifier", config={}),
        }
        dag.adj = {"node1": {None: {"node1"}}}
        dag.rev = {"node1": {"node1"}}

        cycle = _find_cycle_dfs(dag)
        assert cycle == ["node1", "node1"]

    def test_find_cycle_dfs_no_cycle(self):
        """Test finding cycle in acyclic DAG."""
        dag = IntentDAG()
        dag.nodes = {
            "node1": GraphNode(id="node1", type="classifier", config={}),
            "node2": GraphNode(id="node2", type="action", config={}),
        }
        dag.adj = {"node1": {None: {"node2"}}}
        dag.rev = {"node2": {"node1"}}

        cycle = _find_cycle_dfs(dag)
        assert cycle == []

    def test_find_cycle_dfs_complex_cycle(self):
        """Test finding a complex cycle."""
        dag = IntentDAG()
        dag.nodes = {
            "node1": GraphNode(id="node1", type="classifier", config={}),
            "node2": GraphNode(id="node2", type="action", config={}),
            "node3": GraphNode(id="node3", type="action", config={}),
        }
        dag.adj = {
            "node1": {None: {"node2"}},
            "node2": {None: {"node3"}},
            "node3": {None: {"node1"}},
        }
        dag.rev = {
            "node1": {"node3"},
            "node2": {"node1"},
            "node3": {"node2"},
        }

        cycle = _find_cycle_dfs(dag)
        assert len(cycle) >= 3
        assert "node1" in cycle
        assert "node2" in cycle
        assert "node3" in cycle


class TestValidateReachability:
    """Test cases for _validate_reachability function."""

    def test_validate_reachability_all_reachable(self):
        """Test validation when all nodes are reachable."""
        dag = IntentDAG()
        dag.nodes = {
            "node1": GraphNode(id="node1", type="classifier", config={}),
            "node2": GraphNode(id="node2", type="action", config={}),
        }
        dag.adj = {"node1": {None: {"node2"}}}
        dag.rev = {"node2": {"node1"}}
        dag.entrypoints = ["node1"]

        unreachable = _validate_reachability(dag)
        assert unreachable == []

    def test_validate_reachability_with_unreachable(self):
        """Test validation with unreachable nodes."""
        dag = IntentDAG()
        dag.nodes = {
            "node1": GraphNode(id="node1", type="classifier", config={}),
            "node2": GraphNode(id="node2", type="action", config={}),
            "node3": GraphNode(id="node3", type="action", config={}),  # Unreachable
        }
        dag.adj = {"node1": {None: {"node2"}}}
        dag.rev = {"node2": {"node1"}, "node3": set()}
        dag.entrypoints = ["node1"]

        unreachable = _validate_reachability(dag)
        assert unreachable == ["node3"]

    def test_validate_reachability_multiple_entrypoints(self):
        """Test validation with multiple entrypoints."""
        dag = IntentDAG()
        dag.nodes = {
            "node1": GraphNode(id="node1", type="classifier", config={}),
            "node2": GraphNode(id="node2", type="classifier", config={}),
            "node3": GraphNode(id="node3", type="action", config={}),
        }
        dag.adj = {
            "node1": {None: {"node3"}},
            "node2": {None: {"node3"}},
        }
        dag.rev = {"node3": {"node1", "node2"}}
        dag.entrypoints = ["node1", "node2"]

        unreachable = _validate_reachability(dag)
        assert unreachable == []

    def test_validate_reachability_disconnected_components(self):
        """Test validation with disconnected components."""
        dag = IntentDAG()
        dag.nodes = {
            "node1": GraphNode(id="node1", type="classifier", config={}),
            "node2": GraphNode(id="node2", type="action", config={}),
            "node3": GraphNode(id="node3", type="classifier", config={}),
            "node4": GraphNode(id="node4", type="action", config={}),
        }
        dag.adj = {
            "node1": {None: {"node2"}},
            "node3": {None: {"node4"}},
        }
        dag.rev = {
            "node2": {"node1"},
            "node4": {"node3"},
        }
        dag.entrypoints = ["node1"]

        unreachable = _validate_reachability(dag)
        assert set(unreachable) == {"node3", "node4"}


class TestValidateLabels:
    """Test cases for _validate_labels function."""

    def test_validate_labels_valid(self):
        """Test validation of valid labels."""
        dag = IntentDAG()
        dag.nodes = {
            "node1": GraphNode(id="node1", type="classifier", config={}),
            "node2": GraphNode(id="node2", type="action", config={}),
        }
        dag.adj = {"node1": {"success": {"node2"}}}
        dag.rev = {"node2": {"node1"}}

        producer_labels = {"node1": {"success"}}

        issues = _validate_labels(dag, producer_labels)
        assert issues == []

    def test_validate_labels_missing_node(self):
        """Test validation with node not in producer_labels."""
        dag = IntentDAG()
        dag.nodes = {
            "node1": GraphNode(id="node1", type="classifier", config={}),
        }
        dag.adj = {}

        producer_labels = {"nonexistent": {"success"}}

        issues = _validate_labels(dag, producer_labels)
        assert len(issues) == 1
        assert "Node nonexistent in producer_labels does not exist" in issues[0]

    def test_validate_labels_missing_edge(self):
        """Test validation with missing edge for produced label."""
        dag = IntentDAG()
        dag.nodes = {
            "node1": GraphNode(id="node1", type="classifier", config={}),
            "node2": GraphNode(id="node2", type="action", config={}),
        }
        dag.adj = {"node1": {"success": {"node2"}}}
        dag.rev = {"node2": {"node1"}}

        # Node1 can produce "failure" but has no corresponding edge
        producer_labels = {"node1": {"success", "failure"}}

        issues = _validate_labels(dag, producer_labels)
        assert len(issues) == 1
        assert "can produce label 'failure' but has no corresponding edge" in issues[0]

    def test_validate_labels_ignores_default_edges(self):
        """Test validation ignores default/fall-through edges."""
        dag = IntentDAG()
        dag.nodes = {
            "node1": GraphNode(id="node1", type="classifier", config={}),
            "node2": GraphNode(id="node2", type="action", config={}),
        }
        dag.adj = {"node1": {None: {"node2"}}}  # Default edge
        dag.rev = {"node2": {"node1"}}

        producer_labels = {"node1": {"success"}}

        issues = _validate_labels(dag, producer_labels)
        assert len(issues) == 1
        assert "can produce label 'success' but has no corresponding edge" in issues[0]

    def test_validate_labels_multiple_issues(self):
        """Test validation with multiple label issues."""
        dag = IntentDAG()
        dag.nodes = {
            "node1": GraphNode(id="node1", type="classifier", config={}),
            "node2": GraphNode(id="node2", type="action", config={}),
        }
        dag.adj = {"node1": {"success": {"node2"}}}
        dag.rev = {"node2": {"node1"}}

        producer_labels = {"node1": {"success", "failure", "error"}}

        issues = _validate_labels(dag, producer_labels)
        assert len(issues) == 2
        assert any("failure" in issue for issue in issues)
        assert any("error" in issue for issue in issues)
