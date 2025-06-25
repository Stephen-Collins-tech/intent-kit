# IntentGraph Examples

This directory contains a simple example demonstrating IntentGraph functionality.

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

## Running the Example

```bash
# Simple Demo
python examples/simple_demo.py
```

## What the Demo Shows

The `simple_demo.py` demonstrates:

- **LLM-powered intent classification** - Using LLMs to classify user intents
- **LLM-powered argument extraction** - Extracting structured parameters from natural language
- **Basic IntentGraph setup** - Creating and configuring an IntentGraph
- **Multiple intent types** - Greeting, calculations, weather, and help requests
- **Error handling and debug mode** - How the system handles various inputs

## Example Inputs

The demo tests inputs like:
- "Hello, my name is Alice"
- "What's 15 plus 7?"
- "Weather in San Francisco"
- "Help me"
- "Multiply 8 and 3"

This provides a quick way to see IntentGraph in action with minimal setup and complexity. 