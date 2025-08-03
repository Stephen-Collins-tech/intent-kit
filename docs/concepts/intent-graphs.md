# Intent Graphs

Intent graphs are the core architectural concept in intent-kit. They provide a hierarchical, deterministic way to route user input through a series of classifiers and handlers to produce structured outputs.

## Overview

An intent graph is a directed acyclic graph (DAG) where:

- **Nodes** represent decision points or actions
- **Edges** represent the flow between nodes
- **Root nodes** are entry points for user input
- **Leaf nodes** are actions that produce outputs

## Graph Structure

```text
User Input → Root Classifier → Action → Output
```

### Node Types

1. **Classifier Nodes** - Route input to appropriate child nodes (must be root nodes)
2. **Action Nodes** - Execute actions and produce outputs (leaf nodes)

### Single Intent Architecture

All root nodes must be classifier nodes. This ensures focused, single-intent handling:

- **Root Classifiers** - Entry points that classify user input and route to actions
- **Action Nodes** - Leaf nodes that execute specific actions
- **No Splitters** - Multi-intent splitting is not supported in this architecture

## Building Intent Graphs

### Using IntentGraphBuilder

```python
from intent_kit import IntentGraphBuilder, action, llm_classifier

# Define actions
greet_action = action(
    name="greet",
    description="Greet the user",
    action_func=lambda name: f"Hello {name}!",
    param_schema={"name": str}
)

weather_action = action(
    name="weather",
    description="Get weather information",
    action_func=lambda city: f"Weather in {city} is sunny",
    param_schema={"city": str}
)

# Create classifier
main_classifier = llm_classifier(
    name="main",
    description="Route to appropriate action",
    children=[greet_action, weather_action],
    llm_config={"provider": "openai", "model": "gpt-4"}
)

# Build graph
graph = IntentGraphBuilder().root(main_classifier).build()
```

### Using JSON Configuration

```python
from intent_kit import IntentGraphBuilder

# Define your functions
def greet(name, context=None):
    return f"Hello {name}!"

def weather(city, context=None):
    return f"Weather in {city} is sunny"

# Create function registry
function_registry = {
    "greet": greet,
    "weather": weather,
}

# Define your graph in JSON
json_graph = {
    "root": "main_classifier",
    "nodes": {
        "main_classifier": {
            "id": "main_classifier",
            "type": "classifier",
            "classifier_type": "llm",
            "name": "main_classifier",
            "description": "Main intent classifier",
            "children": ["greet_action", "weather_action"],
            "llm_config": {"provider": "openai", "model": "gpt-4"}
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

# Build graph
graph = (
    IntentGraphBuilder()
    .with_json(json_graph)
    .with_functions(function_registry)
    .build()
)
```

## Graph Execution

### Routing Input

```python
# Route user input through the graph
result = graph.route("Hello Alice")
print(result.output)  # → "Hello Alice!"

result = graph.route("What's the weather in San Francisco?")
print(result.output)  # → "Weather in San Francisco is sunny"
```

### Execution Flow

1. **Input Processing** - User input is received
2. **Classification** - Root classifier determines intent
3. **Parameter Extraction** - LLM extracts parameters from input
4. **Action Execution** - Selected action runs with parameters
5. **Output Generation** - Action result is returned

## Graph Validation

### Built-in Validation

IntentGraphBuilder includes validation to ensure:

- No cycles in the graph
- All referenced nodes exist
- All nodes are reachable from root
- Proper node types and relationships

```python
# Validate your graph
try:
    graph = IntentGraphBuilder().with_json(json_graph).build()
    print("Graph is valid!")
except ValueError as e:
    print(f"Graph validation failed: {e}")
```

### Common Validation Errors

- **Missing nodes** - Referenced nodes don't exist
- **Cycles** - Graph contains circular references
- **Unreachable nodes** - Nodes not connected to root
- **Invalid node types** - Incorrect node type specifications

## Advanced Features

### Debug Context

Enable debug context to track execution:

```python
graph = (
    IntentGraphBuilder()
    .with_json(json_graph)
    .with_functions(function_registry)
    .with_debug_context(True)
    .build()
)
```

### Context Tracing

Enable context tracing for detailed execution logs:

```python
graph = (
    IntentGraphBuilder()
    .with_json(json_graph)
    .with_functions(function_registry)
    .with_context_trace(True)
    .build()
)
```

## Best Practices

### Graph Design

1. **Keep it simple** - Start with a single root classifier
2. **Use descriptive names** - Make node names clear and meaningful
3. **Group related actions** - Organize actions logically
4. **Test thoroughly** - Validate with various inputs

### Performance

1. **Optimize classifiers** - Use efficient classification strategies
2. **Cache results** - Cache expensive operations when possible
3. **Monitor execution** - Track performance metrics
4. **Scale gradually** - Add complexity incrementally

### Maintenance

1. **Document your graphs** - Keep JSON configurations well-documented
2. **Version control** - Track changes to graph configurations
3. **Test changes** - Validate modifications before deployment
4. **Monitor usage** - Track how your graphs are being used
