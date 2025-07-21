# Context-Aware Chatbot Example

This example is adapted from `examples/context_demo.py`. It demonstrates how `IntentContext` can persist conversation state across multiple turns.

```python
from intent_kit import IntentGraphBuilder, action
from intent_kit.context import IntentContext

# Action remembers how many times we greeted the user

def greet(name: str, context: IntentContext) -> str:
    count = context.get("greet_count", 0) + 1
    context.set("greet_count", count, modified_by="greet")
    return f"Hello {name}! (greeting #{count})"

hello_action = action(
    name="greet",
    description="Greet the user and track greeting count",
    action_func=greet,
    param_schema={"name": str},
)

graph = IntentGraphBuilder().root(hello_action).build()

ctx = IntentContext(session_id="abc123")
print(graph.route("hello alice", context=ctx).output)
print(graph.route("hello bob", context=ctx).output)  # Greeting count increments
```

Running the above prints:

```
Hello alice! (greeting #1)
Hello bob! (greeting #2)
```

Key take-aways:
* `IntentContext` persists between calls so you can build multi-turn experiences.
* Each action can declare which context keys it reads/writes for explicit dependency tracking.
