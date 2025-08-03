# JSON Serialization

IntentKit supports creating IntentGraph instances from JSON definitions, enabling portable and configurable intent graphs. This feature allows you to define your intent graph structure in JSON format and reference functions from a registry.

## Overview

The JSON serialization system provides:

- **Portable Graph Definitions**: Define your intent graph structure in JSON
- **Function Registry**: Map function names to callable functions
- **LLM-Powered Extraction**: Intelligent parameter extraction from natural language
- **Builder Pattern**: Clean, fluent interface for graph construction

## Quick Start

```python
from intent_kit import IntentGraphBuilder

# Define your functions
def greet_function(name: str) -> str:
    return f"Hello {name}!"

def calculate_function(operation: str, a: float, b: float) -> str:
    # ... calculation logic
    return f"{a} {operation} {b} = {result}"

# Create function registry
function_registry = {
    "greet_function": greet_function,
    "calculate_function": calculate_function,
}

# Define graph in JSON
json_graph = {
    "root_nodes": [
        {
            "name": "main_classifier",
            "type": "classifier",
            "classifier_function": "smart_classifier",
            "children": [
                {
                    "name": "greet_action",
                    "type": "action",
                    "function_name": "greet_function",
                    "param_schema": {"name": "str"},
                    "llm_config": {"provider": "openai", "model": "gpt-4"},
                }
            ]
        }
    ]
}

# Build the graph using the Builder pattern
graph = IntentGraphBuilder().with_functions(function_registry).with_json(json_graph).build()
```

## JSON Schema

### Graph Structure

```json
{
  "root_nodes": [
    {
      "name": "node_name",
      "type": "action|classifier",
      "description": "Optional description",
      "function_name": "registry_function_name",
      "param_schema": {
        "param_name": "str|int|float|bool|list|dict"
      },
      "llm_config": {
        "provider": "openai|anthropic|openrouter",
        "model": "model_name",
        "api_key": "your_api_key"
      },
      "context_inputs": ["input1", "input2"],
      "context_outputs": ["output1", "output2"],
      "remediation_strategies": ["strategy1", "strategy2"],
      "children": [
        // Child nodes follow the same schema
      ]
    }
  ],

  "visualize": false,
  "debug_context": false,
  "context_trace": false
}
```

### Node Types

#### Action Node
```json
{
  "name": "greet_action",
  "type": "action",
  "function_name": "greet_function",
  "param_schema": {"name": "str"},
  "llm_config": {"provider": "openai", "model": "gpt-4"},
  "context_inputs": ["user_name"],
  "context_outputs": ["greeting_sent"]
}
```

#### Classifier Node
```json
{
  "name": "intent_classifier",
  "type": "classifier",
  "classifier_function": "smart_classifier",
  "description": "Routes to appropriate action",
  "children": [
    // Child action nodes
  ],
  "remediation_strategies": ["fallback", "clarification"]
}
```



## LLM-Powered Argument Extraction

When you include `llm_config` in an action node, IntentKit automatically creates an LLM-based argument extractor:

```python
# JSON with LLM config
{
  "name": "weather_action",
  "type": "action",
  "function_name": "weather_function",
  "param_schema": {"location": "str"},
  "llm_config": {
    "provider": "openrouter",
    "model": "meta-llama/llama-4-maverick-17b-128e-instruct",
    "api_key": "your_api_key"
  }
}

# Natural language input: "What's the weather in San Francisco?"
# LLM extracts: {"location": "San Francisco"}
```

## Function Registry

The function registry maps function names to callable functions:

```python
from intent_kit import FunctionRegistry

# Create registry
registry = FunctionRegistry({
    "greet_function": greet_function,
    "calculate_function": calculate_function,
    "weather_function": weather_function,
})

# Register additional functions
registry.register("new_function", my_new_function)

# Check if function exists
if registry.has("greet_function"):
    func = registry.get("greet_function")
```

## Advanced Features

### Multiple Registries

```python
# Different registries for different domains
greeting_registry = FunctionRegistry({
    "greet_function": greet_function,
    "farewell_function": farewell_function,
})

calculation_registry = FunctionRegistry({
    "add_function": add_function,
    "multiply_function": multiply_function,
})

# Use with Builder pattern
graph = IntentGraphBuilder().with_functions(greeting_registry.functions).with_json(json_graph).build()
```

### Context Management

```python
# JSON with context inputs/outputs
{
  "name": "user_profile_action",
  "type": "action",
  "function_name": "update_profile",
  "param_schema": {"name": "str", "age": "int"},
  "context_inputs": ["user_id", "current_profile"],
  "context_outputs": ["updated_profile", "profile_changed"]
}
```

### Remediation Strategies

```python
# JSON with remediation
{
  "name": "payment_action",
  "type": "action",
  "function_name": "process_payment",
  "param_schema": {"amount": "float", "card_number": "str"},
  "remediation_strategies": ["retry", "fallback_payment", "human_escalation"]
}
```

## Error Handling

The system provides clear error messages for common issues:

```python
# Missing function in registry
ValueError: Action function 'missing_function' not found in registry

# Invalid JSON
ValueError: Invalid JSON: Expecting property name enclosed in double quotes

# Missing required fields
KeyError: JSON must contain 'root_nodes' field
```

## Best Practices

1. **Use the Builder Pattern**: Provides better error handling and type safety
2. **Validate Function Registry**: Ensure all referenced functions exist
3. **Test LLM Configurations**: Verify API keys and model availability
4. **Use Descriptive Names**: Make function and node names meaningful
5. **Include Descriptions**: Add descriptions for complex nodes
6. **Handle Errors Gracefully**: Implement remediation strategies

## Example

See `examples/json_llm_demo.py` for a complete working example that demonstrates:

- JSON-based graph configuration
- LLM-powered argument extraction
- Natural language understanding
- Function registry system
- Intelligent parameter parsing
- Builder pattern usage

The demo shows how to create IntentGraph instances using the Builder pattern with LLM-powered argument extraction.
