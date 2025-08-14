# Welcome to Intent Kit

Intent Kit is a Python framework that helps you build intelligent applications using Directed Acyclic Graphs (DAGs) to understand what users want and take the right actions.

## 🚀 Quick Start

Get up and running in minutes with our [Quickstart Guide](quickstart.md).

## 📚 Documentation

### Core Concepts
- [Intent DAGs](concepts/intent-graphs.md) - How to structure your workflows with DAGs
- [Nodes and Actions](concepts/nodes-and-actions.md) - Building blocks for your applications
- [Context Architecture](concepts/context-architecture.md) - Managing state and memory

### Examples
- [Calculator Bot](examples/calculator-bot.md) - Simple math operations
- [Context-Aware Chatbot](examples/context-aware-chatbot.md) - Remembering conversations
- [Context Memory Demo](examples/context-memory-demo.md) - Multi-turn conversations

### Configuration
- [JSON Serialization](configuration/json-serialization.md) - Define workflows in JSON
- [LLM Integration](configuration/llm-integration.md) - OpenAI, Anthropic, Google, Ollama

### Development
- [Building](development/building.md) - How to build the package
- [Testing](development/testing.md) - Unit tests and integration testing
- [Evaluation](development/evaluation.md) - Performance evaluation and benchmarking
- [Debugging](development/debugging.md) - Debugging tools and techniques
- [Performance Monitoring](development/performance-monitoring.md) - Performance tracking and reporting

### API Reference
- [Complete API Reference](api/api-reference.md) - Full API documentation

## 🛠️ Installation

```bash
pip install intentkit-py  # Basic installation
pip install intentkit-py[openai]  # With OpenAI support
pip install intentkit-py[all]  # All AI providers
```

## 💡 What Makes Intent Kit Special

- **🎯 You're in Control** - Define exactly what your app can do, no surprises
- **🧠 Works with Any AI** - OpenAI, Anthropic, Google, Ollama, or your own models
- **🔧 Easy to Build** - Simple, clear API that feels natural to use
- **🧪 Testable & Reliable** - Built-in testing tools for confidence
- **📊 See What's Happening** - Visualize workflows and track decisions
- **🔄 DAG Architecture** - Flexible, scalable workflow design

## 🎯 Common Use Cases

### 🤖 **Chatbots & Virtual Assistants**
Build intelligent bots that understand natural language and take appropriate actions.

**Example:**
```python
from intent_kit import DAGBuilder

# Create a chatbot that can greet users and answer questions
builder = DAGBuilder()
builder.add_node("classifier", "classifier",
                 output_labels=["greet", "question"],
                 description="Understand user intent")

# Add actions for different intents
builder.add_node("greet_action", "action",
                 action=lambda name: f"Hello {name}!",
                 description="Greet the user")

builder.add_node("answer_action", "action",
                 action=lambda question: f"I can help with: {question}",
                 description="Answer user questions")
```

### 🔧 **Task Automation**
Automate complex workflows that require understanding user intent.

**Example:**
```python
# Automate customer support ticket routing
builder.add_node("ticket_classifier", "classifier",
                 output_labels=["bug", "feature", "billing"],
                 description="Classify support tickets")

builder.add_node("bug_handler", "action",
                 action=lambda details: f"Bug ticket created: {details}",
                 description="Handle bug reports")
```

### 📊 **Data Processing**
Route and process information based on what users are asking for.

**Example:**
```python
# Process different types of data requests
builder.add_node("data_classifier", "classifier",
                 output_labels=["analytics", "export", "search"],
                 description="Classify data requests")

builder.add_node("analytics_action", "action",
                 action=lambda query: f"Analytics for: {query}",
                 description="Generate analytics")
```

### 🎯 **Decision Systems**
Create systems that make smart decisions based on user requests.

**Example:**
```python
# Smart recommendation system
builder.add_node("preference_classifier", "classifier",
                 output_labels=["product", "service", "content"],
                 description="Understand user preferences")

builder.add_node("recommend_action", "action",
                 action=lambda category: f"Recommendations for {category}",
                 description="Generate recommendations")
```

## 🚀 Key Features

### Smart Understanding
- **Multi-Provider Support** - Works with OpenAI, Anthropic, Google, Ollama, and more
- **Automatic Parameter Extraction** - Extract names, dates, numbers, and complex objects
- **Intent Classification** - Route requests to the right actions
- **Context Awareness** - Remember previous interactions

### DAG Configuration
- **JSON Definitions** - Define complex workflows in JSON for easy management
- **Visual Workflows** - Clear, understandable workflow structure
- **Flexible Routing** - Support for conditional logic and error handling
- **Reusable Components** - Share nodes across different workflows

### Context Management
- **State Persistence** - Maintain data across multiple interactions
- **Type Safety** - Validate and coerce data types automatically
- **Audit Trails** - Track all context modifications
- **Namespace Protection** - Protect system keys from conflicts

### Developer Friendly
- **Simple API** - Intuitive builder pattern for creating workflows
- **Comprehensive Error Handling** - Clear error messages and recovery strategies
- **Built-in Debugging** - Detailed execution traces and logging
- **Testing Tools** - Built-in evaluation framework for testing workflows

### Testing & Evaluation
- **Test Against Real Data** - Evaluate workflows with real user inputs
- **Performance Metrics** - Track accuracy, response times, and costs
- **A/B Testing** - Compare different workflow configurations
- **Continuous Monitoring** - Monitor workflow performance in production

## 🏗️ Architecture Overview

Intent Kit uses a DAG-based architecture with four main node types:

### Classifier Nodes
Understand user intent and route to appropriate paths.

```python
classifier = ClassifierNode(
    name="main_classifier",
    description="Route user requests to appropriate actions",
    output_labels=["greet", "calculate", "weather"]
)
```

### Extractor Nodes
Extract parameters from natural language using LLM.

```python
extractor = ExtractorNode(
    name="name_extractor",
    description="Extract person's name from greeting",
    param_schema={"name": str}
)
```

### Action Nodes
Execute specific actions and produce outputs.

```python
action = ActionNode(
    name="greet_action",
    action=lambda name: f"Hello {name}!",
    description="Greet the user by name"
)
```

### Clarification Nodes
Handle unclear intent by asking for clarification.

```python
clarification = ClarificationNode(
    name="clarification",
    description="Handle unclear or ambiguous requests"
)
```

## 🔧 Getting Started

### 1. Install Intent Kit

```bash
# Basic installation
pip install intentkit-py

# With specific AI provider
pip install 'intentkit-py[openai]'    # OpenAI
pip install 'intentkit-py[anthropic]'  # Anthropic
pip install 'intentkit-py[all]'        # All providers
```

### 2. Set Up Your API Key

```bash
export OPENAI_API_KEY="your-openai-api-key"
```

### 3. Build Your First Workflow

```python
from intent_kit import DAGBuilder
from intent_kit.core.context import DefaultContext

# Define what your app can do
def greet(name: str) -> str:
    return f"Hello {name}!"

# Create a DAG
builder = DAGBuilder()
builder.with_default_llm_config({
    "provider": "openai",
    "model": "gpt-3.5-turbo"
})

# Add nodes
builder.add_node("classifier", "classifier",
                 output_labels=["greet"],
                 description="Route to appropriate action")

builder.add_node("extract_name", "extractor",
                 param_schema={"name": str},
                 description="Extract name from greeting")

builder.add_node("greet_action", "action",
                 action=greet,
                 description="Greet the user")

# Connect the nodes
builder.add_edge("classifier", "extract_name", "greet")
builder.add_edge("extract_name", "greet_action", "success")
builder.set_entrypoints(["classifier"])

# Build and test
dag = builder.build()
context = DefaultContext()
result = dag.execute("Hello Alice", context)
print(result.data)  # → "Hello Alice!"
```

## 📖 Learn More

- **[Quickstart Guide](quickstart.md)** - Get up and running fast
- **[Examples](examples/index.md)** - See working examples
- **[Core Concepts](concepts/index.md)** - Understand the fundamentals
- **[API Reference](api/api-reference.md)** - Complete API documentation
- **[Development](development/index.md)** - Testing, debugging, and deployment

## 🤝 Contributing

We welcome contributions! Please see our [Development Guide](development/index.md) for:

- Setting up your development environment
- Running tests and linting
- Contributing code changes
- Documentation improvements

## 📄 License

Intent Kit is licensed under the MIT License. See the [LICENSE](../LICENSE) file for details.

## 🆘 Need Help?

- 📚 **[Full Documentation](https://docs.intentkit.io)** - Complete guides and API reference
- 💡 **[Examples](examples/index.md)** - Working examples to learn from
- 🐛 **[GitHub Issues](https://github.com/Stephen-Collins-tech/intent-kit/issues)** - Ask questions or report bugs
- 💬 **[Discussions](https://github.com/Stephen-Collins-tech/intent-kit/discussions)** - Join the community

---

**Ready to build intelligent applications?** Start with our [Quickstart Guide](quickstart.md) and see how easy it is to create AI-powered workflows with Intent Kit!
