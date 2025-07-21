# Multi-Intent Routing Example

The following shows how intent-kit can handle _multiple_ intents in a single user utterance using a splitter node.

```python
from intent_kit import IntentGraphBuilder, action, rule_splitter_node

# Actions for individual intents

def greet(name: str) -> str:
    return f"Hello {name}!"

def weather(city: str) -> str:
    return f"The weather in {city} is sunny."

hello_action = action(
    name="greet",
    description="Greet the user",
    action_func=greet,
    param_schema={"name": str},
)

weather_action = action(
    name="weather",
    description="Get weather information",
    action_func=weather,
    param_schema={"city": str},
)

# Splitter routes parts of the sentence to different actions
splitter = rule_splitter_node(
    name="multi_split",
    children=[hello_action, weather_action],
)

graph = IntentGraphBuilder().root(splitter).build()

result = graph.route("Hello Alice and what's the weather in Paris?")
print(result.output)
```

The `rule_splitter_node` looks for keywords ("hello", "weather", etc.) and breaks the user input into sub-phrases routed to the appropriate actions. The final `result.output` aggregates the outputs from each intent, e.g.:

```
{
  "greet": "Hello Alice!",
  "weather": "The weather in Paris is sunny."
}
```

For a more robust version that uses LLM-based splitting, see `examples/multi_intent_demo.py`.
