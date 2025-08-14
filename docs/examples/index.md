# Examples

These examples demonstrate how to use Intent Kit's DAG approach to build intelligent applications.

## Getting Started

- **[Basic Examples](basic-examples.md)** - Fundamental patterns and common use cases
- **[Calculator Bot](calculator-bot.md)** - Simple math operations with natural language processing
- **[Context-Aware Chatbot](context-aware-chatbot.md)** - Basic context persistence across turns

## Advanced Examples

- **[Context Memory Demo](context-memory-demo.md)** - Multi-turn conversations with sophisticated memory management

## Example Categories

### Basic Patterns

The [Basic Examples](basic-examples.md) guide covers essential patterns:

- **Simple Greeting Bot** - Intent classification and parameter extraction
- **Calculator with Multiple Operations** - Multiple intents and operations
- **Weather Information Bot** - Complex parameter extraction and external APIs
- **Task Management System** - Context management and state persistence
- **Customer Support Router** - Complex routing and error handling
- **Data Query System** - Complex data processing and multiple parameter types

### Context Management

Examples showing different ways to use context:

- **Simple State** - Track basic information like user names
- **Complex Memory** - Maintain conversation history and preferences
- **Multi-User Support** - Handle multiple users with separate contexts

### Parameter Extraction

Examples demonstrate parameter extraction for:

- **Simple Parameters** - Names, numbers, locations
- **Complex Parameters** - Calculations, preferences, settings
- **Contextual Parameters** - Information that depends on previous interactions

## Running Examples

All examples can be run with:

```bash
# Set your API key
export OPENAI_API_KEY="your-api-key-here"

# Run an example
python examples/example_name.py
```

## Key Concepts Demonstrated

- **DAG Architecture** - Flexible workflow design with nodes and edges
- **Context Persistence** - Maintaining state across multiple interactions
- **Natural Language Processing** - Understanding user intent and extracting parameters
- **Error Handling** - Graceful handling of unclear or invalid requests
- **Multi-Intent Support** - Handling different types of user requests in a single DAG

## Example Structure

Most examples follow this pattern:

1. **Classifier Node** - Determines user intent
2. **Extractor Node** - Extracts parameters from natural language
3. **Action Node** - Executes the desired action
4. **Clarification Node** - Handles unclear requests

## Best Practices from Examples

### 1. Start Simple
Begin with basic workflows and gradually add complexity. Each example builds on previous concepts.

### 2. Use Descriptive Names
Choose clear, descriptive names for your nodes and actions:
```python
# Good
builder.add_node("extract_user_name", "extractor", ...)
builder.add_node("send_greeting", "action", ...)

# Avoid
builder.add_node("extract", "extractor", ...)
builder.add_node("action1", "action", ...)
```

### 3. Handle Edge Cases
Always consider what happens when:
- Required parameters are missing
- Invalid data is provided
- External services are unavailable

### 4. Test Thoroughly
Test your workflows with various inputs:
```python
test_cases = [
    "Normal case",
    "Edge case",
    "Error case",
    "Empty input",
    "Very long input"
]
```

### 5. Use Context Effectively
Leverage context to maintain state across interactions:
```python
# Store user preferences
context.set("user_preferences", {"language": "en", "timezone": "UTC"})

# Retrieve in later interactions
prefs = context.get("user_preferences", {})
```

## Next Steps

After exploring these examples:

- Read the [Core Concepts](concepts/index.md) to understand the fundamentals
- Check out the [API Reference](api/api-reference.md) for complete documentation
- Explore [Configuration Options](configuration/index.md) for advanced setup
- Review [Development Guides](development/index.md) for testing and deployment
