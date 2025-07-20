# Intent Graphs

Intent graphs are the core architectural concept in intent-kit. They provide a hierarchical, deterministic way to route user input through a series of classifiers and handlers to produce structured outputs.

## Overview

An intent graph is a directed acyclic graph (DAG) where:

- **Nodes** represent decision points or actions
- **Edges** represent the flow between nodes
- **Root nodes** are entry points for user input
- **Leaf nodes** are actions that produce outputs

## Graph Structure

```
User Input → Root Classifier → Intent Classifier → Action → Output
```

### Node Types

1. **Classifier Nodes** - Route input to appropriate child nodes
2. **Action Nodes** - Execute actions and produce outputs
3. **Splitter Nodes** - Handle multiple intents in single input

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
graph = IntentGraphBuilder().root(main_classifier).with_llm_config({
    "provider": "openai",
    "model": "gpt-4"
}).build()
```

### Using JSON Configuration

```python
from intent_kit import IntentGraphBuilder

json_graph = {
    "root": "main_classifier",
    "intents": {
        "main_classifier": {
            "type": "llm_classifier",
            "children": ["greet_action", "weather_action"],
            "llm_config": {"provider": "openai", "model": "gpt-4"}
        },
        "greet_action": {
            "type": "action",
            "function": "greet_function",
            "param_schema": {"name": "str"}
        },
        "weather_action": {
            "type": "action",
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

## Execution Flow

1. **Input Processing** - User input is received
2. **Root Classification** - Input is classified by root nodes
3. **Intent Routing** - Input is routed to appropriate actions
4. **Parameter Extraction** - Parameters are extracted from input
5. **Action Execution** - Action functions are executed
6. **Output Generation** - Structured output is returned

## Multi-Intent Routing

Intent graphs can handle multiple intents in a single user input using splitter nodes:

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
    .with_llm_config(llm_config)
    .build()
)
```

The `llm_config` is used by the chunk classifier to determine how to process user input:
- **Atomic chunks** - Single intents that can be handled directly
- **Composite chunks** - Multiple intents that need to be split
- **Ambiguous chunks** - Unclear intents that need clarification
- **Invalid chunks** - Input that should be rejected

## Best Practices

1. **Clear Node Names** - Use descriptive names for all nodes
2. **Proper Descriptions** - Provide clear descriptions for classifiers
3. **Parameter Validation** - Define comprehensive parameter schemas
4. **Error Handling** - Include remediation strategies
5. **Testing** - Test with various input scenarios
6. **Documentation** - Document complex graph structures
7. **LLM Configuration** - Set appropriate LLM config for chunk classification
