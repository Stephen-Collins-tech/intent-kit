# Debugging

Intent Kit provides comprehensive debugging tools to help you troubleshoot and optimize your intent graphs.

## Debug Output

### Basic Debugging

Enable debug output to see detailed execution information:

```python
from intent_kit import IntentGraphBuilder, action
from intent_kit.context import Context

# Create a graph with debug enabled
graph = IntentGraphBuilder().root(action(...)).build()
context = Context(session_id="debug_session", debug=True)

result = graph.route("Hello Alice", context=context)
print(context.debug_log)  # View detailed execution log
```

### Structured Debug Logging

Intent Kit now uses structured logging for better diagnostic information. Debug logs are organized into clear sections:

#### Node Execution Diagnostics

```python
# Example structured debug output for action nodes
{
  "node_name": "greet_action",
  "node_path": ["root", "greet_action"],
  "input": "Hello Alice",
  "extracted_params": {"name": "Alice"},
  "context_inputs": ["user_name"],
  "validated_params": {"name": "Alice"},
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
  "node_name": "intent_classifier",
  "node_path": ["root", "intent_classifier"],
  "input": "Hello Alice",
  "available_children": ["greet_action", "farewell_action"],
  "chosen_child": "greet_action",
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

### Context Dependencies

Track how context flows through your graph:

```python
from intent_kit.context.debug import get_context_dependencies

# Analyze context dependencies
dependencies = get_context_dependencies(graph)
print("Context dependencies:", dependencies)
```

### Context Validation

Validate that context is properly managed:

```python
from intent_kit.context.debug import validate_context_flow

# Check for context issues
issues = validate_context_flow(graph, context)
if issues:
    print("Context issues found:", issues)
```

### Context Tracing

Trace context execution step by step:

```python
from intent_kit.context.debug import trace_context_execution

# Get detailed context trace
trace = trace_context_execution(graph, "Hello Alice", context)
for step in trace:
    print(f"Step {step.step}: {step.node} -> {step.context_changes}")
```

### Important Context Keys

Mark specific context keys for detailed logging:

```python
context = Context(session_id="debug_session", debug=True)

# Mark important keys for detailed logging
context.mark_important("user_name")
context.mark_important("session_data")

# Only these keys will be logged in detail
context.set("user_name", "Alice")  # Will be logged
context.set("temp_data", "xyz")    # Won't be logged
```

## Node-Level Debugging

### Action Node Debugging

```python
# Debug action node execution
action_node = action(
    name="debug_action",
    action_func=lambda name: f"Hello {name}!",
    param_schema={"name": str}
)

result = action_node.execute("Hello Alice")
# Structured logs show parameter extraction, validation, and execution
```

### Classifier Node Debugging

```python
# Debug classifier node execution
classifier_node = classifier(
    name="intent_classifier",
    classifier_func=llm_classifier,
    children=[action1, action2]
)

result = classifier_node.execute("Hello Alice")
# Structured logs show classification decision and child selection
```

## Error Debugging

### Error Tracing

```python
try:
    result = graph.route("Invalid input")
except Exception as e:
    print(f"Error: {e}")
    print(f"Error context: {e.context}")
    print(f"Error node: {e.node}")
```

### Validation Errors

```python
# Check parameter validation
action_node = action(
    name="test",
    action_func=lambda x: x,
    param_schema={"x": int}
)

result = action_node.execute("not a number")
if not result.success:
    print(f"Validation errors: {result.validation_errors}")
```

## Logging Configuration

### Configure Logging

```python
import os

# Set log level via environment variable
os.environ["LOG_LEVEL"] = "debug"

# Or set programmatically
from intent_kit.utils.logger import Logger
logger = Logger("my_component", level="debug")
```

### Available Log Levels

- `trace`: Most verbose - detailed execution flow
- `debug`: Debug information for development
- `info`: General information
- `warning`: Warnings that don't stop execution
- `error`: Errors that affect functionality
- `critical`: Critical errors that may cause failure
- `fatal`: Fatal errors that will cause termination
- `off`: No logging

### Structured Logging

Use structured logging for better diagnostic information:

```python
logger.debug_structured(
    {
        "node_name": "my_node",
        "input": user_input,
        "params": extracted_params,
        "cost": 0.000123,
        "tokens": {"input": 45, "output": 12},
    },
    "Node Execution"
)
```

## Performance Monitoring

### Cost Tracking

```python
# Monitor LLM costs across execution
result = graph.route("Hello Alice")
print(f"Total cost: ${result.cost:.6f}")
print(f"Input tokens: {result.input_tokens}")
print(f"Output tokens: {result.output_tokens}")
```

### Timing Information

```python
# Monitor execution timing
import time
start_time = time.time()
result = graph.route("Hello Alice")
duration = time.time() - start_time
print(f"Execution time: {duration:.3f}s")
```

## Best Practices

1. **Use debug mode** during development
2. **Enable structured logging** for better diagnostics
3. **Mark important context keys** for detailed tracking
4. **Monitor costs and tokens** for performance optimization
5. **Use error tracing** for troubleshooting
6. **Test with edge cases** to catch issues early

## Common Issues

### Parameter Extraction Failures

```python
# Debug parameter extraction
action_node = action(
    name="debug",
    action_func=lambda name, age: f"{name} is {age}",
    param_schema={"name": str, "age": int}
)

result = action_node.execute("Alice is 25")
# Structured logs show extraction process and results
```

### Classifier Routing Issues

```python
# Debug classifier routing
classifier_node = classifier(
    name="intent_classifier",
    classifier_func=llm_classifier,
    children=[action1, action2]
)

result = classifier_node.execute("Hello Alice")
# Structured logs show classification decision process
```

## Recent Improvements

### Reduced Log Noise

- **Removed verbose internal state logging** from node execution
- **Consolidated AI client logging** across all providers
- **Added structured logging** for better organization
- **Improved context logging** to only log important changes
- **Enhanced error reporting** with structured error information

### Enhanced Diagnostics

- **Structured parameter extraction logs** with input/output details
- **Classifier decision tracking** with cost and token information
- **Context change monitoring** for important fields only
- **Performance metrics** including cost, tokens, and timing
- **Error context preservation** for better troubleshooting
