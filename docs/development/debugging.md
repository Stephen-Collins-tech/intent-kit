# Debugging

Intent Kit provides comprehensive debugging tools to help you troubleshoot and optimize your DAGs.

## Debug Output

### Basic Debugging

Enable debug output to see detailed execution information:

```python
from intent_kit import DAGBuilder, run_dag
from intent_kit.core.context import DefaultContext

# Create a DAG with debug enabled
def greet(name: str) -> str:
    return f"Hello {name}!"

builder = DAGBuilder()
builder.add_node("classifier", "classifier",
                 output_labels=["greet"],
                 description="Main classifier")
builder.add_node("extract_name", "extractor",
                 param_schema={"name": str},
                 description="Extract name")
builder.add_node("greet_action", "action",
                 action=greet,
                 description="Greet user")
builder.add_edge("classifier", "extract_name", "greet")
builder.add_edge("extract_name", "greet_action", "success")
builder.set_entrypoints(["classifier"])

dag = builder.build()
context = DefaultContext()

result = run_dag(dag, "Hello Alice", context)
print(result.data)  # View execution result
```

### Structured Debug Logging

Intent Kit uses structured logging for better diagnostic information. Debug logs are organized into clear sections:

#### Node Execution Diagnostics

```python
# Example structured debug output for action nodes
{
  "node_name": "greet_action",
  "node_type": "action",
  "input": "Hello Alice",
  "extracted_params": {"name": "Alice"},
  "context_data": {"user.name": "Alice"},
  "output": "Hello Alice!",
  "output_type": "str",
  "success": true,
  "input_tokens": 45,
  "output_tokens": 12,
  "cost": 0.000123,
  "duration": 0.045
}
```

#### Classifier Diagnostics

```python
# Example structured debug output for classifier nodes
{
  "node_name": "classifier",
  "node_type": "classifier",
  "input": "Hello Alice",
  "available_labels": ["greet", "weather"],
  "chosen_label": "greet",
  "confidence": 0.95,
  "classifier_cost": 0.000045,
  "classifier_tokens": {"input": 23, "output": 8},
  "classifier_model": "gpt-4.1-mini",
  "classifier_provider": "openai"
}
```

### Debug Log Format

The debug log shows:
- **Node execution order** with structured diagnostic information
- **Parameter extraction results** with input/output details
- **Context updates** for important fields only
- **Error details** with structured error information
- **Cost and token tracking** across all LLM calls

## Context Debugging

### Context State Analysis

Track how context flows through your DAG:

```python
from intent_kit.core.context import DefaultContext

# Create context and execute DAG
context = DefaultContext()
result = run_dag(dag, "Hello Alice", context)

# Analyze context state
print("Context keys:", context.keys())
print("Context snapshot:", context.snapshot())
```

### Context Validation

Validate that context is properly managed:

```python
def validate_context_state(context):
    """Check for context issues."""
    issues = []

    # Check for required keys
    required_keys = ["user.name", "session.id"]
    for key in required_keys:
        if not context.has(key):
            issues.append(f"Missing required key: {key}")

    # Check for data types
    if context.has("user.age") and not isinstance(context.get("user.age"), int):
        issues.append("user.age should be an integer")

    return issues

# Use in debugging
context = DefaultContext()
result = run_dag(dag, "Hello Alice", context)
issues = validate_context_state(context)
if issues:
    print("Context issues found:", issues)
```

## Error Debugging

### Structured Error Information

Intent Kit provides detailed error information:

```python
# Example error output
{
  "error_type": "ParameterExtractionError",
  "node_name": "extract_name",
  "input": "Invalid input",
  "error_message": "Could not extract name parameter",
  "suggested_fix": "Provide a name in the input",
  "context_state": {"previous_operations": ["classifier"]},
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### Error Handling Patterns

```python
def robust_action(name: str, context=None) -> str:
    """Action with comprehensive error handling."""
    try:
        # Validate input
        if not name or not isinstance(name, str):
            raise ValueError("Name must be a non-empty string")

        # Perform action
        result = f"Hello {name}!"

        # Update context
        if context:
            context.set("last_greeting", result, modified_by="robust_action")

        return result

    except Exception as e:
        # Log error details
        if context:
            context.set("error", str(e), modified_by="robust_action")

        # Return fallback response
        return "Hello there! (I couldn't process your name properly)"
```

## Performance Debugging

### Execution Timing

Track execution time for each node:

```python
import time
from intent_kit import run_dag

def timed_execution(dag, input_text, context):
    """Execute DAG with timing information."""
    start_time = time.time()

    result = run_dag(dag, input_text, context)

    end_time = time.time()
    execution_time = end_time - start_time

    print(f"Total execution time: {execution_time:.3f}s")
    print(f"Result: {result.data}")

    return result

# Use for debugging
context = DefaultContext()
result = timed_execution(dag, "Hello Alice", context)
```

### Memory Usage

Monitor context memory usage:

```python
def monitor_context_memory(context):
    """Monitor context memory usage."""
    snapshot = context.snapshot()

    print(f"Context keys: {len(snapshot)}")
    print(f"Context size: {len(str(snapshot))} characters")

    # Check for large objects
    for key, value in snapshot.items():
        if len(str(value)) > 1000:
            print(f"Large object in {key}: {len(str(value))} characters")

# Use during debugging
context = DefaultContext()
result = run_dag(dag, "Hello Alice", context)
monitor_context_memory(context)
```

## Debugging Tools

### Logger Configuration

Configure logging for debugging:

```python
import logging
from intent_kit.utils.logger import Logger

# Set up debug logging
logging.basicConfig(level=logging.DEBUG)

# Create logger for your application
logger = Logger("my_app")

# Use in your actions
def debug_action(name: str, context=None) -> str:
    logger.debug(f"Processing name: {name}")
    logger.debug(f"Context keys: {context.keys() if context else 'None'}")

    result = f"Hello {name}!"
    logger.info(f"Action completed: {result}")

    return result
```

### Context Inspection

Inspect context state during execution:

```python
def inspect_context(context, stage=""):
    """Inspect context at different stages."""
    print(f"\n=== Context Inspection ({stage}) ===")
    print(f"Keys: {list(context.keys())}")

    for key in context.keys():
        value = context.get(key)
        print(f"  {key}: {type(value).__name__} = {value}")

    print("=" * 40)

# Use throughout execution
context = DefaultContext()
inspect_context(context, "initial")

result1 = run_dag(dag, "Hello Alice", context)
inspect_context(context, "after first execution")

result2 = run_dag(dag, "What's the weather?", context)
inspect_context(context, "after second execution")
```

## Common Debugging Scenarios

### 1. Parameter Extraction Issues

```python
# Debug parameter extraction
def debug_extractor(input_text, param_schema):
    """Debug parameter extraction process."""
    print(f"Input: {input_text}")
    print(f"Schema: {param_schema}")

    # Simulate extraction
    # In real usage, this would be done by the extractor node
    print("Extraction would happen here")

    return {"debug": "extraction_info"}

# Use in your extractor nodes
```

### 2. Classification Problems

```python
# Debug classification
def debug_classifier(input_text, output_labels):
    """Debug classification process."""
    print(f"Input: {input_text}")
    print(f"Available labels: {output_labels}")

    # Simulate classification
    # In real usage, this would be done by the classifier node
    print("Classification would happen here")

    return "greet"  # Example result
```

### 3. Context State Issues

```python
# Debug context state
def debug_context_flow(context, operation=""):
    """Debug context state changes."""
    print(f"\nContext operation: {operation}")
    print(f"Current keys: {list(context.keys())}")

    if context.has("error"):
        print(f"Error state: {context.get('error')}")

    if context.has("last_operation"):
        print(f"Last operation: {context.get('last_operation')}")

# Use throughout your debugging
```

## Best Practices

### 1. **Structured Logging**
- Use consistent log levels (DEBUG, INFO, ERROR)
- Include relevant context in log messages
- Use structured data when possible

### 2. **Error Handling**
- Always catch and log exceptions
- Provide meaningful error messages
- Include context information in errors

### 3. **Performance Monitoring**
- Track execution times for critical paths
- Monitor memory usage patterns
- Use profiling tools for optimization

### 4. **Context Management**
- Validate context state at key points
- Monitor context size and growth
- Clear temporary data when no longer needed

### 5. **Testing**
- Test error conditions explicitly
- Use debug mode during development
- Validate context state in tests
