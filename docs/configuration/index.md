# Configuration

Learn how to configure Intent Kit for your specific needs, including LLM integration, JSON serialization, and advanced settings.

## Overview

Intent Kit provides flexible configuration options to adapt to different use cases and environments:

- **LLM Integration** - Configure AI providers and models
- **JSON Serialization** - Define workflows declaratively
- **Environment Management** - Handle different deployment environments
- **Performance Tuning** - Optimize for your specific requirements

## Configuration Topics

### [LLM Integration](llm-integration.md)
Configure AI providers and models for your workflows:
- **OpenAI** - GPT models with function calling
- **Anthropic** - Claude models with strong reasoning
- **Google** - Gemini models with multimodal support
- **Ollama** - Local models for privacy
- **OpenRouter** - Unified access to multiple providers

### [JSON Serialization](json-serialization.md)
Define DAGs using JSON configuration:
- **Declarative Workflows** - Define complete DAGs in JSON
- **Function References** - Reference Python functions directly
- **Portable Configurations** - Share and version workflows
- **Advanced Patterns** - Complex routing and node reuse

## Quick Configuration Guide

### Basic Setup

```python
from intent_kit import DAGBuilder

# Set default LLM configuration
builder = DAGBuilder()
builder.with_default_llm_config({
    "provider": "openrouter",
    "model": "google/gemma-2-9b-it",
    "api_key": "your-api-key"
})
```

### Environment Variables

```bash
# OpenAI
export OPENAI_API_KEY="your-openai-key"

# Anthropic
export ANTHROPIC_API_KEY="your-anthropic-key"

# Google
export GOOGLE_API_KEY="your-google-key"

# OpenRouter
export OPENROUTER_API_KEY="your-openrouter-key"

# Ollama
export OLLAMA_BASE_URL="http://localhost:11434"
```

### JSON Configuration

```python
# Define DAG in JSON
dag_config = {
    "nodes": {
        "classifier": {
            "type": "classifier",
            "output_labels": ["greet", "weather"],
            "description": "Main intent classifier"
        }
    },
    "edges": [
        {"from": "classifier", "to": "greet_action", "label": "greet"}
    ],
    "entrypoints": ["classifier"]
}

# Build from JSON
dag = DAGBuilder.from_json(dag_config)
```

## Configuration Best Practices

### 1. **Environment-Specific Configurations**

```python
import os

def get_llm_config():
    env = os.getenv("ENVIRONMENT", "development")

    if env == "production":
        return {
            "provider": "openai",
            "model": "gpt-4o",
            "temperature": 0.1
        }
    elif env == "development":
        return {
            "provider": "ollama",
            "model": "llama2",
            "temperature": 0.7
        }
    else:
        return {
            "provider": "openrouter",
            "model": "google/gemma-2-9b-it",
            "temperature": 0.5
        }
```

### 2. **Cost Optimization**

```python
# Use appropriate models for different tasks
task_configs = {
    "classification": {
        "provider": "openrouter",
        "model": "google/gemma-2-9b-it",  # Fast, cheap
        "temperature": 0.1
    },
    "extraction": {
        "provider": "openai",
        "model": "gpt-4o",  # Accurate extraction
        "temperature": 0.0
    },
    "conversation": {
        "provider": "anthropic",
        "model": "claude-3-7-sonnet-20250219",  # Good balance
        "temperature": 0.7
    }
}
```

### 3. **Security Considerations**

```python
# Never hardcode API keys
llm_config = {
    "provider": "openai",
    "model": "gpt-4o",
    "api_key": os.getenv("OPENAI_API_KEY")  # Use environment variables
}

# Validate configuration
def validate_config(config):
    required_keys = ["provider", "model", "api_key"]
    for key in required_keys:
        if key not in config or not config[key]:
            raise ValueError(f"Missing required configuration: {key}")
```

### 4. **Performance Tuning**

```python
# Optimize for your use case
performance_config = {
    "provider": "openrouter",
    "model": "google/gemma-2-9b-it",
    "temperature": 0.1,
    "max_tokens": 100,  # Limit response length
    "timeout": 30,      # Set reasonable timeout
    "retries": 3        # Handle transient failures
}
```

## Configuration Validation

### Schema Validation

```python
from intent_kit.core.validation import validate_dag_config

# Validate your configuration
try:
    validate_dag_config(dag_config)
    print("Configuration is valid!")
except ValueError as e:
    print(f"Configuration error: {e}")
```

### Runtime Validation

```python
# Test configuration at runtime
def test_configuration(dag_config):
    try:
        dag = DAGBuilder.from_json(dag_config)
        result = dag.execute("test input")
        print("Configuration works correctly!")
        return True
    except Exception as e:
        print(f"Configuration test failed: {e}")
        return False
```

## Migration Guide

### Updating Configurations

When updating Intent Kit versions, you may need to update your configurations:

1. **Check the changelog** for breaking changes
2. **Test configurations** in a development environment
3. **Update gradually** to minimize risk
4. **Monitor performance** after updates

### Version Compatibility

```python
# Check version compatibility
import intent_kit

print(f"Intent Kit version: {intent_kit.__version__}")

# Use version-specific configurations
if intent_kit.__version__.startswith("0.6"):
    # Use DAG-based configuration
    config = dag_based_config()
else:
    # Use legacy configuration
    config = legacy_config()
```

## Troubleshooting

### Common Issues

1. **API Key Errors**
   - Verify environment variables are set
   - Check API key permissions
   - Ensure provider is supported

2. **Model Not Found**
   - Verify model names are correct
   - Check provider-specific model availability
   - Use fallback models when needed

3. **Configuration Errors**
   - Validate JSON syntax
   - Check required fields
   - Verify function references

### Debug Configuration

```python
import logging

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)

# Test configuration step by step
def debug_configuration(dag_config):
    print("Testing configuration...")

    # Test JSON parsing
    print("✓ JSON is valid")

    # Test node creation
    print("✓ Nodes created successfully")

    # Test edge validation
    print("✓ Edges validated")

    # Test DAG building
    dag = DAGBuilder.from_json(dag_config)
    print("✓ DAG built successfully")

    return dag
```

## Next Steps

- Read [LLM Integration](llm-integration.md) for detailed provider configuration
- Explore [JSON Serialization](json-serialization.md) for declarative workflows
- Check out [Examples](../examples/index.md) for configuration patterns
- Review [Development](../development/index.md) for testing configurations
