#!/usr/bin/env python3
"""
Example runner scripts for IntentKit.
Provides uv script commands for running examples.
"""

import argparse
import os
import subprocess
import sys
from pathlib import Path
from typing import List

# Load environment variables from .env file
try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    # dotenv not available, continue without it
    pass


# Colors for output
class Colors:
    RED = "\033[0;31m"
    GREEN = "\033[0;32m"
    YELLOW = "\033[1;33m"
    BLUE = "\033[0;34m"
    PURPLE = "\033[0;35m"
    CYAN = "\033[0;36m"
    NC = "\033[0m"  # No Color


def print_status(status: str, message: str) -> None:
    """Print colored status message."""
    status_map = {
        "SUCCESS": f"{Colors.GREEN}✓ SUCCESS{Colors.NC}",
        "ERROR": f"{Colors.RED}✗ ERROR{Colors.NC}",
        "WARNING": f"{Colors.YELLOW}⚠ WARNING{Colors.NC}",
        "INFO": f"{Colors.BLUE}ℹ INFO{Colors.NC}",
        "RUNNING": f"{Colors.CYAN}▶ RUNNING{Colors.NC}",
        "HEADER": f"{Colors.PURPLE}📋 {message}{Colors.NC}",
    }

    if status == "HEADER":
        print(status_map[status])
    else:
        print(f"{status_map[status]}: {message}")


def check_environment() -> bool:
    """Check environment setup."""
    print_status("HEADER", "Checking Environment Setup")

    # Check if we're in the right directory
    if not Path("intent_kit/__init__.py").exists():
        print_status("ERROR", "intent_kit package not found in current directory")
        print_status(
            "INFO", "Make sure you're running this script from the project root"
        )
        return False

    # Check for required environment variables
    missing_vars = []

    if not os.getenv("OPENROUTER_API_KEY"):
        missing_vars.append("OPENROUTER_API_KEY")

    if not os.getenv("OPENAI_API_KEY"):
        missing_vars.append("OPENAI_API_KEY")

    if not os.getenv("GOOGLE_API_KEY"):
        missing_vars.append("GOOGLE_API_KEY")

    if missing_vars:
        print_status("WARNING", f"Some API keys are not set: {', '.join(missing_vars)}")
        print_status("INFO", "Some examples may fail without proper API keys")
    else:
        print_status("SUCCESS", "All required API keys are set")

    # Check for .env file
    if Path(".env").exists():
        print_status("INFO", "Found .env file")
    else:
        print_status("WARNING", "No .env file found")

    print()
    return True


def find_examples() -> List[Path]:
    """Find all Python example files in the examples directory."""
    examples_dir = Path("examples")
    if not examples_dir.exists():
        print("Error: examples directory not found. Run from project root.")
        sys.exit(1)

    example_files = []
    for py_file in examples_dir.rglob("*.py"):
        # Skip __pycache__ and __init__.py files
        if "__pycache__" not in str(py_file) and py_file.name != "__init__.py":
            example_files.append(py_file)

    return sorted(example_files)


def run_example(example_path: Path, timeout: int = 30, verbose: bool = False) -> bool:
    """Run a single example file with timeout."""
    example_name = example_path.stem

    print_status("RUNNING", f"Running {example_name}...")

    try:
        # Run the example
        result = subprocess.run(
            [sys.executable, str(example_path)],
            timeout=timeout,
            capture_output=not verbose,
            text=True,
        )

        if result.returncode == 0:
            print_status("SUCCESS", f"{example_name} completed successfully")
            if verbose and result.stdout:
                print(result.stdout)
            return True
        else:
            print_status(
                "ERROR", f"{example_name} failed with exit code {result.returncode}"
            )
            if verbose and result.stderr:
                print(result.stderr)
            return False

    except subprocess.TimeoutExpired:
        print_status("ERROR", f"{example_name} timed out after {timeout} seconds")
        return False
    except Exception as e:
        print_status("ERROR", f"{example_name} failed with error: {e}")
        return False


def list_examples() -> None:
    """List all available examples."""
    print("Available examples:")
    print()

    examples = find_examples()
    if not examples:
        print("No examples found.")
        return

    # Group by directory
    by_dir: dict[str, list[Path]] = {}
    for example in examples:
        parent = example.parent.name
        if parent not in by_dir:
            by_dir[parent] = []
        by_dir[parent].append(example)

    for dir_name, files in sorted(by_dir.items()):
        print(f"  {dir_name}/")
        for file in sorted(files):
            rel_path = file.relative_to(Path("examples"))
            print(f"    {rel_path}")
        print()


def run_all() -> int:
    """Run all examples."""
    parser = argparse.ArgumentParser(description="Run all IntentKit examples")
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Show detailed output"
    )
    parser.add_argument(
        "-t",
        "--timeout",
        type=int,
        default=30,
        help="Timeout per example in seconds (default: 30)",
    )
    parser.add_argument(
        "-c",
        "--check",
        action="store_true",
        help="Only check environment, don't run examples",
    )

    args = parser.parse_args()

    # Ensure we're in the project root
    if not Path("intent_kit/__init__.py").exists():
        print_status("ERROR", "Must be run from project root directory")
        return 1

    # Check environment
    if not check_environment():
        return 1

    # If check-only mode, exit here
    if args.check:
        print_status("SUCCESS", "Environment check completed")
        return 0

    examples = find_examples()
    if not examples:
        print_status("ERROR", "No example files found")
        return 1

    print_status("HEADER", "Running All IntentKit Examples")
    print()
    print_status("INFO", f"Found {len(examples)} example(s) to run")
    print()

    total_examples = 0
    successful_examples = 0
    failed_examples = 0

    # Skip certain examples that require special setup
    skip_examples = {"eval_api_demo.py", "json_llm_demo.py"}

    for example in examples:
        example_name = example.stem
        total_examples += 1

        if example.name in skip_examples:
            print_status("INFO", f"Skipping {example_name} (requires special setup)")
            continue

        if run_example(example, args.timeout, args.verbose):
            successful_examples += 1
        else:
            failed_examples += 1

        print()

    # Print summary
    print_status("HEADER", "Summary")
    print(f"Total examples: {total_examples}")
    print_status("SUCCESS", f"Successful: {successful_examples}")

    if failed_examples > 0:
        print_status("ERROR", f"Failed: {failed_examples}")
    else:
        print_status("SUCCESS", f"Failed: {failed_examples}")

    # Calculate success rate
    if total_examples > 0:
        success_rate = (successful_examples * 100) // total_examples
        print_status("INFO", f"Success rate: {success_rate}%")

    print()

    return 1 if failed_examples > 0 else 0


def run_single() -> int:
    """Run a single example."""
    parser = argparse.ArgumentParser(description="Run a single IntentKit example")
    parser.add_argument(
        "example", help="Example name (e.g., 'simple_demo' or 'basic/simple_demo')"
    )
    parser.add_argument(
        "-t", "--timeout", type=int, default=30, help="Timeout in seconds (default: 30)"
    )
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Show detailed output"
    )

    args = parser.parse_args()

    # Ensure we're in the project root
    if not Path("intent_kit/__init__.py").exists():
        print_status("ERROR", "Must be run from project root directory")
        return 1

    examples = find_examples()

    # Find matching example
    example_path = None
    for example in examples:
        rel_path = example.relative_to(Path("examples"))
        # Match by full path or just filename (without .py)
        if (
            str(rel_path) == f"{args.example}.py"
            or str(rel_path.with_suffix("")) == args.example
            or example.stem == args.example
        ):
            example_path = example
            break

    if not example_path:
        print_status("ERROR", f"Example file not found: {args.example}.py")
        print_status("INFO", "Available examples:")
        for example in examples:
            rel_path = example.relative_to(Path("examples"))
            print(f"  {rel_path}")
        return 1

    print_status("HEADER", f"Running Single Example: {args.example}")
    print()

    if not check_environment():
        return 1

    success = run_example(example_path, args.timeout, args.verbose)
    return 0 if success else 1


if __name__ == "__main__":
    # This allows the script to be run directly for testing
    if len(sys.argv) > 1 and sys.argv[1] == "list":
        list_examples()
    elif len(sys.argv) > 1 and sys.argv[1] == "single":
        sys.argv = sys.argv[1:]  # Remove "single" from args
        sys.exit(run_single())
    else:
        sys.exit(run_all())
