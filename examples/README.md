# IntentKit Examples

This directory contains examples demonstrating IntentKit functionality.

## Available Examples

### Simple Demo (`simple_demo.py`)
A basic demonstration of IntentKit with LLM-powered intent classification and argument extraction. Shows the core IntentGraph functionality with multiple AI service backends. **Now includes SplitterNode comparison!**

### Splitter Demo (`splitter_demo.py`)
**NEW!** A comprehensive demonstration of the new SplitterNode functionality. Shows how to split multi-intent user inputs using both rule-based and LLM-powered approaches. Perfect for understanding how to handle complex user requests.

### Context Demo (`context_demo.py`)
Shows how to use context and dependencies in IntentKit. Demonstrates state management, dependency tracking, and multi-turn conversations.

### Ollama Demo (`ollama_demo.py`)
Shows how to use IntentKit with local Ollama models for offline LLM processing. Great for development and testing without API costs.

### Error Demo (`error_demo.py`)
Demonstrates error handling and debugging features. Shows how IntentKit handles various error scenarios and provides detailed error information.

### Validation Demo (`validation_demo.py`) - NEW!
**NEW!** A comprehensive demonstration of the new graph validation system. Shows how to enforce splitter-to-classifier routing constraints and validate graph structure. Perfect for understanding best practices and catching configuration errors early.

## Setup Requirements

### API Keys for LLM Services

Most examples require API keys for LLM services. You can set this up in two ways:

#### Option 1: Environment Variables
Set the following environment variables in your shell:

```bash
export OPENAI_API_KEY="your-openai-api-key"
export ANTHROPIC_API_KEY="your-anthropic-api-key"
export GOOGLE_API_KEY="your-google-api-key"
```

#### Option 2: .env File (Recommended for Development)
Create a `.env` file in the project root with the following content:

```
# LLM API Keys for IntentKit Examples
OPENAI_API_KEY=your-openai-api-key-here
ANTHROPIC_API_KEY=your-anthropic-api-key-here
GOOGLE_API_KEY=your-google-api-key-here
```

**Note:** The examples use different providers by default, but you can modify the `LLM_CONFIG` in each demo to use other providers.

### Installing Dependencies
To use the .env file functionality and run all examples, install the dev dependencies:

```bash
pip install -e ".[dev]"
```

Or install required packages directly:

```bash
pip install python-dotenv
pip install ollama  # For ollama_demo.py
```

## Ollama Demo Setup

The `ollama_demo.py` demonstrates using IntentKit with local Ollama models. This is great for offline development and testing.

### Prerequisites
1. **Install Ollama**: Download and install from [https://ollama.ai/](https://ollama.ai/)
2. **Pull a model**: Run `ollama pull llama2` (or any other model)
3. **Install Python package**: `pip install ollama`
4. **Start Ollama**: The Ollama service should be running locally

### Running the Ollama Demo
```bash
python examples/ollama_demo.py
```

The Ollama demo shows:
- Basic Ollama client usage
- Chat functionality with messages format
- Using Ollama through the LLM factory
- Streaming text generation
- Streaming chat conversations
- Model management (listing, showing, pulling)
- Connecting to custom Ollama servers

## Running the Examples

```bash
# Simple Demo (requires OpenAI API key)
python examples/simple_demo.py

# Splitter Demo (NEW!)
python examples/splitter_demo.py

# Validation Demo (NEW!)
python examples/validation_demo.py

# Ollama Demo (requires Ollama installed)
python examples/ollama_demo.py

# Context Demo
python examples/context_demo.py

# Error Demo
python examples/error_demo.py
```

## What Each Demo Shows

### Simple Demo (`simple_demo.py`)
- **LLM-powered intent classification** - Using LLMs to classify user intents
- **LLM-powered argument extraction** - Extracting structured parameters from natural language
- **Basic IntentGraph setup** - Creating and configuring an IntentGraph
- **Multiple intent types** - Greeting, calculations, weather, and help requests
- **Error handling and debug mode** - How the system handles various inputs
- **Multiple AI backends** - OpenAI, Anthropic, Google AI integration
- **SplitterNode comparison** - Shows traditional vs SplitterNode approaches

### Splitter Demo (`splitter_demo.py`) - NEW!
- **Rule-based splitting** - Using keyword-based logic to split multi-intent inputs
- **LLM-powered splitting** - Using AI to intelligently split complex requests
- **Multi-intent handling** - Processing inputs like "Hello Alice and what's the weather in San Francisco"
- **SplitterNode creation** - Using TreeBuilder to create splitter nodes
- **Child result tracking** - How splitter nodes manage multiple child executions
- **Error handling in splits** - Handling cases where some intents fail

### Context Demo (`context_demo.py`)
- **State management** - Persistent context across multiple interactions
- **Dependency tracking** - Declaring what fields intents read/write
- **Multi-turn conversations** - Maintaining state between user inputs
- **Context history** - Audit trail of all context changes
- **Thread-safe operations** - Safe concurrent access to context

### Ollama Demo (`ollama_demo.py`)
- **Local LLM processing** - Using Ollama for offline LLM operations
- **Multiple Ollama features** - Basic generation, streaming, model listing
- **Factory integration** - Using Ollama through the LLM factory
- **Custom server configuration** - Connecting to different Ollama instances
- **Context-aware workflows** - Full context support with local models

### Error Demo (`error_demo.py`)
- **Error handling** - How IntentKit handles various error scenarios
- **Debug information** - Detailed error reporting and logging
- **Graceful degradation** - Fallback mechanisms when things go wrong
- **Error recovery** - Continuing execution despite individual failures

### Validation Demo (`validation_demo.py`) - NEW!
- **Splitter-to-classifier routing validation** - Enforcing that splitter nodes only route to classifier nodes
- **Graph structure validation** - Checking for cycles, orphaned nodes, and proper node types
- **Automatic validation** - Validation happens automatically when adding root nodes
- **Manual validation** - Manual validation methods for debugging and analysis
- **Comprehensive statistics** - Detailed graph analysis and node counting
- **Error reporting** - Clear error messages with specific node and type information

## Example Inputs

The demos test various inputs to showcase different capabilities:

### Simple Demo Inputs
- "Hello, my name is Alice"
- "What's 15 plus 7?"
- "Weather in San Francisco"
- "Help me"
- "Multiply 8 and 3"
- **Multi-intent inputs:**
  - "Hello Alice and what's the weather in San Francisco"
  - "Calculate 5 plus 3 and also greet Bob"

### Splitter Demo Inputs - NEW!
- **Multi-intent inputs that get split:**
  - "Hello Alice and what's the weather in San Francisco"
  - "Calculate 5 plus 3 and also greet Bob"
  - "Help me and get weather for New York"
  - "Greet John, calculate 10 times 2, and weather in London"

### Context Demo Inputs
- "Hello, my name is Alice"
- "What's my name?"
- "Calculate 10 + 5"
- "What was my last calculation?"
- "Set my preference to metric units"

### Ollama Demo Inputs
- "Hello, my name is Alice"
- "What's 15 plus 7?"
- "Weather in San Francisco"
- "Chat: Tell me a story about a robot"
- "What was my last calculation?"

### Error Demo Inputs
- Invalid inputs to trigger error handling
- Malformed requests to test error recovery
- Edge cases to demonstrate robustness

### Validation Demo Inputs - NEW!
- **Valid graph configurations** - Proper splitter-to-classifier routing
- **Invalid graph configurations** - Splitter nodes routing directly to intent nodes
- **Complex graph structures** - Multi-level graphs with nested classifiers
- **Graph statistics** - Node counting, cycle detection, orphaned node analysis

## Key Features Demonstrated

### Intent Classification
- Keyword-based classification
- LLM-powered classification
- Multi-intent splitting and routing

### SplitterNode Functionality - NEW!
- **Rule-based splitting** - Using conjunctions like "and", "also", "," to split inputs
- **LLM-powered splitting** - AI-driven intelligent splitting of complex requests
- **Multi-intent processing** - Handling multiple intents in a single user input
- **Child result aggregation** - Collecting and organizing results from multiple intents
- **Error handling in splits** - Graceful handling when some intents fail

### Graph Validation System - NEW!
- **Splitter-to-classifier routing constraints** - Enforcing proper pipeline structure
- **Automatic validation** - Validation on graph construction and node addition
- **Manual validation methods** - `validate_graph()`, `validate_splitter_routing()`
- **Comprehensive statistics** - Node counts, cycle detection, orphaned node analysis
- **Clear error reporting** - Specific error messages with node names and types
- **Best practices enforcement** - Ensuring proper graph architecture

### Argument Extraction
- Regex-based extraction
- LLM-powered extraction
- Type validation and conversion

### Context Management
- Session persistence
- Dependency tracking
- Thread-safe operations
- Audit trails

### Error Handling
- Comprehensive error reporting
- Graceful degradation
- Debug information
- Error recovery

### Visualization
- Interactive HTML graphs
- Execution path visualization
- Node type color coding
- Debug information display

## SplitterNode Usage Examples

### Creating a Rule-Based Splitter
```python
from intent_kit.tree import TreeBuilder

splitter = TreeBuilder.rule_splitter_node(
    name="my_splitter",
    children=[intent1, intent2, intent3],
    description="Split multi-intent inputs using rules"
)
```

### Creating an LLM-Powered Splitter
```python
splitter = TreeBuilder.llm_splitter_node(
    name="smart_splitter",
    children=[intent1, intent2, intent3],
    llm_config={"llm_client": my_llm_client},
    description="AI-powered intent splitting"
)
```

### Custom Splitter Function
```python
def my_custom_splitter(user_input: str, debug: bool = False):
    # Custom splitting logic
    return ["part1", "part2", "part3"]

splitter = TreeBuilder.splitter_node(
    name="custom_splitter",
    splitter_function=my_custom_splitter,
    children=[intent1, intent2, intent3]
)
```

This provides a comprehensive way to see IntentKit in action with minimal setup and complexity, including the new SplitterNode functionality for handling complex multi-intent scenarios. 