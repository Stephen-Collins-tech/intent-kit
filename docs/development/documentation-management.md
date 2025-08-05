# Documentation Management Guide

This guide explains how to manage and organize the intent-kit documentation using the built-in CRUD system.

## Overview

The documentation is organized into logical sections:

- **Core Concepts** - Fundamental concepts and architecture
- **API Reference** - Complete API documentation
- **Configuration** - Configuration and setup guides
- **Examples** - Working examples and tutorials
- **Development** - Development and testing guides

## Management Script

Use the `scripts/manage_docs.py` script to manage documentation:

```bash
# List all documentation files
python scripts/manage_docs.py list

# List files in a specific section
python scripts/manage_docs.py list --section concepts

# Create a new file
python scripts/manage_docs.py create \
  --section api \
  --filename new_api.md \
  --title "New API" \
  --description "Documentation for new API"

# Update file metadata
python scripts/manage_docs.py update \
  --section api \
  --filename new_api.md \
  --status complete

# Move a file
python scripts/manage_docs.py move \
  --section examples \
  --filename old_example.md \
  --new-section concepts \
  --new-filename new_concept.md

# Delete a file
python scripts/manage_docs.py delete \
  --section examples \
  --filename old_example.md

# Generate status report
python scripts/manage_docs.py report

# Validate file structure
python scripts/manage_docs.py validate
```

## File Status

Each documentation file has a status:

- **pending** - File exists but needs content
- **complete** - File is fully documented

## File Structure

Each documentation file should follow this structure:

```markdown
# Title

Brief description of the content.

## Overview

Detailed explanation of the concept or feature.

## Examples

```python
# Code examples here
```

## Reference

API reference, parameters, return values, etc.

## Best Practices

Guidelines and recommendations.
```

## Terminology Updates

The documentation has been updated to use consistent terminology:

- **Actions** instead of "handlers" - Functions that execute and produce outputs
- **Classifiers** - Nodes that route input to appropriate actions
- **Classifiers** - Nodes that route input to appropriate actions

## Navigation Structure

The documentation uses a hierarchical navigation structure defined in `mkdocs.yml`:

```yaml
nav:
  - Home: index.md
  - Quickstart: quickstart.md
  - Core Concepts:
      - Intent Graphs: concepts/intent-graphs.md
      - Nodes and Actions: concepts/nodes_and_handlers.md
      # ... more sections
```

## Best Practices

### Content Guidelines

1. **Clear Titles** - Use descriptive, action-oriented titles
2. **Consistent Formatting** - Follow markdown conventions
3. **Code Examples** - Include working, copy-pasteable examples
4. **Cross-References** - Link to related documentation
5. **Status Tracking** - Keep file status up to date

### Organization Guidelines

1. **Logical Grouping** - Group related concepts together
2. **Progressive Complexity** - Start simple, build to advanced
3. **Consistent Naming** - Use consistent file and section names
4. **Regular Updates** - Keep documentation current with code changes

### Maintenance Guidelines

1. **Regular Reviews** - Review and update documentation regularly
2. **Validation** - Run validation to check for missing files
3. **Status Reports** - Generate reports to track completion
4. **Version Control** - Commit documentation changes with code changes

## Common Tasks

### Adding New Documentation

1. Create the file using the management script
2. Write comprehensive content
3. Update the status to "complete"
4. Update navigation if needed

### Updating Existing Documentation

1. Edit the file content
2. Update metadata if needed
3. Validate links and references
4. Test examples and code snippets

### Reorganizing Documentation

1. Use the move command to relocate files
2. Update navigation structure
3. Update cross-references
4. Validate the new structure

### Archiving Documentation

1. Move to appropriate archive section
2. Update navigation to remove from main sections
3. Add deprecation notices if needed
4. Update cross-references

## Automation

The documentation system can be automated:

```bash
# Generate status report for CI/CD
python scripts/manage_docs.py report > docs_status.txt

# Validate before deployment
python scripts/manage_docs.py validate

# Create missing files from structure
python scripts/manage_docs.py create --section api --filename missing.md --title "Missing" --description "Auto-created"
```

## Integration with Development

- Documentation changes should be part of feature development
- Update documentation when APIs change
- Include documentation in code reviews
- Test documentation examples in CI/CD
