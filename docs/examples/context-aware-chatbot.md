# Context-Aware Chatbot Example

This example demonstrates how to use context across multiple turns to maintain conversation state and memory between interactions using Intent Kit's DAG approach.

```python
import os
from intent_kit import DAGBuilder, run_dag
from intent_kit.core.context import DefaultContext

# Action that remembers how many times we greeted the user
def greet(name: str, **kwargs) -> str:
    # In a real implementation, you'd access context through kwargs or a global context
    # For this example, we'll simulate context persistence
    global _greet_count
    _greet_count = getattr(greet, '_count', 0) + 1
    greet._count = _greet_count
    return f"Hello {name}! (greeting #{_greet_count})"

# Create DAG
builder = DAGBuilder()

# Set default LLM configuration
builder.with_default_llm_config({
    "provider": "openrouter",
    "api_key": os.getenv("OPENROUTER_API_KEY"),
    "model": "google/gemma-2-9b-it"
})

# Add classifier
builder.add_node("classifier", "classifier",
                 output_labels=["greet"],
                 description="Detect greeting intent")

# Add extractor for name
builder.add_node("extract_name", "extractor",
                 param_schema={"name": str},
                 description="Extract name from greeting",
                 output_key="extracted_params")

# Add action
builder.add_node("greet_action", "action",
                 action=greet,
                 description="Greet the user and track greeting count")

# Add clarification
builder.add_node("clarification", "clarification",
                 clarification_message="I'm not sure what you'd like me to do. Try saying hello!",
                 available_options=["Say hello to someone"])

# Connect nodes
builder.add_edge("classifier", "extract_name", "greet")
builder.add_edge("extract_name", "greet_action", "success")
builder.add_edge("classifier", "clarification", "clarification")

# Set entrypoints
builder.set_entrypoints(["classifier"])

# Build DAG
dag = builder.build()

# Test with context persistence
result, context = run_dag(dag, "hello alice")
print(result.data)
result, context = run_dag(dag, "hello bob", context)  # Greeting count increments
print(result.data)
```

Running the above prints:

```
Hello alice! (greeting #1)
Hello bob! (greeting #2)
```

## Key Takeaways

* **Context Persistence** - `DefaultContext` persists between calls so you can build multi-turn experiences
* **State Management** - Actions can read and write to context for maintaining conversation state
* **Memory Across Turns** - The greeting count is maintained across different user interactions
* **Flexible Context** - Context can store any data needed for your application

## Context Features

- **Automatic Persistence** - Context data persists across multiple DAG executions
- **Type Safety** - Context supports typed data with validation
- **Audit Trail** - Track which actions modified which context values
- **Namespace Protection** - Built-in protection for system keys
