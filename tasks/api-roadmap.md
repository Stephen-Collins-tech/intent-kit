# API Roadmap & Developer Experience

## Current API Status
- ✅ **IntentGraphBuilder API**: Fluent interface for building intent graphs
- ✅ **Simplified Action Creation**: `action()` function with automatic argument extraction
- ✅ **LLM Classifier Helper**: `llm_classifier()` function with auto-wired descriptions
- ✅ **Context Integration**: All demos use IntentContext for state management
- ✅ **Multi-Intent Demo**: Uses LLM-powered splitting for intelligent intent handling
- ✅ **JSON-Based Construction**: Flat JSON API for IntentGraphBuilder (complete)

---

## Developer Experience (DX)

### IntentGraphBuilder & Simplified API

* [x] **IntentGraphBuilder Class** - Fluent interface for building intent graphs
* [x] **action() Function** - Simplified action creation with automatic argument extraction
* [x] **llm_classifier() Function** - Simplified LLM classifier creation with auto-wired descriptions
* [x] **llm_splitter_node() Function** - Simplified splitter node creation
* [x] **rule_splitter_node() Function** - Simplified rule-based splitter creation
* [x] **Auto-Description Wiring** - Automatic generation of node descriptions for classifiers
* [x] **Integrated LLM Config** - Seamless LLM configuration integration

**API Examples:**
```python
# Create actions with automatic argument extraction
action = action(name="greet", action_func=greet_func, param_schema={"name": str}, llm_config=LLM_CONFIG)

# Create classifiers with auto-wired descriptions
classifier = llm_classifier(name="root", children=[action1, action2], llm_config=LLM_CONFIG)

# Build complete graphs
graph = IntentGraphBuilder().root(classifier).build()
```

### JSON API Refactoring

* [x] **JSON-Based Construction** - Flat JSON API for IntentGraphBuilder (complete)
* [x] **Function Registry Support** - Function mapping for JSON-based construction
* [x] **YAML Support** - YAML file loading and parsing
* [x] **Graph Validation** - Cycle detection and validation
* [x] **Backward Compatibility** - Original manual API still works
* [x] **Error Handling** - Comprehensive validation and error messages

#### Checklist: Refactor IntentGraphBuilder for Flat JSON API

* [x] **Add `.with_json(json_graph: dict)` method**
* [x] **Add `.with_functions(function_registry: dict)` method**
* [x] **Refactor `.build()` to support flat JSON graph**
* [x] **Implement `_build_from_json(graph_spec: dict, function_registry: dict)`**
* [x] **Add error handling and validation**
* [x] **Update docstrings and provide usage examples**
* [x] **(Optional) Add `.with_yaml(path_or_obj)` for YAML support**
* [x] **Add comprehensive JSON validation**

---

## Future Enhancements (API/DX)

- [ ] **Graph Serialization** - Save/load intent graphs
- [ ] **Graph Versioning** - Version control for intent graphs
- [ ] **Graph Migration** - Migration tools for graph updates
- [ ] **Graph Optimization** - Performance optimization for large graphs
- [ ] **Graph Validation** - Comprehensive graph validation
