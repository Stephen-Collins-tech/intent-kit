#!/usr/bin/env python3
"""Stepwise lint/format wrapper."""

import sys
import subprocess


def run_step(cmd, desc):
    print(f"==> {desc}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.stdout:
        print(result.stdout, end="")
    if result.stderr:
        print(result.stderr, end="", file=sys.stderr)
    return result.returncode


def main():
    # Parse command line arguments
    fix_mode = "--fix" in sys.argv
    # Remove --fix from argv to avoid passing it to subprocesses
    args = [arg for arg in sys.argv[1:] if arg != "--fix"]

    if fix_mode:
        steps = [
            {
                "cmd": [sys.executable, "-m", "ruff", "check", "--fix", "."] + args,
                "desc": "ruff check --fix",
            },
            {
                "cmd": [sys.executable, "-m", "black", "."] + args,
                "desc": "black format",
            },
        ]
    else:
        steps = [
            {
                "cmd": [sys.executable, "-m", "ruff", "check", "."] + args,
                "desc": "ruff check",
            },
            {
                "cmd": [sys.executable, "-m", "black", "--check", "."] + args,
                "desc": "black check",
            },
        ]

    failed = False
    for step in steps:
        code = run_step(step["cmd"], step["desc"])
        if code != 0:
            failed = True

    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
