# Classifiers TASKS.md

## Overview

This document outlines the tasks needed to expand the classifier ecosystem in Intentify, supporting a comprehensive range of classification approaches from simple rule-based to advanced ML/LLM-based methods.

---

## Current Classifiers Status

### ✅ Implemented
- **Keyword Classifier** (`keyword_classifier`) - Simple substring matching
- **OpenAI Classifier** (`openai_classifier`) - GPT-3.5-turbo based
- **Google Classifier** (`google_classifier`) - Gemini Pro based  
- **Anthropic Classifier** (`anthropic_classifier`) - Claude-3-Sonnet based

### 🔧 Needs Fixing
- **Anthropic Classifier** - Has linter error with `anthropic.Anthropic()` import

---

## New Classifiers to Implement

### 1. Regex Classifier
- [ ] **Task:** Implement `regex_classifier` function
  - *Context:* Pattern-based matching using regular expressions
  - *Use case:* Structured inputs, commands, IDs, validation patterns
  - *Implementation:* Use Python's `re` module for pattern matching
  - *Acceptance:* Can match patterns like `r"account\d+"` to route to account-related intents

### 2. Fuzzy Match Classifier
- [ ] **Task:** Implement `fuzzy_classifier` function
  - *Context:* Handle typos and slight variations in user input
  - *Use case:* User-friendly matching with tolerance for errors
  - *Implementation:* Use `fuzzywuzzy` or `rapidfuzz` library
  - *Acceptance:* "weathr" matches "weather" intent with high confidence

### 3. Confidence-Based Classifier Wrapper
- [ ] **Task:** Implement `confidence_classifier` wrapper
  - *Context:* Add confidence scoring to existing classifiers
  - *Use case:* Implement fallback logic and uncertainty handling
  - *Implementation:* Wrapper that returns both node and confidence score
  - *Acceptance:* Can set confidence thresholds and trigger fallbacks

### 4. Ensemble Classifier
- [ ] **Task:** Implement `ensemble_classifier` function
  - *Context:* Combine multiple classifiers for improved reliability
  - *Use case:* Voting or weighted scoring across multiple approaches
  - *Implementation:* Support voting, weighted averaging, or stacking
  - *Acceptance:* Can combine keyword + fuzzy + LLM classifiers

### 5. Local LLM Classifier
- [ ] **Task:** Implement `local_llm_classifier` function
  - *Context:* Use local models like Llama, Mistral, or other open-source models
  - *Use case:* No API dependencies, offline operation, privacy
  - *Implementation:* Support Ollama, llama.cpp, or other local inference
  - *Acceptance:* Can run classification without internet connection

### 6. Semantic Search Classifier
- [ ] **Task:** Implement `semantic_classifier` function
  - *Context:* Use embeddings and vector similarity for classification
  - *Use case:* Find semantically similar intents beyond exact matches
  - *Implementation:* Use sentence-transformers or similar embedding models
  - *Acceptance:* "What's the temperature?" matches "weather" intent

### 7. Intent-Specific Domain Classifiers
- [ ] **Task:** Implement domain-specific classifier templates
  - *Context:* Specialized classifiers for specific domains
  - *Use case:* Financial, medical, technical, customer service domains
  - *Implementation:* Template classes with domain-specific rules and knowledge
  - *Acceptance:* Financial classifier understands "transfer funds" vs "check balance"

### 8. Hybrid Classifier
- [ ] **Task:** Implement `hybrid_classifier` function
  - *Context:* Combine rule-based and ML approaches intelligently
  - *Use case:* Use rules for common cases, ML for edge cases
  - *Implementation:* Rule-first approach with ML fallback
  - *Acceptance:* Fast for common patterns, sophisticated for complex cases

---

## Infrastructure Improvements

### 9. Classifier Interface Standardization
- [ ] **Task:** Define abstract base class for classifiers
  - *Context:* Ensure all classifiers follow consistent interface
  - *Implementation:* Create `BaseClassifier` ABC with required methods
  - *Acceptance:* All classifiers inherit from base class

### 10. Classifier Configuration System
- [ ] **Task:** Implement configuration management for classifiers
  - *Context:* Allow customization of classifier parameters
  - *Implementation:* Config classes for each classifier type
  - *Acceptance:* Can configure confidence thresholds, model parameters, etc.

### 11. Classifier Performance Metrics
- [ ] **Task:** Add performance tracking and metrics
  - *Context:* Monitor classifier accuracy, speed, and reliability
  - *Implementation:* Logging and metrics collection
  - *Acceptance:* Can track success rates, response times, confidence distributions

### 12. Classifier Testing Framework
- [ ] **Task:** Create comprehensive test suite for classifiers
  - *Context:* Ensure reliability and correctness of all classifiers
  - *Implementation:* Unit tests, integration tests, performance tests
  - *Acceptance:* All classifiers have >90% test coverage

---

## Documentation and Examples

### 13. Classifier Selection Guide
- [ ] **Task:** Create decision tree for choosing classifiers
  - *Context:* Help developers select appropriate classifier for their use case
  - *Implementation:* Interactive guide with pros/cons of each type
  - *Acceptance:* Clear guidance for different scenarios

### 14. Classifier Performance Benchmarks
- [ ] **Task:** Benchmark all classifiers on common datasets
  - *Context:* Provide performance comparisons for informed decisions
  - *Implementation:* Standardized benchmark suite
  - *Acceptance:* Published performance metrics for each classifier

### 15. Real-World Examples
- [ ] **Task:** Create example implementations for common scenarios
  - *Context:* Show practical usage of different classifiers
  - *Implementation:* Example projects and use cases
  - *Acceptance:* At least 5 different example scenarios

---

## Dependencies and Installation

### 16. Optional Dependencies Management
- [ ] **Task:** Implement optional dependency groups
  - *Context:* Allow users to install only needed classifier dependencies
  - *Implementation:* Use `extras_require` in setup.py/pyproject.toml
  - *Acceptance:* `pip install intentify[openai]` installs OpenAI classifier

### 17. Dependency Documentation
- [ ] **Task:** Document all classifier dependencies
  - *Context:* Clear installation instructions for each classifier
  - *Implementation:* Requirements files and installation guides
  - *Acceptance:* Users can easily install dependencies for chosen classifiers

---

## Prioritization

**Phase 1 (Core Improvements):**
1. Fix Anthropic classifier linter error
2. Implement Regex classifier
3. Implement Fuzzy classifier
4. Create BaseClassifier interface

**Phase 2 (Advanced Features):**
5. Implement Confidence wrapper
6. Implement Ensemble classifier
7. Add configuration system
8. Create testing framework

**Phase 3 (Specialized Classifiers):**
9. Implement Local LLM classifier
10. Implement Semantic classifier
11. Create domain-specific templates
12. Implement Hybrid classifier

**Phase 4 (Production Ready):**
13. Add performance metrics
14. Create benchmarks
15. Improve documentation
16. Optimize dependencies

---

## Success Criteria

- [ ] All classifiers follow consistent interface
- [ ] Each classifier has comprehensive tests
- [ ] Performance benchmarks available
- [ ] Clear documentation for each classifier
- [ ] Easy installation and configuration
- [ ] Graceful fallback mechanisms
- [ ] Confidence scoring where appropriate
- [ ] No external API dependencies for core classifiers

---

## Notes

- All classifiers should maintain the existing fallback to keyword matching
- Consider memory and performance implications for local models
- Ensure classifiers work well with the existing tree-based architecture
- Maintain backward compatibility with existing classifier interface 