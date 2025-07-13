# Calculator Bot Example

This example shows how to build a simple calculator bot that can add and subtract numbers using intent-kit.

```python
from intent_kit import IntentGraphBuilder, handler

def add(a: int, b: int) -> str:
    return str(a + b)

def subtract(a: int, b: int) -> str:
    return str(a - b)

add_handler = handler(
    name="add",
    description="Add two numbers",
    handler_func=add,
    param_schema={"a": int, "b": int},
)

subtract_handler = handler(
    name="subtract",
    description="Subtract two numbers",
    handler_func=subtract,
    param_schema={"a": int, "b": int},
)

graph = (
    IntentGraphBuilder()
    .root(add_handler)
    .root(subtract_handler)
    .build()
)

print(graph.route("add 2 3").output)  # -> 5
```
