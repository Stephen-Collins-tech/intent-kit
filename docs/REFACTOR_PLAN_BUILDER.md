# Refactor Plan for `builder.py`

## Overview

The current `builder.py` file has grown to handle multiple responsibilities and contains duplicated logic. This refactor plan aims to improve code organization, maintainability, and reusability.

## Current Issues

### 1. **Mixed Responsibilities**
- Utility functions mixed with node creation functions
- Parameter extraction logic embedded in node creation
- No clear separation of concerns

### 2. **Code Duplication**
- Parent-child relationship setting repeated across functions
- Similar node creation patterns not abstracted
- Parameter extraction logic duplicated

### 3. **Large Functions**
- Some functions handle multiple concerns
- Complex parameter extraction logic in single functions
- Hard to test individual components

### 4. **Inconsistent Patterns**
- Different node creation functions have different parameter patterns
- No standardized approach to common operations

## Proposed Refactor Structure

### Phase 1: Extract Utility Modules ✅

**Created:**
- `intent_kit/utils/param_extraction.py` - Parameter extraction utilities
- `intent_kit/utils/node_factory.py` - Node creation factory functions

### Phase 2: Refactor `builder.py`

**New Structure:**
```
intent_kit/builder.py
├── Imports (organized by category)
├── Node Creation Functions (simplified)
├── IntentGraphBuilder Class (enhanced)
└── Convenience Functions
```

### Phase 3: Create Node Builders

**New Modules:**
- `intent_kit/builders/handler_builder.py`
- `intent_kit/builders/classifier_builder.py`
- `intent_kit/builders/splitter_builder.py`

## Detailed Refactor Steps

### Step 1: Update `builder.py` to use new utilities

```python
# Updated imports
from intent_kit.utils.param_extraction import create_arg_extractor
from intent_kit.utils.node_factory import (
    create_handler_node,
    create_classifier_node,
    create_splitter_node,
    set_parent_relationships
)

# Simplified handler function
def handler(
    *,
    name: str,
    description: str,
    handler_func: Callable[..., Any],
    param_schema: Dict[str, Type],
    llm_config: Optional[Dict[str, Any]] = None,
    extraction_prompt: Optional[str] = None,
    context_inputs: Optional[Set[str]] = None,
    context_outputs: Optional[Set[str]] = None,
    input_validator: Optional[Callable[[Dict[str, Any]], bool]] = None,
    output_validator: Optional[Callable[[Any], bool]] = None,
    remediation_strategies: Optional[List[Union[str, RemediationStrategy]]] = None,
) -> TreeNode:
    """Create a handler node with automatic argument extraction."""
    arg_extractor = create_arg_extractor(
        param_schema=param_schema,
        llm_config=llm_config,
        extraction_prompt=extraction_prompt,
        node_name=name
    )

    return create_handler_node(
        name=name,
        description=description,
        handler_func=handler_func,
        param_schema=param_schema,
        arg_extractor=arg_extractor,
        context_inputs=context_inputs,
        context_outputs=context_outputs,
        input_validator=input_validator,
        output_validator=output_validator,
        remediation_strategies=remediation_strategies,
    )
```

### Step 2: Create Node Builder Classes ✅

**Created fluent interface builders:**

```python
# Handler Builder Example
from intent_kit.builders import HandlerBuilder

greet_handler = (HandlerBuilder("greet")
    .with_description("Greet the user")
    .with_handler(lambda name: f"Hello {name}!")
    .with_param_schema({"name": str})
    .with_llm_config(LLM_CONFIG)
    .with_context_outputs({"user_name"})
    .build())

# Classifier Builder Example
from intent_kit.builders import ClassifierBuilder

classifier = (ClassifierBuilder("main_classifier")
    .with_description("Main intent classifier")
    .with_children([greet_handler, calc_handler, weather_handler])
    .with_remediation_strategies(["retry", "fallback"])
    .build())

# Splitter Builder Example
from intent_kit.builders import SplitterBuilder
from intent_kit.splitters.functions import rule_splitter

splitter = (SplitterBuilder("multi_intent_splitter")
    .with_description("Split multi-intent requests")
    .with_splitter(rule_splitter)
    .with_children([classifier])
    .build())
```

### Step 3: Enhance IntentGraphBuilder

```python
class IntentGraphBuilder:
    """Enhanced builder for creating IntentGraph instances."""
    
    def __init__(self):
        self._root_nodes: List[TreeNode] = []
        self._splitter = None
        self._debug_context = False
        self._context_trace = False
        self._llm_config = None
        self._visualize = False
    
    def add_root_node(self, node: TreeNode) -> "IntentGraphBuilder":
        """Add a root node to the graph."""
        self._root_nodes.append(node)
        return self
    
    def with_splitter(self, splitter_func) -> "IntentGraphBuilder":
        """Set a custom splitter function."""
        self._splitter = splitter_func
        return self
    
    def with_llm_config(self, llm_config: Dict[str, Any]) -> "IntentGraphBuilder":
        """Set LLM configuration for the graph."""
        self._llm_config = llm_config
        return self
    
    def with_visualization(self, enabled: bool = True) -> "IntentGraphBuilder":
        """Enable graph visualization."""
        self._visualize = enabled
        return self
    
    def build(self) -> IntentGraph:
        """Build and return the IntentGraph instance."""
        if not self._root_nodes:
            raise ValueError("No root nodes set. Call .add_root_node() before .build()")
        
        graph = IntentGraph(
            root_nodes=self._root_nodes,
            splitter=self._splitter,
            visualize=self._visualize,
            llm_config=self._llm_config,
            debug_context=self._debug_context,
            context_trace=self._context_trace,
        )
        
        return graph
```

## Benefits of This Refactor

### 1. **Separation of Concerns**
- Parameter extraction logic isolated in dedicated module
- Node creation logic separated from argument extraction
- Each module has a single, clear responsibility

### 2. **Improved Testability**
- Individual components can be tested in isolation
- Mock dependencies more easily
- Unit tests for specific functionality

### 3. **Enhanced Reusability**
- Utilities can be used across different modules
- Node factory functions can be reused
- Consistent patterns across the codebase

### 4. **Better Maintainability**
- Changes to parameter extraction only need to be made in one place
- Node creation patterns are standardized
- Easier to add new node types

### 5. **Fluent Interface Support**
- Builder pattern for complex node creation
- Method chaining for better readability
- Type-safe configuration

## Migration Strategy

### Phase 1: Create Utility Modules ✅
- [x] Extract parameter extraction utilities
- [x] Create node factory functions
- [x] Update imports in existing code

### Phase 2: Update builder.py ✅
- [x] Remove duplicated utility functions
- [x] Update node creation functions to use utilities
- [x] Enhance IntentGraphBuilder class
- [x] Add comprehensive type hints
- [x] Remove duplicate IntentGraphBuilder from serialization.py

### Phase 3: Create Node Builders ✅
- [x] Create HandlerBuilder class
- [x] Create ClassifierBuilder class
- [x] Create SplitterBuilder class
- [x] Add fluent interface examples

### Phase 4: Update Documentation
- [ ] Update docstrings and examples
- [ ] Create migration guide
- [ ] Add usage examples for new patterns

## Backward Compatibility

The refactor maintains backward compatibility by:
- Keeping existing function signatures
- Preserving the same return types
- Maintaining the same behavior for existing code
- Adding new functionality without breaking changes

## Testing Strategy

### Unit Tests
- Test parameter extraction utilities independently
- Test node factory functions with mocked dependencies
- Test builder classes with various configurations

### Integration Tests
- Test complete graph creation workflows
- Test serialization/deserialization with new utilities
- Test backward compatibility with existing code

### Performance Tests
- Benchmark parameter extraction performance
- Test memory usage with large graphs
- Compare performance before and after refactor

## Summary of Accomplishments

### ✅ **Phase 1: Extract Utility Modules (COMPLETED)**
- **Created `intent_kit/utils/param_extraction.py`** - Contains all parameter extraction logic
- **Created `intent_kit/utils/node_factory.py`** - Contains node creation factory functions
- **Eliminated code duplication** between `builder.py` and `serialization.py`

### ✅ **Phase 2: Refactor `builder.py` (COMPLETED)**
- **Organized imports** by category (core, node types, LLM, utilities)
- **Removed duplicated utility functions** that are now in separate modules
- **Simplified node creation functions** to use new utilities
- **Enhanced IntentGraphBuilder** with support for multiple root nodes, LLM config, and visualization
- **Removed duplicate IntentGraphBuilder** from `serialization.py`

### ✅ **Phase 3: Create Node Builders (COMPLETED)**
- **Created `HandlerBuilder`** - Fluent interface for creating handler nodes
- **Created `ClassifierBuilder`** - Fluent interface for creating classifier nodes  
- **Created `SplitterBuilder`** - Fluent interface for creating splitter nodes
- **Added comprehensive validation** and error handling in builders
- **Integrated with existing utilities** for consistent behavior

### 🎯 **Key Benefits Achieved**

1. **Separation of Concerns** ✅
   - Parameter extraction logic isolated in dedicated module
   - Node creation logic separated from argument extraction
   - Each module has a single, clear responsibility

2. **Improved Testability** ✅
   - Individual components can be tested in isolation
   - Mock dependencies more easily
   - Unit tests for specific functionality

3. **Enhanced Reusability** ✅
   - Utilities can be used across different modules
   - Node factory functions can be reused
   - Consistent patterns across the codebase

4. **Better Maintainability** ✅
   - Changes to parameter extraction only need to be made in one place
   - Node creation patterns are standardized
   - Easier to add new node types

5. **Fluent Interface Support** ✅
   - Builder pattern for complex node creation
   - Method chaining for better readability
   - Type-safe configuration

6. **Reduced Code Duplication** ✅
   - Eliminated duplicated parent-child relationship setting
   - Removed duplicated parameter extraction logic
   - Standardized node creation patterns

### 🔄 **Backward Compatibility** ✅
- All existing function signatures preserved
- Same return types maintained
- Existing behavior unchanged
- New functionality added without breaking changes

### 📚 **Usage Examples**

**Traditional approach (still supported):**
```python
greet_handler = handler(
    name="greet",
    description="Greet the user", 
    handler_func=lambda name: f"Hello {name}!",
    param_schema={"name": str},
    llm_config=LLM_CONFIG
)
```

**New fluent interface:**
```python
greet_handler = (HandlerBuilder("greet")
    .with_description("Greet the user")
    .with_handler(lambda name: f"Hello {name}!")
    .with_param_schema({"name": str})
    .with_llm_config(LLM_CONFIG)
    .build())
```

## Conclusion

This refactor successfully addresses all the original issues in `builder.py` while maintaining backward compatibility and improving the overall code quality. The modular approach makes the codebase more maintainable and easier to extend in the future. The new fluent interface provides an alternative, more readable way to create complex node configurations. 