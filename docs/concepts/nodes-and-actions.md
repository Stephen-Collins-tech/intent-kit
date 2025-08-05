# Nodes and Actions

Nodes and actions are the fundamental building blocks of intent graphs. They define how user input is processed, classified, and acted upon.

## Architecture Overview

Intent graphs use a **single intent architecture** where:
- **Root nodes must be classifiers** - They classify user input and route to actions
- **Action nodes are leaf nodes** - They execute specific actions and produce outputs
- **No multi-intent splitting** - Each input is handled as a single, focused intent

This architecture ensures deterministic, focused intent processing without the complexity of multi-intent handling.

## Node Types

### Action Nodes

Action nodes execute actions and produce outputs. They are the leaf nodes of intent graphs.

```python
from intent_kit import action

# Basic action
greet_action = action(
    name="greet",
    description="Greet the user",
    action_func=lambda name: f"Hello {name}!",
    param_schema={"name": str}
)

# Action with LLM parameter extraction
weather_action = action(
    name="weather",
    description="Get weather information for a city",
    action_func=lambda city: f"Weather in {city} is sunny",
    param_schema={"city": str}
)
```

#### Action Parameters

- **name** - Unique identifier for the action
- **description** - Human-readable description
- **action_func** - Function to execute
- **param_schema** - Parameter type definitions

#### Argument Extraction

Actions automatically extract parameters from user input using the argument extraction system:

- **RuleBasedArgumentExtractor** - Uses pattern matching and rules for fast extraction
- **LLMArgumentExtractor** - Uses LLM for intelligent parameter extraction
- **Automatic Selection** - Intent Kit chooses the best extractor based on your configuration

```python
from intent_kit import action

# Rule-based extraction (fast, deterministic)
greet_action = action(
    name="greet",
    description="Greet the user",
    action_func=lambda name: f"Hello {name}!",
    param_schema={"name": str},
    argument_extractor="rule"  # Use rule-based extraction
)

# LLM-based extraction (intelligent, flexible)
weather_action = action(
    name="weather",
    description="Get weather information",
    action_func=lambda city: f"Weather in {city} is sunny",
    param_schema={"city": str},
    argument_extractor="llm"  # Use LLM extraction
)
```

#### Error Handling Strategies

Actions support pluggable error handling strategies for robust execution:

```python
from intent_kit import action

# Retry on failure
retry_action = action(
    name="retry_example",
    description="Example with retry strategy",
    action_func=lambda x: x / 0,  # Will fail
    param_schema={"x": float},
    remediation_strategy="retry_on_fail",
    remediation_config={
        "max_attempts": 3,
        "base_delay": 1.0
    }
)

# Fallback to another action
fallback_action = action(
    name="fallback_example",
    description="Example with fallback strategy",
    action_func=lambda x: x / 0,  # Will fail
    param_schema={"x": float},
    remediation_strategy="fallback_to_another_node",
    remediation_config={
        "fallback_name": "safe_calculation"
    }
)

# Self-reflection for parameter correction
reflect_action = action(
    name="reflect_example",
    description="Example with self-reflection",
    action_func=lambda name: f"Hello {name}!",
    param_schema={"name": str},
    remediation_strategy="self_reflect",
    remediation_config={
        "max_reflections": 2,
        "llm_config": {"provider": "openai", "model": "gpt-3.5-turbo"}
    }
)
```

### Classifier Nodes

Classifier nodes route input to appropriate child nodes based on classification logic.

#### LLM Classifier

Uses LLM to classify input:

```python
from intent_kit import llm_classifier

main_classifier = llm_classifier(
    name="main",
    description="Route user input to appropriate action",
    children=[greet_action, weather_action, calculator_action],
    llm_config={"provider": "openai", "model": "gpt-4"}
)
```

## Using JSON Configuration

For more complex workflows, you can define nodes in JSON:

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
graph_config = {
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
                "model": "gpt-3.5-turbo",
            },
            "children": ["greet_action", "weather_action"],
        },
        "greet_action": {
            "id": "greet_action",
            "type": "action",
            "name": "greet_action",
            "description": "Greet the user",
            "function": "greet",
            "param_schema": {"name": "str"},
        },
        "weather_action": {
            "id": "weather_action",
            "type": "action",
            "name": "weather_action",
            "description": "Get weather information",
            "function": "weather",
            "param_schema": {"city": "str"},
        },
    },
}

# Build your graph
graph = (
    IntentGraphBuilder()
    .with_json(graph_config)
    .with_functions(function_registry)
    .build()
)
```

## Parameter Extraction

### Automatic Extraction

When using LLM classifiers, parameters are automatically extracted from natural language:

```python
# Input: "What's the weather in San Francisco?"
# Extracted: {"city": "San Francisco"}

# Input: "Hello Alice"
# Extracted: {"name": "Alice"}
```

### Parameter Schema

Define the expected parameters and their types:

```python
param_schema = {
    "name": str,
    "age": int,
    "city": str,
    "temperature": float
}
```

## Building Graphs

### Using IntentGraphBuilder

```python
from intent_kit import IntentGraphBuilder
from intent_kit.utils.node_factory import action, llm_classifier

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

For complex workflows, JSON configuration provides more flexibility:

```python
# Define your graph in JSON
graph_config = {
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
                "model": "gpt-4"
            },
            "children": ["greet_action", "weather_action"],
        },
        "greet_action": {
            "id": "greet_action",
            "type": "action",
            "name": "greet_action",
            "description": "Greet the user",
            "function": "greet",
            "param_schema": {"name": "str"},
        },
        "weather_action": {
            "id": "weather_action",
            "type": "action",
            "name": "weather_action",
            "description": "Get weather information",
            "function": "weather",
            "param_schema": {"city": "str"},
        },
    },
}

# Build graph
graph = (
    IntentGraphBuilder()
    .with_json(graph_config)
    .with_functions(function_registry)
    .build()
)
```

## Testing Your Workflows

```python
# Test your workflow
result = graph.route("Hello Alice")
print(result.output)  # → "Hello Alice!"

result = graph.route("What's the weather in San Francisco?")
print(result.output)  # → "Weather in San Francisco is sunny"
```

## Best Practices

1. **Keep actions focused** - Each action should do one thing well
2. **Use descriptive names** - Make your action and classifier names clear
3. **Provide good descriptions** - Help the LLM understand what each action does
4. **Test thoroughly** - Use the evaluation framework to test your workflows
5. **Handle errors gracefully** - Make sure your actions can handle unexpected inputs
