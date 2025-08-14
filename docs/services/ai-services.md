# AI Services

Intent Kit provides a comprehensive AI services layer that supports multiple LLM providers with unified interfaces, cost tracking, and performance monitoring.

## Overview

The AI services layer includes:
- **Multiple LLM Providers** - OpenAI, Anthropic, Google, Ollama, OpenRouter
- **Unified Interface** - Consistent API across all providers
- **Cost Tracking** - Real-time token usage and cost calculation
- **Performance Monitoring** - Response times and metrics
- **Factory Pattern** - Easy provider switching and configuration

## Supported Providers

### OpenAI
- **Models**:
  - GPT-5-2025-08-07 (Latest)
  - GPT-4
  - GPT-4-turbo
  - GPT-4o
  - GPT-4o-mini
  - GPT-3.5-turbo
- **Features**: Function calling, streaming, fine-tuning
- **Cost**: Pay-per-token pricing

### Anthropic
- **Models**:
  - Claude Opus 4 (claude-opus-4-20250514)
  - Claude 3.7 Sonnet (claude-3-7-sonnet-20250219)
  - Claude 3.5 Haiku (claude-3-5-haiku-20241022)
- **Features**: Constitutional AI, tool use, streaming
- **Cost**: Pay-per-token pricing

### Google
- **Models**:
  - Gemini 2.5 Flash Lite (gemini-2.5-flash-lite)
  - Gemini 2.5 Flash (gemini-2.5-flash)
  - Gemini 2.5 Pro (gemini-2.5-pro)
- **Features**: Multimodal, code generation, reasoning
- **Cost**: Pay-per-token pricing

### Ollama
- **Models**: Local models (Llama, Mistral, CodeLlama, etc.)
- **Features**: Local deployment, custom models, privacy
- **Cost**: Free (local compute)

### OpenRouter
- **Models**:
  - Google Gemma 2 9B IT (google/gemma-2-9b-it)
  - Meta Llama 3.2 3B Instruct (meta-llama/llama-3.2-3b-instruct)
  - Moonshot Kimi K2 (moonshotai/kimi-k2)
  - Mistral Devstral Small (mistralai/devstral-small)
  - Qwen 3 32B (qwen/qwen3-32b)
  - Z-AI GLM 4.5 (z-ai/glm-4.5)
  - Qwen 3 30B A3B Instruct (qwen/qwen3-30b-a3b-instruct-2507)
  - Mistral 7B Instruct (mistralai/mistral-7b-instruct)
  - Mistral Ministral 8B (mistralai/ministral-8b)
  - Mistral Nemo 20B (mistralai/mistral-nemo-20b)
  - Liquid LFM 40B (liquid/lfm-40b)
  - Plus access to 100+ additional models from various providers
- **Features**: Unified API, model comparison, cost optimization
- **Cost**: Pay-per-token with provider-specific pricing

## Basic Usage

### Using the Factory Pattern

```python
from intent_kit.services.ai.llm_factory import LLMFactory
from intent_kit.services.ai.llm_service import LLMService

# Create LLM service with factory
llm_service = LLMService()

# Configure OpenAI
openai_config = {
    "provider": "openai",
    "model": "gpt-4",
    "api_key": "your-openai-key"
}

# Get client
client = llm_service.get_client(openai_config)

# Generate response
response = client.generate("Hello, how are you?")
print(response.content)
```

### Environment Variable Configuration

```bash
# OpenAI
export OPENAI_API_KEY="your-key"
export OPENAI_MODEL="gpt-4o"  # or "gpt-5-2025-08-07" for latest

# Anthropic
export ANTHROPIC_API_KEY="your-key"
export ANTHROPIC_MODEL="claude-3-7-sonnet-20250219"  # or "claude-opus-4-20250514" for latest

# Google
export GOOGLE_API_KEY="your-key"
export GOOGLE_MODEL="gemini-2.5-flash-lite"  # or "gemini-2.5-pro" for latest

# Ollama
export OLLAMA_BASE_URL="http://localhost:11434"
export OLLAMA_MODEL="llama2"

# OpenRouter
export OPENROUTER_API_KEY="your-key"
export OPENROUTER_MODEL="mistralai/mistral-7b-instruct"  # or any supported model
```

## Provider-Specific Configuration

### OpenAI Configuration

```python
openai_config = {
    "provider": "openai",
    "model": "gpt-4o",  # or "gpt-5-2025-08-07" for latest
    "api_key": "your-key",
    "temperature": 0.7,
    "max_tokens": 1000,
    "top_p": 0.9,
    "frequency_penalty": 0.0,
    "presence_penalty": 0.0,
    "stream": False
}
```

### Anthropic Configuration

```python
anthropic_config = {
    "provider": "anthropic",
    "model": "claude-3-7-sonnet-20250219",  # or "claude-opus-4-20250514" for latest
    "api_key": "your-key",
    "max_tokens": 1000,
    "temperature": 0.7,
    "top_p": 0.9,
    "system": "You are a helpful assistant."
}
```

### Google Configuration

```python
google_config = {
    "provider": "google",
    "model": "gemini-2.5-flash-lite",  # or "gemini-2.5-pro" for latest
    "api_key": "your-key",
    "temperature": 0.7,
    "max_output_tokens": 1000,
    "top_p": 0.9,
    "top_k": 40
}
```

### Ollama Configuration

```python
ollama_config = {
    "provider": "ollama",
    "model": "llama2",
    "base_url": "http://localhost:11434",
    "temperature": 0.7,
    "top_p": 0.9,
    "num_predict": 1000
}
```

### OpenRouter Configuration

```python
openrouter_config = {
    "provider": "openrouter",
    "model": "mistralai/mistral-7b-instruct",  # or any supported model
    "api_key": "your-key",
    "temperature": 0.7,
    "max_tokens": 1000,
    "top_p": 0.9
}
```

## Advanced Features

### Streaming Responses

```python
# Configure for streaming
config = {
    "provider": "openai",
    "model": "gpt-4",
    "stream": True
}

client = llm_service.get_client(config)

# Stream response
for chunk in client.generate_stream("Tell me a story"):
    print(chunk.content, end="", flush=True)
```

### Function Calling

```python
# Define functions
functions = [
    {
        "name": "get_weather",
        "description": "Get weather information",
        "parameters": {
            "type": "object",
            "properties": {
                "location": {"type": "string"},
                "unit": {"type": "string", "enum": ["celsius", "fahrenheit"]}
            },
            "required": ["location"]
        }
    }
]

# Configure with functions
config = {
    "provider": "openai",
    "model": "gpt-4",
    "functions": functions,
    "function_call": "auto"
}

client = llm_service.get_client(config)
response = client.generate("What's the weather in New York?")
```

### Structured Output

```python
# Configure for structured output
config = {
    "provider": "anthropic",
    "model": "claude-3-sonnet-20240229",
    "response_format": {
        "type": "json_object",
        "schema": {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "age": {"type": "integer"},
                "email": {"type": "string"}
            }
        }
    }
}

client = llm_service.get_client(config)
response = client.generate("Extract user information from: John is 25 years old, email: john@example.com")
```

## Cost Tracking

### Real-Time Cost Calculation

```python
from intent_kit.services.ai.pricing_service import PricingService

# Initialize pricing service
pricing_service = PricingService()

# Track costs
config = {
    "provider": "openai",
    "model": "gpt-4"
}

client = llm_service.get_client(config)
response = client.generate("Hello world")

# Get cost information
print(f"Input tokens: {response.input_tokens}")
print(f"Output tokens: {response.output_tokens}")
print(f"Total cost: ${response.cost:.4f}")
```

### Cost Optimization

```python
# Compare costs across providers
providers = [
    {"provider": "openai", "model": "gpt-4o"},
    {"provider": "anthropic", "model": "claude-3-7-sonnet-20250219"},
    {"provider": "google", "model": "gemini-2.5-flash-lite"},
    {"provider": "openrouter", "model": "mistralai/mistral-7b-instruct"}
]

for provider_config in providers:
    client = llm_service.get_client(provider_config)
    response = client.generate("Hello world")
    print(f"{provider_config['provider']}: ${response.cost:.4f}")
```

## Performance Monitoring

### Response Time Tracking

```python
import time

# Track performance
start_time = time.time()
response = client.generate("Complex query")
end_time = time.time()

print(f"Response time: {end_time - start_time:.2f} seconds")
print(f"Tokens per second: {response.output_tokens / (end_time - start_time):.2f}")
```

### Batch Processing

```python
# Process multiple requests efficiently
queries = [
    "What is AI?",
    "Explain machine learning",
    "Describe neural networks"
]

responses = []
for query in queries:
    response = client.generate(query)
    responses.append(response)

# Aggregate metrics
total_cost = sum(r.cost for r in responses)
total_tokens = sum(r.input_tokens + r.output_tokens for r in responses)
print(f"Total cost: ${total_cost:.4f}")
print(f"Total tokens: {total_tokens}")
```

## Error Handling

### Provider-Specific Errors

```python
from intent_kit.services.ai.base_client import LLMError

try:
    response = client.generate("Hello world")
except LLMError as e:
    print(f"LLM Error: {e.message}")
    print(f"Provider: {e.provider}")
    print(f"Model: {e.model}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

### Retry Logic

```python
import time
from functools import wraps

def retry_on_failure(max_retries=3, delay=1):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except LLMError as e:
                    if attempt == max_retries - 1:
                        raise
                    time.sleep(delay * (2 ** attempt))  # Exponential backoff
            return None
        return wrapper
    return decorator

@retry_on_failure(max_retries=3)
def generate_with_retry(client, prompt):
    return client.generate(prompt)
```

## Best Practices

### 1. Model Selection

```python
# Choose appropriate model for task
task_models = {
    "conversation": "gpt-4o",
    "code_generation": "claude-3-7-sonnet-20250219",
    "reasoning": "gemini-2.5-pro",
    "local_development": "llama2",
    "cost_optimized": "mistralai/mistral-7b-instruct"
}
```

### 2. Cost Management

```python
# Set budget limits
def generate_within_budget(client, prompt, max_cost=0.01):
    response = client.generate(prompt)
    if response.cost > max_cost:
        raise ValueError(f"Cost ${response.cost:.4f} exceeds budget ${max_cost:.4f}")
    return response
```

### 3. Caching

```python
import hashlib
import json

class ResponseCache:
    def __init__(self):
        self.cache = {}

    def get_cache_key(self, config, prompt):
        data = json.dumps({"config": config, "prompt": prompt}, sort_keys=True)
        return hashlib.md5(data.encode()).hexdigest()

    def get(self, config, prompt):
        key = self.get_cache_key(config, prompt)
        return self.cache.get(key)

    def set(self, config, prompt, response):
        key = self.get_cache_key(config, prompt)
        self.cache[key] = response

# Use caching
cache = ResponseCache()
cached_response = cache.get(config, prompt)
if cached_response:
    return cached_response

response = client.generate(prompt)
cache.set(config, prompt, response)
return response
```

### 4. Environment Management

```python
# Use environment-specific configurations
import os

def get_llm_config():
    env = os.getenv("ENVIRONMENT", "development")

    if env == "production":
        return {
            "provider": "openai",
            "model": "gpt-4o",
            "temperature": 0.1  # More deterministic
        }
    elif env == "development":
        return {
            "provider": "ollama",
            "model": "llama2",
            "temperature": 0.7  # More creative
        }
    else:
        return {
            "provider": "anthropic",
            "model": "claude-3-5-haiku-20241022",
            "temperature": 0.5
        }
```

## Integration with DAGs

### Using AI Services in DAGs

```python
from intent_kit import DAGBuilder
from intent_kit.services.ai.llm_service import LLMService

# Initialize LLM service
llm_service = LLMService()

# Create DAG with AI services
builder = DAGBuilder()

# Set default LLM configuration
builder.with_default_llm_config({
    "provider": "openai",
    "model": "gpt-4o",
    "temperature": 0.7
})

# Add nodes that use AI services
builder.add_node("classifier", "classifier",
                 output_labels=["greet", "weather"],
                 description="Classify user intent")

builder.add_node("extractor", "extractor",
                 param_schema={"location": str, "date": str},
                 description="Extract parameters")

# Build and execute
dag = builder.build()
context = DefaultContext()
context.set("llm_service", llm_service)

result = dag.execute("What's the weather in New York tomorrow?", context)
```

### Context-Aware AI Configuration

```python
# Use different models for different tasks
def get_task_specific_config(task_type):
    configs = {
        "classification": {
            "provider": "anthropic",
            "model": "claude-3-5-haiku-20241022",
            "temperature": 0.1
        },
        "extraction": {
            "provider": "openai",
            "model": "gpt-4o",
            "temperature": 0.0
        },
        "conversation": {
            "provider": "google",
            "model": "gemini-2.5-flash-lite",
            "temperature": 0.7
        },
        "cost_optimized": {
            "provider": "openrouter",
            "model": "mistralai/mistral-7b-instruct",
            "temperature": 0.7
        }
    }
    return configs.get(task_type, configs["conversation"])
```
