# TASKS.md — Refactor **intent-kit** from Trees to DAGs (pre-v1, no back-compat)

## ✅ Completed Milestones: 0, 1, 2, 3, 4, 5, 6, 7 ✅

## Ground rules

* No `parent`/`children` in any code or JSON.
* Edges are first-class; labels optional (`null` means default/fall-through).
* Multiple entrypoints supported.
* Deterministic traversal; hard fail on cycles.
* Fan-out and fan-in are supported.
* Context propagation via immutable patches with deterministic merging.
* Tight tests, clear docs, observable execution.

---

## Deliverables

* ✅ `intent_kit/core`: new DAG primitives, traversal, validation, loader.
* ✅ Nodes updated to return `ExecutionResult(next_edges=[...])`.
* ✅ JSON schema switched to `{entrypoints, nodes, edges}`.
* ✅ Example graphs + README snippets.
* ✅ Pytest suite: traversal, validation, fan-out/fan-in, remediation.
* ✅ Logging/metrics for per-edge hops.

---

## Milestone 0 — Repo hygiene ✅

* [x] Create feature branch: `feature/dag-core`.
* [x] Enable `pytest -q` in CI (or keep existing).
* [x] Add `ruff`/`black` config (if not present).
* [x] Protect branch with required checks.

**Done when:** CI runs on branch and fails if tests fail or lints fail.

---

## Milestone 1 — Core DAG types ✅

**Files:** `intent_kit/core/graph.py`

* [x] Define `GraphNode` dataclass:

  * `id: str`, `type: str`, `config: dict = {}`.
* [x] Define `IntentDAG` dataclass:

  * `nodes: dict[str, GraphNode]`
  * `adj: dict[str, dict[str|None, set[str]]]` (outgoing)
  * `rev: dict[str, set[str]]` (incoming)
  * `entrypoints: list[str]`
* [x] Provide helper methods:

  * [x] `add_node(id, type, **config) -> GraphNode`
  * [x] `add_edge(src, dst, label: str|None) -> None`
  * [x] `freeze() -> None` (optionally make sets immutable to catch mutation bugs)

**Acceptance:**

* [x] Type hints pass; basic import sanity test runs.
* [x] Adding nodes/edges produces expected `adj/rev`.

---

## Milestone 2 — Node execution interface ✅

**Files:** `intent_kit/core/node_iface.py`

* [x] Define `ExecutionResult`:

  * `data: Any = None`
  * `next_edges: list[str]|None = None`
  * `terminate: bool = False`
  * `metrics: dict = {}`
  * `context_patch: dict = {}`
  * [x] Provide `merge_metrics(other: dict)`.
* [x] Define `NodeProtocol` protocol/ABC:

  * `execute(user_input: str, ctx: "Context") -> ExecutionResult`

**Acceptance:**

* [x] Stub implementation compiles; example node can return `next_edges`.

---

## Milestone 3 — DAG loader (JSON → `IntentDAG`) ✅

**Files:** `intent_kit/core/loader.py`

* [x] Define JSON contract:

```json
{
  "entrypoints": ["rootA"],
  "nodes": {
    "rootA": {"type": "classifier", "config": {}},
    "wx":    {"type": "action",     "config": {}}
  },
  "edges": [
    {"from": "rootA", "to": "wx", "label": "weather"}
  ]
}
```

* [x] Implement `load_dag(obj: dict) -> IntentDAG`.
* [x] Validate presence/shape of `entrypoints`, `nodes`, `edges` (but leave cycle checks to validator).
* [x] Factory hook: `resolve_impl(node: GraphNode) -> NodeProtocol` (DI point; wire later).

**Acceptance:**

* [x] Loading a minimal JSON yields `IntentDAG` with correct adjacency.

---

## Milestone 4 — Validation (strict) ✅

**Files:** `intent_kit/core/validate.py`

* [x] `validate_ids(dag)` — all ref’d ids exist.
* [x] `validate_acyclic(dag)` — DFS/Kahn; raise `CycleError` with path.
* [x] `validate_entrypoints(dag)` — non-empty list; every entrypoint exists.
* [x] `validate_reachability(dag)` — compute reachable from entrypoints; list unreachable.
* [x] `validate_labels(dag, producer_labels: dict[node_id, set[label]])` (optional lint):

  * If a node emits labels (declared by node type), ensure those labels exist on `adj[src]`.
  * Classifiers must emit explicit labels (no default `null`).
  * Reserved labels: `"error"` for error routing, `"done"` for terminal convenience.
* [x] `validate(dag)` orchestrator; returns issues or raises.

**Acceptance:**

* [x] Unit tests for: good graph, cycle, bad id, no entrypoints, unreachable node.

---

## Milestone 5 — Traversal engine ✅

**Files:** `intent_kit/core/traversal.py`

* [x] `run_dag(dag: IntentDAG, ctx, user_input: str) -> tuple[ExecutionResult, dict]`

  * Worklist (BFS) starting from `entrypoints`.
  * Track `seen_steps: set[tuple[node_id, label]]` to avoid re-enqueue of same labeled hop.
  * Aggregate `metrics` across node results.
  * Respect `terminate=True` (stop entire traversal).
  * If `next_edges` empty or `None`, do not enqueue children.
  * **Context merging**: Apply `context_patch` from each node, merge deterministically (last-writer-wins by BFS order).
  * **Error handling**: Catch `NodeError`, apply error context patch, route via `"error"` edge if exists, else stop.
  * **Memoization**: Optional per-node memoization using `(node_id, context_hash, input_hash)` key.
* [x] Deterministic behavior:

  * Stable queue order by insertion (entrypoints order preserved).
* [x] Hard caps:

  * [x] `max_steps` (configurable; default e.g., 1000).
  * [x] `max_fanout_per_node` (default e.g., 16).
  * On exceed → raise `TraversalLimitError`.

**Acceptance:**

* [x] Tests: linear path, fan-out, fan-in, early terminate, limits enforced.

---

## Milestone 6 — Implementation resolver (DI) ✅

**Files:** `intent_kit/core/registry.py`

* [x] `NodeRegistry` mapping `type` → class implementing `NodeProtocol`.
* [x] `resolve_impl(node: GraphNode) -> NodeProtocol` using registry with fallback error.
* [x] Decorator `@register_node("type")`.

**Acceptance:**

* [x] Register two demo nodes; traversal uses them successfully.

---

## Milestone 7 — Update built-in nodes to DAG contract ✅

**Files:** `intent_kit/nodes/**`

* [x] Replace any tree-era returns with `ExecutionResult(next_edges=[...], context_patch={...})`.
* [x] Ensure classifiers return explicit label(s) (strings) that match outgoing edge labels (no default `null`).
* [x] Ensure actions set `terminate=True` when they represent terminal states (if applicable).
* [x] Ensure remediation nodes expose `"resume"` (or chosen label) if intended.
* [x] Add `context_merge_decl` and `memoize` config options where appropriate.

**Acceptance:**

* [x] All built-in nodes compile and pass minimal smoke tests with the new interface.
* [x] Created new DAG nodes (`DAGActionNode`, `DAGClassifierNode`) that implement NodeProtocol directly.
* [x] Removed all tree-era concepts (children, parent) from DAG nodes.
* [x] Factory functions registered with NodeRegistry for DAG node types.

---

## Milestone 8 — Logging & metrics

**Files:** `intent_kit/runtime/logging.py`, `intent_kit/runtime/metrics.py`

* [ ] Per-hop log record: `{from, label, to, node_type, duration_ms, tokens, cost, success, error?, context_patch?}`.
* [ ] Execution trace collector: ordered list of hops with context merge history.
* [ ] Aggregation utilities: sum tokens/cost, count node invocations, context conflict detection.
* [ ] Hook traversal to emit logs; allow injection of logger for tests.

**Acceptance:**

* [ ] Running an example produces a readable trace; metrics totals are correct.

---

## Milestone 9 — Example graphs

**Files:** `intent_kit/examples/*.json`

* [ ] `demo_weather_payment.json` — classifier routes to two actions, then joins to summarize.
* [ ] `demo_shared_remediation.json` — two actions share a remediation node with context merging.
* [ ] `demo_multiple_entrypoints.json` — chat vs API entrypoints converge to router with fan-in.
* [ ] `demo_fanout_fanin.json` — branch to A/B then converge with context patch merging.

**Acceptance:**

* [ ] `pytest` examples test loads + validates + traverses; traces show expected order.

---

## Milestone 10 — Pytest suite

**Files:** `tests/test_loader.py`, `tests/test_validate.py`, `tests/test_traversal.py`, `tests/test_nodes.py`

**Loader**

* [ ] Loads minimal JSON, complex JSON.
* [ ] Errors when missing keys or bad shapes.

**Validate**

* [ ] Detects cycles with explicit cycle path in message.
* [ ] Detects unreachable nodes.
* [ ] Fails when entrypoints missing.
* [ ] Passes on valid graphs.

**Traversal**

* [ ] Linear path executes all nodes once.
* [ ] Fan-out executes both branches; fan-in merges without duplicates.
* [ ] Early terminate stops processing.
* [ ] Limits (max\_steps, max\_fanout) trigger exceptions.
* [ ] Deterministic order across runs.
* [ ] Context patches merge correctly in fan-in scenarios.
* [ ] Error routing via `"error"` edges works as expected.
* [ ] Memoization prevents duplicate node executions.

**Nodes**

* [ ] Classifier emits correct labels.
* [ ] Remediation path taken on simulated error.
* [ ] Context patches are applied and merged correctly.
* [ ] Memoization works for repeated node executions.

**Acceptance:**

* [ ] `pytest -q` green; coverage for `core` ≥ 85%.

---

## Milestone 11 — Developer ergonomics

**Files:** `intent_kit/core/builder.py`

* [ ] Fluent builder for programmatic graphs:

  * `g = GraphBuilder().entrypoints("root").node("root","classifier").edge("root","wx","weather")...`
* [ ] `GraphBuilder.build() -> IntentDAG` + `validate(dag)`.

**Acceptance:**

* [ ] Example using builder matches JSON example behavior.

---

## Milestone 12 — CLI (optional but useful)

**Files:** `intent_kit/cli.py`

* [ ] `intent-kit validate FILE.json`
* [ ] `intent-kit run FILE.json --input "..." --trace`
* [ ] `--max-steps`, `--fanout-cap` flags.
* [ ] Exit codes: 0 success, non-zero on validation/traversal errors.

**Acceptance:**

* [ ] Manual runs show trace and metrics. CI smoke test executes CLI on example.

---

## Milestone 13 — Documentation updates

**Files:** `README.md`, `docs/dag.md`

* [ ] **README**:

  * Replace tree language with DAG concepts.
  * Show JSON schema (`entrypoints`, `nodes`, `edges`) with context merging examples.
  * 30-second demo snippet with fan-in/fan-out patterns.
* [ ] **docs/dag.md**:

  * Why DAG vs Tree.
  * Patterns: shared remediation, fan-out/fan-in, multiple entrypoints, terminate-and-restart (clarify) without cycles.
  * Context merging strategies and conflict resolution.
  * Error handling and routing patterns.
  * ASCII diagrams.

**Acceptance:**

* [ ] Docs build; internal links valid; examples runnable.

---

## Milestone 14 — Removal of legacy code

* [ ] Delete `parent`/`children` fields and all tree traversal code.
* [ ] Remove/rename any “Tree\*” modules.
* [ ] Update imports throughout.

**Acceptance:**

* [ ] Ripgrep for `children`, `parent`, `Tree` returns nothing meaningful.
* [ ] All tests still green.

---

## Milestone 15 — Final polish

* [ ] Add type guards and defensive errors with actionable messages.
* [ ] Ensure exceptions include node ids and labels for debugging.
* [ ] Ensure logs redact sensitive data if any.
* [ ] Pin dependencies; bump version `0.x` with CHANGELOG.

**Acceptance:**

* [ ] Dry run with examples yields clean, readable traces; no TODOs in code.

---

## Reference interfaces (copy/paste)

```python
# intent_kit/core/graph.py
from dataclasses import dataclass, field
from typing import Dict, Set, Optional

EdgeLabel = Optional[str]

@dataclass
class GraphNode:
    id: str
    type: str
    config: dict = field(default_factory=dict)

@dataclass
class IntentDAG:
    nodes: Dict[str, GraphNode] = field(default_factory=dict)
    adj: Dict[str, Dict[EdgeLabel, Set[str]]] = field(default_factory=dict)
    rev: Dict[str, Set[str]] = field(default_factory=dict)
    entrypoints: list[str] = field(default_factory=list)
```

```python
# intent_kit/core/node_iface.py
from typing import Any, Optional, List, Dict, Protocol

class ExecutionResult:
    def __init__(self, data: Any=None, next_edges: Optional[List[str]]=None,
                 terminate: bool=False, metrics: Optional[Dict]=None, context_patch: Optional[Dict]=None):
        self.data = data
        self.next_edges = next_edges
        self.terminate = terminate
        self.metrics = metrics or {}
        self.context_patch = context_patch or {}

class NodeProtocol(Protocol):
    def execute(self, user_input: str, ctx: "Context") -> ExecutionResult: ...
```

```python
# intent_kit/core/traversal.py
from collections import deque
from time import perf_counter

class TraversalLimitError(RuntimeError): ...
class NodeError(RuntimeError): ...
class TraversalError(RuntimeError): ...
class ContextConflictError(RuntimeError): ...

def run_dag(dag, ctx, user_input, max_steps=1000, max_fanout_per_node=16, resolve_impl=None):
    q = deque(dag.entrypoints)
    seen = set()  # (node_id, label)
    steps = 0
    last = None
    totals = {}
    context_patches = {}  # node_id -> merged context patch

    while q:
        nid = q.popleft()
        steps += 1
        if steps > max_steps:
            raise TraversalLimitError("Exceeded max_steps")

        node = dag.nodes[nid]
        impl = resolve_impl(node)
        
        # Apply merged context patch for this node
        if nid in context_patches:
            ctx.update(context_patches[nid])
        
        t0 = perf_counter()
        try:
            res = impl.execute(user_input, ctx)
        except NodeError as e:
            # Error handling: apply error context, route via "error" edge if exists
            error_patch = {"last_error": str(e), "error_node": nid}
            if "error" in dag.adj.get(nid, {}):
                # Route to error handler
                for error_target in dag.adj[nid]["error"]:
                    step = (error_target, "error")
                    if step not in seen:
                        seen.add(step)
                        q.append(error_target)
                        context_patches[error_target] = error_patch
            else:
                # Stop traversal
                raise TraversalError(f"Node {nid} failed: {e}")
            continue
            
        dt = (perf_counter() - t0) * 1000

        # metrics/log
        m = res.metrics or {}
        for k,v in m.items(): totals[k] = totals.get(k, 0) + v
        ctx.logger.info({"node": nid, "type": node.type, "duration_ms": round(dt,2), "context_patch": res.context_patch})

        last = res
        if res.terminate:
            break

        labels = res.next_edges or []
        if not labels:
            continue

        fanout_count = 0
        for lab in labels:
            for nxt in dag.adj.get(nid, {}).get(lab, set()):
                step = (nxt, lab)
                if step not in seen:
                    seen.add(step)
                    q.append(nxt)
                    fanout_count += 1
                    if fanout_count > max_fanout_per_node:
                        raise TraversalLimitError("Exceeded max_fanout_per_node")
                    
                    # Merge context patches for downstream nodes
                    if res.context_patch:
                        if nxt not in context_patches:
                            context_patches[nxt] = {}
                        context_patches[nxt].update(res.context_patch)

    return last, totals
```

---

## Progress Summary

### ✅ Completed Milestones (0-7)
- **Milestone 0**: Repo hygiene (branch, CI, linting) ✅
- **Milestone 1**: Core DAG types (GraphNode, IntentDAG, helper methods) ✅
- **Milestone 2**: Node execution interface (ExecutionResult, NodeProtocol protocol) ✅
- **Milestone 3**: DAG loader (JSON → IntentDAG, validation) ✅
- **Milestone 4**: Validation (cycle detection, reachability, labels) ✅
- **Milestone 5**: Traversal engine (BFS, context merging, error handling) ✅
- **Milestone 6**: Implementation resolver (DI) ✅
- **Milestone 7**: Update built-in nodes to DAG contract ✅

### 📊 Test Coverage
- **Total Tests**: 111 tests across all core modules
- **Adapter Tests**: 16 comprehensive tests covering all scenarios
- **All Tests Passing**: ✅

### 🎯 Next Up
- **Milestone 8**: Logging & metrics

---

## Quick smoke command (after wiring examples)

* [ ] `pytest -q`
* [ ] `python -m intent_kit.cli validate intent_kit/examples/demo_weather_payment.json`
* [ ] `python -m intent_kit.cli run intent_kit/examples/demo_weather_payment.json --input "what's the weather?" --trace`

---

## Review checklist (pre-merge)

* [ ] No references to `parent`, `children`, or `Tree*`.
* [ ] All examples validate and run.
* [ ] Deterministic traversal order proven by test (seeded).
* [ ] Cycle detection test shows readable path.
* [ ] Docs match code; code samples compile.
* [ ] CI green.