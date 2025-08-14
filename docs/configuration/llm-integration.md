# LLM Integration

Intent Kit supports multiple Large Language Model (LLM) providers, allowing you to choose the best AI service for your needs. This guide covers configuration, best practices, and provider-specific features.

## Supported Providers

### OpenAI

OpenAI provides access to GPT models including GPT-3.5-turbo and GPT-4.

#### Configuration

```python
llm_config = {
    "provider": "openai",
    "model": "gpt-5-2025-08-07",  # or "gpt-4", "gpt-4-turbo"
    "api_key": "your-openai-api-key",
    "temperature": 0.1,
    "max_tokens": 1000
}
```

#### Environment Variable

```bash
export OPENAI_API_KEY="your-openai-api-key"
```

#### Features

- **Fast response times** - Optimized for real-time applications
- **Cost-effective** - Competitive pricing for most use cases
- **Reliable** - High availability and uptime
- **Function calling** - Native support for structured outputs

#### Best Practices

- Use `gpt-3.5-turbo` for classification and extraction tasks
- Use `gpt-4` for complex reasoning tasks
- Set `temperature` to 0.1-0.3 for consistent results
- Monitor token usage to control costs

### Anthropic

Anthropic provides access to Claude models with strong reasoning capabilities.

#### Configuration

```python
llm_config = {
    "provider": "anthropic",
    "model": "claude-3-sonnet-20240229",  # or "claude-3-haiku", "claude-3-opus"
    "api_key": "your-anthropic-api-key",
    "temperature": 0.1,
    "max_tokens": 1000
}
```

#### Environment Variable

```bash
export ANTHROPIC_API_KEY="your-anthropic-api-key"
```

#### Features

- **Strong reasoning** - Excellent for complex decision-making
- **Safety-focused** - Built with safety and alignment in mind
- **Long context** - Support for large conversation histories
- **Structured outputs** - Native support for JSON and other formats

#### Best Practices

- Use `claude-3-sonnet` for most tasks (good balance of speed and capability)
- Use `claude-3-opus` for complex reasoning tasks
- Use `claude-3-haiku` for simple, fast tasks
- Leverage long context for multi-turn conversations

### Google

Google provides access to Gemini models with strong multimodal capabilities.

#### Configuration

```python
llm_config = {
    "provider": "google",
    "model": "gemini-pro",  # or "gemini-pro-vision"
    "api_key": "your-google-api-key",
    "temperature": 0.1,
    "max_tokens": 1000
}
```

#### Environment Variable

```bash
export GOOGLE_API_KEY="your-google-api-key"
```

#### Features

- **Multimodal** - Support for text, images, and other media
- **Cost-effective** - Competitive pricing
- **Fast inference** - Optimized for real-time applications
- **Google ecosystem** - Integration with Google Cloud services

#### Best Practices

- Use `gemini-pro` for text-based tasks
- Use `gemini-pro-vision` for image-related tasks
- Leverage Google Cloud integration for enterprise features
- Monitor usage through Google Cloud Console

### Ollama

Ollama allows you to run open-source models locally on your machine.

#### Configuration

```python
llm_config = {
    "provider": "ollama",
    "model": "llama2",  # or "mistral", "codellama", "llama2:13b"
    "base_url": "http://localhost:11434",  # Default Ollama URL
    "temperature": 0.1
}
```

#### Installation

```bash
# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Pull a model
ollama pull llama2
```

#### Features

- **Local deployment** - No API keys or external dependencies
- **Privacy** - Data stays on your machine
- **Customizable** - Fine-tune models for your specific needs
- **Cost-effective** - No per-token charges

#### Best Practices

- Use appropriate model sizes for your hardware
- Consider using quantized models for better performance
- Monitor memory usage with large models
- Use GPU acceleration when available

### OpenRouter

OpenRouter provides access to multiple AI providers through a unified API.

#### Configuration

```python
llm_config = {
    "provider": "openrouter",
    "model": "openai/gpt-3.5-turbo",  # or "anthropic/claude-3-sonnet"
    "api_key": "your-openrouter-api-key",
    "base_url": "https://openrouter.ai/api/v1",
    "temperature": 0.1
}
```

#### Environment Variable

```bash
export OPENROUTER_API_KEY="your-openrouter-api-key"
```

#### Features

- **Provider agnostic** - Access multiple AI providers
- **Cost comparison** - Compare pricing across providers
- **Unified API** - Single interface for multiple providers
- **Model marketplace** - Access to many different models

## Configuration Options

### Common Parameters

All providers support these common configuration options:

```python
llm_config = {
    "provider": "openai",  # Required: Provider name
    "model": "gpt-3.5-turbo",  # Required: Model name
    "api_key": "your-api-key",  # Required: API key
    "temperature": 0.1,  # Optional: Sampling temperature (0.0-2.0)
    "max_tokens": 1000,  # Optional: Maximum tokens to generate
    "timeout": 30,  # Optional: Request timeout in seconds
    "retries": 3,  # Optional: Number of retry attempts
}
```

### Provider-Specific Options

#### OpenAI

```python
llm_config = {
    "provider": "openai",
    "model": "gpt-3.5-turbo",
    "api_key": "your-api-key",
    "temperature": 0.1,
    "max_tokens": 1000,
    "top_p": 1.0,  # Nucleus sampling
    "frequency_penalty": 0.0,  # Frequency penalty
    "presence_penalty": 0.0,  # Presence penalty
}
```

#### Anthropic

```python
llm_config = {
    "provider": "anthropic",
    "model": "claude-3-sonnet-20240229",
    "api_key": "your-api-key",
    "temperature": 0.1,
    "max_tokens": 1000,
    "top_p": 1.0,  # Top-p sampling
    "top_k": 40,  # Top-k sampling
}
```

#### Google

```python
llm_config = {
    "provider": "google",
    "model": "gemini-pro",
    "api_key": "your-api-key",
    "temperature": 0.1,
    "max_tokens": 1000,
    "top_p": 1.0,  # Top-p sampling
    "top_k": 40,  # Top-k sampling
}
```

## Usage Examples

### Basic Configuration

```python
from intent_kit import DAGBuilder

# Create builder with default LLM config
builder = DAGBuilder()
builder.with_default_llm_config({
    "provider": "openai",
    "model": "gpt-3.5-turbo",
    "api_key": "your-api-key",
    "temperature": 0.1
})

# Add nodes (they'll use the default config)
builder.add_node("classifier", "classifier",
                 output_labels=["greet", "calculate"],
                 description="Main intent classifier")
```

### Per-Node Configuration

```python
# Override LLM config for specific nodes
builder.add_node("classifier", "classifier",
                 output_labels=["greet", "calculate"],
                 description="Main intent classifier",
                 llm_config={
                     "provider": "anthropic",
                     "model": "claude-3-sonnet-20240229",
                     "api_key": "your-anthropic-api-key",
                     "temperature": 0.1
                 })
```

### JSON Configuration

```python
dag_config = {
    "default_llm_config": {
        "provider": "openai",
        "model": "gpt-3.5-turbo",
        "api_key": "your-api-key",
        "temperature": 0.1
    },
    "nodes": {
        "classifier": {
            "type": "classifier",
            "output_labels": ["greet", "calculate"],
            "description": "Main intent classifier"
        },
        "extractor": {
            "type": "extractor",
            "param_schema": {"name": str},
            "description": "Extract name from greeting",
            "llm_config": {
                "provider": "anthropic",
                "model": "claude-3-sonnet-20240229",
                "api_key": "your-anthropic-api-key"
            }
        }
    }
}
```

## Best Practices

### Model Selection

1. **Classification Tasks**: Use faster, cheaper models (GPT-3.5-turbo, Claude-3-haiku)
2. **Extraction Tasks**: Use models with good instruction following (GPT-3.5-turbo, Claude-3-sonnet)
3. **Complex Reasoning**: Use more capable models (GPT-4, Claude-3-opus)
4. **Privacy-Sensitive**: Use local models (Ollama)

### Temperature Settings

- **0.0-0.2**: Consistent, deterministic outputs (recommended for classification)
- **0.2-0.5**: Balanced creativity and consistency
- **0.5-1.0**: More creative, varied outputs
- **1.0+**: Highly creative, less predictable

### Cost Optimization

1. **Use appropriate models** - Don't use GPT-4 for simple tasks
2. **Set reasonable limits** - Use `max_tokens` to control costs
3. **Cache results** - Implement caching for repeated requests
4. **Monitor usage** - Track token consumption and costs
5. **Use local models** - Consider Ollama for development and testing

### Error Handling

```python
from intent_kit.core.exceptions import LLMError

try:
    result = dag.execute("Hello Alice", context)
except LLMError as e:
    print(f"LLM error: {e}")
    # Handle rate limits, API errors, etc.
```

### Rate Limiting

```python
llm_config = {
    "provider": "openai",
    "model": "gpt-3.5-turbo",
    "api_key": "your-api-key",
    "retries": 3,
    "retry_delay": 1.0,  # Seconds between retries
    "timeout": 30
}
```

## Troubleshooting

### Common Issues

#### API Key Errors

```python
# Check environment variables
import os
print(os.getenv("OPENAI_API_KEY"))  # Should not be None
```

#### Rate Limiting

```python
# Implement exponential backoff
llm_config = {
    "retries": 5,
    "retry_delay": 2.0,
    "backoff_factor": 2.0
}
```

#### Model Not Found

```python
# Check model names
# OpenAI: "gpt-3.5-turbo", "gpt-4"
# Anthropic: "claude-3-sonnet-20240229", "claude-3-haiku"
# Google: "gemini-pro", "gemini-pro-vision"
# Ollama: "llama2", "mistral", "codellama"
```

#### Timeout Issues

```python
# Increase timeout for complex tasks
llm_config = {
    "timeout": 60,  # 60 seconds
    "max_tokens": 2000
}
```

## Migration Guide

### Switching Providers

To switch from one provider to another:

1. **Update configuration**:
   ```python
   # From OpenAI
   llm_config = {"provider": "openai", "model": "gpt-3.5-turbo"}

   # To Anthropic
   llm_config = {"provider": "anthropic", "model": "claude-3-sonnet-20240229"}
   ```

2. **Update environment variables**:
   ```bash
   # Remove old
   unset OPENAI_API_KEY

   # Set new
   export ANTHROPIC_API_KEY="your-anthropic-api-key"
   ```

3. **Test thoroughly** - Different providers may have slightly different outputs

### Model Upgrades

When upgrading to newer models:

1. **Test compatibility** - Ensure your prompts work with the new model
2. **Adjust parameters** - New models may need different temperature settings
3. **Monitor performance** - Track accuracy and response times
4. **Update costs** - Newer models may have different pricing

## Security Considerations

### API Key Management

1. **Use environment variables** - Never hardcode API keys
2. **Rotate keys regularly** - Change API keys periodically
3. **Use least privilege** - Only grant necessary permissions
4. **Monitor usage** - Track API key usage for anomalies

### Data Privacy

1. **Review data handling** - Understand what data is sent to providers
2. **Use local models** - Consider Ollama for sensitive data
3. **Implement data retention** - Clear sensitive data after processing
4. **Audit logs** - Keep logs of all LLM interactions

## Performance Monitoring

### Metrics to Track

1. **Response time** - Time to get LLM response
2. **Token usage** - Number of tokens consumed
3. **Cost per request** - Monetary cost of each request
4. **Success rate** - Percentage of successful requests
5. **Error rate** - Percentage of failed requests

### Monitoring Setup

```python
# Enable detailed logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Track metrics
from intent_kit.utils.perf_util import track_execution

@track_execution
def my_function():
    # Your code here
    pass
```
