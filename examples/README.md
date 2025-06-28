# IntentGraph Examples

This directory contains examples demonstrating IntentGraph functionality.

## Available Examples

### Simple Demo (`simple_demo.py`)
A basic demonstration of IntentGraph with LLM-powered intent classification and argument extraction.

### Context Demo (`context_demo.py`)
Shows how to use context and dependencies in IntentGraph.

### Error Demo (`error_demo.py`)
Demonstrates error handling and debugging features.

### Ollama Demo (`ollama_demo.py`)
Shows how to use IntentGraph with local Ollama models for offline LLM processing.

## Simple Demo Setup

The `simple_demo.py` requires an API key for LLM services. You can set this up in two ways:

### Option 1: Environment Variables
Set the following environment variable in your shell:

```bash
export OPENAI_API_KEY="your-openai-api-key"
```

### Option 2: .env File (Recommended for Development)
Create a `.env` file in the project root with the following content:

```
# LLM API Key for IntentGraph Demo
OPENAI_API_KEY=your-openai-api-key-here
```

**Note:** The demo uses OpenAI by default, but you can modify the `LLM_CONFIG` in the demo to use other providers.

### Installing python-dotenv
To use the .env file functionality, install the dev dependencies:

```bash
pip install -e ".[dev]"
```

Or install python-dotenv directly:

```bash
pip install python-dotenv
```

## Ollama Demo Setup

The `ollama_demo.py` demonstrates using IntentGraph with local Ollama models. This is great for offline development and testing.

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
# Simple Demo
python examples/simple_demo.py

# Ollama Demo
python examples/ollama_demo.py

# Context Demo
python examples/context_demo.py

# Error Demo
python examples/error_demo.py
```

## What the Demos Show

### Simple Demo
- **LLM-powered intent classification** - Using LLMs to classify user intents
- **LLM-powered argument extraction** - Extracting structured parameters from natural language
- **Basic IntentGraph setup** - Creating and configuring an IntentGraph
- **Multiple intent types** - Greeting, calculations, weather, and help requests
- **Error handling and debug mode** - How the system handles various inputs

### Ollama Demo
- **Local LLM processing** - Using Ollama for offline LLM operations
- **Multiple Ollama features** - Basic generation, streaming, model listing
- **Factory integration** - Using Ollama through the LLM factory
- **Custom server configuration** - Connecting to different Ollama instances

## Example Inputs

The simple demo tests inputs like:
- "Hello, my name is Alice"
- "What's 15 plus 7?"
- "Weather in San Francisco"
- "Help me"
- "Multiply 8 and 3"

This provides a quick way to see IntentGraph in action with minimal setup and complexity. 