# Audit Log Trail Feature

The audit log trail feature provides comprehensive logging of all LLM interactions for compliance, debugging, and analytics purposes.

## Overview

The audit log automatically captures every input and output interaction with LLM models, storing detailed information about each request including timestamps, token usage, costs, and performance metrics.

## Features

- **Automatic Logging**: All LLM interactions are automatically logged without requiring additional code
- **Comprehensive Data**: Captures input prompts, output responses, model information, token usage, costs, and timing
- **Easy Access**: Simple methods to retrieve and manage audit logs
- **Transparent**: Works with all existing LLM client implementations

## Implementation

### Base Class Integration

The audit log is implemented in the `BaseLLMClient` class:

```python
class BaseLLMClient(ABC):
    def __init__(self, ...):
        # ... existing initialization ...
        self.audit_log: List[AuditLogEntry] = []
    
    def _log_audit_entry(self, response: LLMResponse, prompt: str) -> None:
        """Log an audit entry for the LLM interaction."""
        audit_entry = AuditLogEntry(
            timestamp=datetime.now(),
            input_prompt=prompt,
            output_response=response.output,
            model=response.model,
            provider=response.provider,
            input_tokens=response.input_tokens,
            output_tokens=response.output_tokens,
            cost=response.cost,
            duration=response.duration,
        )
        self.audit_log.append(audit_entry)
```

### Audit Log Entry Structure

Each audit log entry contains:

```python
@dataclass
class AuditLogEntry:
    timestamp: datetime          # When the interaction occurred
    input_prompt: str           # The input prompt sent to the model
    output_response: str        # The response from the model
    model: str                  # The model used (e.g., "gpt-4")
    provider: str               # The provider (e.g., "openai")
    input_tokens: int          # Number of input tokens
    output_tokens: int         # Number of output tokens
    cost: float                # Cost of the interaction
    duration: float            # Time taken for the interaction
```

## Usage

### Basic Usage

```python
from intent_kit.services.ai.openai_client import OpenAIClient

# Initialize client
client = OpenAIClient(api_key="your-api-key")

# Make LLM calls (audit logging happens automatically)
response1 = client.generate("What is AI?", model="gpt-4")
response2 = client.generate("Explain machine learning", model="gpt-4")

# Access audit log
audit_log = client.get_audit_log()
print(f"Total interactions: {len(audit_log)}")

# Process audit entries
for entry in audit_log:
    print(f"Model: {entry.model}, Cost: ${entry.cost:.4f}")
    print(f"Input: {entry.input_prompt[:50]}...")
    print(f"Output: {entry.output_response[:50]}...")
    print("---")
```

### Available Methods

- `get_audit_log() -> List[AuditLogEntry]`: Get a copy of the complete audit log
- `clear_audit_log() -> None`: Clear all audit log entries
- `audit_log`: Direct access to the audit log list (read-only recommended)

### Working with Audit Data

```python
# Calculate total costs
total_cost = sum(entry.cost for entry in client.get_audit_log())

# Find interactions with specific models
gpt4_interactions = [
    entry for entry in client.get_audit_log() 
    if entry.model == "gpt-4"
]

# Analyze token usage patterns
total_input_tokens = sum(entry.input_tokens for entry in client.get_audit_log())
total_output_tokens = sum(entry.output_tokens for entry in client.get_audit_log())

# Find expensive interactions
expensive_interactions = [
    entry for entry in client.get_audit_log() 
    if entry.cost > 0.10
]
```

## Supported Clients

The audit log feature is automatically available in all LLM client implementations:

- `OpenAIClient` - OpenAI GPT models
- `AnthropicClient` - Anthropic Claude models  
- `OllamaClient` - Local Ollama models
- `GoogleClient` - Google Gemini models
- `OpenRouterClient` - OpenRouter models

## Benefits

### Compliance
- Track all AI interactions for regulatory requirements
- Maintain detailed logs for audit purposes
- Monitor usage patterns and costs

### Debugging
- Review input/output pairs for quality issues
- Analyze performance and cost patterns
- Troubleshoot model behavior

### Analytics
- Calculate total costs across all interactions
- Analyze token usage patterns
- Monitor response times and performance

## Example Output

```
Audit Log (3 entries):
========================================

Entry 1:
  Timestamp: 2025-08-05 23:15:35.495048
  Input: What is the capital of France?
  Output: The capital of France is Paris.
  Model: gpt-4
  Provider: openai
  Tokens: 6 in, 8 out
  Cost: $0.0003
  Duration: 1.234s

Entry 2:
  Timestamp: 2025-08-05 23:15:37.123456
  Input: Explain quantum computing
  Output: Quantum computing is a type of computation...
  Model: gpt-4
  Provider: openai
  Tokens: 3 in, 45 out
  Cost: $0.0012
  Duration: 2.567s
```

## Notes

- Audit logs are stored in memory and will be cleared when the client is destroyed
- For persistent storage, consider saving audit logs to a database or file
- The audit log is thread-safe for basic operations but consider synchronization for concurrent access
- Large audit logs may consume significant memory; use `clear_audit_log()` periodically if needed