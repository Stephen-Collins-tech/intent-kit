# Calculator Bot Example

This minimal example shows how to create a calculator bot that doubles or triples a number depending on the intent parsed.

```python
from intent_kit import IntentGraphBuilder, handler
from intent_kit.classifiers.regex import regex_classifier
from intent_kit.classifiers import ClassifierNode

# Handlers

double = handler(
    name="double",
    description="Double a number",
    handler_func=lambda n, context=None: n * 2,
    param_schema={"n": int},
)
setattr(double, "regex_patterns", [r"\bdouble\b", r"\btimes\s*2\b"])

triple = handler(
    name="triple",
    description="Triple a number",
    handler_func=lambda n, context=None: n * 3,
    param_schema={"n": int},
)
setattr(triple, "regex_patterns", [r"\btriple\b", r"\btimes\s*3\b"])

# Root classifier
root = ClassifierNode(
    name="calc_root",
    classifier=regex_classifier,
    children=[double, triple]
)

# Build graph
graph = IntentGraphBuilder().root(root).build()

print(graph.route("double 7").output)  # -> 14
print(graph.route("Triple 4").output)   # -> 12
```
