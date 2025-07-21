# Calculator Bot Example

This example shows how to build a simple calculator bot that can add and subtract numbers using intent-kit.

```python
from intent_kit import IntentGraphBuilder, action

def add(a: int, b: int) -> str:
    return str(a + b)

def subtract(a: int, b: int) -> str:
    return str(a - b)

add_action = action(
    name="add",
    description="Add two numbers",
    action_func=add,
    param_schema={"a": int, "b": int},
)

subtract_action = action(
    name="subtract",
    description="Subtract two numbers",
    action_func=subtract,
    param_schema={"a": int, "b": int},
)

graph = (
    IntentGraphBuilder()
    .root(add_action)
    .root(subtract_action)
    .build()
)

print(graph.route("add 2 3").output)  # -> 5
```
