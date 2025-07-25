# IntentKit Examples

This directory contains various examples demonstrating different features of IntentKit.

## Quick Start

### Run All Examples
```bash
# Using uv scripts (recommended)
uv run examples

# Or using bash script from project root
./run_examples.sh
```

### Run a Single Example
```bash
# Using uv scripts (recommended)
uv run example simple_demo
uv run example basic/simple_demo

# Or using bash script from project root
./run_examples.sh -s basic/simple_demo
```

### List Available Examples
```bash
# Using uv scripts
uv run list-examples

# Or using bash script
./run_examples.sh -h  # Shows help with available examples
```

### Check Environment Only
```bash
# Using bash script from project root
./run_examples.sh -c
```

## Available Examples

### Basic Examples (`basic/`)

| Example | Description | Files |
|---------|-------------|-------|
| `simple_demo` | Basic intent graph with LLM classifier | `simple_demo.py`, `simple_demo.json` |
| `ollama_demo` | Local Ollama model integration | `ollama_demo.py`, `ollama_demo.json` |
| `llm_config_demo` | LLM configuration demonstration | `llm_config_demo.py`, `llm_config_demo.json` |

### Context and Debugging (`context-debugging/`)

| Example | Description | Files |
|---------|-------------|-------|
| `context_demo` | Context-aware actions with history tracking | `context_demo.py`, `context_demo.json` |
| `context_debug_demo` | Context debugging features | `context_debug_demo.py`, `context_debug_demo.json` |

### Error Handling and Remediation (`error-handling/`)

| Example | Description | Files |
|---------|-------------|-------|
| `error_demo` | Structured error handling | `error_demo.py`, `error_demo.json` |
| `remediation_demo` | Basic remediation strategies | `remediation_demo.py`, `remediation_demo.json` |
| `advanced_remediation_demo` | Advanced remediation strategies | `advanced_remediation_demo.py`, `advanced_remediation_demo.json` |
| `classifier_remediation_demo` | Classifier remediation strategies | `classifier_remediation_demo.py`, `classifier_remediation_demo.json` |

### API Integration (`api-integration/`)

| Example | Description | Files |
|---------|-------------|-------|
| `json_api_demo` | JSON API demonstration | `json_api_demo.py`, `json_api_demo.json` |
| `custom_client_demo` | Custom LLM client implementation | `custom_client_demo.py`, `custom_client_demo.json` |

### Advanced Examples (`advanced/`)

| Example | Description | Files |
|---------|-------------|-------|
| `multi_intent_demo` | Multi-intent handling with LLM splitting | `multi_intent_demo/` (directory) |
| `eval_api_demo` | Evaluation API demonstration | `eval_api_demo.py` |
| `json_llm_demo` | JSON LLM demonstration (deprecated) | `json_llm_demo.py` |

## Environment Setup

### Required Environment Variables

Most examples require API keys to be set:

```bash
# OpenRouter (for most examples)
export OPENROUTER_API_KEY="your-openrouter-api-key"

# OpenAI (for some examples)
export OPENAI_API_KEY="your-openai-api-key"

# Google (for some examples)
export GOOGLE_API_KEY="your-google-api-key"
```

### Using .env File

Create a `.env` file in the project root:

```bash
OPENROUTER_API_KEY=your-openrouter-api-key
OPENAI_API_KEY=your-openai-api-key
GOOGLE_API_KEY=your-google-api-key
```

### Ollama Setup (for ollama_demo)

If you want to run the Ollama demo, you need to have Ollama installed and running:

```bash
# Install Ollama (macOS)
curl -fsSL https://ollama.ai/install.sh | sh

# Start Ollama
ollama serve

# Pull a model (in another terminal)
ollama pull gemma3:27b
```

## Example Structure

All examples follow the JSON-led pattern:

1. **Python File** (`example.py`): Contains the action functions and main execution logic
2. **JSON File** (`example.json`): Defines the graph structure and configuration

### Python File Structure

```python
# Action functions
def greet_action(name: str, context=None) -> str:
    return f"Hello {name}!"

def calculate_action(operation: str, a: float, b: float, context=None) -> str:
    # Implementation
    pass

# Classifier function
def main_classifier(user_input: str, children, **kwargs):
    # Routing logic
    pass

# Function registry
function_registry = {
    "greet_action": greet_action,
    "calculate_action": calculate_action,
    "main_classifier": main_classifier,
}

# Graph creation
def create_intent_graph():
    json_path = os.path.join(os.path.dirname(__file__), "example.json")
    with open(json_path, "r") as f:
        json_graph = json.load(f)

    return (
        IntentGraphBuilder()
        .with_json(json_graph)
        .with_functions(function_registry)
        .build()
    )
```

### JSON File Structure

```json
{
  "root": "main_classifier",
  "nodes": {
    "main_classifier": {
      "id": "main_classifier",
      "type": "classifier",
      "name": "main_classifier",
      "description": "Main intent classifier",
      "classifier_function": "main_classifier",
      "children": ["greet_action", "calculate_action"]
    },
    "greet_action": {
      "id": "greet_action",
      "type": "action",
      "name": "greet_action",
      "description": "Greet the user",
      "function": "greet_action",
      "param_schema": {"name": "str"}
    },
    "calculate_action": {
      "id": "calculate_action",
      "type": "action",
      "name": "calculate_action",
      "description": "Perform calculations",
      "function": "calculate_action",
      "param_schema": {"operation": "str", "a": "float", "b": "float"}
    }
  }
}
```

## Troubleshooting

### Common Issues

1. **API Key Errors**: Make sure your API keys are set correctly
2. **Import Errors**: Ensure you're running from the project root
3. **Timeout Errors**: Some examples may take longer than 30 seconds
4. **Ollama Connection**: Make sure Ollama is running for ollama_demo

### Debug Mode

To see detailed output from examples, you can run them individually:

```bash
# Direct Python execution
python3 examples/basic/simple_demo.py

# Using uv scripts with verbose output
uv run examples --verbose

# Using bash script with verbose output
./run_examples.sh -v
```

### Skipped Examples

Some examples are automatically skipped by the run scripts:

- `eval_api_demo`: Requires special evaluation setup
- `json_llm_demo`: Deprecated, use `json_api_demo` instead

## Contributing

When adding new examples:

1. Create both `.py` and `.json` files
2. Follow the established naming convention
3. Include proper error handling
4. Add the example to this README
5. Test with the run script

## Script Options

### UV Scripts (Recommended)

```bash
# Run all examples
uv run examples [--verbose] [--timeout SECONDS]

# Run a single example
uv run example EXAMPLE_NAME [--timeout SECONDS]

# List all available examples
uv run list-examples
```

### Bash Script (from project root)

```bash
./run_examples.sh [OPTIONS]

Options:
  -h, --help     Show help message
  -s, --single   Run a single example (requires example name)
  -c, --check    Only check environment, don't run examples
  -v, --verbose  Show detailed output from examples

Examples:
  ./run_examples.sh                       # Run all examples
  ./run_examples.sh -s simple_demo        # Run only simple_demo (searches examples/ subdirectories)
  ./run_examples.sh -s basic/simple_demo  # Run with full path from examples/
  ./run_examples.sh -c                    # Check environment only
  ./run_examples.sh -v                    # Run all examples with verbose output
```
