# Quick-Start

This short guide shows how to install Intent-Kit, define a couple of intents, and route a piece of user input.

```bash
# Core framework – zero dependencies
pip install intent-kit

# With optional AI back-ends & visualisation
pip install 'intent-kit[openai,viz]'
```

```python
from intent_kit import IntentGraphBuilder, handler, regex_classifier, fuzzy_classifier
from intent_kit.context import IntentContext
from intent_kit.classifiers import ClassifierNode

# Define two simple handlers
hello = handler(
    name="hello",
    description="Say hello",
    handler_func=lambda name, context=None: f"Hello {name}!",
    param_schema={"name": str}
)

calc = handler(
    name="calc",
    description="Double a number",
    handler_func=lambda n, context=None: n * 2,
    param_schema={"n": int}
)

# Root classifier – typo-tolerant
root = ClassifierNode(
    name="root",
    classifier=fuzzy_classifier,
    children=[hello, calc]
)

# Build the graph
graph = IntentGraphBuilder().root(root).build()

ctx = IntentContext(session_id="demo")
result = graph.route("helo Alice", context=ctx)
print(result.output)  # -> "Hello Alice!"
```

For more examples see the `examples/` directory in the repository.