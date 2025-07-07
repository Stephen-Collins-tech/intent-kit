# Quickstart

Install intent-kit:

```bash
pip install intent-kit  # Or 'intent-kit[openai]' for LLM support
```

Create and run a simple graph:

```python
from intent_kit import IntentGraphBuilder, handler

hello_handler = handler(
    name="greet",
    description="Greet the user",
    handler_func=lambda name: f"Hello {name}!",
    param_schema={"name": str},
)

graph = IntentGraphBuilder().root(hello_handler).build()
print(graph.route("hello alice").output)
```

For more in-depth examples, see the Examples section.