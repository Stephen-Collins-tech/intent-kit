#!/usr/bin/env python3
"""
Security audit script for Intent Kit.

This script runs pip-audit to check for known vulnerabilities in dependencies.
"""

import subprocess
import sys
from pathlib import Path


def run_pip_audit():
    """Run pip-audit and return the result."""
    try:
        # Try to find pip-audit in common locations
        pip_audit_paths = [
            "pip-audit",
            str(Path.home() / ".local/bin/pip-audit"),
            "/usr/local/bin/pip-audit",
        ]

        for path in pip_audit_paths:
            try:
                result = subprocess.run(
                    [path, "--local"], capture_output=True, text=True, check=True
                )
                return True, result.stdout
            except (subprocess.CalledProcessError, FileNotFoundError):
                continue

        return False, "pip-audit not found. Install it with: pip install pip-audit"
    except Exception as e:
        return False, f"Error running pip-audit: {e}"


def main():
    """Main function to run security audit."""
    print("🔒 Running security audit...")
    print("=" * 50)

    success, output = run_pip_audit()

    if success:
        print("✅ Security audit passed!")
        print("No known vulnerabilities found.")
        print("\nAudit output:")
        print(output)
        return 0
    else:
        print("❌ Security audit failed!")
        print("Vulnerabilities found or audit failed to run.")
        print("\nError output:")
        print(output)
        return 1


if __name__ == "__main__":
    sys.exit(main())
