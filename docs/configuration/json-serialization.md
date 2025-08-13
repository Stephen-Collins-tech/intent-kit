# JSON Serialization

Intent Kit supports creating DAG instances from JSON definitions, enabling portable and configurable intent workflows. This feature allows you to define your DAG structure in JSON format and reference functions directly.

## Overview

The JSON serialization system provides:

- **Portable DAG Definitions**: Define your DAG structure in JSON
- **Direct Function References**: Reference Python functions directly in JSON
- **LLM-Powered Extraction**: Intelligent parameter extraction from natural language
- **Builder Pattern**: Clean, fluent interface for DAG construction

## Quick Start

```python
from intent_kit import DAGBuilder

# Define your functions
def greet_function(name: str) -> str:
    return f"Hello {name}!"

def calculate_function(operation: str, a: float, b: float) -> str:
    if operation == "add":
        return str(a + b)
    elif operation == "subtract":
        return str(a - b)
    return "Unknown operation"

# Define DAG in JSON
dag_config = {
    "nodes": {
        "classifier": {
            "type": "classifier",
            "output_labels": ["greet", "calculate"],
            "description": "Main intent classifier",
            "llm_config": {"provider": "openai", "model": "gpt-4"}
        },
        "extract_greet": {
            "type": "extractor",
            "param_schema": {"name": str},
            "description": "Extract name from greeting",
            "output_key": "extracted_params"
        },
        "extract_calc": {
            "type": "extractor",
            "param_schema": {"operation": str, "a": float, "b": float},
            "description": "Extract calculation parameters",
            "output_key": "extracted_params"
        },
        "greet_action": {
            "type": "action",
            "action": greet_function,
            "description": "Greet the user"
        },
        "calculate_action": {
            "type": "action",
            "action": calculate_function,
            "description": "Perform calculation"
        }
    },
    "edges": [
        {"from": "classifier", "to": "extract_greet", "label": "greet"},
        {"from": "extract_greet", "to": "greet_action", "label": "success"},
        {"from": "classifier", "to": "extract_calc", "label": "calculate"},
        {"from": "extract_calc", "to": "calculate_action", "label": "success"}
    ],
    "entrypoints": ["classifier"]
}

# Build the DAG
dag = DAGBuilder.from_json(dag_config)
```

## JSON Schema

### DAG Structure

```json
{
  "nodes": {
    "node_id": {
      "type": "classifier|extractor|action|clarification",
      "description": "Optional description",
      // Node-specific configuration
    }
  },
  "edges": [
    {
      "from": "source_node_id",
      "to": "target_node_id",
      "label": "optional_edge_label"
    }
  ],
  "entrypoints": ["node_id1", "node_id2"]
}
```

### Node Types

#### Classifier Node
```json
{
  "type": "classifier",
  "output_labels": ["label1", "label2", "label3"],
  "description": "Classify user intent",
  "llm_config": {
    "provider": "openai|anthropic|google|ollama|openrouter",
    "model": "model_name",
    "api_key": "your_api_key",
    "temperature": 0.7,
    "max_tokens": 1000
  },
  "classification_func": "optional_custom_function_name"
}
```

#### Extractor Node
```json
{
  "type": "extractor",
  "param_schema": {
    "param_name": "str|int|float|bool|list|dict"
  },
  "description": "Extract parameters from input",
  "output_key": "extracted_params",
  "llm_config": {
    "provider": "openai",
    "model": "gpt-4"
  }
}
```

#### Action Node
```json
{
  "type": "action",
  "action": "function_reference",
  "description": "Execute action",
  "terminate_on_success": true,
  "param_key": "extracted_params"
}
```

#### Clarification Node
```json
{
  "type": "clarification",
  "clarification_message": "I'm not sure what you'd like me to do.",
  "available_options": ["Option 1", "Option 2", "Option 3"],
  "description": "Ask for clarification"
}
```

## Complete Example

```python
import os
from intent_kit import DAGBuilder, run_dag
from intent_kit.core.context import DefaultContext

def greet(name: str) -> str:
    return f"Hello {name}!"

def get_weather(city: str) -> str:
    return f"Weather in {city} is sunny"

def calculate(operation: str, a: float, b: float) -> str:
    if operation == "add":
        return str(a + b)
    elif operation == "subtract":
        return str(a - b)
    return "Unknown operation"

# Define complete DAG
dag_config = {
    "nodes": {
        "classifier": {
            "type": "classifier",
            "output_labels": ["greet", "weather", "calculate"],
            "description": "Main intent classifier",
            "llm_config": {
                "provider": "openai",
                "model": "gpt-3.5-turbo",
                "api_key": os.getenv("OPENAI_API_KEY")
            }
        },
        "extract_name": {
            "type": "extractor",
            "param_schema": {"name": str},
            "description": "Extract name from greeting",
            "output_key": "extracted_params"
        },
        "extract_location": {
            "type": "extractor",
            "param_schema": {"city": str},
            "description": "Extract city from weather request",
            "output_key": "extracted_params"
        },
        "extract_calc": {
            "type": "extractor",
            "param_schema": {"operation": str, "a": float, "b": float},
            "description": "Extract calculation parameters",
            "output_key": "extracted_params"
        },
        "greet_action": {
            "type": "action",
            "action": greet,
            "description": "Greet the user"
        },
        "weather_action": {
            "type": "action",
            "action": get_weather,
            "description": "Get weather information"
        },
        "calculate_action": {
            "type": "action",
            "action": calculate,
            "description": "Perform calculation"
        },
        "clarification": {
            "type": "clarification",
            "clarification_message": "I'm not sure what you'd like me to do. You can greet me, ask about weather, or perform calculations!",
            "available_options": ["Say hello", "Ask about weather", "Calculate something"]
        }
    },
    "edges": [
        {"from": "classifier", "to": "extract_name", "label": "greet"},
        {"from": "extract_name", "to": "greet_action", "label": "success"},
        {"from": "classifier", "to": "extract_location", "label": "weather"},
        {"from": "extract_location", "to": "weather_action", "label": "success"},
        {"from": "classifier", "to": "extract_calc", "label": "calculate"},
        {"from": "extract_calc", "to": "calculate_action", "label": "success"},
        {"from": "classifier", "to": "clarification", "label": "clarification"}
    ],
    "entrypoints": ["classifier"]
}

# Build and execute DAG
dag = DAGBuilder.from_json(dag_config)
context = DefaultContext()

# Test different inputs
result = run_dag(dag, "Hello Alice", context)
print(result.data)  # → "Hello Alice!"

result = run_dag(dag, "What's the weather in San Francisco?", context)
print(result.data)  # → "Weather in San Francisco is sunny"

result = run_dag(dag, "Add 5 and 3", context)
print(result.data)  # → "8"
```

## Advanced Configuration

### Default LLM Configuration

You can set default LLM configuration for the entire DAG:

```python
# Set default LLM config
builder = DAGBuilder()
builder.with_default_llm_config({
    "provider": "openai",
    "model": "gpt-4",
    "api_key": os.getenv("OPENAI_API_KEY")
})

# Individual nodes can override this
dag_config = {
    "nodes": {
        "classifier": {
            "type": "classifier",
            "output_labels": ["greet", "weather"],
            "description": "Main classifier"
            # Uses default LLM config
        },
        "extract_name": {
            "type": "extractor",
            "param_schema": {"name": str},
            "description": "Extract name",
            "llm_config": {
                "provider": "anthropic",  # Override default
                "model": "claude-3-sonnet-20240229"
            }
        }
    }
}
```

### Error Handling Edges

Add error handling by connecting nodes to clarification:

```json
{
  "edges": [
    {"from": "extract_name", "to": "greet_action", "label": "success"},
    {"from": "extract_name", "to": "clarification", "label": "error"},
    {"from": "greet_action", "to": "clarification", "label": "error"}
  ]
}
```

### Complex Parameter Schemas

Define complex parameter types:

```json
{
  "type": "extractor",
  "param_schema": {
    "name": "str",
    "age": "int",
    "city": "str",
    "temperature": "float",
    "is_active": "bool",
    "tags": "list[str]",
    "preferences": "dict"
  },
  "description": "Extract user profile information"
}
```

## Validation

### DAG Structure Validation

The JSON configuration is validated when building the DAG:

```python
try:
    dag = DAGBuilder.from_json(dag_config)
    print("DAG is valid!")
except ValueError as e:
    print(f"DAG validation failed: {e}")
```

### Common Validation Errors

- **Missing required fields** - Node type, description, etc.
- **Invalid node types** - Must be classifier, extractor, action, or clarification
- **Missing edges** - Referenced nodes don't exist
- **Cycles** - DAG contains circular references
- **Unreachable nodes** - Nodes not connected to entrypoints

## Best Practices

### Node Naming

- Use descriptive, consistent node names
- Follow a naming convention (e.g., `{type}_{purpose}`)
- Avoid special characters in node IDs

### Edge Labels

- Use meaningful edge labels for routing
- Common labels: `success`, `error`, `clarification`
- Use intent-specific labels for classifier outputs

### Function References

- Reference functions directly in JSON
- Ensure functions are available in the current scope
- Use type hints for better parameter extraction

### Error Handling

- Always include clarification nodes for unclear intent
- Add error handling edges for robust operation
- Test with various input scenarios

### Documentation

- Provide clear descriptions for all nodes
- Document parameter schemas thoroughly
- Include examples in node descriptions
