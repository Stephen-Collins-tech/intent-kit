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
User Input → Root Classifier → Intent Classifier → Action → Output
```

### Node Types

1. **Classifier Nodes** - Route input to appropriate child nodes
2. **Action Nodes** - Execute actions and produce outputs
3. **Splitter Nodes** - Handle multiple nodes in single input

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

# Build graph with LLM configuration for chunk classification
graph = IntentGraphBuilder().root(main_classifier).with_default_llm_config({
    "provider": "openai",
    "model": "gpt-4"
}).build()
```

### Using JSON Configuration

```python
from intent_kit import IntentGraphBuilder

json_graph = {
    "root": "main_classifier",
    "nodes": {
        "main_classifier": {
            "id": "main_classifier",  # Explicit ID (optional - defaults to 'name')
            "type": "llm_classifier",
            "name": "main_classifier",
            "description": "Main intent classifier",
            "children": ["greet_action", "weather_action"],
            "llm_config": {"provider": "openai", "model": "gpt-4"}
        },
        "greet_action": {
            "id": "greet_action",  # Explicit ID
            "type": "action",
            "name": "greet_action",
            "description": "Greet the user",
            "function": "greet_function",
            "param_schema": {"name": "str"}
        },
        "weather_action": {
            "type": "action",  # No explicit ID - defaults to 'name'
            "name": "weather_action",
            "description": "Get weather information",
            "function": "weather_function",
            "param_schema": {"city": "str"}
        }
    }
}

function_registry = {
    "greet_function": lambda name: f"Hello {name}!",
    "weather_function": lambda city: f"Weather in {city} is sunny"
}

graph = IntentGraphBuilder().with_json(json_graph).with_functions(function_registry).build()
```

**Node ID Behavior:**
- Each node can have an explicit `"id"` field
- If `"id"` is not provided, it defaults to the `"name"` field
- At least one of `"id"` or `"name"` must be present
- The `"id"` is used for internal node references and child relationships

## Execution Flow

1. **Input Processing** - User input is received
2. **Root Classification** - Input is classified by root nodes
3. **Intent Routing** - Input is routed to appropriate actions
4. **Parameter Extraction** - Parameters are extracted from input
5. **Action Execution** - Action functions are executed
6. **Output Generation** - Structured output is returned

## Multi-Intent Routing

Intent graphs can handle multiple nodes in a single user input using splitter nodes:

```python
from intent_kit import rule_splitter_node

splitter = rule_splitter_node(
    name="multi_split",
    children=[greet_action, weather_action]
)

graph = IntentGraphBuilder().root(splitter).build()

# Handle: "Hello Alice and what's the weather in Paris?"
result = graph.route("Hello Alice and what's the weather in Paris?")
# Output: {"greet": "Hello Alice!", "weather": "Weather in Paris is sunny"}
```

## Context Management

Intent graphs support stateful conversations through context:

```python
from intent_kit import IntentContext

context = IntentContext()
context.set("user_name", "Alice")
context.set("conversation_history", [])

result = graph.route("Hello!", context=context)
```

## Error Handling

Intent graphs include comprehensive error handling:

- **Remediation Strategies** - Automatic error recovery
- **Fallback Mechanisms** - Alternative execution paths
- **Error Logging** - Detailed error tracking
- **Graceful Degradation** - Partial success handling

## Visualization

Intent graphs can be visualized for debugging:

```python
# Generate HTML visualization
graph.visualize("graph.html")

# Enable debug mode
graph.route("Hello Alice", debug=True)
```

## LLM Configuration

Intent graphs can be configured with LLM settings for intelligent chunk classification:

```python
# Set LLM configuration at the graph level
llm_config = {
    "provider": "openai",
    "model": "gpt-4",
    "api_key": "your-api-key"
}

graph = (
    IntentGraphBuilder()
    .root(classifier)
    .with_default_llm_config(llm_config)
    .build()
)
```
