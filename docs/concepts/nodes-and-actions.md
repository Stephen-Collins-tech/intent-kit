# Nodes and Actions

Nodes and actions are the fundamental building blocks of intent DAGs. They define how user input is processed, classified, extracted, and acted upon.

## Architecture Overview

Intent DAGs use a **flexible node architecture** where:
- **Classifier nodes** - Classify user input and route to appropriate paths
- **Extractor nodes** - Extract parameters from user input using LLM
- **Action nodes** - Execute specific actions and produce outputs
- **Clarification nodes** - Handle unclear intent by asking for clarification

This architecture provides flexible, scalable intent processing with clear separation of concerns.

## Node Types

### Classifier Nodes

Classifier nodes route input to appropriate child nodes based on classification logic.

```python
from intent_kit import DAGBuilder

builder = DAGBuilder()

# LLM-based classifier
builder.add_node("classifier", "classifier",
                 output_labels=["greet", "weather", "calculate"],
                 description="Route user input to appropriate action",
                 llm_config={"provider": "openai", "model": "gpt-4"})

# Custom classifier function
def custom_classifier(user_input: str, context) -> str:
    if "hello" in user_input.lower():
        return "greet"
    elif "weather" in user_input.lower():
        return "weather"
    return "unknown"

builder.add_node("custom_classifier", "classifier",
                 output_labels=["greet", "weather", "unknown"],
                 description="Custom classification logic",
                 classification_func=custom_classifier)
```

#### Classifier Parameters

- **output_labels** - List of possible classification outputs
- **description** - Human-readable description for LLM
- **llm_config** - LLM configuration for AI-based classification
- **classification_func** - Custom function for classification (overrides LLM)

### Extractor Nodes

Extractor nodes use LLM to extract parameters from natural language input.

```python
# Extract name from greeting
builder.add_node("extract_name", "extractor",
                 param_schema={"name": str},
                 description="Extract name from greeting",
                 output_key="extracted_params")

# Extract calculation parameters
builder.add_node("extract_calc", "extractor",
                 param_schema={"operation": str, "a": float, "b": float},
                 description="Extract calculation parameters",
                 output_key="extracted_params")
```

#### Extractor Parameters

- **param_schema** - Dictionary defining expected parameters and their types
- **description** - Human-readable description for LLM
- **output_key** - Key in context where extracted parameters are stored
- **llm_config** - Optional LLM configuration (uses default if not specified)

### Action Nodes

Action nodes execute actions and produce outputs. They are typically terminal nodes in the DAG.

```python
from intent_kit import DAGBuilder

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

# Basic action
builder.add_node("greet_action", "action",
                 action=greet,
                 description="Greet the user")

# Action with parameters from context
builder.add_node("weather_action", "action",
                 action=get_weather,
                 description="Get weather information for a city")

# Complex action
builder.add_node("calculate_action", "action",
                 action=calculate,
                 description="Perform mathematical calculations")
```

#### Action Parameters

- **action** - Function to execute
- **description** - Human-readable description
- **terminate_on_success** - Whether to terminate after successful execution (default: True)
- **param_key** - Key in context to get parameters from (default: "extracted_params")

### Clarification Nodes

Clarification nodes handle unclear intent by asking for clarification.

```python
builder.add_node("clarification", "clarification",
                 clarification_message="I'm not sure what you'd like me to do. You can greet me, ask about weather, or perform calculations!",
                 available_options=["Say hello", "Ask about weather", "Calculate something"],
                 description="Ask for clarification when intent is unclear")
```

#### Clarification Parameters

- **clarification_message** - Message to display to the user
- **available_options** - List of options the user can choose from
- **description** - Human-readable description

## Building DAGs

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

# Add classifier
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

# Add actions
builder.add_node("greet_action", "action",
                 action=greet,
                 description="Greet the user")

builder.add_node("weather_action", "action",
                 action=get_weather,
                 description="Get weather information")

# Add clarification
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

For complex workflows, JSON configuration provides more flexibility:

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
            "llm_config": {
                "provider": "openai",
                "model": "gpt-4"
            }
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

## Parameter Extraction

### Automatic Extraction

When using extractor nodes, parameters are automatically extracted from natural language:

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
    "temperature": float,
    "is_active": bool
}
```

### Context Integration

Parameters are stored in context and can be accessed by actions:

```python
def greet(name: str, context=None) -> str:
    # Access additional context if needed
    user_preference = context.get("user.preference", "formal") if context else "formal"
    if user_preference == "casual":
        return f"Hey {name}!"
    return f"Hello {name}!"
```

## Testing Your Workflows

```python
# Test your DAG
context = DefaultContext()
result = run_dag(dag, "Hello Alice", context)
print(result.data)  # → "Hello Alice!"

result = run_dag(dag, "What's the weather in San Francisco?", context)
print(result.data)  # → "Weather in San Francisco is sunny"
```

## Error Handling

### Built-in Error Handling

DAGs provide robust error handling:

```python
# Add error handling edges
builder.add_edge("extract_name", "clarification", "error")
builder.add_edge("greet_action", "clarification", "error")
```

### Custom Error Handling

Actions can handle errors gracefully:

```python
def safe_calculate(operation: str, a: float, b: float) -> str:
    try:
        if operation == "add":
            return str(a + b)
        elif operation == "divide":
            if b == 0:
                return "Error: Cannot divide by zero"
            return str(a / b)
        return "Unknown operation"
    except Exception as e:
        return f"Error: {str(e)}"
```

## Best Practices

1. **Keep actions focused** - Each action should do one thing well
2. **Use descriptive names** - Make your node names clear
3. **Provide good descriptions** - Help the LLM understand what each node does
4. **Test thoroughly** - Use the evaluation framework to test your workflows
5. **Handle errors gracefully** - Make sure your actions can handle unexpected inputs
6. **Use context effectively** - Leverage context for stateful operations
7. **Document your schemas** - Keep parameter schemas well-documented
