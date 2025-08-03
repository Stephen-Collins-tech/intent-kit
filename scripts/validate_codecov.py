#!/usr/bin/env python3
"""
Validate codecov.yml against actual directory structure.

This script checks that all paths referenced in codecov.yml actually exist
in the filesystem, and reports any missing directories or files.
"""

import os
import sys
import yaml
import subprocess
import json
from pathlib import Path
from typing import List, Set


def get_actual_directory_structure() -> Set[str]:
    """Get the actual directory structure using 'tree' command."""
    try:
        # Run tree command to get directory structure
        result = subprocess.run(
            ["tree", "-I", "*.pyc|htmlcov|site|dist", "-f"],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent,
        )

        if result.returncode != 0:
            print(f"Error running tree command: {result.stderr}")
            return set()

        # Parse tree output to get file paths
        paths = set()
        for line in result.stdout.split("\n"):
            if (
                line.strip()
                and not line.startswith("└──")
                and not line.startswith("├──")
            ):
                # Extract the file path from tree output
                parts = line.split("── ")
                if len(parts) > 1:
                    path = parts[1].strip()
                    if path and not path.endswith("/"):
                        paths.add(path)

        return paths

    except FileNotFoundError:
        print("Error: 'tree' command not found. Please install tree.")
        return set()
    except Exception as e:
        print(f"Error getting directory structure: {e}")
        return set()


def get_codecov_paths() -> Set[str]:
    """Extract all paths from codecov.yml file."""
    codecov_file = Path(__file__).parent.parent / ".codecov.yml"

    if not codecov_file.exists():
        print(f"Error: {codecov_file} not found")
        return set()

    try:
        with open(codecov_file, "r") as f:
            config = yaml.safe_load(f)

        paths = set()

        # Extract paths from component_management.individual_components
        if "component_management" in config:
            components = config["component_management"].get("individual_components", [])
            for component in components:
                component_paths = component.get("paths", [])
                for path in component_paths:
                    # Convert glob patterns to actual paths
                    if "**" in path:
                        # Handle directory globs
                        base_path = path.replace("/**", "")
                        if os.path.exists(base_path):
                            for root, dirs, files in os.walk(base_path):
                                for file in files:
                                    if file.endswith(".py"):
                                        paths.add(os.path.join(root, file))
                    elif path.endswith("**"):
                        # Handle directory globs
                        base_path = path[:-2]
                        if os.path.exists(base_path):
                            for root, dirs, files in os.walk(base_path):
                                for file in files:
                                    if file.endswith(".py"):
                                        paths.add(os.path.join(root, file))
                    elif path.endswith(".py"):
                        # Handle specific Python files
                        if os.path.exists(path):
                            paths.add(path)
                    else:
                        # Handle specific directories
                        if os.path.exists(path):
                            for root, dirs, files in os.walk(path):
                                for file in files:
                                    if file.endswith(".py"):
                                        paths.add(os.path.join(root, file))

        return paths

    except yaml.YAMLError as e:
        print(f"Error parsing codecov.yml: {e}")
        return set()
    except Exception as e:
        print(f"Error reading codecov.yml: {e}")
        return set()


def validate_codecov_online() -> bool:
    """Validate codecov.yml using the online validator."""
    codecov_file = Path(__file__).parent.parent / ".codecov.yml"

    if not codecov_file.exists():
        print(f"Error: {codecov_file} not found")
        return False

    try:
        with open(codecov_file, "r") as f:
            content = f.read()
            result = subprocess.run(
                ["curl", "--data-binary", "@-", "https://codecov.io/validate"],
                input=content,
                capture_output=True,
                text=True,
            )

        if result.returncode == 0:
            # Remove "Valid!" prefix if present
            stdout = result.stdout.strip()
            if stdout.startswith("Valid!"):
                stdout = stdout[6:].strip()

            try:
                response = json.loads(stdout)
                if "component_management" in response:
                    print("✅ codecov.yml is valid according to online validator")
                    return True
                else:
                    print("❌ codecov.yml is invalid according to online validator")
                    return False
            except json.JSONDecodeError:
                print(
                    f"❌ Invalid JSON response from online validator: {result.stdout}"
                )
                return False
        else:
            print(f"❌ Error calling online validator: {result.stderr}")
            return False

    except Exception as e:
        print(f"❌ Error validating codecov.yml online: {e}")
        return False


def check_missing_paths(codecov_paths: Set[str], actual_paths: Set[str]) -> List[str]:
    """Check for paths in codecov.yml that don't exist in the filesystem."""
    missing = []

    for path in codecov_paths:
        if path not in actual_paths:
            # Check if it's a directory that should exist
            if path.endswith("/**") or path.endswith("**"):
                base_path = path.replace("/**", "").replace("**", "")
                if not os.path.exists(base_path):
                    missing.append(f"Directory does not exist: {base_path}")
            elif path.endswith(".py"):
                if not os.path.exists(path):
                    missing.append(f"File does not exist: {path}")
            else:
                if not os.path.exists(path):
                    missing.append(f"Path does not exist: {path}")

    return missing


def check_uncovered_paths(codecov_paths: Set[str], actual_paths: Set[str]) -> List[str]:
    """Check for Python files in the filesystem that aren't covered by codecov.yml."""
    uncovered = []

    for path in actual_paths:
        if path.endswith(".py") and path not in codecov_paths:
            # Skip some common directories that might not need coverage
            skip_dirs = {"__pycache__", "tests", "examples", "scripts"}
            if not any(skip_dir in path for skip_dir in skip_dirs):
                uncovered.append(path)

    return uncovered


def main():
    """Main validation function."""
    print("🔍 Validating codecov.yml against directory structure...")
    print()

    # Get actual directory structure
    print("📁 Scanning directory structure...")
    actual_paths = get_actual_directory_structure()
    print(f"Found {len(actual_paths)} files in directory structure")

    # Get codecov paths
    print("📋 Extracting paths from codecov.yml...")
    codecov_paths = get_codecov_paths()
    print(f"Found {len(codecov_paths)} paths in codecov.yml")

    # Validate online
    print("🌐 Validating codecov.yml online...")
    online_valid = validate_codecov_online()

    # Check for missing paths
    print("🔍 Checking for missing paths...")
    missing_paths = check_missing_paths(codecov_paths, actual_paths)

    # Check for uncovered paths
    print("🔍 Checking for uncovered paths...")
    uncovered_paths = check_uncovered_paths(codecov_paths, actual_paths)

    # Report results
    print()
    print("=" * 60)
    print("VALIDATION RESULTS")
    print("=" * 60)

    if missing_paths:
        print("❌ MISSING PATHS (referenced in codecov.yml but don't exist):")
        for path in missing_paths:
            print(f"  - {path}")
        print()
    else:
        print("✅ All paths in codecov.yml exist in filesystem")

    if uncovered_paths:
        print("⚠️  UNCOVERED PATHS (exist in filesystem but not in codecov.yml):")
        for path in uncovered_paths[:10]:  # Show first 10
            print(f"  - {path}")
        if len(uncovered_paths) > 10:
            print(f"  ... and {len(uncovered_paths) - 10} more")
        print()
    else:
        print("✅ All Python files are covered by codecov.yml")

    # Overall result
    if missing_paths:
        print("❌ VALIDATION FAILED: Missing paths found")
        return 1
    elif not online_valid:
        print("❌ VALIDATION FAILED: Online validation failed")
        return 1
    else:
        print("✅ VALIDATION PASSED: All checks passed")
        return 0


if __name__ == "__main__":
    sys.exit(main())
