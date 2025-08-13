# Examples

These examples demonstrate how to use Intent Kit's DAG approach to build intelligent applications.

## Getting Started

- **[Calculator Bot](calculator-bot.md)** - Simple math operations with natural language processing
- **[Context-Aware Chatbot](context-aware-chatbot.md)** - Basic context persistence across turns

## Advanced Examples

- **[Context Memory Demo](context-memory-demo.md)** - Multi-turn conversations with sophisticated memory management

## Example Patterns

### Basic DAG Structure

Most examples follow this pattern:

1. **Classifier Node** - Determines user intent
2. **Extractor Node** - Extracts parameters from natural language
3. **Action Node** - Executes the desired action
4. **Clarification Node** - Handles unclear requests

### Context Management

Examples show different ways to use context:

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
