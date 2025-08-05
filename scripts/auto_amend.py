#!/usr/bin/env python3
"""
Auto-amend script for pre-commit hooks.

This script automatically stages any files that were reformatted by previous hooks.
It runs after formatting tools (black, ruff) to ensure reformatted files are included in the commit.
"""

import subprocess
import sys
from pathlib import Path


def get_staged_files():
    """Get list of files that are currently staged for commit."""
    try:
        result = subprocess.run(
            ["git", "diff", "--cached", "--name-only"],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip().split('\n') if result.stdout.strip() else []
    except subprocess.CalledProcessError:
        return []


def get_modified_files():
    """Get list of files that have been modified (including by formatters)."""
    try:
        result = subprocess.run(
            ["git", "diff", "--name-only"],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip().split('\n') if result.stdout.strip() else []
    except subprocess.CalledProcessError:
        return []


def stage_files(files):
    """Stage the specified files."""
    if not files:
        return True
    
    try:
        subprocess.run(
            ["git", "add"] + files,
            check=True
        )
        return True
    except subprocess.CalledProcessError:
        return False


def main():
    """Main function to auto-stage reformatted files."""
    print("🔄 Auto-staging reformatted files...")
    
    # Get files that were modified by formatters
    modified_files = get_modified_files()
    
    if not modified_files:
        print("✅ No files were reformatted")
        return 0
    
    print(f"📝 Found {len(modified_files)} reformatted files:")
    for file in modified_files:
        print(f"  - {file}")
    
    # Stage the reformatted files
    if not stage_files(modified_files):
        print("❌ Failed to stage reformatted files")
        return 1
    
    print("✅ Successfully staged reformatted files")
    print("💡 These files will be included in your commit")
    return 0


if __name__ == "__main__":
    sys.exit(main())