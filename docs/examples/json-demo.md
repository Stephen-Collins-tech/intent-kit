# JSON Demo

This example demonstrates how to create DAGs using JSON configuration, providing a declarative approach to defining intent workflows.

## Overview

The JSON demo shows how to:
- Define complete DAGs in JSON format
- Reference Python functions directly in JSON
- Use the `DAGBuilder.from_json()` method
- Create portable, configurable workflows

## Full Example

```python
import os
import json
from dotenv import load_dotenv
from intent_kit import DAGBuilder, run_dag

load_dotenv()

def greet(name: str) -> str:
    return f"Hello {name}!"

def create_dag_from_json():
    """Create a DAG using JSON configuration."""

    # Define the entire DAG as a dictionary
    dag_config = {
        "nodes": {
            "classifier": {
                "type": "classifier",
                "output_labels": ["greet"],
                "description": "Classify if input is a greeting",
                "llm_config": {
                    "provider": "openrouter",
                    "api_key": os.getenv("OPENROUTER_API_KEY"),
                    "model": "google/gemma-2-9b-it",
                },
            },
            "extractor": {
                "type": "extractor",
                "param_schema": {"name": str},
                "description": "Extract name from greeting",
                "llm_config": {
                    "provider": "openrouter",
                    "api_key": os.getenv("OPENROUTER_API_KEY"),
                    "model": "google/gemma-2-9b-it",
                },
                "output_key": "extracted_params",
            },
            "greet_action": {
                "type": "action",
                "action": greet,
                "description": "Greet the user",
            },
            "clarification": {
                "type": "clarification",
                "clarification_message": "I'm not sure what you'd like me to do. Please try saying hello!",
                "available_options": ["Say hello to someone"],
                "description": "Ask for clarification when intent is unclear",
            },
        },
        "edges": [
            {"from": "classifier", "to": "extractor", "label": "greet"},
            {"from": "extractor", "to": "greet_action", "label": "success"},
            {"from": "classifier", "to": "clarification", "label": "clarification"},
        ],
        "entrypoints": ["classifier"],
    }

    # Use the convenience method to create DAG from JSON
    return DAGBuilder.from_json(dag_config)

if __name__ == "__main__":
    print("=== JSON DAG Demo ===\n")

    # Show the JSON structure (with string types for display)
    print("DAG Configuration:")
    display_config = {
        "nodes": {
            "classifier": {
                "type": "classifier",
                "output_labels": ["greet"],
                "description": "Classify if input is a greeting",
                "llm_config": {
                    "provider": "openrouter",
                    "model": "google/gemma-2-9b-it",
                },
            },
            "extractor": {
                "type": "extractor",
                "param_schema": {"name": "str"},
                "description": "Extract name from greeting",
            },
            "greet_action": {
                "type": "action",
                "action": "greet",
                "description": "Greet the user",
            },
            "clarification": {
                "type": "clarification",
                "clarification_message": "I'm not sure what you'd like me to do. Please try saying hello!",
            },
        },
        "edges": [
            {"from": "classifier", "to": "extractor", "label": "greet"},
            {"from": "extractor", "to": "greet_action", "label": "success"},
            {"from": "classifier", "to": "clarification", "label": "clarification"},
        ],
        "entrypoints": ["classifier"],
    }

    print(json.dumps(display_config, indent=2))

    print("\n" + "=" * 50)
    print("Executing DAG from JSON config:")

    # Execute the DAG using the convenience method
    builder = create_dag_from_json()

    test_inputs = ["Hello, I'm Alice!", "What's the weather?", "Hi there!"]

    for user_input in test_inputs:
        print(f"\nInput: '{user_input}'")
        dag = builder.build()
        result, _ = run_dag(dag, user_input)

        if result and result.data:
            if "action_result" in result.data:
                print(f"Result: {result.data['action_result']}")
            elif "clarification_message" in result.data:
                print(f"Clarification: {result.data['clarification_message']}")
            else:
                print(f"Result: {result.data}")
        else:
            print("No result detected")
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
  }
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
    "provider": "openrouter",
    "model": "google/gemma-2-9b-it"
  }
}
```

#### Action Node
```json
{
  "type": "action",
  "action": "function_reference",
  "description": "Execute action"
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

## Key Features

### 1. **Declarative Configuration**
Define your entire DAG structure in JSON for easy management and version control.

### 2. **Function References**
Reference Python functions directly in JSON configuration.

### 3. **Portable Workflows**
JSON configurations can be easily shared, versioned, and deployed.

### 4. **Flexible Routing**
Support for complex edge routing with labels and conditions.

### 5. **LLM Integration**
Configure different LLM providers and models per node.

## Best Practices

### 1. **Node Naming**
- Use descriptive, consistent node names
- Follow a naming convention (e.g., `{type}_{purpose}`)
- Avoid special characters in node IDs

### 2. **Edge Labels**
- Use meaningful edge labels for routing
- Common labels: `success`, `error`, `clarification`
- Use intent-specific labels for classifier outputs

### 3. **Function References**
- Reference functions directly in JSON
- Ensure functions are available in the current scope
- Use type hints for better parameter extraction

### 4. **Error Handling**
- Always include clarification nodes for unclear intent
- Add error handling edges for robust operation
- Test with various input scenarios

### 5. **Documentation**
- Provide clear descriptions for all nodes
- Document parameter schemas thoroughly
- Include examples in node descriptions

## Running the Demo

```bash
# Set your API key
export OPENROUTER_API_KEY="your-api-key-here"

# Run the demo
python examples/json_demo.py
```

## Expected Output

```
=== JSON DAG Demo ===

DAG Configuration:
{
  "nodes": {
    "classifier": {
      "type": "classifier",
      "output_labels": ["greet"],
      "description": "Classify if input is a greeting"
    },
    ...
  }
}

==================================================
Executing DAG from JSON config:

Input: 'Hello, I'm Alice!'
Result: Hello Alice!

Input: 'What's the weather?'
Clarification: I'm not sure what you'd like me to do. Please try saying hello!

Input: 'Hi there!'
Result: Hello there!
```

## Next Steps

- Explore [Basic Examples](basic-examples.md) for more patterns
- Learn about [DAG Examples](dag-examples.md) for advanced workflows
- Check out [JSON Serialization](../configuration/json-serialization.md) for detailed configuration options
