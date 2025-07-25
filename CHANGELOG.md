# Changelog

All notable changes to this project will be documented in this file.

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
