# Changelog

All notable changes to this project will be documented in this file.

## [v0.6.1] - 2025-08-14

### Changed
- **Documentation Updates** - Updated README.md to reflect DAG-based architecture and new API patterns
- **Removed Outdated Files** - Cleaned up completed task files (CONTEXT_REFACTOR_TASKS.md, TASKS.md)

## [v0.6.0] - 2025-08-14

### Added
- **DAG Architecture** - Complete refactor from tree-based to directed acyclic graph (DAG) patterns for enhanced flexibility and node reuse
- **Node Reuse Capabilities** - Nodes can now be shared across multiple execution paths, enabling more efficient and modular intent processing
- **Enhanced Context System** - Simplified context management with improved debugging and execution tracing
- **Structured Logging** - Comprehensive logging system with structured output for better observability
- **Flattened Examples Directory** - Reorganized examples for better discoverability and maintenance

### Changed
- **Core Architecture Pattern** - Migrated from hierarchical tree structures to flexible DAG patterns, allowing nodes to have multiple parents and children
- **Node Class Construction** - Simplified node creation and configuration with cleaner, more maintainable patterns
- **Context Implementation** - Streamlined context handling with reduced complexity and improved performance
- **Evaluation Framework** - Updated evaluation system to work with new DAG architecture
- **Documentation Updates** - Comprehensive documentation refresh to reflect DAG-based patterns and capabilities

### Removed
- **Excessive Logging** - Removed verbose logging in favor of structured, targeted logging
- **Tree-Specific Constraints** - Eliminated hierarchical limitations that prevented node reuse and complex routing patterns

### Breaking Changes
- **Architecture Pattern** - Complete shift from tree-based to DAG-based execution patterns
- **Node Relationships** - Nodes can now have multiple parents and children, breaking previous tree-only constraints
- **Context API** - Simplified context interface with updated methods and properties
- **Graph Construction** - Updated graph building patterns to support DAG structures

## [v0.5.0] - 2025-08-03

### Added
- Single Intent Architecture - Complete redesign for focused, deterministic intent processing
- Enhanced Context Management - Context tracing, debug context, and state capture capabilities
- Improved Error Handling - Pluggable remediation strategies with RetryOnFailStrategy, FallbackToAnotherNodeStrategy, and SelfReflectStrategy
- Performance Monitoring - PerfUtil class for comprehensive performance tracking and cost calculation
- Argument Extraction System - Structured parameter extraction with RuleBasedArgumentExtractor and LLMArgumentExtractor
- Enhanced AI Services - Reorganized AI client wrappers with improved error handling and cost tracking
- Builder Pattern Improvements - Fluent builders for ActionNode and ClassifierNode with enhanced configuration options
- Token Usage Tracking - Real-time token consumption and cost calculation across all LLM operations

### Changed
- Architecture Overhaul - Migrated temporarily from multi-intent to single intent architecture for improved reliability
- Node System Restructure - Renamed `intent_kit/node/` to `intent_kit/nodes/` for better organization
- Classifier Simplification - Removed KEYWORD and CHUNK classifier types, streamlined to RULE and LLM only
- IntentGraph Redesign - Root nodes must now be classifiers, action nodes are leaf nodes only
- Documentation Updates - Complete overhaul of architecture docs and examples for single intent patterns
- Service Layer Reorganization - Moved AI services to `intent_kit/services/ai/` with enhanced factory pattern
- Test Suite Updates - Comprehensive test updates for new architecture and enhanced coverage

### Removed
- Splitter Node System - Complete removal of SplitterNode, SplitterBuilder, and all splitter implementations
- Multi-Intent Handling - Eliminated ability to process multiple intents in single user input
- Splitter Types - Removed SPLITTER from NodeType enum and all splitter-related enums
- Complex Examples - Removed multi_intent_demo.py, context_demo.py, remediation_demo.py and related JSON configs
- Builder Directory - Moved IntentGraphBuilder to graph module, removed separate builders package
- Old Node Structure - Removed entire `intent_kit/node/splitters/` directory and related files
- Splitter Validation - Removed all splitter routing validation and related validation logic

### Breaking Changes
- Node Type Changes - NodeType enum now only supports ACTION and CLASSIFIER (SPLITTER removed)
- Architecture Requirements - All root nodes must be classifiers, no more splitter nodes
- Import Path Updates - `intent_kit.node` renamed to `intent_kit.nodes` throughout codebase
- Builder API Changes - IntentGraphBuilder moved from builders package to graph module
- Multi-Intent Support - No longer supports splitting user input into multiple intents

## [v0.4.0] - 2025-07-25

### Added
- Enhanced LLM config handling with environment variable support and improved code organization
- PerfUtil utility class for performance monitoring
- NodeType enum for better type safety
- Comprehensive test suite for ActionNode with various scenarios
- Pre-commit configuration with version sync and changelog check scripts
- CodeCov components for test coverage reporting

### Changed
- Updated examples to use new model configurations
- Enhanced development coverage script with additional tests
- Improved code organization by refactoring out of evals node_library
- Updated documentation and configuration files

### Removed
- Unused dependencies from project configuration

## [v0.3.0] - 2025-07-18

### Added
- Comprehensive test suites for core types, nodes, and services
- Custom LLM client demo example showcasing extensibility
- Enhanced test coverage across all major modules
- Script to fix trailing whitespace issues

### Changed
- Simplified README description of Intent Kit's control feature for clarity
- Updated documentation links and improved messaging
- Enhanced test organization and formatting

### Removed
- Unused imports across test files for cleaner codebase

## [v0.2.0] - 2025-07-14

### Added
- JSON-based intent graph configuration for declarative graph definition
- YAML service for configuration management
- Comprehensive test suites for IntentKit graph, context, and node modules
- Enhanced pre-commit configuration with lint/typecheck scripts
- Optional dependencies support for flexible installation

### Changed
- Refactored "handler" terminology to "action" throughout codebase for consistency
- Updated documentation structure and organization
- Enhanced CI/CD pipeline with improved workflows
- Updated dependencies and development tooling

### Removed
- Binder environment support

## [v0.1.0] - 2025-07-07

### Added
- Experimental CI/CD pipeline with linting, type checking, test coverage reporting via Codecov, and trusted publishing.
- MkDocs documentation site using the Material theme with live search and API reference.
- Binder environment for interactive notebooks and examples.
- Pre-commit configuration powered by Ruff, Black, and mypy.
- Documentation badges for CI, coverage, docs, and PyPI.

### Changed
- Updated development dependencies and tooling for modern Python 3.11 ecosystem.

### Removed
- N/A
