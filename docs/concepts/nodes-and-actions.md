# Nodes and Actions

Nodes and actions are the fundamental building blocks of intent graphs. They define how user input is processed, classified, and acted upon.

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
    param_schema={"city": str},
    llm_config={"provider": "openai", "model": "gpt-4"}
)
```

#### Action Parameters

- **name** - Unique identifier for the action
- **description** - Human-readable description
- **action_func** - Function to execute
- **param_schema** - Parameter type definitions
- **llm_config** - Optional LLM configuration for parameter extraction
- **context_inputs** - Context keys the action reads
- **context_outputs** - Context keys the action writes
- **remediation_strategies** - Error handling strategies

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

#### Keyword Classifier

Uses keyword matching for classification:

```python
from intent_kit import keyword_classifier

main_classifier = keyword_classifier(
    name="main",
    description="Route user input to appropriate action",
    children=[greet_action, weather_action, calculator_action],
    keywords={"greet": ["hello", "hi"], "weather": ["weather", "forecast"]}
)
```

#### Chunk Classifier

Classifies text chunks for processing:

```python
from intent_kit import chunk_classifier

content_classifier = chunk_classifier(
    name="content",
    description="Classify content types",
    children=[text_action, image_action, audio_action],
    chunk_size=1000
)
```

### Splitter Nodes

Splitter nodes handle multiple nodes in a single input by splitting the input into parts.

#### Rule Splitter

Uses rule-based splitting:

```python
from intent_kit import rule_splitter_node

multi_splitter = rule_splitter_node(
    name="multi_split",
    children=[greet_action, weather_action, calculator_action],
    rules={
        "greet": ["hello", "hi", "greetings"],
        "weather": ["weather", "temperature", "forecast"],
        "calculator": ["add", "subtract", "multiply", "divide"]
    }
)
```

#### LLM Splitter

Uses LLM for intelligent splitting:

```python
from intent_kit import llm_splitter

smart_splitter = llm_splitter(
    name="smart_split",
    children=[greet_action, weather_action],
    llm_config={"provider": "openai", "model": "gpt-4"}
)
```

## Parameter Extraction

### Automatic Extraction

When `llm_config` is provided, parameters are automatically extracted from natural language:

```python
# Input: "What's the weather in San Francisco?"
# Extracted: {"city": "San Francisco"}

weather_action = action(
    name="weather",
    action_func=lambda city: f"Weather in {city} is sunny",
    param_schema={"city": str},
    llm_config={"provider": "openai", "model": "gpt-4"}
)
```

### Manual Extraction

Parameters can be extracted manually using regex or other methods:

```python
import re

def extract_city(text):
    match = re.search(r"weather in (\w+)", text)
    return {"city": match.group(1)} if match else {}

weather_action = action(
    name="weather",
    action_func=lambda city: f"Weather in {city} is sunny",
    param_schema={"city": str},
    param_extractor=extract_city
)
```

## Context Integration

### Reading Context

Handlers can read from context:

```python
def personalized_greet(name, context):
    user_preference = context.get("user_preference", "formal")
    if user_preference == "formal":
        return f"Good day, {name}!"
    else:
        return f"Hey {name}!"

greet_action = action(
    name="greet",
    action_func=personalized_greet,
    param_schema={"name": str},
    context_inputs=["user_preference"]
)
```

### Writing Context

Handlers can write to context:

```python
def track_conversation(name, context):
    history = context.get("conversation_history", [])
    history.append(f"Greeted {name}")
    context.set("conversation_history", history)
    return f"Hello {name}!"

greet_action = action(
    name="greet",
    action_func=track_conversation,
    param_schema={"name": str},
    context_outputs=["conversation_history"]
)
```

## Error Handling

### Remediation Strategies

Handlers can include remediation strategies:

```python
from intent_kit import RetryStrategy, FallbackStrategy

weather_action = action(
    name="weather",
    action_func=get_weather,
    param_schema={"city": str},
    remediation_strategies=[
        RetryStrategy(max_retries=3),
        FallbackStrategy(fallback_func=lambda: "Weather service unavailable")
    ]
)
```

### Error Recovery

Handlers can recover from errors:

```python
def robust_weather(city):
    try:
        return get_weather_api(city)
    except Exception as e:
        return f"Weather information for {city} is currently unavailable"

weather_action = action(
    name="weather",
    action_func=robust_weather,
    param_schema={"city": str}
)
```

## Best Practices

### Naming Conventions

- Use descriptive, lowercase names with underscores
- Prefix classifiers with their type (e.g., `llm_classifier`, `keyword_classifier`)
- Use action-oriented names for actions (e.g., `greet_user`, `get_weather`)

### Parameter Schemas

- Define comprehensive parameter schemas
- Use appropriate types (str, int, float, bool, list, dict)
- Include validation where possible

### Error Handling

- Always include error handling
- Use appropriate remediation strategies
- Provide meaningful error messages

### Documentation

- Write clear descriptions for all nodes
- Document complex parameter extraction logic
- Include usage examples

### Testing

- Test actions with various input scenarios
- Test error conditions and edge cases
- Validate parameter extraction accuracy
