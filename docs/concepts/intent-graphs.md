# Intent DAGs

Intent DAGs (Directed Acyclic Graphs) are the core architectural concept in Intent Kit. They provide a flexible, scalable way to route user input through a series of nodes to produce structured outputs.

## Overview

An intent DAG is a directed acyclic graph where:

- **Nodes** represent decision points, extractors, or actions
- **Edges** represent the flow between nodes with optional labels
- **Entrypoints** are starting nodes for user input
- **Actions** are terminal nodes that produce outputs

## DAG Structure

```text
User Input → Classifier → Extractor → Action → Output
                ↓
            Clarification
```

### Node Types

1. **Classifier Nodes** - Route input to appropriate child nodes based on intent
2. **Extractor Nodes** - Extract parameters from user input using LLM
3. **Action Nodes** - Execute actions and produce outputs
4. **Clarification Nodes** - Ask for clarification when intent is unclear

## Building Intent DAGs

### Using DAGBuilder

```python
from intent_kit import DAGBuilder, run_dag
from intent_kit.core.context import DefaultContext

def greet(name: str) -> str:
    return f"Hello {name}!"

def get_weather(city: str) -> str:
    return f"Weather in {city} is sunny"

# Create DAG
builder = DAGBuilder()

# Set default LLM configuration
builder.with_default_llm_config({
    "provider": "openai",
    "model": "gpt-4"
})

# Add classifier node
builder.add_node("classifier", "classifier",
                 output_labels=["greet", "weather"],
                 description="Route to appropriate action")

# Add extractors
builder.add_node("extract_name", "extractor",
                 param_schema={"name": str},
                 description="Extract name from greeting",
                 output_key="extracted_params")

builder.add_node("extract_city", "extractor",
                 param_schema={"city": str},
                 description="Extract city from weather request",
                 output_key="extracted_params")

# Add action nodes
builder.add_node("greet_action", "action",
                 action=greet,
                 description="Greet the user")

builder.add_node("weather_action", "action",
                 action=get_weather,
                 description="Get weather information")

# Add clarification node
builder.add_node("clarification", "clarification",
                 clarification_message="I'm not sure what you'd like me to do. You can greet me or ask about weather!",
                 available_options=["Say hello", "Ask about weather"])

# Connect nodes
builder.add_edge("classifier", "extract_name", "greet")
builder.add_edge("extract_name", "greet_action", "success")
builder.add_edge("classifier", "extract_city", "weather")
builder.add_edge("extract_city", "weather_action", "success")
builder.add_edge("classifier", "clarification", "clarification")

# Set entrypoints
builder.set_entrypoints(["classifier"])

# Build DAG
dag = builder.build()
```

### Using JSON Configuration

```python
from intent_kit import DAGBuilder, run_dag

def greet(name: str) -> str:
    return f"Hello {name}!"

def get_weather(city: str) -> str:
    return f"Weather in {city} is sunny"

# Define your DAG in JSON
dag_config = {
    "nodes": {
        "classifier": {
            "type": "classifier",
            "output_labels": ["greet", "weather"],
            "description": "Main intent classifier",
            "llm_config": {"provider": "openai", "model": "gpt-4"}
        },
        "extract_name": {
            "type": "extractor",
            "param_schema": {"name": str},
            "description": "Extract name from greeting",
            "output_key": "extracted_params"
        },
        "extract_city": {
            "type": "extractor",
            "param_schema": {"city": str},
            "description": "Extract city from weather request",
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
        "clarification": {
            "type": "clarification",
            "clarification_message": "I'm not sure what you'd like me to do. You can greet me or ask about weather!",
            "available_options": ["Say hello", "Ask about weather"]
        }
    },
    "edges": [
        {"from": "classifier", "to": "extract_name", "label": "greet"},
        {"from": "extract_name", "to": "greet_action", "label": "success"},
        {"from": "classifier", "to": "extract_city", "label": "weather"},
        {"from": "extract_city", "to": "weather_action", "label": "success"},
        {"from": "classifier", "to": "clarification", "label": "clarification"}
    ],
    "entrypoints": ["classifier"]
}

# Build DAG
dag = DAGBuilder.from_json(dag_config)
```

## DAG Execution

### Running a DAG

```python
# Execute the DAG with user input
context = DefaultContext()
result = run_dag(dag, "Hello Alice", context)
print(result.data)  # → "Hello Alice!"

result = run_dag(dag, "What's the weather in San Francisco?", context)
print(result.data)  # → "Weather in San Francisco is sunny"
```

### Execution Flow

1. **Input Processing** - User input is received
2. **Classification** - Classifier determines intent and routes to appropriate path
3. **Parameter Extraction** - Extractor uses LLM to extract parameters from input
4. **Action Execution** - Selected action runs with extracted parameters
5. **Output Generation** - Action result is returned

## DAG Validation

### Built-in Validation

DAGBuilder includes validation to ensure:

- No cycles in the DAG
- All referenced nodes exist
- All nodes are reachable from entrypoints
- Proper node types and relationships

```python
# Validate your DAG
try:
    dag = DAGBuilder.from_json(dag_config)
    print("DAG is valid!")
except ValueError as e:
    print(f"DAG validation failed: {e}")
```

### Common Validation Errors

- **Missing nodes** - Referenced nodes don't exist
- **Cycles** - DAG contains circular references
- **Unreachable nodes** - Nodes not connected to entrypoints
- **Invalid node types** - Incorrect node type specifications

## Advanced Features

### Context Management

DAGs support rich context management for stateful operations:

```python
# Context persists across executions
context = DefaultContext()
context.set("user.name", "Alice")

result = run_dag(dag, "What's the weather?", context)
# The action can access context.get("user.name")
```

### LLM Service Integration

DAGs can use different LLM providers and models:

```python
builder = DAGBuilder()
builder.with_default_llm_config({
    "provider": "anthropic",
    "api_key": os.getenv("ANTHROPIC_API_KEY"),
    "model": "claude-3-sonnet-20240229"
})
```

### Error Handling

DAGs provide robust error handling and routing:

```python
# Add error handling edges
builder.add_edge("extract_name", "clarification", "error")
builder.add_edge("greet_action", "clarification", "error")
```

## Best Practices

### DAG Design

1. **Keep it simple** - Start with a single entrypoint classifier
2. **Use descriptive names** - Make node names clear and meaningful
3. **Group related functionality** - Organize nodes logically
4. **Test thoroughly** - Validate with various inputs

### Performance

1. **Optimize classifiers** - Use efficient classification strategies
2. **Cache results** - Cache expensive operations when possible
3. **Monitor execution** - Track performance metrics
4. **Scale gradually** - Add complexity incrementally

### Maintenance

1. **Document your DAGs** - Keep JSON configurations well-documented
2. **Version control** - Track changes to DAG configurations
3. **Test changes** - Validate modifications before deployment
4. **Monitor usage** - Track how your DAGs are being used

## Node Types in Detail

### Classifier Nodes

Classifiers determine intent and route to appropriate paths:

```python
builder.add_node("classifier", "classifier",
                 output_labels=["greet", "weather", "calculate"],
                 description="Main intent classifier")
```

### Extractor Nodes

Extractors use LLM to extract parameters from natural language:

```python
builder.add_node("extract_calc", "extractor",
                 param_schema={"operation": str, "a": float, "b": float},
                 description="Extract calculation parameters",
                 output_key="extracted_params")
```

### Action Nodes

Actions execute functions with extracted parameters:

```python
def calculate(operation: str, a: float, b: float) -> str:
    if operation == "add":
        return str(a + b)
    return "Unknown operation"

builder.add_node("calculate_action", "action",
                 action=calculate,
                 description="Perform calculation")
```

### Clarification Nodes

Clarification nodes handle unclear intent:

```python
builder.add_node("clarification", "clarification",
                 clarification_message="I'm not sure what you'd like me to do.",
                 available_options=["Say hello", "Ask about weather", "Calculate something"])
```
