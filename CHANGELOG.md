# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0-alpha] - YYYY-MM-DD
### Added
- **RegexClassifier** – pattern-based matching (#50)
- **FuzzyClassifier** – typo-tolerant classifier using `difflib` (#52)
- **End-to-end integration test** exercising `IntentGraphBuilder` with the new classifiers (#55)
- MkDocs documentation site with Material theme, quick-start guide and auto-generated API reference (#60)
- GitHub Actions CI (lint, type-check, tests, build) (#61)
- CI publishing pipeline to TestPyPI / PyPI on version tags (#62)

### Changed
- Package exports now include `regex_classifier` & `fuzzy_classifier`.

### Fixed
- Type-checking noise in classifier test suites.

### Deprecated
- Nothing.

### Removed
- Nothing.

### Security
- None.