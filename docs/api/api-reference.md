# API Reference

This document provides a reference for the Intent Kit API.

## Core Classes

### DAGBuilder

The main builder class for creating intent DAGs.

```python
from intent_kit import DAGBuilder
```

#### Methods

##### `add_node(node_id, node_type, **config)`
Add a node to the DAG.

```python
builder = DAGBuilder()

# Add classifier node
builder.add_node("classifier", "classifier",
                 output_labels=["greet", "weather"],
                 description="Main intent classifier")

# Add extractor node
builder.add_node("extract_name", "extractor",
                 param_schema={"name": str},
                 description="Extract name from greeting",
                 output_key="extracted_params")

# Add action node
builder.add_node("greet_action", "action",
                 action=greet_function,
                 description="Greet the user")
```

##### `add_edge(from_node, to_node, label=None)`
Add an edge between nodes.

```python
# Connect classifier to extractor
builder.add_edge("classifier", "extract_name", "greet")

# Connect extractor to action
builder.add_edge("extract_name", "greet_action", "success")

# Add error handling edge
builder.add_edge("extract_name", "clarification", "error")
```

##### `set_entrypoints(entrypoints)`
Set the entry points for the DAG.

```python
builder.set_entrypoints(["classifier"])
```

##### `with_default_llm_config(config)`
Set default LLM configuration for the DAG.

```python
llm_config = {
    "provider": "openai",
    "model": "gpt-3.5-turbo",
    "api_key": "your-api-key"
}

builder.with_default_llm_config(llm_config)
```

##### `from_json(config)`
Create a DAGBuilder from JSON configuration.

```python
dag_config = {
    "nodes": {
        "classifier": {
            "type": "classifier",
            "output_labels": ["greet", "weather"],
            "description": "Main intent classifier"
        },
        "greet_action": {
            "type": "action",
            "action": greet_function,
            "description": "Greet the user"
        }
    },
    "edges": [
        {"from": "classifier", "to": "greet_action", "label": "greet"}
    ],
    "entrypoints": ["classifier"]
}

dag = DAGBuilder.from_json(dag_config)
```

##### `build()`
Build and return the IntentDAG instance.

```python
dag = builder.build()
```

### IntentDAG

The core DAG data structure.

```python
from intent_kit.core.types import IntentDAG
```

#### Properties

- **nodes** - Dictionary mapping node IDs to GraphNode instances
- **adj** - Adjacency list for forward edges
- **rev** - Reverse adjacency list for backward edges
- **entrypoints** - List of entry point node IDs
- **metadata** - Dictionary of DAG metadata

### GraphNode

Represents a node in the DAG.

```python
from intent_kit.core.types import GraphNode
```

#### Properties

- **id** - Unique node identifier
- **type** - Node type (classifier, extractor, action, clarification)
- **config** - Node configuration dictionary

### ExecutionResult

Result of a node execution.

```python
from intent_kit.core.types import ExecutionResult
```

#### Properties

- **data** - Execution result data
- **next_edges** - List of next edge labels to follow
- **terminate** - Whether to terminate execution
- **metrics** - Dictionary of execution metrics
- **context_patch** - Dictionary of context updates

## Node Types

### ClassifierNode

Classifier nodes determine intent and route to appropriate paths.

```python
from intent_kit.nodes.classifier import ClassifierNode

classifier = ClassifierNode(
    name="main_classifier",
    output_labels=["greet", "weather", "calculate"],
    description="Main intent classifier",
    llm_config={"provider": "openai", "model": "gpt-4"}
)
```

#### Parameters

- **name** - Node name
- **output_labels** - List of possible classification outputs
- **description** - Human-readable description for LLM
- **llm_config** - LLM configuration for AI-based classification
- **classification_func** - Custom function for classification (overrides LLM)

### ExtractorNode

Extractor nodes use LLM to extract parameters from natural language.

```python
from intent_kit.nodes.extractor import ExtractorNode

extractor = ExtractorNode(
    name="name_extractor",
    param_schema={"name": str},
    description="Extract name from greeting",
    output_key="extracted_params"
)
```

#### Parameters

- **name** - Node name
- **param_schema** - Dictionary defining expected parameters and their types
- **description** - Human-readable description for LLM
- **output_key** - Key in context where extracted parameters are stored
- **llm_config** - Optional LLM configuration (uses default if not specified)

### ActionNode

Action nodes execute actions and produce outputs.

```python
from intent_kit.nodes.action import ActionNode

def greet(name: str) -> str:
    return f"Hello {name}!"

action = ActionNode(
    name="greet_action",
    action=greet,
    description="Greet the user"
)
```

#### Parameters

- **name** - Node name
- **action** - Function to execute
- **description** - Human-readable description
- **terminate_on_success** - Whether to terminate after successful execution (default: True)
- **param_key** - Key in context to get parameters from (default: "extracted_params")

### ClarificationNode

Clarification nodes handle unclear intent by asking for clarification.

```python
from intent_kit.nodes.clarification import ClarificationNode

clarification = ClarificationNode(
    name="clarification",
    clarification_message="I'm not sure what you'd like me to do.",
    available_options=["Say hello", "Ask about weather", "Calculate something"]
)
```

#### Parameters

- **name** - Node name
- **clarification_message** - Message to display to the user
- **available_options** - List of options the user can choose from
- **description** - Human-readable description

## Context Management

### DefaultContext

The default context implementation with type safety and audit trails.

```python
from intent_kit.core.context import DefaultContext

context = DefaultContext()
```

#### Methods

##### `get(key, default=None)`
Get a value from context.

```python
name = context.get("user.name", "Unknown")
```

##### `set(key, value, modified_by=None)`
Set a value in context.

```python
context.set("user.name", "Alice", modified_by="greet_action")
```

##### `snapshot()`
Create an immutable snapshot of the context.

```python
snapshot = context.snapshot()
```

##### `apply_patch(patch)`
Apply a context patch.

```python
patch = {"user.name": "Bob", "user.age": 30}
context.apply_patch(patch)
```

## Execution

### run_dag

Execute a DAG with user input and context.

```python
from intent_kit import run_dag

result = run_dag(dag, "Hello Alice", context)
print(result.data)  # → "Hello Alice!"
```

#### Parameters

- **dag** - IntentDAG instance to execute
- **user_input** - User input string
- **context** - Context instance for state management
- **max_steps** - Maximum execution steps (default: 100)
- **max_fanout** - Maximum fanout per node (default: 10)
- **memoize** - Whether to memoize results (default: True)

#### Returns

- **ExecutionResult** - Result containing data, metrics, and context updates

## Validation

### validate_dag_structure

Validate DAG structure and configuration.

```python
from intent_kit.core.validation import validate_dag_structure

try:
    validate_dag_structure(dag)
    print("DAG is valid!")
except ValueError as e:
    print(f"DAG validation failed: {e}")
```

## Error Handling

### Built-in Exceptions

```python
from intent_kit.core.exceptions import (
    ExecutionError,
    TraversalLimitError,
    NodeError,
    TraversalError,
    ContextConflictError,
    CycleError,
    NodeResolutionError
)
```

## Configuration

### LLM Configuration

```python
llm_config = {
    "provider": "openai",  # openai, anthropic, google, ollama, openrouter
    "model": "gpt-3.5-turbo",
    "api_key": "your-api-key",
    "temperature": 0.7,
    "max_tokens": 1000
}
```

### Parameter Schema

```python
param_schema = {
    "name": str,
    "age": int,
    "city": str,
    "temperature": float,
    "is_active": bool,
    "tags": list[str]
}
```
