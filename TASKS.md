# Root TASKS.md

## **Overview**

This document covers the open-source core engine, developer APIs, intent classification, classifier plug-ins, param extraction, reliability, and core CLI demos.

---

## **Core Engine (OSS)**

### **1. Intent Tree & Handler Engine**

* [x] API for declaring intent trees, named intents, parameters, handler registration.
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

### **5. Handler Execution**

* [x] Typed handler execution, structured error surfaces.
* [x] Comprehensive error handling with detailed logging.
* [x] Context-aware execution with dependency tracking.

---

## **Reliability, Observability, Audit**

* [x] Structured error reporting and logging.
* [x] Per-request trace/workflow audit log.
* [x] Surface confidence/errors in API responses.
* [x] Robust error handling with no unhandled exceptions.
* [x] Interactive execution path visualization.

---

## **Developer Experience (DX)**

* [x] Minimal API for declaring intent trees.
* [x] Document core APIs, cookbook, patterns.
* [x] Comprehensive unit/integration tests.
* [x] Type safety with full type hints throughout.
* [x] Clean, Pythonic API design.

---

## **Integrations & Connectors**

* [x] Support OpenAI, Anthropic, Google AI, Ollama for classifier/param extraction.
* [x] Outbound connectors (webhooks, email, REST; can provide stubs).
* [x] AI service integration with multiple backends via LLM factory.

---

## **Demos & Recipes**

* [x] **simple_demo.py** - Basic IntentGraph with LLM integration
* [x] **context_demo.py** - Complete context-aware workflow example
* [x] **ollama_demo.py** - Local Ollama models for offline processing
* [x] **error_demo.py** - Error handling and debugging features
* [x] All demos documented, runnable from CLI.
* [x] Comprehensive examples with real LLM integration.

---

## **Context & Task State Management**

Support for robust, agent-like workflows in intent-kit depends on introducing a first-class, extensible `Context` entity.
This section tracks requirements and implementation progress for context-driven agent task state:

### **Context Entity & Task State Management**

* [x] **Simple Context Object**
  Implement a minimal, idiomatic `IntentContext` (user/session ID, params, results, metadata, history).

* [x] **Context Package Structure**
  Move context entity to its own subpackage (`context/`), enable multiple context types.

* [x] **Context Pass-through & Mutation**
  Ensure context is passed to all intent trees, handlers, splitters, and can be mutated at every step.

* [x] **Multi-Turn/Session Context Support**
  Add support for persistent context objects spanning multiple user turns/workflows (not just single input).

* [x] **Per-Field (Fine-Grained) Locking**
  Implement per-field lockable dicts for concurrent, safe mutation during parallel/async intent execution.

* [x] **Context Dependency Declarations**
  Require intents to declare context fields they read/write (`inputs`, `outputs`) for dependency graph building.

* [x] **Task State & History Logging**
  Log all steps, mutations, and outcomes in context history for replay/audit.

* [ ] **Context Debug/Trace API**
  Expose APIs/utilities for inspecting context evolution and intent/task state transitions.

* [ ] **Type-Safe Context Extensions**
  Allow domain-specific extensions and type-safe fields for custom workflows.

> **Implementation Notes:**
> - ✅ **IntentContext Class**: Thread-safe context with field-level locking, complete audit trail, and session isolation
> - ✅ **Context Dependencies**: Declarative system for specifying what fields intents read/write
> - ✅ **Backward Compatibility**: Existing handlers work without modification, context is optional
> - ✅ **Context as Final Parameter**: All handlers receive context as the final parameter for consistency
> - ✅ **Enhanced IntentNode**: Supports context_inputs and context_outputs declarations
> - ✅ **Updated IntentGraph**: Passes context through all execution paths with fallback support
> - ✅ **Demo Implementation**: Complete working example in `examples/context_demo.py`
> - ✅ **Splitter Integration**: Basic support added, needs testing with context-aware splitters
> - 🔄 **Advanced Features**: Debug API and type-safe extensions planned for future iterations

> **Note:**
> intent-kit's agent/task state is always explicit and auditable—never emergent.
> All task context, dependencies, and results must be statically declared and analyzable.

---

## **IntentGraph Implementation Status**

### ✅ **Completed Features:**

1. **IntentGraph Data Structure** (`graph/intent_graph.py`)
   - Registry of root nodes with `.route()` method support
   - `add_root_node()`, `remove_root_node()`, `list_root_nodes()`
   - Consistent `ExecutionResult` return format

2. **Function-Based Splitters** (`graph/splitters/`)
   - `rule_splitter()` - Keyword-based intent splitting
   - `llm_splitter()` - LLM-powered intent splitting
   - Custom splitter function support
   - Graceful fallback from LLM to rule-based

3. **Multi-Tree Dispatch**
   - Route to multiple intent trees based on splits
   - Exception handling for tree calls
   - Error aggregation in consistent format

4. **Orchestration and Aggregation**
   - Unified result aggregation
   - Consistent output format for single/multi-intent

5. **API/Interface Design**
   - Clean Pythonic API: `IntentGraph(splitter=rule_splitter)`
   - Custom splitter support
   - Consistent return format

6. **Error Handling & Fallbacks**
   - No recognizable intent found handling
   - No root node matched handling
   - Comprehensive error logging

7. **Logging and Debugging**
   - Integrated with `utils.logger.Logger`
   - Debug flag support throughout
   - Verbose logging when `debug=True`

8. **Interactive Visualization**
   - HTML graph generation with pyvis
   - Node type color coding
   - Interactive features (zoom, pan, hover)
   - Execution path visualization

9. **Testing**
   - Unit tests for rule_splitter and llm_splitter
   - Integration tests for IntentGraph
   - Edge case testing and error scenarios

### **Success Criteria Met:**
- ✅ Handles single and multi-intent queries with consistent return format
- ✅ Supports both rule-based and LLM-based splitter functions
- ✅ Extensible with new intent trees or splitter functions
- ✅ Accurate, clear aggregation and error reporting
- ✅ Idiomatic API with `.route()` method for all trees
- ✅ Thoroughly tested and documented
- ✅ Robust error handling with no unhandled exceptions
- ✅ Graceful fallback from LLM to rule-based splitting
- ✅ Comprehensive documentation with examples as focal point
- ✅ Interactive visualization for debugging and analysis

---

## **Testing & Quality Assurance**

### **Current Test Coverage:**
- ✅ **Core Components**: Basic unit tests for tree, context, and graph components
- ✅ **Splitters**: Comprehensive tests for rule_splitter and llm_splitter
- ✅ **Context System**: Full test coverage for IntentContext and dependencies
- [ ] **Integration Tests**: End-to-end workflow testing
- [ ] **Performance Tests**: Load testing and benchmarking
- [ ] **Error Scenarios**: Comprehensive error handling tests
- [ ] **Classifier Tests**: Individual classifier unit tests
- [ ] **Service Integration Tests**: AI service connectivity tests

### **Test Statistics:**
- **Total Python Files**: 33
- **Test Files**: 4
- **Test Coverage**: ~12% (needs improvement)

---

## **Advanced Features (Stretch Goals)**

* [x] **Splitter interface**: Pluggable (function-based, not class-based or registry-based).
* [ ] **Context-aware splitting** (user/session history).
* [ ] **Async execution** (for parallel intent tree invocation).

---

## **Performance & Scalability**

* [ ] **Async/Await Support**: Implement async handlers and classifiers
* [ ] **Parallel Execution**: Support for concurrent intent processing
* [ ] **Caching**: Result caching for repeated queries
* [ ] **Rate Limiting**: Built-in rate limiting for AI service calls
* [ ] **Connection Pooling**: Efficient HTTP connection management

---

## **Documentation & Examples**

* [x] **Core API Documentation**: Comprehensive docstrings and type hints
* [x] **Example Demos**: Multiple working examples with real LLM integration
* [x] **README**: Clear project overview and setup instructions
* [ ] **API Reference**: Auto-generated API documentation
* [ ] **Cookbook**: Common patterns and recipes
* [ ] **Tutorial**: Step-by-step guide for new users
* [ ] **Architecture Guide**: Detailed system design documentation

---

## **How to Contribute**

* Code: type hints, docstrings, unit tests.
* Docs: must update with PRs, pass tests.
* All classifiers should maintain existing fallback to keyword matching
* Consider memory and performance implications for local models
* Ensure classifiers work well with existing tree-based architecture
* Maintain backward compatibility with existing classifier interface
* Focus on improving test coverage and documentation
* Implement missing classifier types (regex, fuzzy, ensemble, etc.)
* Add async support for better performance
* Enhance context debugging and tracing capabilities 