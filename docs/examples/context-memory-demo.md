# Context Memory Demo

This example demonstrates how to build a sophisticated chatbot that can remember context across multiple turns using Intent Kit's declarative context management system.

## Overview

The Context Memory Demo shows how to:
- Use declarative context read/write configuration
- Remember user information across conversations
- Use context to personalize responses
- Handle multiple intents with a single DAG
- Maintain conversation state with persistent context

## Full Example

```python
import os
from dotenv import load_dotenv
from intent_kit import DAGBuilder, run_dag
from intent_kit.core.context import DefaultContext

load_dotenv()

def remember_name(name: str, **kwargs) -> str:
    """Remember the user's name in context for future interactions."""
    return f"Nice to meet you, {name}! I'll remember your name."

def get_weather(location: str, user_name: Optional[str] = None, **kwargs) -> str:
    """Get weather for a location, using remembered name if available."""
    # Check for user.name from context first, then user_name parameter
    context_user_name = kwargs.get('user.name')
    if context_user_name:
        return f"Hey {context_user_name}! The weather in {location} is sunny and 72°F."
    elif user_name:
        return f"Hey {user_name}! The weather in {location} is sunny and 72°F."
    else:
        return f"Hey there! The weather in {location} is sunny and 72°F."

def get_remembered_name(user_name: Optional[str] = None, **kwargs) -> str:
    """Get the remembered name from context."""
    # Check for user.name from context first, then user_name parameter
    context_user_name = kwargs.get('user.name')
    if context_user_name:
        return f"I remember you! Your name is {context_user_name}."
    elif user_name:
        return f"I remember you! Your name is {user_name}."
    else:
        return "I don't remember your name yet. Try introducing yourself first!"

def create_memory_dag():
    """Create a DAG that can remember context across turns."""
    builder = DAGBuilder()

    # Set default LLM configuration for the entire graph
    builder.with_default_llm_config({
        "provider": "openrouter",
        "api_key": os.getenv("OPENROUTER_API_KEY"),
        "model": "google/gemma-2-9b-it"
    })

    # Add classifier node to determine intent
    builder.add_node("classifier", "classifier",
                     output_labels=["greet", "weather", "remember", "unknown"],
                     description="Classify user intent")

    # Add extractor for name extraction
    builder.add_node("extract_name", "extractor",
                     param_schema={"name": str},
                     description="Extract name from greeting",
                     output_key="name_params")  # Use specific key to avoid conflicts

    # Add extractor for location extraction
    builder.add_node("extract_location", "extractor",
                     param_schema={"location": str},
                     description="Extract location from weather request",
                     output_key="location_params")  # Use specific key to avoid conflicts

    # Add action nodes with context read/write configuration
    builder.add_node("remember_name_action", "action",
                     action=remember_name,
                     description="Remember the user's name",
                     param_keys=["name_params", "extracted_params"],  # Look for name parameters
                     context_write=["user.name", "user.first_seen"])  # Write name to context

    builder.add_node("weather_action", "action",
                     action=get_weather,
                     description="Get weather information",
                     param_keys=["location_params", "extracted_params"],  # Look for location parameters
                     context_read=["user.name"],  # Read user name from context
                     context_write=["weather.requests", "weather.last_location"])  # Write weather data

    builder.add_node("get_name_action", "action",
                     action=get_remembered_name,
                     description="Get remembered name from context",
                     param_keys=["name_params", "extracted_params"],  # Look for name parameters
                     context_read=["user.name"])  # Read user name from context

    # Add clarification node
    builder.add_node("clarification", "clarification",
                     clarification_message="I'm not sure what you'd like me to do. You can greet me, ask about weather, or ask me to remember your name!",
                     available_options=[
                         "Say hello", "Ask about weather", "Ask me to remember your name"],
                     description="Ask for clarification when intent is unclear")

    # Connect nodes
    builder.add_edge("classifier", "extract_name", "greet")
    builder.add_edge("extract_name", "remember_name_action", "success")
    builder.add_edge("classifier", "extract_location", "weather")
    builder.add_edge("extract_location", "weather_action", "success")
    builder.add_edge("classifier", "get_name_action", "remember")
    builder.add_edge("classifier", "clarification", "unknown")
    builder.set_entrypoints(["classifier"])

    return builder.build()

def simulate_conversation():
    """Simulate a multi-turn conversation with context memory."""
    dag = create_memory_dag()
    context = DefaultContext()

    print("=== Context Memory Demo ===\n")

    # Turn 1: User introduces themselves
    print("User: Hi, my name is Alice")
    result, context = run_dag(dag, "Hi, my name is Alice")
    print(f"Bot: {result.data}\n")

    # Turn 2: User asks about weather (bot remembers name)
    print("User: What's the weather like in San Francisco?")
    result, context = run_dag(dag, "What's the weather like in San Francisco?", context)
    print(f"Bot: {result.data}\n")

    # Turn 3: User asks bot to remember their name
    print("User: Do you remember my name?")
    result, context = run_dag(dag, "Do you remember my name?", context)
    print(f"Bot: {result.data}\n")

    # Turn 4: Different user introduces themselves
    print("User: Hello, I'm Bob")
    result, context = run_dag(dag, "Hello, I'm Bob", context)
    print(f"Bot: {result.data}\n")

    # Turn 5: Bob asks about weather (bot uses Bob's name)
    print("User: How's the weather in New York?")
    result, context = run_dag(dag, "How's the weather in New York?", context)
    print(f"Bot: {result.data}\n")

if __name__ == "__main__":
    simulate_conversation()
```

## Running the Demo

When you run this demo, you'll see output like:

```
=== Context Memory Demo ===

User: Hi, my name is Alice
Bot: Nice to meet you, Alice! I'll remember your name.

User: What's the weather like in San Francisco?
Bot: Hey Alice! The weather in San Francisco is sunny and 72°F.

User: Do you remember my name?
Bot: I remember you! Your name is Alice.

User: Hello, I'm Bob
Bot: Nice to meet you, Bob! I'll remember your name.

User: How's the weather in New York?
Bot: Hey Bob! The weather in New York is sunny and 72°F.
```

## Key Features Demonstrated

### 1. **Declarative Context Management**
Nodes explicitly declare their context dependencies:
- `context_read`: Specifies which context keys to read before execution
- `context_write`: Specifies which context keys to write after execution
- `param_keys`: Specifies which parameter keys to check for parameters

### 2. **Context-Aware Action Functions**
Action functions receive context data through `**kwargs`:
- Access context values like `kwargs.get('user.name')`
- Fallback to function parameters if context not available
- No need for global variables or manual context management

### 3. **Parameter Key Configuration**
Action nodes can specify multiple parameter sources:
- `param_keys=["name_params", "extracted_params"]` checks multiple keys
- Prevents parameter conflicts between different extractors
- Enables flexible parameter sourcing

### 4. **Context Persistence**
The bot remembers user information across multiple turns:
- Names are stored and retrieved using `user.name` context key
- Weather requests are tracked with `weather.requests` counter
- Last location is remembered with `weather.last_location`

### 5. **Multi-Intent Classification**
The classifier can handle multiple types of requests:
- Greetings with name introduction
- Weather inquiries
- Memory retrieval requests

### 6. **Parameter Extraction**
Different extractors handle different parameter types:
- Name extraction from greetings (stored in `name_params`)
- Location extraction from weather requests (stored in `location_params`)

### 7. **Flexible Routing**
The DAG routes to different paths based on classification:
- Greeting → Name extraction → Remember action
- Weather → Location extraction → Weather action
- Memory → Direct memory retrieval action

### 8. **Error Handling**
Clarification node handles unclear requests gracefully.

## Advanced Context Features

### Declarative Context Management
This example demonstrates Intent Kit's declarative approach to context management:
- **Explicit Dependencies**: Nodes declare exactly what context they read and write
- **Clear Data Flow**: Context modifications are visible in node configuration
- **Prevent Conflicts**: No accidental overwrites of important context data
- **Self-Documenting**: Context usage is part of the node's configuration

### Context Persistence Patterns
The demo shows several context persistence patterns:
- **User Information**: `user.name`, `user.first_seen` for persistent user data
- **Request Tracking**: `weather.requests` for analytics and counting
- **State Management**: `weather.last_location` for conversation state
- **Parameter Isolation**: `name_params`, `location_params` to avoid conflicts

### Context-Aware Functions
Action functions can access context data seamlessly:
- **Automatic Injection**: Context data is automatically passed to action functions
- **Fallback Logic**: Functions can check both context and parameters
- **Type Safety**: Context values maintain their original types
- **Error Handling**: Graceful handling of missing context data

### Production Context Management
In production applications, you might:
- Use a database for persistent storage across sessions
- Implement user session management with context isolation
- Add context expiration and cleanup policies
- Use distributed context storage for scalability
- Implement context encryption for sensitive data

### Context Security and Auditing
The context system provides:
- **Namespace Protection**: System keys are protected from accidental modification
- **Audit Trails**: All context modifications are tracked with provenance
- **Type Validation**: Context values are validated against expected types
- **Immutable Snapshots**: Context state can be captured for debugging
- **Access Control**: Fine-grained control over context read/write permissions

## Extending the Demo

You can extend this demo by:
- Adding more intents (e.g., calendar, reminders)
- Implementing more sophisticated memory (e.g., conversation history)
- Adding user preferences and settings
- Implementing multi-user support
- Adding natural language generation for responses
