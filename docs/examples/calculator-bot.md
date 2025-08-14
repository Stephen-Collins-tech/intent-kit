# Calculator Bot Example

This example shows how to build a simple calculator bot that can add and subtract numbers using Intent Kit's DAG approach.

```python
import os
from intent_kit import DAGBuilder, run_dag
from intent_kit.core.context import DefaultContext

def add(a: float, b: float) -> str:
    return str(a + b)

def subtract(a: float, b: float) -> str:
    return str(a - b)

# Create DAG
builder = DAGBuilder()

# Set default LLM configuration
builder.with_default_llm_config({
    "provider": "openai",
    "api_key": os.getenv("OPENAI_API_KEY"),
    "model": "gpt-3.5-turbo"
})

# Add classifier to determine operation
builder.add_node("classifier", "classifier",
                 output_labels=["add", "subtract"],
                 description="Determine if user wants to add or subtract")

# Add extractor for calculation parameters
builder.add_node("extract_params", "extractor",
                 param_schema={"a": float, "b": float},
                 description="Extract two numbers for calculation",
                 output_key="extracted_params")

# Add action nodes
builder.add_node("add_action", "action",
                 action=add,
                 description="Add two numbers")

builder.add_node("subtract_action", "action",
                 action=subtract,
                 description="Subtract two numbers")

# Add clarification node
builder.add_node("clarification", "clarification",
                 clarification_message="I can help you add or subtract numbers. Please specify which operation you'd like to perform.",
                 available_options=["Add numbers", "Subtract numbers"])

# Connect nodes
builder.add_edge("classifier", "extract_params", "add")
builder.add_edge("extract_params", "add_action", "success")
builder.add_edge("classifier", "extract_params", "subtract")
builder.add_edge("extract_params", "subtract_action", "success")
builder.add_edge("classifier", "clarification", "clarification")

# Set entrypoints
builder.set_entrypoints(["classifier"])

# Build DAG
dag = builder.build()

# Test it!
context = DefaultContext()
result = run_dag(dag, "add 2 and 3", context)
print(result.data)  # → "5"

result = run_dag(dag, "subtract 10 from 15", context)
print(result.data)  # → "5"
```

## What This Example Shows

1. **Classifier Node** - Determines whether the user wants to add or subtract
2. **Extractor Node** - Extracts the two numbers from natural language
3. **Action Nodes** - Perform the actual calculations
4. **Clarification Node** - Handles unclear requests
5. **Edge Routing** - Routes based on classification results

## Key Features

- **Natural Language Processing** - Understands "add 2 and 3" or "subtract 10 from 15"
- **Parameter Extraction** - Automatically extracts numbers from text
- **Error Handling** - Clarification when intent is unclear
- **Flexible Routing** - Different paths for different operations
