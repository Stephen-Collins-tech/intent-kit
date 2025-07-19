<p align="center">
  <img src="assets/logo.png" alt="Intent Kit Logo" height="100" style="border-radius: 16px;"/>
</p>

<h1 align="center">Intent Kit</h1>
<p align="center">Build intelligent workflows that understand what users want</p>

<p align="center">
  <a href="https://github.com/Stephen-Collins-tech/intent-kit/actions/workflows/ci.yml">
    <img src="https://github.com/Stephen-Collins-tech/intent-kit/actions/workflows/ci.yml/badge.svg" alt="CI"/>
  </a>
  <a href="https://codecov.io/gh/Stephen-Collins-tech/intent-kit">
    <img src="https://codecov.io/gh/Stephen-Collins-tech/intent-kit/branch/main/graph/badge.svg" alt="Coverage Status"/>
  </a>
  <a href="https://docs.intentkit.io">
    <img src="https://img.shields.io/badge/docs-online-blue" alt="Documentation"/>
  </a>
  <a href="https://pypi.org/project/intentkit-py">
    <img src="https://img.shields.io/pypi/v/intentkit-py" alt="PyPI"/>
  </a>
</p>

---

## What is Intent Kit?

Intent Kit helps you build AI-powered applications that understand what users want and take the right actions. Think of it as a smart router that can:

- **Understand user requests** using any AI model (OpenAI, Anthropic, Google, or your own)
- **Extract important details** like names, dates, and preferences automatically
- **Take actions** like sending messages, making calculations, or calling APIs
- **Handle complex requests** that involve multiple steps
- **Keep track of conversations** so your app remembers context

The best part? You stay in complete control. You define exactly what your app can do and how it should respond.

---

## Why Intent Kit?

### 🎯 **You're in Control**
Define every possible action upfront. No surprises, no unexpected behavior.

### 🚀 **Works with Any AI**
Use OpenAI, Anthropic, Google, Ollama, or even simple rules. Mix and match as needed.

### 🔧 **Easy to Build**
Simple, clear API that feels natural to use. No complex abstractions to learn.

### 🧪 **Testable & Reliable**
Built-in testing tools let you verify your workflows work correctly before deploying.

### 📊 **See What's Happening**
Visualize your workflows and track exactly how decisions are made.

---

## Quick Start

### 1. Install Intent Kit

```bash
pip install intentkit-py
```

For AI features, add your preferred provider:
```bash
pip install 'intentkit-py[openai]'    # OpenAI
pip install 'intentkit-py[anthropic]'  # Anthropic
pip install 'intentkit-py[all]'        # All providers
```

### 2. Build Your First Workflow

```python
from intent_kit import IntentGraphBuilder, action, llm_classifier

# Define what your app can do
greet = action(
    name="greet",
    description="Greet the user by name",
    action_func=lambda name: f"Hello {name}!",
    param_schema={"name": str}
)

weather = action(
    name="weather",
    description="Get weather for a location",
    action_func=lambda city: f"Weather in {city}: 72°F, Sunny",
    param_schema={"city": str}
)

# Create a classifier to understand user requests
classifier = llm_classifier(
    name="main",
    children=[greet, weather],
    llm_config={"provider": "openrouter", "model": "google/gemma-2-27b"}
)

# Build your workflow
graph = IntentGraphBuilder().root(classifier).build()

# Test it!
result = graph.route("Hello Alice")
print(result.output)  # → "Hello Alice!"
```

### 3. Try More Examples

```python
# Get weather
result = graph.route("What's the weather in San Francisco?")
print(result.output)  # → "Weather in San Francisco: 72°F, Sunny"

# Handle multiple requests
result = graph.route("Greet Bob and check weather in NYC")
print(result.output)  # → Handles both requests!
```

---

## How It Works

Intent Kit uses a simple but powerful pattern:

1. **Actions** - Define what your app can do (send messages, make API calls, etc.)
2. **Classifiers** - Understand what the user wants using AI or rules
3. **Graphs** - Connect everything together into a workflow
4. **Context** - Remember conversations and user preferences

The magic happens when a user sends a message:
- The classifier figures out what they want
- Intent Kit extracts the important details (names, locations, etc.)
- The right action runs with those details
- You get back a response

---

## Handling Ambiguous Requests

Sometimes users provide unclear or incomplete information. Intent Kit's **Clarifier nodes** help you handle these situations gracefully.

### When Clarification is Needed

```python
from intent_kit import clarifier

# Create a clarifier for booking requests
booking_clarifier = clarifier(
    name="booking_clarifier",
    clarification_prompt="Your booking request '{input}' is unclear. Please provide more details.",
    expected_response_format="Please specify: [type] [destination] [date] [time]",
    max_clarification_attempts=3
)

# Add it to your graph
graph = IntentGraphBuilder().root(booking_clarifier).build()

# Handle ambiguous input
result = graph.route("book something")
# → Returns clarification request with helpful message
```

### How Clarification Works

1. **User provides unclear input** - "book something"
2. **Clarifier node triggers** - Asks for more details
3. **User provides clarification** - "book a flight to Paris tomorrow"
4. **System processes clarified input** - Extracts details and takes action

### Advanced Clarification Features

```python
# Regular clarifier with context tracking
clarifier_node = clarifier(
    name="smart_clarifier",
    clarification_prompt="I need more details about your request: {input}",
    expected_response_format="Please provide: [specific details]",
    max_clarification_attempts=2
)

# LLM-powered clarifier for contextual clarification
llm_clarifier_node = llm_clarifier(
    name="smart_llm_clarifier",
    llm_config={"provider": "openrouter", "model": "google/gemma-2-27b"},
    clarification_prompt_template="""You are a helpful assistant. The user's request is unclear.

User Input: {user_input}
{context_info}

Generate a helpful clarification prompt that identifies what information is missing.

Expected Response Format: {expected_format}
Maximum Clarification Attempts: {max_attempts}

Clarification Prompt:""",
    expected_response_format="Please specify: [details]",
    max_clarification_attempts=3
)

# Handle clarification responses
context = IntentContext()
context.set("user_preferences", "window seat")
result = llm_clarifier_node.execute("book something", context=context)

# User provides clarification
response = llm_clarifier_node.handle_clarification_response(
    "book a flight to Paris tomorrow", context=context
)
```

---

## Real-World Testing

Most AI frameworks are black boxes that are hard to test. Intent Kit is different.

### Test Your Workflows Like Real Software

```python
from intent_kit.evals import run_eval, load_dataset

# Load test cases
dataset = load_dataset("tests/greeting_tests.yaml")

# Test your workflow
result = run_eval(dataset, graph)

print(f"Accuracy: {result.accuracy():.1%}")
result.save_report("test_results.md")
```

### What You Can Test

- **Accuracy** - Does your workflow understand requests correctly?
- **Performance** - How fast does it respond?
- **Edge Cases** - What happens with unusual inputs?
- **Regressions** - Catch when changes break existing functionality

This means you can deploy with confidence, knowing your AI workflows work reliably.

---

## Key Features

### 🧠 **Smart Understanding**
- Works with any AI model (OpenAI, Anthropic, Google, Ollama)
- Extracts parameters automatically (names, dates, preferences)
- Handles complex, multi-step requests

### 🔄 **Multi-Step Workflows**
- Chain actions together
- Handle "do X and Y" requests
- Remember context across conversations

### 🎨 **Visualization**
- See your workflows as interactive diagrams
- Track how decisions are made
- Debug complex flows easily

### 🛠️ **Developer Friendly**
- Simple, clear API
- Comprehensive error handling
- Built-in debugging tools
- JSON configuration support

### 🧪 **Testing & Evaluation**
- Test against real datasets
- Measure accuracy and performance
- Catch regressions automatically

---

## Common Use Cases

### 🤖 **Chatbots & Virtual Assistants**
Build intelligent bots that understand natural language and take appropriate actions.

### 🔧 **Task Automation**
Automate complex workflows that require understanding user intent.

### 📊 **Data Processing**
Route and process information based on what users are asking for.

### 🎯 **Decision Systems**
Create systems that make smart decisions based on user requests.

---

## Installation Options

```bash
# Basic installation (Python only)
pip install intentkit-py

# With specific AI providers
pip install 'intentkit-py[openai]'      # OpenAI
pip install 'intentkit-py[anthropic]'    # Anthropic  
pip install 'intentkit-py[google]'       # Google AI
pip install 'intentkit-py[ollama]'       # Ollama

# With visualization tools
pip install 'intentkit-py[viz]'

# Everything (all providers + tools)
pip install 'intentkit-py[all]'

# Development (includes testing tools)
pip install 'intentkit-py[dev]'
```

---

## Project Structure

```
intent-kit/
├── intent_kit/        # Main library code
├── examples/          # Working examples
├── docs/             # Documentation
├── tests/            # Test suite
└── pyproject.toml    # Project configuration
```

---

## Getting Help

- 📚 **[Full Documentation](https://docs.intentkit.io)** - Guides, API reference, and examples
- 🚀 **[Quickstart Guide](https://docs.intentkit.io/quickstart/)** - Get up and running fast
- 💡 **[Examples](https://docs.intentkit.io/examples/)** - See how others use Intent Kit
- 🐛 **[GitHub Issues](https://github.com/Stephen-Collins-tech/intent-kit/issues)** - Report bugs or ask questions

---

## Contributing

We welcome contributions! Here's how to get started:

```bash
git clone git@github.com:Stephen-Collins-tech/intent-kit.git
cd intent-kit
pip install -e ".[dev]"
pytest tests/
```

See our [Contributing Guide](https://github.com/Stephen-Collins-tech/intent-kit/blob/main/CONTRIBUTING.md) for more details.

---

## License

MIT License - feel free to use Intent Kit in your projects!
