# Core Concepts

Learn the fundamental concepts behind Intent Kit's DAG-based architecture.

## Architecture Overview

- **[Intent DAGs](intent-graphs.md)** - Understanding the core DAG structure and workflow design
- **[Nodes and Actions](nodes-and-actions.md)** - Building blocks for creating intelligent workflows
- **[Context Architecture](context-architecture.md)** - Managing state and memory across interactions

## Key Concepts

### DAG-Based Workflows

Intent Kit uses Directed Acyclic Graphs (DAGs) to structure intelligent workflows:

- **Nodes** represent decision points, extractors, or actions
- **Edges** define the flow between nodes with optional labels
- **Entrypoints** are starting nodes for user input
- **Flexible Routing** allows complex workflow patterns

### Node Types

- **Classifier Nodes** - Determine user intent and route to appropriate paths
- **Extractor Nodes** - Extract parameters from natural language using LLM
- **Action Nodes** - Execute specific actions and produce outputs
- **Clarification Nodes** - Handle unclear intent by asking for clarification

### Context Management

The context system provides:

- **State Persistence** - Maintain data across multiple interactions
- **Type Safety** - Validate and coerce data types
- **Audit Trails** - Track context modifications
- **Namespace Protection** - Protect system keys from conflicts

## Design Principles

### Separation of Concerns

Each node type has a specific responsibility:
- Classification is separate from parameter extraction
- Actions focus on execution, not understanding
- Context management is handled independently

### Flexibility

The DAG approach provides:
- **Scalable Architecture** - Add new nodes and paths easily
- **Reusable Components** - Share nodes across different DAGs
- **Complex Workflows** - Support sophisticated routing patterns
- **Error Handling** - Graceful degradation with clarification

### Reliability

Built-in features ensure robust operation:
- **Validation** - DAG structure and node configuration validation
- **Error Recovery** - Automatic routing to clarification nodes
- **Context Safety** - Protected namespaces and type validation
- **Execution Tracing** - Detailed logs for debugging and monitoring
