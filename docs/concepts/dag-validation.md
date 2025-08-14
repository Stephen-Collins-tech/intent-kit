# DAG Validation

Intent Kit provides comprehensive DAG validation to ensure correctness, completeness, and optimal performance of intent classification workflows.

## Overview

DAG validation checks for:

- **Structural Integrity** - All nodes and edges are properly connected
- **Cyclic Dependencies** - No cycles in the graph structure
- **Reachability** - All nodes are accessible from entrypoints
- **Label Consistency** - Edge labels match node capabilities
- **Configuration Validity** - Node configurations are correct

## Validation Functions

### validate_dag_structure

The primary validation function that performs comprehensive DAG analysis:

```python
from intent_kit.core.validation import validate_dag_structure

# Basic validation
issues = validate_dag_structure(dag)

if issues:
    print("Validation issues found:")
    for issue in issues:
        print(f"  - {issue}")
else:
    print("DAG structure is valid")
```

**Parameters:**
- `dag` (IntentDAG): The DAG to validate
- `producer_labels` (Dict[str, Set[str]], optional): Dictionary mapping node_id to set of labels it can produce

**Returns:**
- `List[str]`: List of validation issues (empty if all valid)

**Raises:**
- `CycleError`: If a cycle is detected in the DAG
- `ValueError`: If basic structure is invalid

## Validation Checks

### 1. ID Consistency

Ensures all referenced node IDs exist in the DAG:

```python
# Valid DAG
dag = DAGBuilder()
dag.add_node("classifier", "classifier", ...)
dag.add_node("extractor", "extractor", ...)
dag.add_edge("classifier", "extractor", "success")  # Both nodes exist

# Invalid DAG - missing node
dag.add_edge("classifier", "missing_node", "error")  # Will fail validation
```

**Common Issues:**
- Edge source node doesn't exist
- Edge destination node doesn't exist
- Entrypoint node doesn't exist

### 2. Entrypoint Validation

Ensures DAG has valid entrypoints:

```python
# Valid DAG with entrypoints
dag = DAGBuilder()
dag.add_node("classifier", "classifier", ...)
dag.set_entrypoints(["classifier"])

# Invalid DAG - no entrypoints
dag = DAGBuilder()
dag.add_node("classifier", "classifier", ...)
# Missing set_entrypoints() call - will fail validation
```

**Requirements:**
- At least one entrypoint must be defined
- All entrypoints must exist in the DAG
- Entrypoints must be reachable

### 3. Cycle Detection

Detects cycles in the DAG structure using Kahn's algorithm:

```python
# Valid DAG - no cycles
dag = DAGBuilder()
dag.add_node("A", "classifier", ...)
dag.add_node("B", "extractor", ...)
dag.add_node("C", "action", ...)
dag.add_edge("A", "B")
dag.add_edge("B", "C")

# Invalid DAG - cycle detected
dag.add_edge("C", "A")  # Creates cycle A -> B -> C -> A
```

**Cycle Detection Algorithm:**
1. Calculate in-degrees for all nodes
2. Add nodes with zero in-degree to queue
3. Process queue, reducing in-degrees of neighbors
4. If all nodes are processed, no cycles exist
5. If nodes remain unprocessed, cycles exist

### 4. Reachability Analysis

Ensures all nodes are reachable from entrypoints:

```python
# Valid DAG - all nodes reachable
dag = DAGBuilder()
dag.add_node("classifier", "classifier", ...)
dag.add_node("extractor", "extractor", ...)
dag.add_node("action", "action", ...)
dag.add_edge("classifier", "extractor")
dag.add_edge("extractor", "action")
dag.set_entrypoints(["classifier"])

# Invalid DAG - unreachable node
dag.add_node("orphan", "action", ...)  # No edges to/from this node
```

**Reachability Algorithm:**
1. Start from entrypoints
2. Traverse edges using BFS
3. Mark visited nodes
4. Report unvisited nodes as unreachable

### 5. Label Validation

Validates edge labels against node capabilities (when producer_labels provided):

```python
from intent_kit.core.validation import validate_dag_structure

# Define node capabilities
producer_labels = {
    "classifier": {"greet", "weather", "booking"},
    "extractor": {"success", "error"},
    "action": {"success", "error"}
}

# Validate with label constraints
issues = validate_dag_structure(dag, producer_labels)

# Valid edges
dag.add_edge("classifier", "extractor", "greet")  # "greet" in classifier labels
dag.add_edge("extractor", "action", "success")    # "success" in extractor labels

# Invalid edge
dag.add_edge("classifier", "extractor", "invalid_label")  # Not in classifier labels
```

## Error Handling

### Common Exceptions

#### CycleError

Raised when a cycle is detected in the DAG:

```python
from intent_kit.core.exceptions import CycleError

try:
    issues = validate_dag_structure(dag)
except CycleError as e:
    print(f"Cycle detected: {e}")
    # Handle cycle - typically requires DAG redesign
```

#### ValueError

Raised for basic structural issues:

```python
try:
    issues = validate_dag_structure(dag)
except ValueError as e:
    print(f"Structural error: {e}")
    # Handle structural issues
```

### Validation Issue Types

```python
# Common validation issues
issues = [
    "Unreachable nodes: orphan_node",
    "Missing node: referenced_node",
    "Invalid entrypoint: non_existent_entrypoint",
    "Cycle detected: A -> B -> C -> A",
    "Invalid edge label: 'invalid_label' not in producer labels"
]
```

## Advanced Validation

### Custom Validation Rules

Extend validation with custom rules:

```python
def custom_validation(dag):
    issues = []

    # Check for required node types
    has_classifier = any(node.type == "classifier" for node in dag.nodes.values())
    if not has_classifier:
        issues.append("DAG must contain at least one classifier node")

    # Check for proper error handling
    has_clarification = any(node.type == "clarification" for node in dag.nodes.values())
    if not has_clarification:
        issues.append("Consider adding clarification nodes for error handling")

    return issues

# Combine with built-in validation
builtin_issues = validate_dag_structure(dag)
custom_issues = custom_validation(dag)
all_issues = builtin_issues + custom_issues
```

### Performance Validation

Validate DAG performance characteristics:

```python
def performance_validation(dag):
    issues = []

    # Check for excessive fanout
    for node_id, node in dag.nodes.items():
        outgoing_edges = len(dag.adj.get(node_id, {}))
        if outgoing_edges > 10:
            issues.append(f"Node {node_id} has high fanout ({outgoing_edges} edges)")

    # Check for deep chains
    max_depth = calculate_max_depth(dag)
    if max_depth > 20:
        issues.append(f"DAG has deep execution chain ({max_depth} levels)")

    return issues

def calculate_max_depth(dag):
    """Calculate maximum depth from entrypoints to any node."""
    depths = {}

    def dfs(node_id, depth):
        if node_id in depths:
            depths[node_id] = max(depths[node_id], depth)
        else:
            depths[node_id] = depth

        for labels in dag.adj.get(node_id, {}).values():
            for next_node in labels:
                dfs(next_node, depth + 1)

    for entrypoint in dag.entrypoints:
        dfs(entrypoint, 0)

    return max(depths.values()) if depths else 0
```

## Integration with DAG Building

### Automatic Validation

DAG validation is automatically performed during build:

```python
from intent_kit import DAGBuilder

builder = DAGBuilder()

# Add nodes and edges
builder.add_node("classifier", "classifier", ...)
builder.add_node("extractor", "extractor", ...)
builder.add_edge("classifier", "extractor", "success")

# Build with validation (default)
dag = builder.build()  # Validates automatically

# Build without validation (not recommended)
dag = builder.build(validate_structure=False)
```

### Validation During Development

Use validation during DAG development:

```python
# Validate after each major change
builder = DAGBuilder()
builder.add_node("classifier", "classifier", ...)

# Check intermediate state
try:
    dag = builder.build()
    print("DAG is valid so far")
except Exception as e:
    print(f"Validation failed: {e}")

# Continue building
builder.add_node("extractor", "extractor", ...)
builder.add_edge("classifier", "extractor", "success")

# Final validation
dag = builder.build()
print("DAG is complete and valid")
```

## Best Practices

### 1. Start with Simple DAGs

```python
# Start simple and add complexity
builder = DAGBuilder()

# Phase 1: Basic classifier -> action
builder.add_node("classifier", "classifier", ...)
builder.add_node("action", "action", ...)
builder.add_edge("classifier", "action", "success")
dag = builder.build()  # Validate

# Phase 2: Add extractor
builder.add_node("extractor", "extractor", ...)
builder.add_edge("classifier", "extractor", "success")
builder.add_edge("extractor", "action", "success")
dag = builder.build()  # Validate

# Phase 3: Add error handling
builder.add_node("clarification", "clarification", ...)
builder.add_edge("classifier", "clarification", "error")
builder.add_edge("extractor", "clarification", "error")
dag = builder.build()  # Validate
```

### 2. Use Descriptive Node Names

```python
# Good - descriptive names
builder.add_node("intent_classifier", "classifier", ...)
builder.add_node("extract_user_name", "extractor", ...)
builder.add_node("send_greeting", "action", ...)

# Avoid - unclear names
builder.add_node("node1", "classifier", ...)
builder.add_node("node2", "extractor", ...)
builder.add_node("node3", "action", ...)
```

### 3. Validate Early and Often

```python
# Validate at each step
builder = DAGBuilder()

# Step 1: Add classifier
builder.add_node("classifier", "classifier", ...)
try:
    dag = builder.build()
    print("✓ Classifier added successfully")
except Exception as e:
    print(f"✗ Classifier validation failed: {e}")
    return

# Step 2: Add extractor
builder.add_node("extractor", "extractor", ...)
builder.add_edge("classifier", "extractor", "success")
try:
    dag = builder.build()
    print("✓ Extractor added successfully")
except Exception as e:
    print(f"✗ Extractor validation failed: {e}")
    return
```

### 4. Handle Validation Errors Gracefully

```python
def build_dag_with_validation():
    builder = DAGBuilder()

    try:
        # Build DAG
        builder.add_node("classifier", "classifier", ...)
        builder.add_node("extractor", "extractor", ...)
        builder.add_edge("classifier", "extractor", "success")

        # Validate and build
        dag = builder.build()
        print("DAG built successfully")
        return dag

    except CycleError as e:
        print(f"Cycle detected: {e}")
        print("Please review your DAG structure")
        return None

    except ValueError as e:
        print(f"Structural error: {e}")
        print("Please check node IDs and connections")
        return None

    except Exception as e:
        print(f"Unexpected error: {e}")
        return None
```

### 5. Use Label Constraints

```python
# Define clear label constraints
producer_labels = {
    "intent_classifier": {"greet", "weather", "booking", "help"},
    "user_extractor": {"success", "missing_name", "invalid_format"},
    "weather_action": {"success", "api_error", "location_not_found"},
    "greeting_action": {"success", "error"}
}

# Validate with constraints
issues = validate_dag_structure(dag, producer_labels)
if issues:
    print("Label validation issues:")
    for issue in issues:
        print(f"  - {issue}")
```

## Performance Considerations

### 1. Validation Overhead

```python
# Validation adds overhead - use judiciously
import time

# Time validation
start = time.time()
issues = validate_dag_structure(dag)
validation_time = time.time() - start

print(f"Validation took {validation_time:.3f} seconds")

# For large DAGs, consider validation levels
if dag_size < 100:
    # Full validation for small DAGs
    issues = validate_dag_structure(dag)
else:
    # Basic validation for large DAGs
    issues = validate_dag_structure(dag, producer_labels=None)
```

### 2. Caching Validation Results

```python
# Cache validation results for unchanged DAGs
class CachedDAG:
    def __init__(self, dag):
        self.dag = dag
        self._validation_cache = None
        self._dag_hash = None

    def validate(self):
        current_hash = hash(str(self.dag.nodes) + str(self.dag.adj))

        if self._dag_hash == current_hash and self._validation_cache is not None:
            return self._validation_cache

        issues = validate_dag_structure(self.dag)
        self._validation_cache = issues
        self._dag_hash = current_hash
        return issues
```

DAG validation ensures your intent classification workflows are robust, efficient, and maintainable.
