#!/usr/bin/env python3
"""Wrapper script for mypy type checking."""
import sys
import subprocess


def main():
    """Run mypy with the current directory."""
    try:
        cmd = [sys.executable, "-m", "mypy", "."] + sys.argv[1:]
        result = subprocess.run(cmd, capture_output=False, text=True)
        sys.exit(result.returncode)
    except KeyboardInterrupt:
        sys.exit(1)


if __name__ == "__main__":
    main()
