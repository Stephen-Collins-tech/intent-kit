# Core Engine & Feature Roadmap

## Core Engine (OSS)

### 1. Intent Tree & Action Engine

* [x] API for declaring intent trees, named nodes, parameters, action registration.
* [x] Parameter typing/schema for each intent.
* [x] Tree-based intent architecture with classifier and intent nodes.
* [x] Flexible node system mixing classifier nodes and intent nodes.

### 2. IntentGraph Multi-Intent Routing

* [x] **IntentGraph Data Structure** - Root-level dispatcher for user input
* [x] **Function-Based Intent Splitting** - Rule-based and LLM-based splitters
* [x] **Multi-Tree Dispatch** - Route to multiple intent trees
* [x] **Orchestration and Aggregation** - Consistent result format
* [x] **Fallbacks and Error Handling** - Comprehensive error management
* [x] **Logging and Debugging** - Integrated with logger system
* [x] **Interactive Visualization** - HTML graph generation of execution paths

### 3. Classifier Plug-in Support

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

### 4. Parameter Extraction

* [x] Pluggable param extraction: regex, LLM, hybrid.
* [x] Human-in-the-loop fallback (CLI/MVP).
* [x] Automatic parameter extraction with type validation.
* [x] LLM-powered argument extraction with multiple backends.

### 5. Action Execution

* [x] Typed action execution, structured error surfaces.
* [x] Comprehensive error handling with detailed logging.
* [x] Context-aware execution with dependency tracking.

### 8. Remediation System

* [x] **Remediation Strategies** - Pluggable error handling strategies
* [x] **Retry Strategies** - Exponential backoff and retry logic
* [x] **Fallback Strategies** - Fallback to alternative actions
* [x] **Self-Reflection Strategies** - LLM self-reflection for error recovery
* [x] **Consensus Voting Strategies** - Multiple LLM consensus for reliability
* [x] **Custom Strategies** - User-defined remediation strategies

---

## Future Enhancements (Engine)

- [ ] **Multi-Tenant Support** - Multi-tenant architecture
- [ ] **Audit Logging** - Comprehensive audit logging
- [ ] **Security Features** - Security and compliance features
- [ ] **Scalability** - Horizontal scaling support
- [ ] **Monitoring** - Production monitoring and alerting
- [ ] **Framework Integrations** - Integration with popular frameworks
- [ ] **Cloud Provider Support** - Cloud provider integrations
- [ ] **CI/CD Integration** - Continuous integration support
- [ ] **Deployment Tools** - Deployment and orchestration tools
- [ ] **Plugin System** - Extensible plugin architecture
