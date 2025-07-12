# Welcome to intent-kit

intent-kit is a universal Python framework for building hierarchical intent graphs with deterministic, fully-auditable execution models.

## 🚀 Quick Start

Get up and running in minutes with our [Quickstart Guide](quickstart.md).

## 📚 Documentation

### Core Concepts
- [Intent Graphs](concepts/intent-graphs.md) - Understanding the core architecture
- [Nodes and Actions](concepts/nodes-and-actions.md) - Building blocks of intent graphs
- [Context System](concepts/context_system.md) - State management and dependency tracking
- [Remediation](concepts/remediation.md) - Error handling and recovery strategies

### API Reference
- [IntentGraphBuilder](api/intent_graph_builder.md) - Fluent interface for building graphs
- [Node Types](api/node_types.md) - Action, Classifier, and Splitter nodes
- [Context API](api/context_api.md) - Context management and debugging
- [Remediation API](api/remediation_api.md) - Error handling strategies

### Configuration
- [JSON Serialization](configuration/json-serialization.md) - Define graphs in JSON
- [LLM Integration](configuration/llm_integration.md) - OpenAI, Anthropic, Google, Ollama
- [Function Registry](configuration/function_registry.md) - Managing function mappings

### Examples
- [Basic Examples](examples/basic_examples.md) - Simple intent graphs
- [Advanced Examples](examples/advanced_examples.md) - Complex workflows
- [Multi-Intent Routing](examples/multi_intent_routing.md) - Handling multiple intents
- [Context-Aware Workflows](examples/context_workflows.md) - Stateful conversations

### Development
- [Testing](development/testing.md) - Unit tests and integration testing
- [Evaluation](development/evaluation.md) - Performance evaluation and benchmarking
- [Debugging](development/debugging.md) - Debugging tools and techniques

## 🛠️ Installation

```bash
pip install intent-kit  # Basic installation
pip install intent-kit[openai]  # With OpenAI support
pip install intent-kit[all]  # All LLM providers
```

## 💡 Key Features

- **Hierarchical Intent Graphs** - Build complex decision trees
- **Multi-Intent Routing** - Handle multiple intents in single input
- **Context Management** - Stateful conversations with dependency tracking
- **LLM Integration** - Support for OpenAI, Anthropic, Google, and Ollama
- **JSON Configuration** - Define graphs declaratively
- **Error Remediation** - Robust error handling and recovery
- **Evaluation Framework** - Test and benchmark your graphs

## 🎯 Use Cases

- **Chatbots** - Natural language conversation flows
- **Task Automation** - Complex workflow automation
- **API Orchestration** - Multi-step API integrations
- **Content Processing** - Intelligent content routing and processing
- **Decision Systems** - Rule-based and ML-powered decision making