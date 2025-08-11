# Context Architecture

## Overview

The Intent Kit framework provides a sophisticated context management system that supports both persistent state management and execution tracking. This document covers the architectural design, implementation details, and practical usage of the context system.

## Architecture Components

### BaseContext Abstract Base Class

The `BaseContext` abstract base class provides a unified interface for all context implementations, extracting shared characteristics between `Context` and `StackContext` classes.

#### Shared Characteristics
- Session-based architecture with UUID generation
- Debug logging support with configurable verbosity
- Error tracking capabilities with structured logging
- State persistence patterns with export functionality
- Thread safety considerations
- Common utility methods for logging and session management

#### Abstract Methods
- `get_error_count()` - Get total number of errors
- `add_error()` - Add error to context log
- `get_errors()` - Retrieve errors with optional filtering
- `clear_errors()` - Clear all errors
- `get_history()` - Get operation history
- `export_to_dict()` - Export context to dictionary

#### Concrete Utility Methods
- `get_session_id()` - Get session identifier
- `is_debug_enabled()` - Check debug mode status
- `log_debug()`, `log_info()`, `log_error()` - Structured logging methods
- `__str__()` and `__repr__()` - String representations

### Context Class

The `Context` class provides thread-safe state management for workflow execution with key-value storage and comprehensive audit trails.

#### Core Features
- **State Management**: Direct key-value storage with field-level locking
- **Thread Safety**: Field-level locking for concurrent access
- **Audit Trail**: Operation history (get/set/delete) with metadata
- **Error Tracking**: Error entries with comprehensive metadata
- **Session Management**: Session-based isolation

#### Data Structures
```python
@dataclass
class ContextField:
    value: Any
    lock: Lock
    last_modified: datetime
    modified_by: Optional[str]
    created_at: datetime

@dataclass
class ContextHistoryEntry:
    timestamp: datetime
    action: str  # 'set', 'get', 'delete'
    key: str
    value: Any
    modified_by: Optional[str]
    session_id: Optional[str]

@dataclass
class ContextErrorEntry:
    timestamp: datetime
    node_name: str
    user_input: str
    error_message: str
    error_type: str
    stack_trace: str
    params: Optional[Dict[str, Any]]
    session_id: Optional[str]
```

### StackContext Class

The `StackContext` class provides execution stack tracking and context state snapshots for debugging and analysis.

#### Core Features
- **Execution Stack Management**: Call stack tracking with parent-child relationships
- **Context State Snapshots**: Complete context state capture at each frame
- **Graph Execution Tracking**: Node path tracking through the graph
- **Execution Flow Analysis**: Frame-based execution history

#### Data Structures
```python
@dataclass
class StackFrame:
    frame_id: str
    timestamp: datetime
    function_name: str
    node_name: str
    node_path: List[str]
    user_input: str
    parameters: Dict[str, Any]
    context_state: Dict[str, Any]
    context_field_count: int
    context_history_count: int
    context_error_count: int
    depth: int
    parent_frame_id: Optional[str]
    children_frame_ids: List[str]
    execution_result: Optional[Dict[str, Any]]
    error_info: Optional[Dict[str, Any]]
```

## Inheritance Hierarchy

```
BaseContext (ABC)
├── Context (concrete implementation)
└── StackContext (concrete implementation)
```

## Integration Patterns

### How Context and StackContext Work Together

1. **StackContext depends on Context**
   - StackContext takes a Context instance in constructor
   - StackContext captures Context state in frames
   - StackContext queries Context for state information

2. **Complementary Roles**
   - Context: Persistent state storage
   - StackContext: Execution flow tracking

3. **Shared Session Identity**
   - Both use the same session_id for correlation
   - Both maintain session-specific state

## Practical Usage Guide

### Basic Context Usage

#### Creating and Configuring Context

```python
from intent_kit.context import Context

# Basic context with default settings
context = Context()

# Context with custom session ID and debug mode
context = Context(
    session_id="my-custom-session",
    debug=True
)

# Context with specific configuration
context = Context(
    session_id="workflow-123",
    debug=True,
    log_level="DEBUG"
)
```

#### State Management Operations

```python
# Setting values
context.set("user_id", "12345", modified_by="auth_node")
context.set("preferences", {"theme": "dark", "language": "en"})

# Getting values
user_id = context.get("user_id")
preferences = context.get("preferences")

# Checking existence
if context.has("user_id"):
    print("User ID exists")

# Deleting values
context.delete("temporary_data")

# Getting all keys
all_keys = context.keys()

# Clearing all data
context.clear()
```

#### Error Handling

```python
# Adding errors
context.add_error(
    node_name="classifier_node",
    user_input="Hello world",
    error_message="Failed to classify intent",
    error_type="ClassificationError",
    params={"confidence": 0.3}
)

# Getting error count
error_count = context.get_error_count()

# Getting all errors
all_errors = context.get_errors()

# Getting errors for specific node
node_errors = context.get_errors(node_name="classifier_node")

# Clearing errors
context.clear_errors()
```

#### History and Audit Trail

```python
# Getting operation history
history = context.get_history()

# Getting history for specific key
key_history = context.get_history(key="user_id")

# Getting recent operations
recent_history = context.get_history(limit=10)
```

### StackContext Usage

#### Creating StackContext

```python
from intent_kit.context import Context, StackContext

# Create base context
context = Context(session_id="workflow-123", debug=True)

# Create stack context that wraps the base context
stack_context = StackContext(context)
```

#### Execution Tracking

```python
# Push a frame when entering a node
frame_id = stack_context.push_frame(
    function_name="classify_intent",
    node_name="intent_classifier",
    node_path=["root", "classifier"],
    user_input="Hello world",
    parameters={"model": "gpt-3.5-turbo"}
)

# Execute your logic here
result = {"intent": "greeting", "confidence": 0.95}

# Pop the frame when exiting the node
stack_context.pop_frame(frame_id, execution_result=result)
```

#### Debugging and Analysis

```python
# Get current frame
current_frame = stack_context.get_current_frame()

# Get all frames
all_frames = stack_context.get_all_frames()

# Get frames for specific node
node_frames = stack_context.get_frames_by_node("intent_classifier")

# Get frames for specific function
function_frames = stack_context.get_frames_by_function("classify_intent")

# Get frame by ID
specific_frame = stack_context.get_frame_by_id("frame-123")

# Print stack trace
stack_context.print_stack_trace()

# Get execution summary
summary = stack_context.get_execution_summary()
```

#### Context State Analysis

```python
# Get context changes between frames
changes = stack_context.get_context_changes_between_frames(
    frame_id_1="frame-1",
    frame_id_2="frame-2"
)

# Export complete state
export_data = stack_context.export_to_dict()
```

### Advanced Usage Patterns

#### Polymorphic Context Usage

```python
from intent_kit.context import Context, StackContext, BaseContext
from typing import List

# Create different context types
contexts: List[BaseContext] = [
    Context(session_id="session-1"),
    StackContext(Context(session_id="session-2"))
]

# Use them polymorphically
for ctx in contexts:
    ctx.add_error("test_node", "test_input", "test_error", "test_type")
    print(f"Session: {ctx.get_session_id()}, Errors: {ctx.get_error_count()}")
```

#### Context Serialization

```python
# Export context to dictionary
context_data = context.export_to_dict()

# Export stack context
stack_data = stack_context.export_to_dict()

# Both return consistent dictionary structures
assert "session_id" in context_data
assert "session_id" in stack_data
```

#### Thread-Safe Operations

```python
import threading
from intent_kit.context import Context

context = Context(session_id="multi-threaded")

def worker(thread_id: int):
    for i in range(10):
        context.set(f"thread_{thread_id}_value_{i}", i, modified_by=f"thread_{thread_id}")

# Create multiple threads
threads = []
for i in range(3):
    thread = threading.Thread(target=worker, args=(i,))
    threads.append(thread)
    thread.start()

# Wait for all threads to complete
for thread in threads:
    thread.join()

# All operations are thread-safe
print(f"Total fields: {len(context.keys())}")
```

#### Integration with Intent Graphs

```python
from intent_kit.graph import IntentGraphBuilder
from intent_kit.context import Context, StackContext

# Create context
context = Context(session_id="graph-execution", debug=True)
stack_context = StackContext(context)

# Build graph
builder = IntentGraphBuilder()
graph = builder.add_node(classifier_node).build()

# Execute with context
result = graph.execute("Hello world", context=stack_context)

# Analyze execution
frames = stack_context.get_all_frames()
print(f"Execution involved {len(frames)} frames")
```

## Performance Characteristics

### Context Performance
- **Memory**: Linear with number of fields
- **Operations**: O(1) for field access with locking overhead
- **History**: Linear growth with operations
- **Threading**: Field-level locking for concurrent access

### StackContext Performance
- **Memory**: Linear with number of frames
- **Operations**: O(1) for frame access, O(n) for context snapshots
- **History**: Frame-based with complete state snapshots
- **Threading**: Relies on Context's thread safety

## Design Patterns

### Context Patterns
- **Builder Pattern**: Field creation and modification
- **Observer Pattern**: History tracking of all operations
- **Factory Pattern**: ContextField creation
- **Decorator Pattern**: Metadata wrapping of values

### StackContext Patterns
- **Stack Pattern**: LIFO frame management
- **Snapshot Pattern**: State capture at each frame
- **Visitor Pattern**: Frame traversal and analysis
- **Memento Pattern**: State restoration capabilities

## Best Practices

### 1. **Context Management**
- Use descriptive session IDs for easy identification
- Enable debug mode during development
- Clear sensitive data when no longer needed
- Use meaningful field names and metadata

### 2. **Error Handling**
- Add errors with descriptive messages and types
- Include relevant parameters for debugging
- Use consistent error types across your application
- Regularly check error counts and clear when appropriate

### 3. **Performance Optimization**
- Limit history size for long-running applications
- Use StackContext selectively (not for every operation)
- Consider frame snapshot frequency based on debugging needs
- Monitor memory usage with large context states

### 4. **Thread Safety**
- Context operations are thread-safe by default
- Use field-level locking for concurrent access
- Avoid long-running operations while holding locks
- Consider async patterns for high-concurrency scenarios

### 5. **Debugging and Monitoring**
- Use StackContext for execution flow analysis
- Export context state for external analysis
- Monitor error rates and patterns
- Track context size and growth over time

## Use Case Analysis

### Context Use Cases
- **State Persistence**: Storing user data, configuration, results
- **Cross-Node Communication**: Sharing data between workflow steps
- **Audit Trails**: Tracking all state modifications
- **Error Accumulation**: Collecting errors across execution

### StackContext Use Cases
- **Execution Debugging**: Understanding execution flow
- **Performance Analysis**: Tracking execution patterns
- **Error Diagnosis**: Identifying where errors occurred
- **State Evolution**: Understanding how context changes during execution

## Troubleshooting

### Common Issues

1. **Memory Growth**
   - Clear history periodically
   - Limit frame snapshots in StackContext
   - Monitor context size in long-running applications

2. **Thread Contention**
   - Avoid long operations while holding locks
   - Consider async patterns for high concurrency
   - Use field-level operations when possible

3. **Debug Information Missing**
   - Ensure debug mode is enabled
   - Check log level configuration
   - Verify session ID is set correctly

4. **Performance Issues**
   - Monitor operation frequency
   - Consider caching for frequently accessed data
   - Optimize frame snapshot frequency

## Future Enhancements

### Potential New Context Types
- `AsyncContext` - For async/await patterns
- `PersistentContext` - For database-backed state
- `DistributedContext` - For multi-process scenarios
- `CachedContext` - For performance optimization

### Additional Features
- `import_from_dict()` - For deserialization
- `validate_state()` - For state validation
- `get_statistics()` - For performance metrics
- `backup()` and `restore()` - For state persistence

## Conclusion

The context architecture in Intent Kit provides a robust foundation for state management and execution tracking. By following the patterns and best practices outlined in this guide, you can:

- **Build reliable applications** with comprehensive state management
- **Debug effectively** with detailed execution tracking
- **Scale applications** with thread-safe operations
- **Monitor performance** with built-in analytics capabilities

The architecture follows the Intent Kit project's patterns and provides a solid foundation for future enhancements while maintaining clear boundaries between concerns.
