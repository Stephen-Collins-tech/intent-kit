# API Reference

This document provides a reference for the Intent Kit API.

## Core Classes

### IntentGraphBuilder

The main builder class for creating intent graphs.

```python
from intent_kit import IntentGraphBuilder
```

#### Methods

##### `root(node)`
Set the root node for the graph.

```python
graph = IntentGraphBuilder().root(classifier).build()
```

##### `with_json(json_graph)`
Configure the graph using JSON specification.

```python
graph = (
    IntentGraphBuilder()
    .with_json(graph_config)
    .with_functions(function_registry)
    .build()
)
```

##### `with_functions(function_registry)`
Register functions for use in actions.

```python
function_registry = {
    "greet": lambda name: f"Hello {name}!",
    "calculate": lambda op, a, b: a + b if op == "add" else None,
}

graph = (
    IntentGraphBuilder()
    .with_json(graph_config)
    .with_functions(function_registry)
    .build()
)
```

##### `with_default_llm_config(config)`
Set default LLM configuration for the graph.

```python
llm_config = {
    "provider": "openai",
    "model": "gpt-3.5-turbo",
    "api_key": "your-api-key"
}

graph = (
    IntentGraphBuilder()
    .with_json(graph_config)
    .with_functions(function_registry)
    .with_default_llm_config(llm_config)
    .build()
)
```

##### `with_debug_context(enabled=True)`
Enable debug context for execution tracking.

```python
graph = (
    IntentGraphBuilder()
    .with_json(graph_config)
    .with_functions(function_registry)
    .with_debug_context(True)
    .build()
)
```

##### `with_context_trace(enabled=True)`
Enable context tracing for detailed execution logs.

```python
graph = (
    IntentGraphBuilder()
    .with_json(graph_config)
    .with_functions(function_registry)
    .with_context_trace(True)
    .build()
)
```

##### `build()`
Build and return the IntentGraph instance.

```python
graph = IntentGraphBuilder().root(classifier).build()
```

## Node Factory Functions

### action()

Create an action node.

```python
from intent_kit import action

greet_action = action(
    name="greet",
    description="Greet the user by name",
    action_func=lambda name: f"Hello {name}!",
    param_schema={"name": str}
)
```

#### Parameters

- **name** (str): Unique identifier for the action
- **description** (str): Human-readable description
- **action_func** (callable): Function to execute
- **param_schema** (dict): Parameter type definitions

### llm_classifier()

Create an LLM classifier node.

```python
from intent_kit import llm_classifier

classifier = llm_classifier(
    name="main",
    description="Route to appropriate action",
    children=[greet_action, weather_action],
    llm_config={"provider": "openai", "model": "gpt-3.5-turbo"}
)
```

#### Parameters

- **name** (str): Unique identifier for the classifier
- **description** (str): Human-readable description
- **children** (list): List of child nodes
- **llm_config** (dict): LLM configuration

## JSON Configuration

### Graph Structure

```json
{
  "root": "main_classifier",
  "nodes": {
    "main_classifier": {
      "id": "main_classifier",
      "type": "classifier",
      "classifier_type": "llm",
      "name": "main_classifier",
      "description": "Main intent classifier",
      "llm_config": {
        "provider": "openai",
        "model": "gpt-3.5-turbo"
      },
      "children": ["greet_action", "weather_action"]
    },
    "greet_action": {
      "id": "greet_action",
      "type": "action",
      "name": "greet_action",
      "description": "Greet the user",
      "function": "greet",
      "param_schema": {"name": "str"}
    },
    "weather_action": {
      "id": "weather_action",
      "type": "action",
      "name": "weather_action",
      "description": "Get weather information",
      "function": "weather",
      "param_schema": {"city": "str"}
    }
  }
}
```

### Node Types

#### Classifier Nodes

```json
{
  "id": "classifier_id",
  "type": "classifier",
  "classifier_type": "llm",
  "name": "classifier_name",
  "description": "Classifier description",
  "llm_config": {
    "provider": "openai",
    "model": "gpt-3.5-turbo",
    "api_key": "your-api-key"
  },
  "children": ["action1", "action2"]
}
```

#### Action Nodes

```json
{
  "id": "action_id",
  "type": "action",
  "name": "action_name",
  "description": "Action description",
  "function": "function_name",
  "param_schema": {
    "param1": "str",
    "param2": "int"
  }
}
```

## LLM Configuration

### Supported Providers

#### OpenAI

```python
llm_config = {
    "provider": "openai",
    "model": "gpt-3.5-turbo",
    "api_key": "your-openai-api-key"
}
```

#### Anthropic

```python
llm_config = {
    "provider": "anthropic",
    "model": "claude-3-sonnet-20240229",
    "api_key": "your-anthropic-api-key"
}
```

#### Google AI

```python
llm_config = {
    "provider": "google",
    "model": "gemini-pro",
    "api_key": "your-google-api-key"
}
```

#### Ollama

```python
llm_config = {
    "provider": "ollama",
    "model": "llama2",
    "base_url": "http://localhost:11434"
}
```

#### OpenRouter

```python
llm_config = {
    "provider": "openrouter",
    "model": "mistralai/ministral-8b",
    "api_key": "your-openrouter-api-key"
}
```

## Graph Execution

### Routing Input

```python
# Route user input through the graph
result = graph.route("Hello Alice")
print(result.output)  # → "Hello Alice!"
```

### Execution Result

The `route()` method returns an execution result object with:

- **output**: The result of the action execution
- **node_path**: The path of nodes that were executed
- **parameters**: The extracted parameters
- **metadata**: Additional execution metadata

## Error Handling

### Common Errors

#### Missing Functions

```python
# Error: Function not found in registry
function_registry = {"greet": greet_func}
# Missing "weather" function referenced in JSON
```

#### Invalid JSON Configuration

```python
# Error: Invalid node type
{
  "type": "invalid_type"  # Must be "classifier" or "action"
}
```

#### Missing Required Parameters

```python
# Error: Missing required parameter
param_schema = {"name": "str"}
# Input doesn't contain name parameter
```

## Best Practices

### Function Registry

- Register all functions referenced in your JSON configuration
- Use descriptive function names
- Include proper error handling in your functions

### JSON Configuration

- Use descriptive node names and IDs
- Provide clear descriptions for all nodes
- Validate your JSON configuration before deployment

### LLM Configuration

- Store API keys securely (use environment variables)
- Choose appropriate models for your use case
- Monitor API usage and costs

### Error Handling

- Always handle potential errors in your action functions
- Provide meaningful error messages
- Test with various input scenarios
