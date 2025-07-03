# IntentKit Examples

This directory contains simplified examples demonstrating IntentKit functionality.

## Available Examples

### Simple Demo (`simple_demo.py`)
A basic demonstration of IntentKit with LLM-powered intent classification and argument extraction. Shows the core IntentGraph functionality with a **pass-through splitter** (default behavior).

### Multi-Intent Demo (`multi_intent_demo.py`)
**NEW!** A demonstration of multi-intent handling using the rule-based splitter. Shows how to handle complex inputs like "Hello Alice and what's the weather in San Francisco".

### Error Demo (`error_demo.py`)
A demonstration of error handling and debugging features. Shows how to handle various error scenarios and debug intent routing issues.

### Context Demo (`context_demo.py`)
A demonstration of context and dependency management. Shows how handlers can read from and write to shared context.

### Ollama Demo (`ollama_demo.py`)
A demonstration of using IntentKit with local Ollama models. Shows how to configure and use local LLM models.

## Default Behavior

By default, IntentKit uses a **pass-through splitter** that doesn't split user input. This is the safest approach for most use cases, as it avoids accidentally splitting inputs like "What's 15 plus 7?" on mathematical operators.

If you need multi-intent handling, explicitly configure the rule-based splitter:

```python
from intent_kit.splitters import rule_splitter

return IntentGraphBuilder().root(classifier).splitter(rule_splitter).build()
```

## Running the Examples

1. Set up your environment variables (see individual demos for requirements)
2. Run any demo: `python examples/simple_demo.py`
3. For Ollama demo, ensure Ollama is running and you have a model pulled

## Key Features Demonstrated

- **Intent Classification**: LLM-powered intent routing
- **Argument Extraction**: Automatic parameter extraction from user input
- **Context Management**: Shared state across handlers
- **Error Handling**: Robust error handling and debugging
- **Multi-Intent**: Handling complex, multi-part requests
- **Local Models**: Using Ollama for local LLM processing

## Quick Start

### Minimal Example
```python
from intent_kit import IntentGraphBuilder, handler, llm_classifier

def create_intent_graph():
    handlers = [
        handler(
            name="greet",
            description="Greet the user",
            handler_func=lambda name: f"Hello {name}!",
            param_schema={"name": str}
        ),
        handler(
            name="calculate",
            description="Perform a calculation",
            handler_func=lambda operation, a, b: f"{a} {operation} {b} = {eval(f'{a} {operation} {b}')}",
            param_schema={"operation": str, "a": float, "b": float}
        )
    ]
    
    classifier = llm_classifier(
        name="root",
        children=handlers,
        llm_config={},  # Empty config uses fallback classification
        description="Main intent classifier"
    )
    
    return IntentGraphBuilder().root(classifier).build()

# Use the graph
graph = create_intent_graph()
result = graph.route("Hello, my name is Alice")
print(result.output)  # "Hello Alice!"
```

## Setup Requirements

### API Keys for LLM Services (Optional)

For LLM-powered features, you can set up API keys:

#### Option 1: Environment Variables
```bash
export OPENAI_API_KEY="your-openai-api-key"
export ANTHROPIC_API_KEY="your-anthropic-api-key"
export GOOGLE_API_KEY="your-google-api-key"
```

#### Option 2: .env File
Create a `.env` file in the project root:
```
OPENAI_API_KEY=your-openai-api-key-here
ANTHROPIC_API_KEY=your-anthropic-api-key-here
GOOGLE_API_KEY=your-google-api-key-here
```

**Note:** The minimal and rule-based demos work without any API keys!

## Running the Examples

```bash
# Start with the minimal demo (no API key required)
python examples/minimal_demo.py

# Simple demo with LLM features
python examples/simple_demo.py

# Splitter demo for multi-intent handling
python examples/splitter_demo.py

# New API demo showing different configurations
python examples/new_api_demo.py

# Rule-based demo (no API key required)
python examples/rule_based_demo.py
```

## What Each Demo Shows

### Minimal Demo (`minimal_demo.py`)
- **Simplest configuration** - Absolute minimum code needed
- **No API dependencies** - Works without any LLM API keys
- **Basic intent handling** - Greeting and calculation intents
- **Fallback classification** - Uses simple keyword matching

### Simple Demo (`simple_demo.py`)
- **LLM-powered classification** - Using LLMs to classify user intents
- **LLM-powered argument extraction** - Extracting structured parameters
- **Multiple intent types** - Greeting, calculations, weather, and help
- **Error handling** - How the system handles various inputs

### Splitter Demo (`splitter_demo.py`)
- **Multi-intent handling** - Processing complex requests
- **Rule-based splitting** - Keyword-based logic for splitting
- **LLM-powered splitting** - AI-powered intelligent splitting
- **Child result tracking** - Managing multiple executions

### New API Demo (`new_api_demo.py`)
- **Mixed configurations** - LLM-based and rule-based extraction
- **Different handler types** - Various parameter extraction methods
- **Auto-wired descriptions** - Automatic classifier configuration

### Rule-Based Demo (`rule_based_demo.py`)
- **No LLM dependencies** - Works entirely offline
- **Fallback behavior** - Simple keyword-based classification
- **Rule-based extraction** - Basic parameter extraction
- **Offline development** - Perfect for testing without API costs

## Example Inputs

### Minimal Demo Inputs
- "Hello, my name is Alice"
- "What's 15 plus 7?"
- "Help me"

### Simple Demo Inputs
- "Hello, my name is Alice"
- "What's 15 plus 7?"
- "Weather in San Francisco"
- "Help me"
- "Multiply 8 and 3"

### Splitter Demo Inputs
- "Hello Alice and what's the weather in San Francisco"
- "Calculate 5 plus 3 and also greet Bob"
- "Help me and get weather for New York"

## Key Concepts

### Handler Configuration
```python
# LLM-based argument extraction
handler(
    name="greet",
    description="Greet the user",
    handler_func=lambda name: f"Hello {name}!",
    param_schema={"name": str},
    llm_config=LLM_CONFIG  # Enables LLM extraction
)

# Rule-based argument extraction
handler(
    name="greet",
    description="Greet the user", 
    handler_func=lambda name: f"Hello {name}!",
    param_schema={"name": str}
    # No llm_config = rule-based extraction
)
```

### Classifier Configuration
```python
# LLM-powered classification
llm_classifier(
    name="root",
    children=handlers,
    llm_config=LLM_CONFIG,
    description="Main classifier"
)

# Fallback classification (no API key needed)
llm_classifier(
    name="root",
    children=handlers,
    llm_config={},  # Empty config uses fallback
    description="Main classifier"
)
```

### Graph Building
```python
# Simple graph
graph = IntentGraphBuilder().root(classifier).build()

# With splitter for multi-intent
graph = IntentGraphBuilder().root(splitter).build()
```

## Next Steps

1. **Start with `minimal_demo.py`** - Understand the basic structure
2. **Try `rule_based_demo.py`** - See how it works without LLMs
3. **Explore `simple_demo.py`** - Add LLM-powered features
4. **Check `splitter_demo.py`** - Handle complex multi-intent inputs
5. **Review `new_api_demo.py`** - Mix different configuration approaches

All demos are designed to be minimal and focused on the intent graph configuration, with minimal boilerplate code. 