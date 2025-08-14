# Quickstart

Get Intent Kit up and running in just a few minutes!

## Install Intent Kit

```bash
pip install intentkit-py
```

For AI features, add your preferred provider:
```bash
pip install 'intentkit-py[openai]'    # OpenAI
pip install 'intentkit-py[anthropic]'  # Anthropic
pip install 'intentkit-py[all]'        # All providers
```

## Your First DAG

Let's build a simple greeting bot that can understand names and respond:

```python
import os
from intent_kit import DAGBuilder, run_dag
from intent_kit.core.context import DefaultContext

# Define what your bot can do
def greet(name: str, **kwargs) -> str:
    return f"Hello {name}!"

# Create a DAG
builder = DAGBuilder()

# Set default LLM configuration
builder.with_default_llm_config({
    "provider": "openrouter",
    "api_key": os.getenv("OPENROUTER_API_KEY"),
    "model": "google/gemma-2-9b-it"
})

# Add classifier node to understand user requests
builder.add_node("classifier", "classifier",
                 output_labels=["greet"],
                 description="Route to appropriate action")

# Add extractor to get the name
builder.add_node("extract_name", "extractor",
                 param_schema={"name": str},
                 description="Extract name from greeting",
                 output_key="extracted_params")

# Add action node
builder.add_node("greet_action", "action",
                 action=greet,
                 description="Greet the user")

# Connect the nodes
builder.add_edge("classifier", "extract_name", "greet")
builder.add_edge("extract_name", "greet_action", "success")
builder.set_entrypoints(["classifier"])

# Build the DAG
dag = builder.build()

# Test it!
result, context = run_dag(dag, "Hello Alice")
print(result.data)  # → "Hello Alice!"
```

## What Just Happened?

1. **We defined an action** - `greet` function knows how to greet someone by name
2. **We created a classifier** - This uses AI to understand what the user wants
3. **We added an extractor** - This extracts parameters from the user input
4. **We built a DAG** - This connects everything together with edges
5. **We tested it** - The bot understood "Hello Alice" and extracted the name "Alice"

## Using JSON Configuration

For more complex workflows, you can define your DAG in JSON:

```python
from intent_kit import DAGBuilder, run_dag

# Define your functions
def greet(name: str, **kwargs) -> str:
    return f"Hello {name}!"

def calculate(operation: str, a: float, b: float, **kwargs) -> str:
    if operation == "add":
        return str(a + b)
    elif operation == "subtract":
        return str(a - b)
    return "Unknown operation"

# Define your DAG in JSON
dag_config = {
    "nodes": {
        "classifier": {
            "type": "classifier",
            "output_labels": ["greet", "calculate"],
            "description": "Main intent classifier",
            "llm_config": {
                "provider": "openrouter",
                "model": "google/gemma-2-9b-it",
            }
        },
        "extract_greet": {
            "type": "extractor",
            "param_schema": {"name": str},
            "description": "Extract name from greeting",
            "output_key": "extracted_params"
        },
        "extract_calc": {
            "type": "extractor",
            "param_schema": {"operation": str, "a": float, "b": float},
            "description": "Extract calculation parameters",
            "output_key": "extracted_params"
        },
        "greet_action": {
            "type": "action",
            "action": greet,
            "description": "Greet the user"
        },
        "calculate_action": {
            "type": "action",
            "action": calculate,
            "description": "Perform a calculation"
        }
    },
    "edges": [
        {"from": "classifier", "to": "extract_greet", "label": "greet"},
        {"from": "extract_greet", "to": "greet_action", "label": "success"},
        {"from": "classifier", "to": "extract_calc", "label": "calculate"},
        {"from": "extract_calc", "to": "calculate_action", "label": "success"}
    ],
    "entrypoints": ["classifier"]
}

# Build your DAG
dag = DAGBuilder.from_json(dag_config)

# Test it!
result, context = run_dag(dag, "Hello Alice")
print(result.data)  # → "Hello Alice!"

result, context = run_dag(dag, "Add 5 and 3", context)
print(result.data)  # → "8"
```

## Try More Examples

```python
# Test with different inputs
result, context = run_dag(dag, "Hi Bob", context)
print(result.data)  # → "Hello Bob!"

result, context = run_dag(dag, "Greet Sarah", context)
print(result.data)  # → "Hello Sarah!"

# Test calculations
result = run_dag(dag, "Subtract 10 from 15", context)
print(result.data)  # → "5"
```

## Next Steps

- Check out the [Examples](examples/index.md) to see more complex workflows
- Learn about [Intent DAGs](concepts/intent-graphs.md) to understand the architecture
- Read about [Nodes and Actions](concepts/nodes-and-actions.md) to build more features
- Explore the [Development](development/index.md) guides for testing and debugging

## Need Help?

- 📚 **[Full Documentation](https://docs.intentkit.io)** - Complete guides and API reference
- 💡 **[Examples](examples/index.md)** - Working examples to learn from
- 🐛 **[GitHub Issues](https://github.com/Stephen-Collins-tech/intent-kit/issues)** - Ask questions or report bugs
