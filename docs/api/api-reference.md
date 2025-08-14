# API Reference

This document provides a comprehensive reference for the Intent Kit API.

## Table of Contents

- [Core Classes](#core-classes)
- [Node Types](#node-types)
- [Context Management](#context-management)
- [LLM Integration](#llm-integration)
- [Configuration](#configuration)
- [Utilities](#utilities)

## Core Classes

### DAGBuilder

The main builder class for creating intent DAGs.

```python
from intent_kit import DAGBuilder
```

#### Constructor

```python
DAGBuilder()
```

Creates a new DAG builder instance.

#### Methods

##### `add_node(node_id, node_type, **config)`
Add a node to the DAG.

**Parameters:**
- `node_id` (str): Unique identifier for the node
- `node_type` (str): Type of node ("classifier", "extractor", "action", "clarification")
- `**config`: Node-specific configuration

**Examples:**

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

# Add clarification node
builder.add_node("clarification", "clarification",
                 description="Handle unclear requests")
```

##### `add_edge(from_node, to_node, label=None)`
Add an edge between nodes.

**Parameters:**
- `from_node` (str): Source node ID
- `to_node` (str): Target node ID
- `label` (str, optional): Edge label for conditional routing

**Examples:**

```python
# Connect classifier to extractor
builder.add_edge("classifier", "extract_name", "greet")

# Connect extractor to action
builder.add_edge("extract_name", "greet_action", "success")

# Add error handling edge
builder.add_edge("extract_name", "clarification", "error")

# Add clarification to retry
builder.add_edge("clarification", "classifier", "retry")
```

##### `set_entrypoints(entrypoints)`
Set the entry points for the DAG.

**Parameters:**
- `entrypoints` (List[str]): List of node IDs that can receive initial input

**Example:**

```python
builder.set_entrypoints(["classifier"])
```

##### `with_default_llm_config(config)`
Set default LLM configuration for the DAG.

**Parameters:**
- `config` (dict): LLM configuration dictionary

**Example:**

```python
llm_config = {
    "provider": "openai",
    "model": "gpt-3.5-turbo",
    "api_key": "your-api-key",
    "temperature": 0.1
}

builder.with_default_llm_config(llm_config)
```

##### `from_json(config)`
Create a DAGBuilder from JSON configuration.

**Parameters:**
- `config` (dict): DAG configuration dictionary

**Example:**

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
Build and return the final DAG instance.

**Returns:**
- `IntentDAG`: Configured DAG instance

**Example:**

```python
dag = builder.build()
```

### IntentDAG

The main DAG class for executing intent workflows.

```python
from intent_kit import IntentDAG
```

#### Methods

##### `execute(input_text, context=None)`
Execute the DAG with the given input.

**Parameters:**
- `input_text` (str): User input to process
- `context` (Context, optional): Context instance for state management

**Returns:**
- `ExecutionResult`: Result of the execution

**Example:**

```python
from intent_kit.core.context import DefaultContext

context = DefaultContext()
result = dag.execute("Hello Alice", context)
print(result.data)  # → "Hello Alice!"
```

##### `validate()`
Validate the DAG structure.

**Returns:**
- `bool`: True if valid, raises exception if invalid

**Example:**

```python
try:
    dag.validate()
    print("DAG is valid")
except Exception as e:
    print(f"DAG validation failed: {e}")
```

## Node Types

### ClassifierNode

Classifies user intent and routes to appropriate paths.

```python
from intent_kit.nodes.classifier import ClassifierNode
```

#### Constructor

```python
ClassifierNode(
    name: str,
    description: str,
    output_labels: List[str],
    children: List[TreeNode] = None,
    llm_config: dict = None
)
```

**Parameters:**
- `name` (str): Node name
- `description` (str): Description of the classifier's purpose
- `output_labels` (List[str]): Possible output labels
- `children` (List[TreeNode], optional): Child nodes
- `llm_config` (dict, optional): LLM configuration

**Example:**

```python
classifier = ClassifierNode(
    name="main_classifier",
    description="Route user requests to appropriate actions",
    output_labels=["greet", "calculate", "weather"],
    children=[greet_action, calculate_action, weather_action]
)
```

### ExtractorNode

Extracts parameters from natural language using LLM.

```python
from intent_kit.nodes.extractor import ExtractorNode
```

#### Constructor

```python
ExtractorNode(
    name: str,
    description: str,
    param_schema: dict,
    output_key: str = "extracted_params",
    llm_config: dict = None
)
```

**Parameters:**
- `name` (str): Node name
- `description` (str): Description of what to extract
- `param_schema` (dict): Schema defining parameters to extract
- `output_key` (str): Key for storing extracted parameters in context
- `llm_config` (dict, optional): LLM configuration

**Example:**

```python
extractor = ExtractorNode(
    name="name_extractor",
    description="Extract person's name from greeting",
    param_schema={"name": str},
    output_key="extracted_params"
)
```

### ActionNode

Executes specific actions and produces outputs.

```python
from intent_kit.nodes.action import ActionNode
```

#### Constructor

```python
ActionNode(
    name: str,
    action: Callable,
    description: str,
    param_schema: dict = None
)
```

**Parameters:**
- `name` (str): Node name
- `action` (Callable): Function to execute
- `description` (str): Description of the action
- `param_schema` (dict, optional): Expected parameter schema

**Example:**

```python
def greet_action(name: str) -> str:
    return f"Hello {name}!"

action = ActionNode(
    name="greet_action",
    action=greet_action,
    description="Greet the user by name",
    param_schema={"name": str}
)
```

### ClarificationNode

Handles unclear intent by asking for clarification.

```python
from intent_kit.nodes.clarification import ClarificationNode
```

#### Constructor

```python
ClarificationNode(
    name: str,
    description: str,
    clarification_prompt: str = None
)
```

**Parameters:**
- `name` (str): Node name
- `description` (str): Description of when clarification is needed
- `clarification_prompt` (str, optional): Custom clarification message

**Example:**

```python
clarification = ClarificationNode(
    name="clarification",
    description="Handle unclear or ambiguous requests",
    clarification_prompt="I'm not sure what you mean. Could you please clarify?"
)
```

## Context Management

### DefaultContext

Default context implementation for state management.

```python
from intent_kit.core.context import DefaultContext
```

#### Constructor

```python
DefaultContext()
```

#### Methods

##### `set(key, value)`
Set a value in the context.

**Parameters:**
- `key` (str): Context key
- `value` (Any): Value to store

**Example:**

```python
context = DefaultContext()
context.set("user_name", "Alice")
context.set("conversation_count", 5)
```

##### `get(key, default=None)`
Get a value from the context.

**Parameters:**
- `key` (str): Context key
- `default` (Any, optional): Default value if key not found

**Returns:**
- `Any`: Stored value or default

**Example:**

```python
user_name = context.get("user_name", "Unknown")
count = context.get("conversation_count", 0)
```

##### `has(key)`
Check if a key exists in the context.

**Parameters:**
- `key` (str): Context key

**Returns:**
- `bool`: True if key exists

**Example:**

```python
if context.has("user_name"):
    print(f"User: {context.get('user_name')}")
```

##### `clear()`
Clear all context data.

**Example:**

```python
context.clear()
```

## LLM Integration

### Supported Providers

Intent Kit supports multiple LLM providers:

#### OpenAI

```python
llm_config = {
    "provider": "openai",
    "model": "gpt-3.5-turbo",
    "api_key": "your-openai-api-key",
    "temperature": 0.1
}
```

#### Anthropic

```python
llm_config = {
    "provider": "anthropic",
    "model": "claude-3-sonnet-20240229",
    "api_key": "your-anthropic-api-key",
    "temperature": 0.1
}
```

#### Google

```python
llm_config = {
    "provider": "google",
    "model": "gemini-pro",
    "api_key": "your-google-api-key",
    "temperature": 0.1
}
```

#### Ollama

```python
llm_config = {
    "provider": "ollama",
    "model": "llama2",
    "base_url": "http://localhost:11434",
    "temperature": 0.1
}
```

### LLM Configuration Options

Common configuration options:

- `provider` (str): LLM provider name
- `model` (str): Model name
- `api_key` (str): API key for the provider
- `temperature` (float): Sampling temperature (0.0-2.0)
- `max_tokens` (int): Maximum tokens to generate
- `base_url` (str): Custom base URL (for Ollama)

## Configuration

### Environment Variables

Set these environment variables for API keys:

```bash
export OPENAI_API_KEY="your-openai-api-key"
export ANTHROPIC_API_KEY="your-anthropic-api-key"
export GOOGLE_API_KEY="your-google-api-key"
```

### JSON Configuration Schema

Complete JSON configuration schema:

```json
{
  "nodes": {
    "node_id": {
      "type": "classifier|extractor|action|clarification",
      "description": "Node description",
      "llm_config": {
        "provider": "openai|anthropic|google|ollama",
        "model": "model-name",
        "api_key": "api-key",
        "temperature": 0.1
      },
      "param_schema": {
        "param_name": "param_type"
      },
      "output_key": "context_key",
      "action": "function_reference"
    }
  },
  "edges": [
    {
      "from": "source_node_id",
      "to": "target_node_id",
      "label": "edge_label"
    }
  ],
  "entrypoints": ["node_id1", "node_id2"],
  "default_llm_config": {
    "provider": "openai",
    "model": "gpt-3.5-turbo"
  }
}
```

## Utilities

### run_dag

Convenience function for executing DAGs.

```python
from intent_kit import run_dag
```

#### Usage

```python
result = run_dag(dag, "Hello Alice", context)
print(result.data)
```

### llm_classifier

Convenience function for creating LLM-powered classifiers.

```python
from intent_kit import llm_classifier
```

#### Usage

```python
classifier = llm_classifier(
    name="main",
    description="Route user requests",
    children=[action1, action2],
    llm_config={"provider": "openai", "model": "gpt-3.5-turbo"}
)
```

## Error Handling

### Common Exceptions

#### DAGValidationError
Raised when DAG structure is invalid.

```python
from intent_kit.core.exceptions import DAGValidationError

try:
    dag.validate()
except DAGValidationError as e:
    print(f"DAG validation failed: {e}")
```

#### NodeExecutionError
Raised when node execution fails.

```python
from intent_kit.core.exceptions import NodeExecutionError

try:
    result = dag.execute("Hello Alice", context)
except NodeExecutionError as e:
    print(f"Node execution failed: {e}")
```

#### ContextError
Raised when context operations fail.

```python
from intent_kit.core.exceptions import ContextError

try:
    context.set("key", value)
except ContextError as e:
    print(f"Context operation failed: {e}")
```

## Best Practices

### DAG Design

1. **Start with a classifier** - Always begin with a classifier node
2. **Use extractors** - Extract parameters before actions
3. **Handle errors** - Add clarification nodes for error handling
4. **Keep it simple** - Start with simple workflows and add complexity

### Context Management

1. **Use meaningful keys** - Use descriptive context key names
2. **Validate data** - Always validate data before using it
3. **Clear when needed** - Clear context when starting new sessions
4. **Protect system keys** - Avoid using reserved system key names

### LLM Configuration

1. **Use appropriate models** - Choose models based on your needs
2. **Set temperature** - Use lower temperature for classification
3. **Handle rate limits** - Implement retry logic for API calls
4. **Monitor costs** - Track API usage and costs

### Testing

1. **Test each node** - Test individual nodes in isolation
2. **Test workflows** - Test complete workflows end-to-end
3. **Test edge cases** - Test error conditions and edge cases
4. **Use evaluation tools** - Use built-in evaluation framework
