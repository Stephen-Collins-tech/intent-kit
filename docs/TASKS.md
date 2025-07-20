# Root TASKS.md

## **Overview**

This document covers the open-source core engine, developer APIs, intent classification, classifier plug-ins, param extraction, reliability, and core CLI demos.

### **Current API Status**
- ✅ **IntentGraphBuilder API**: Fluent interface for building intent graphs
- ✅ **Simplified Action Creation**: `action()` function with automatic argument extraction
- ✅ **LLM Classifier Helper**: `llm_classifier()` function with auto-wired descriptions
- ✅ **Context Integration**: All demos use IntentContext for state management
- ✅ **Multi-Intent Demo**: Uses LLM-powered splitting for intelligent intent handling
- ✅ **JSON-Based Construction**: Flat JSON API for IntentGraphBuilder (complete)

---

## **Core Engine (OSS)**

### **1. Intent Tree & Action Engine**

* [x] API for declaring intent trees, named intents, parameters, action registration.
* [x] Parameter typing/schema for each intent.
* [x] Tree-based intent architecture with classifier and intent nodes.
* [x] Flexible node system mixing classifier nodes and intent nodes.

### **2. IntentGraph Multi-Intent Routing**

* [x] **IntentGraph Data Structure** - Root-level dispatcher for user input
* [x] **Function-Based Intent Splitting** - Rule-based and LLM-based splitters
* [x] **Multi-Tree Dispatch** - Route to multiple intent trees
* [x] **Orchestration and Aggregation** - Consistent result format
* [x] **Fallbacks and Error Handling** - Comprehensive error management
* [x] **Logging and Debugging** - Integrated with logger system
* [x] **Interactive Visualization** - HTML graph generation of execution paths

### **3. Classifier Plug-in Support**

* [x] Rule-based (keyword/regex) classifiers.
* [x] LLM-backed classifiers (OpenAI, function-calling, JSON output).
* [x] Classifier confidence scoring and routing.
* [x] Support for OpenAI, Anthropic, Google AI, and Ollama services.

**Current Classifiers Status:**
- ✅ **Keyword Classifier** - Simple substring matching
- ✅ **LLM Classifier** - Generic LLM-powered classification with multiple backends
- ✅ **OpenAI Integration** - GPT models via LLM factory
- ✅ **Google Integration** - Gemini models via LLM factory
- ✅ **Anthropic Integration** - Claude models via LLM factory
- ✅ **Ollama Integration** - Local models via LLM factory

**Additional Classifiers to Implement:**
- [ ] **Regex Classifier** - Pattern-based matching
- [ ] **Fuzzy Match Classifier** - Handle typos and variations
- [ ] **Confidence-Based Classifier Wrapper** - Add confidence scoring
- [ ] **Ensemble Classifier** - Combine multiple classifiers
- [ ] **Semantic Search Classifier** - Vector similarity
- [ ] **Hybrid Classifier** - Rule-based + ML approaches

### **4. Parameter Extraction**

* [x] Pluggable param extraction: regex, LLM, hybrid.
* [x] Human-in-the-loop fallback (CLI/MVP).
* [x] Automatic parameter extraction with type validation.
* [x] LLM-powered argument extraction with multiple backends.

### **5. Action Execution**

* [x] Typed action execution, structured error surfaces.
* [x] Comprehensive error handling with detailed logging.
* [x] Context-aware execution with dependency tracking.

---

## **Developer Experience (DX)**

### **6. IntentGraphBuilder & Simplified API**

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

**Current Status:**
- ✅ **IntentGraphBuilder** - Fluent interface for building intent graphs
- ✅ **action() Function** - Simplified action creation with automatic argument extraction
- ✅ **llm_classifier() Function** - Simplified LLM classifier creation with auto-wired descriptions
- ✅ **llm_splitter_node() Function** - Simplified splitter node creation
- ✅ **rule_splitter_node() Function** - Simplified rule-based splitter creation
- ✅ **Auto-Description Wiring** - Automatic generation of node descriptions for classifiers
- ✅ **Integrated LLM Config** - Seamless LLM configuration integration

### **6.1. IntentGraphBuilder JSON API Refactoring**

**Current Status:**
- ✅ **JSON-Based Construction** - Flat JSON API for IntentGraphBuilder (complete)
- ✅ **Function Registry Support** - Function mapping for JSON-based construction
- ✅ **YAML Support** - YAML file loading and parsing
- ✅ **Graph Validation** - Cycle detection and validation
- ✅ **Backward Compatibility** - Original manual API still works
- ✅ **Error Handling** - Comprehensive validation and error messages

#### **Checklist: Refactor IntentGraphBuilder for Flat JSON API**

* [x] **Add `.with_json(json_graph: dict)` method**

  * Accept and store a flat intent graph JSON/dict in a private property.

* [x] **Add `.with_functions(function_registry: dict)` method**

  * Accept and store a function registry (mapping function names to callables).

* [x] **Refactor `.build()` to support flat JSON graph**

  * If `.with_json()` has been called, construct the graph using the JSON and registry.
  * Otherwise, fall back to manual root node logic.

* [x] **Implement `_build_from_json(graph_spec: dict, function_registry: dict)`**

  * Create all nodes as `TreeNode` objects, mapping by ID.
  * Link nodes by resolving `children` IDs.
  * Identify and use the root node from `graph_spec["root"]`.
  * Pass through any `llm_config` if present.
  * Return an `IntentGraph` instance.

* [x] **Add error handling and validation**

  * Raise clear errors for missing/invalid child or function references.
  * Raise a clear error for missing/invalid root node.

* [x] **Update docstrings and provide usage examples**

  * Document usage for both JSON-driven and manual API.
  * Add code example showing function registry + JSON input.

* [x] **(Optional) Add `.with_yaml(path_or_obj)` for YAML support**

  * Parse YAML and treat as JSON/dict.

* [x] **Add comprehensive JSON validation**

  * Internal validation during build ensures graph integrity
  * Optional public validation API for detailed validation reporting
  * Validate cycles, unreachable nodes, and duplicate IDs

---

**JSON API Example:**
```python
# Flat JSON-based construction
json_graph = {
    "root": "greet_classifier",
    "intents": {
        "greet_classifier": {
            "type": "llm_classifier",
            "children": ["greet_action"],
            "llm_config": {...}
        },
        "greet_action": {
            "type": "action",
            "function": "greet_user",
            "param_schema": {"name": "string"}
        }
    }
}

function_registry = {
    "greet_user": greet_user_function
}

graph = IntentGraphBuilder().with_json(json_graph).with_functions(function_registry).build()
```

### **7. Context System**

* [x] **IntentContext Class** - Session-aware context management
* [x] **Dependency Tracking** - Automatic tracking of context inputs/outputs
* [x] **Context Validation** - Validate context flow and dependencies
* [x] **Context Debugging** - Debug context state and flow
* [x] **Context Tracing** - Trace context changes during execution

**Current Status:**
- ✅ **IntentContext** - Session-aware context management
- ✅ **Dependency Tracking** - Automatic tracking of context inputs/outputs
- ✅ **Context Validation** - Validate context flow and dependencies
- ✅ **Context Debugging** - Debug context state and flow
- ✅ **Context Tracing** - Trace context changes during execution

### **8. Remediation System**

* [x] **Remediation Strategies** - Pluggable error handling strategies
* [x] **Retry Strategies** - Exponential backoff and retry logic
* [x] **Fallback Strategies** - Fallback to alternative actions
* [x] **Self-Reflection Strategies** - LLM self-reflection for error recovery
* [x] **Consensus Voting Strategies** - Multiple LLM consensus for reliability
* [x] **Custom Strategies** - User-defined remediation strategies

**Current Status:**
- ✅ **Remediation Strategies** - Pluggable error handling strategies
- ✅ **Retry Strategies** - Exponential backoff and retry logic
- ✅ **Fallback Strategies** - Fallback to alternative actions
- ✅ **Self-Reflection Strategies** - LLM self-reflection for error recovery
- ✅ **Consensus Voting Strategies** - Multiple LLM consensus for reliability
- ✅ **Custom Strategies** - User-defined remediation strategies

---

## **Evaluation & Testing**

### **9. Eval API**

* [x] **Dataset Loading** - YAML and programmatic dataset loading
* [x] **Evaluation Engine** - Run evaluations on nodes and graphs
* [x] **Reporting** - Markdown, CSV, and JSON output
* [x] **Mock Mode** - API-free testing mode
* [x] **Regression Tracking** - Track results over time

**Current Status:**
- ✅ **Dataset Loading** - YAML and programmatic dataset loading
- ✅ **Evaluation Engine** - Run evaluations on nodes and graphs
- ✅ **Reporting** - Markdown, CSV, and JSON output
- ✅ **Mock Mode** - API-free testing mode
- ✅ **Regression Tracking** - Track results over time

### **10. Testing Infrastructure**

* [x] **Unit Tests** - Comprehensive unit test coverage
* [x] **Integration Tests** - End-to-end integration tests
* [x] **Mock Tests** - Mock-based testing for external dependencies
* [x] **Performance Tests** - Performance benchmarking
* [x] **Coverage Reports** - Code coverage tracking

**Current Status:**
- ✅ **Unit Tests** - Comprehensive unit test coverage
- ✅ **Integration Tests** - End-to-end integration tests
- ✅ **Mock Tests** - Mock-based testing for external dependencies
- ✅ **Performance Tests** - Performance benchmarking
- ✅ **Coverage Reports** - Code coverage tracking

---

## **Documentation & Examples**

### **11. Documentation**

* [x] **API Documentation** - Comprehensive API reference
* [x] **User Guides** - Step-by-step user guides
* [x] **Examples** - Working examples and demos
* [x] **Jupyter Notebooks** - Interactive notebooks
* [x] **Tutorials** - Tutorial series for different use cases

**Current Status:**
- ✅ **API Documentation** - Comprehensive API reference
- ✅ **User Guides** - Step-by-step user guides
- ✅ **Examples** - Working examples and demos
- ✅ **Jupyter Notebooks** - Interactive notebooks
- ✅ **Tutorials** - Tutorial series for different use cases

### **12. Examples & Demos**

* [x] **Simple Demo** - Basic intent graph example
* [x] **Multi-Intent Demo** - Multi-intent handling example
* [x] **Context Demo** - Context-aware workflows
* [x] **Remediation Demo** - Error handling and remediation
* [x] **Advanced Remediation Demo** - Advanced remediation strategies
* [x] **Classifier Remediation Demo** - Classifier-specific remediation
* [x] **Ollama Demo** - Local LLM integration
* [x] **JSON Config Demo** - Configuration-driven graphs

**Current Status:**
- ✅ **Simple Demo** - Basic intent graph example
- ✅ **Multi-Intent Demo** - Multi-intent handling example
- ✅ **Context Demo** - Context-aware workflows
- ✅ **Remediation Demo** - Error handling and remediation
- ✅ **Advanced Remediation Demo** - Advanced remediation strategies
- ✅ **Classifier Remediation Demo** - Classifier-specific remediation
- ✅ **Ollama Demo** - Local LLM integration
- ✅ **JSON Config Demo** - Configuration-driven graphs

---

## **Future Enhancements**

### **13. Advanced Features**

* [ ] **Graph Serialization** - Save/load intent graphs
* [ ] **Graph Versioning** - Version control for intent graphs
* [ ] **Graph Migration** - Migration tools for graph updates
* [ ] **Graph Optimization** - Performance optimization for large graphs
* [ ] **Graph Validation** - Comprehensive graph validation

### **14. Enterprise Features**

* [ ] **Multi-Tenant Support** - Multi-tenant architecture
* [ ] **Audit Logging** - Comprehensive audit logging
* [ ] **Security Features** - Security and compliance features
* [ ] **Scalability** - Horizontal scaling support
* [ ] **Monitoring** - Production monitoring and alerting

### **15. Ecosystem Integration**

* [ ] **Framework Integrations** - Integration with popular frameworks
* [ ] **Cloud Provider Support** - Cloud provider integrations
* [ ] **CI/CD Integration** - Continuous integration support
* [ ] **Deployment Tools** - Deployment and orchestration tools
* [ ] **Plugin System** - Extensible plugin architecture

---

## **Completed Tasks**

### **Phase 1: Core Engine** ✅
- [x] Basic intent tree architecture
- [x] Handler node implementation
- [x] Classifier node implementation
- [x] Parameter extraction system
- [x] Basic error handling
- [x] Simple examples and demos

### **Phase 2: Enhanced Features** ✅
- [x] IntentGraph multi-intent routing
- [x] Context system with dependency tracking
- [x] Remediation strategies
- [x] Advanced error handling
- [x] LLM integration improvements
- [x] Enhanced examples and demos

### **Phase 3: Developer Experience** ✅
- [x] IntentGraphBuilder fluent interface
- [x] Simplified action creation API
- [x] Auto-wired classifier descriptions
- [x] Context debugging tools
- [x] Comprehensive documentation
- [x] Evaluation API

### **Phase 4: JSON API Integration** 🚧
- [ ] IntentGraphBuilder JSON API refactoring
- [ ] Flat graph construction from JSON
- [ ] Function registry support
- [ ] Input validation and error handling
- [ ] Enhanced documentation and examples

### **Phase 5: Production Ready** 🚧
- [ ] Performance optimization
- [ ] Advanced testing infrastructure
- [ ] Enterprise features
- [ ] Cloud integrations
- [ ] Production deployment tools
