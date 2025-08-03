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

## Your First Workflow

Let's build a simple greeting bot that can understand names and respond:

```python
from intent_kit import IntentGraphBuilder, action, llm_classifier

# Define what your bot can do
greet_action = action(
    name="greet",
    description="Greet the user by name",
    action_func=lambda name: f"Hello {name}!",
    param_schema={"name": str}
)

# Create a classifier to understand user requests
classifier = llm_classifier(
    name="main",
    description="Route to appropriate action",
    children=[greet_action],
    llm_config={"provider": "openai", "model": "gpt-3.5-turbo"}
)

# Build your workflow
graph = IntentGraphBuilder().root(classifier).build()

# Test it!
result = graph.route("Hello Alice")
print(result.output)  # → "Hello Alice!"
```

## What Just Happened?

1. **We defined an action** - `greet_action` knows how to greet someone by name
2. **We created a classifier** - This uses AI to understand what the user wants
3. **We built a graph** - This connects everything together
4. **We tested it** - The bot understood "Hello Alice" and extracted the name "Alice"

## Using JSON Configuration

For more complex workflows, you can define your graph in JSON:

```python
from intent_kit import IntentGraphBuilder

# Define your functions
def greet(name, context=None):
    return f"Hello {name}!"

def calculate(operation, a, b, context=None):
    if operation == "add":
        return a + b
    return None

# Create function registry
function_registry = {
    "greet": greet,
    "calculate": calculate,
}

# Define your graph in JSON
graph_config = {
    "root": "main_classifier",
    "nodes": {
        "main_classifier": {
            "id": "main_classifier",
            "type": "classifier",
            "classifier_type": "llm",
            "name": "main_classifier",
            "description": "Main intent classifier",
            "llm_config": {
                "provider": "openai",
                "model": "gpt-3.5-turbo",
            },
            "children": ["greet_action", "calculate_action"],
        },
        "greet_action": {
            "id": "greet_action",
            "type": "action",
            "name": "greet_action",
            "description": "Greet the user",
            "function": "greet",
            "param_schema": {"name": "str"},
        },
        "calculate_action": {
            "id": "calculate_action",
            "type": "action",
            "name": "calculate_action",
            "description": "Perform a calculation",
            "function": "calculate",
            "param_schema": {"operation": "str", "a": "float", "b": "float"},
        },
    },
}

# Build your graph
graph = (
    IntentGraphBuilder()
    .with_json(graph_config)
    .with_functions(function_registry)
    .build()
)

# Test it!
result = graph.route("Hello Alice")
print(result.output)  # → "Hello Alice!"
```

## Try More Examples

```python
# Test with different inputs
result = graph.route("Hi Bob")
print(result.output)  # → "Hello Bob!"

result = graph.route("Greet Sarah")
print(result.output)  # → "Hello Sarah!"

# Test calculations
result = graph.route("Add 5 and 3")
print(result.output)  # → 8
```

## Next Steps

- Check out the [Examples](examples/index.md) to see more complex workflows
- Learn about [Intent Graphs](concepts/intent-graphs.md) to understand the architecture
- Read about [Nodes and Actions](concepts/nodes-and-actions.md) to build more features
- Explore the [Development](development/index.md) guides for testing and debugging

## Need Help?

- 📚 **[Full Documentation](https://docs.intentkit.io)** - Complete guides and API reference
- 💡 **[Examples](examples/index.md)** - Working examples to learn from
- 🐛 **[GitHub Issues](https://github.com/Stephen-Collins-tech/intent-kit/issues)** - Ask questions or report bugs
