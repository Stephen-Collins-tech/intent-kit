# Context Memory Demo

This example demonstrates how to build a sophisticated chatbot that can remember context across multiple turns using Intent Kit's DAG approach.

## Overview

The Context Memory Demo shows how to:
- Remember user information across conversations
- Use context to personalize responses
- Handle multiple intents with a single DAG
- Maintain conversation state

## Full Example

```python
import os
from dotenv import load_dotenv
from intent_kit import DAGBuilder, run_dag
from intent_kit.core.context import DefaultContext

load_dotenv()

# Global context for this demo (in a real app, you'd use a proper context management system)
_global_context = {}

def remember_name(name: str, **kwargs) -> str:
    """Remember the user's name in context for future interactions."""
    global _global_context
    _global_context["user.name"] = name
    return f"Nice to meet you, {name}! I'll remember your name."

def get_weather(location: str, **kwargs) -> str:
    """Get weather for a location, using remembered name if available."""
    global _global_context
    user_name = _global_context.get("user.name", "there")
    return f"Hey {user_name}! The weather in {location} is sunny and 72°F."

def get_remembered_name(**kwargs) -> str:
    """Get the remembered name from context."""
    global _global_context
    name = _global_context.get("user.name")
    if name:
        return f"I remember you! Your name is {name}."
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
                     output_key="extracted_params")

    # Add extractor for location extraction
    builder.add_node("extract_location", "extractor",
                     param_schema={"location": str},
                     description="Extract location from weather request",
                     output_key="extracted_params")

    # Add action nodes
    builder.add_node("remember_name_action", "action",
                     action=remember_name,
                     description="Remember the user's name")

    builder.add_node("weather_action", "action",
                     action=get_weather,
                     description="Get weather information")

    builder.add_node("get_name_action", "action",
                     action=get_remembered_name,
                     description="Get remembered name from context")

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
    result = run_dag(dag, "Hi, my name is Alice", context)
    print(f"Bot: {result.data}\n")

    # Turn 2: User asks about weather (bot remembers name)
    print("User: What's the weather like in San Francisco?")
    result = run_dag(dag, "What's the weather like in San Francisco?", context)
    print(f"Bot: {result.data}\n")

    # Turn 3: User asks bot to remember their name
    print("User: Do you remember my name?")
    result = run_dag(dag, "Do you remember my name?", context)
    print(f"Bot: {result.data}\n")

    # Turn 4: Different user introduces themselves
    print("User: Hello, I'm Bob")
    result = run_dag(dag, "Hello, I'm Bob", context)
    print(f"Bot: {result.data}\n")

    # Turn 5: Bob asks about weather (bot uses Bob's name)
    print("User: How's the weather in New York?")
    result = run_dag(dag, "How's the weather in New York?", context)
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

### 1. **Multi-Intent Classification**
The classifier can handle multiple types of requests:
- Greetings with name introduction
- Weather inquiries
- Memory retrieval requests

### 2. **Context Persistence**
The bot remembers user information across multiple turns:
- Names are stored and retrieved
- Personalized responses based on remembered data

### 3. **Parameter Extraction**
Different extractors handle different parameter types:
- Name extraction from greetings
- Location extraction from weather requests

### 4. **Flexible Routing**
The DAG routes to different paths based on classification:
- Greeting → Name extraction → Remember action
- Weather → Location extraction → Weather action
- Memory → Direct memory retrieval action

### 5. **Error Handling**
Clarification node handles unclear requests gracefully.

## Advanced Context Features

### Global Context Management
This example uses a simple global dictionary, but in production you might:
- Use a database for persistent storage
- Implement user session management
- Add context expiration and cleanup
- Use distributed context storage for scalability

### Context Security
The context system provides:
- Namespace protection for system keys
- Audit trails for context modifications
- Type validation for context values
- Immutable snapshots for debugging

## Extending the Demo

You can extend this demo by:
- Adding more intents (e.g., calendar, reminders)
- Implementing more sophisticated memory (e.g., conversation history)
- Adding user preferences and settings
- Implementing multi-user support
- Adding natural language generation for responses
