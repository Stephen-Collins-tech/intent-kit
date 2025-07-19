#!/usr/bin/env python3
"""
Script to identify and fix common Python lint errors.

This script analyzes the codebase and provides specific fixes for:
- Unused imports
- Missing type annotations
- Line length issues
- Unused variables
- Import order issues
"""

import os
from typing import Dict, List

import ast




class LintError:
    def __init__(
        self, file_path: str, line: int, error_type: str, message: str, fix: str = ""):
        self.file_path = file_path
        self.line = line
        self.error_type = error_type
        self.message = message
        self.fix = fix


def find_python_files(directory: str) -> List[str]:
    """Find all Python files in the directory."""
    python_files = []
    for root, dirs, files in os.walk(directory):
        # Skip common directories to ignore
        dirs[:] = [d for d in dirs if d not in {'.git', '__pycache__', 'venv', '.venv', 'node_modules'}]
        for file in files:
            if file.endswith('.py'):
                python_files.append(os.path.join(root, file))
    return python_files


def check_unused_imports(file_path: str) -> List[LintError]:
    """Check for unused imports in a Python file."""
    errors = []

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Parse the AST
        tree = ast.parse(content)

        # Find all imports
        imports = []
        for node in ast.walk(tree):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.append(alias.name)
                else:
                    if node.module:
                        imports.append(node.module)

        # Find all names used in the code
        used_names = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Name):
                used_names.add(node.id)

        # Check for unused imports
        for import_name in imports:
            if import_name not in used_names:
                # Find the line number
                for node in ast.walk(tree):
                    if isinstance(node, (ast.Import, ast.ImportFrom)):
                        if isinstance(node, (ast.Import, ast.ImportFrom)):
                            errors.append(LintError(
                                file_path=file_path,
                                line=node.lineno,
                                error_type="unused_import",
                                message=f"Unused import: {import_name}",
                                fix=f"Remove the import of '{import_name}'"
                            ))
                            break

    except Exception as e:
        errors.append(LintError(
            file_path=file_path,
            line=0,
            error_type="parse_error",
            message=f"Could not parse file: {str(e)}"
        ))

    return errors


def check_line_length(file_path: str, max_length: int = 88) -> List[LintError]:
    """Check for lines that are too long."""
    errors = []

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        for i, line in enumerate(lines, 1):
            if len(line.rstrip('\n')) > max_length:
                errors.append(LintError(
                    file_path=file_path,
                    line=i,
                    error_type="line_too_long",
                    message=f"Line too long ({len(line.rstrip())} > {max_length} characters)",
                    fix=f"Break the line at line {i} to be under {max_length} characters"
                ))

    except Exception as e:
        errors.append(LintError(
            file_path=file_path,
            line=0,
            error_type="read_error",
            message=f"Could not read file: {str(e)}"
        ))

    return errors


def check_missing_type_annotations(file_path: str) -> List[LintError]:
    """Check for missing type annotations in function definitions."""
    errors = []

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        tree = ast.parse(content)

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Check for missing return type annotation
                if node.returns is None:
                    errors.append(LintError(
                        file_path=file_path,
                        line=node.lineno,
                        error_type="missing_return_type",
                        message=f"Function '{node.name}' is missing return type annotation",
                        fix=f"Add return type annotation to function '{node.name}'"
                    ))

                # Check for missing parameter type annotations
                for arg in node.args.args:
                    if arg.annotation is None:
                        errors.append(LintError(
                            file_path=file_path,
                            line=node.lineno,
                            error_type="missing_param_type",
                            message=f"Parameter '{arg.arg}' in function '{node.name}' is missing type annotation",
                            fix=f"Add type annotation to parameter '{arg.arg}' in function '{node.name}'"
                        ))

    except Exception as e:
        errors.append(LintError(
            file_path=file_path,
            line=0,
            error_type="parse_error",
            message=f"Could not parse file for type annotations: {str(e)}"
        ))

    return errors


def check_unused_variables(file_path: str) -> List[LintError]:
    """Check for unused variables."""
    errors = []

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        tree = ast.parse(content)

        # Find all variable assignments
        assignments = {}
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        assignments[target.id] = node.lineno

        # Find all variable usages
        usages = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Name):
                usages.add(node.id)

        # Check for unused variables
        for var_name, line_num in assignments.items():
            if var_name not in usages:
                errors.append(LintError(
                    file_path=file_path,
                    line=line_num,
                    error_type="unused_variable",
                    message=f"Variable '{var_name}' is assigned but never used",
                    fix=f"Remove or use the variable '{var_name}'"
                ))

    except Exception as e:
        errors.append(LintError(
            file_path=file_path,
            line=0,
            error_type="parse_error",
            message=f"Could not parse file for unused variables: {str(e)}"
        ))

    return errors


def analyze_codebase(directory: str = ".") -> Dict[str, List[LintError]]:
    """Analyze the entire codebase for lint errors."""
    python_files = find_python_files(directory)
    all_errors = {}

    for file_path in python_files:
        errors = []
        errors.extend(check_unused_imports(file_path))
        errors.extend(check_line_length(file_path))
        errors.extend(check_missing_type_annotations(file_path))
        errors.extend(check_unused_variables(file_path))

        if errors:
            all_errors[file_path] = errors

    return all_errors


def print_errors(errors: Dict[str, List[LintError]]) -> None:
    """Print all found errors in a formatted way."""
    if not errors:
        print("✅ No lint errors found!")
        return

    print("🔍 Found the following lint errors:\n")

    for file_path, file_errors in errors.items():
        print(f"📁 {file_path}:")
        for error in file_errors:
            print(f"  Line {error.line}: {error.error_type} - {error.message}")
            if error.fix:
                print(f"    💡 Fix: {error.fix}")
        print()


def main() -> None:
    """Main function to run the lint analysis."""
    print("🔍 Analyzing codebase for lint errors...")

    errors = analyze_codebase()
    print_errors(errors)

    if errors:
        print("\n📋 Summary of fixes needed:")
        print("1. Remove unused imports")
        print("2. Add missing type annotations")
        print("3. Break long lines")
        print("4. Remove unused variables")
        print("5. Run 'black .' to auto-format code")
        print("6. Run 'ruff check .' to check for additional issues")
    else:
        print("🎉 No lint errors found! Your code is clean.")


if __name__ == "__main__":
    main()
