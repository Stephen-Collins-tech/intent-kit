#!/usr/bin/env python3
"""
Documentation Management Script for intent-kit

This script provides CRUD operations for managing documentation files.
It helps organize, create, update, and maintain documentation structure.
"""

import argparse
import json
from pathlib import Path
from typing import Dict, Optional


class DocManager:
    def __init__(self, docs_dir: str = "docs"):
        self.docs_dir = Path(docs_dir)
        self.structure_file = self.docs_dir / "structure.json"
        self.load_structure()

    def load_structure(self):
        """Load the documentation structure from JSON file."""
        if self.structure_file.exists():
            with open(self.structure_file, "r") as f:
                self.structure = json.load(f)
        else:
            self.structure = self._create_default_structure()
            self.save_structure()

    def save_structure(self):
        """Save the documentation structure to JSON file."""
        with open(self.structure_file, "w") as f:
            json.dump(self.structure, f, indent=2)

    def _create_default_structure(self) -> Dict:
        """Create default documentation structure."""
        return {
            "sections": {
                "concepts": {
                    "title": "Core Concepts",
                    "description": "Fundamental concepts and architecture",
                    "files": {
                        "intent_graphs.md": {
                            "title": "Intent Graphs",
                            "description": "Understanding the core architecture",
                            "status": "complete",
                        },
                        "nodes_and_actions.md": {
                            "title": "Nodes and Actions",
                            "description": "Building blocks of intent graphs",
                            "status": "complete",
                        },
                        "context_system.md": {
                            "title": "Context System",
                            "description": "State management and dependency tracking",
                            "status": "pending",
                        },
                        "remediation.md": {
                            "title": "Remediation",
                            "description": "Error handling and recovery strategies",
                            "status": "pending",
                        },
                    },
                },
                "api": {
                    "title": "API Reference",
                    "description": "Complete API documentation",
                    "files": {
                        "intent_graph_builder.md": {
                            "title": "IntentGraphBuilder",
                            "description": "Fluent interface for building graphs",
                            "status": "pending",
                        },
                        "node_types.md": {
                            "title": "Node Types",
                            "description": "Action, Classifier, and Splitter nodes",
                            "status": "pending",
                        },
                        "context_api.md": {
                            "title": "Context API",
                            "description": "Context management and debugging",
                            "status": "pending",
                        },
                        "remediation_api.md": {
                            "title": "Remediation API",
                            "description": "Error handling strategies",
                            "status": "pending",
                        },
                    },
                },
                "configuration": {
                    "title": "Configuration",
                    "description": "Configuration and setup guides",
                    "files": {
                        "json_serialization.md": {
                            "title": "JSON Serialization",
                            "description": "Define graphs in JSON",
                            "status": "complete",
                        },
                        "llm_integration.md": {
                            "title": "LLM Integration",
                            "description": "OpenAI, Anthropic, Google, Ollama",
                            "status": "pending",
                        },
                        "function_registry.md": {
                            "title": "Function Registry",
                            "description": "Managing function mappings",
                            "status": "pending",
                        },
                    },
                },
                "examples": {
                    "title": "Examples",
                    "description": "Working examples and tutorials",
                    "files": {
                        "basic_examples.md": {
                            "title": "Basic Examples",
                            "description": "Simple intent graphs",
                            "status": "pending",
                        },
                        "advanced_examples.md": {
                            "title": "Advanced Examples",
                            "description": "Complex workflows",
                            "status": "pending",
                        },
                        "multi_intent_routing.md": {
                            "title": "Multi-Intent Routing",
                            "description": "Handling multiple intents",
                            "status": "pending",
                        },
                        "context_workflows.md": {
                            "title": "Context Workflows",
                            "description": "Stateful conversations",
                            "status": "pending",
                        },
                    },
                },
                "development": {
                    "title": "Development",
                    "description": "Development and testing guides",
                    "files": {
                        "testing.md": {
                            "title": "Testing",
                            "description": "Unit tests and integration testing",
                            "status": "pending",
                        },
                        "evaluation.md": {
                            "title": "Evaluation",
                            "description": "Performance evaluation and benchmarking",
                            "status": "pending",
                        },
                        "debugging.md": {
                            "title": "Debugging",
                            "description": "Debugging tools and techniques",
                            "status": "pending",
                        },
                    },
                },
            }
        }

    def list_files(self, section: Optional[str] = None):
        """List all documentation files or files in a specific section."""
        if section:
            if section not in self.structure["sections"]:
                print(f"Section '{section}' not found.")
                return

            section_data = self.structure["sections"][section]
            print(f"\n{section_data['title']} - {section_data['description']}")
            print("=" * 60)

            for filename, file_data in section_data["files"].items():
                status_icon = "✅" if file_data["status"] == "complete" else "⏳"
                print(f"{status_icon} {file_data['title']} ({filename})")
                print(f"    {file_data['description']}")
                print()
        else:
            for section_name, section_data in self.structure["sections"].items():
                print(f"\n{section_data['title']} - {section_data['description']}")
                print("=" * 60)

                for filename, file_data in section_data["files"].items():
                    status_icon = "✅" if file_data["status"] == "complete" else "⏳"
                    print(f"{status_icon} {file_data['title']} ({filename})")
                    print(f"    {file_data['description']}")
                    print()

    def create_file(self, section: str, filename: str, title: str, description: str):
        """Create a new documentation file."""
        if section not in self.structure["sections"]:
            print(f"Section '{section}' not found.")
            return

        section_dir = self.docs_dir / section
        section_dir.mkdir(exist_ok=True)

        file_path = section_dir / filename

        if file_path.exists():
            print(f"File {file_path} already exists.")
            return

        # Create the file with a template
        template = f"""# {title}

{description}

## Overview

[Add overview content here]

## Examples

```python
# Add code examples here
```

## Reference

[Add reference content here]
"""

        with open(file_path, "w") as f:
            f.write(template)

        # Update structure
        self.structure["sections"][section]["files"][filename] = {
            "title": title,
            "description": description,
            "status": "pending",
        }
        self.save_structure()

        print(f"Created {file_path}")

    def update_file(self, section: str, filename: str, **kwargs):
        """Update file metadata in the structure."""
        if section not in self.structure["sections"]:
            print(f"Section '{section}' not found.")
            return

        if filename not in self.structure["sections"][section]["files"]:
            print(f"File '{filename}' not found in section '{section}'.")
            return

        file_data = self.structure["sections"][section]["files"][filename]

        for key, value in kwargs.items():
            if key in file_data:
                file_data[key] = value
            else:
                print(f"Unknown field '{key}'")

        self.save_structure()
        print(f"Updated {filename}")

    def delete_file(self, section: str, filename: str):
        """Delete a documentation file."""
        if section not in self.structure["sections"]:
            print(f"Section '{section}' not found.")
            return

        if filename not in self.structure["sections"][section]["files"]:
            print(f"File '{filename}' not found in section '{section}'.")
            return

        file_path = self.docs_dir / section / filename

        if file_path.exists():
            file_path.unlink()
            print(f"Deleted {file_path}")

        del self.structure["sections"][section]["files"][filename]
        self.save_structure()

    def move_file(
        self, old_section: str, old_filename: str, new_section: str, new_filename: str
    ):
        """Move a file from one section to another."""
        if old_section not in self.structure["sections"]:
            print(f"Source section '{old_section}' not found.")
            return

        if new_section not in self.structure["sections"]:
            print(f"Destination section '{new_section}' not found.")
            return

        if old_filename not in self.structure["sections"][old_section]["files"]:
            print(f"File '{old_filename}' not found in section '{old_section}'.")
            return

        old_path = self.docs_dir / old_section / old_filename
        new_path = self.docs_dir / new_section / new_filename

        if not old_path.exists():
            print(f"Source file {old_path} does not exist.")
            return

        # Create destination directory if it doesn't exist
        new_path.parent.mkdir(exist_ok=True)

        # Move the file
        old_path.rename(new_path)

        # Update structure
        file_data = self.structure["sections"][old_section]["files"][old_filename]
        del self.structure["sections"][old_section]["files"][old_filename]

        self.structure["sections"][new_section]["files"][new_filename] = file_data
        self.save_structure()

        print(f"Moved {old_path} to {new_path}")

    def generate_report(self):
        """Generate a status report of all documentation."""
        total_files = 0
        complete_files = 0

        print("Documentation Status Report")
        print("=" * 50)

        for section_name, section_data in self.structure["sections"].items():
            section_files = len(section_data["files"])
            section_complete = sum(
                1 for f in section_data["files"].values() if f["status"] == "complete"
            )

            total_files += section_files
            complete_files += section_complete

            completion = (
                (section_complete / section_files * 100) if section_files > 0 else 0
            )
            print(
                f"\n{section_data['title']}: {section_complete}/{section_files} ({completion:.1f}%)"
            )

            for filename, file_data in section_data["files"].items():
                status_icon = "✅" if file_data["status"] == "complete" else "⏳"
                print(f"  {status_icon} {file_data['title']}")

        overall_completion = (
            (complete_files / total_files * 100) if total_files > 0 else 0
        )
        print(f"\nOverall: {complete_files}/{total_files} ({overall_completion:.1f}%)")

    def validate_links(self):
        """Validate that all files referenced in the structure exist."""
        print("Validating documentation structure...")
        missing_files = []

        for section_name, section_data in self.structure["sections"].items():
            section_dir = self.docs_dir / section_name

            for filename in section_data["files"].keys():
                file_path = section_dir / filename
                if not file_path.exists():
                    missing_files.append(f"{section_name}/{filename}")

        if missing_files:
            print("Missing files:")
            for file_path in missing_files:
                print(f"  - {file_path}")
        else:
            print("All files exist! ✅")


def main():
    parser = argparse.ArgumentParser(description="Manage intent-kit documentation")
    parser.add_argument(
        "command",
        choices=["list", "create", "update", "delete", "move", "report", "validate"],
    )
    parser.add_argument("--section", help="Section name")
    parser.add_argument("--filename", help="File name")
    parser.add_argument("--title", help="File title")
    parser.add_argument("--description", help="File description")
    parser.add_argument("--new-section", help="New section name (for move)")
    parser.add_argument("--new-filename", help="New filename (for move)")
    parser.add_argument("--status", choices=["pending", "complete"], help="File status")

    args = parser.parse_args()

    doc_manager = DocManager()

    if args.command == "list":
        doc_manager.list_files(args.section)

    elif args.command == "create":
        if not all([args.section, args.filename, args.title, args.description]):
            print(
                "create command requires --section, --filename, --title, and --description"
            )
            return
        doc_manager.create_file(
            args.section, args.filename, args.title, args.description
        )

    elif args.command == "update":
        if not all([args.section, args.filename]):
            print("update command requires --section and --filename")
            return

        update_data = {}
        if args.title:
            update_data["title"] = args.title
        if args.description:
            update_data["description"] = args.description
        if args.status:
            update_data["status"] = args.status

        if not update_data:
            print("update command requires at least one field to update")
            return

        doc_manager.update_file(args.section, args.filename, **update_data)

    elif args.command == "delete":
        if not all([args.section, args.filename]):
            print("delete command requires --section and --filename")
            return
        doc_manager.delete_file(args.section, args.filename)

    elif args.command == "move":
        if not all([args.section, args.filename, args.new_section, args.new_filename]):
            print(
                "move command requires --section, --filename, --new-section, and --new-filename"
            )
            return
        doc_manager.move_file(
            args.section, args.filename, args.new_section, args.new_filename
        )

    elif args.command == "report":
        doc_manager.generate_report()

    elif args.command == "validate":
        doc_manager.validate_links()


if __name__ == "__main__":
    main()
