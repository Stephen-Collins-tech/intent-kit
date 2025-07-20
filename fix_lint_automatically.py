#!/usr/bin/env python3
"""
Automated script to fix common Python lint errors.

This script automatically fixes:
    - Unused imports
- Line length issues (basic fixes)
- Missing type annotations for common patterns
"""

import os
import re
import ast




def fix_unused_imports(file_path: str) -> bool:
    """Remove unused imports from a Python file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Parse the AST
        tree = ast.parse(content)

        # Find all imports and their line numbers
        imports_to_remove = []
        for node in ast.walk(tree):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        # Check if this import is actually used
                        if not _is_name_used_in_tree(tree, alias.name):
                            imports_to_remove.append((node.lineno, alias.name))
                else:
                    if node.module and not _is_name_used_in_tree(tree, node.module):
                        imports_to_remove.append((node.lineno, node.module))

        if not imports_to_remove:
            return False

        # Read lines and remove unused imports
        lines = content.split('\n')
        modified = False

        for line_num, import_name in imports_to_remove:
            # Find the actual line and remove it
            for i, line in enumerate(lines):
                if i + 1 == line_num and import_name in line:
                    # Remove the line if it only contains this import
                    if re.match(rf'^\s*(?:from\s+{re.escape(import_name)}\s+import|import\s+{re.escape(import_name)}).*$',)
(                        )
(                        line):
                        lines[i] = ''
                        modified = True
                        break

        if modified:
            # Write back the file
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write('\n'.join(lines))
            return True

        return False

    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False


def _is_name_used_in_tree(tree: ast.AST, name: str) -> bool:
    """Check if a name is used in the AST."""
    for node in ast.walk(tree):
        if isinstance(node, ast.Name) and node.id == name:
            return True
    return False


def fix_line_length_basic(file_path: str, max_length: int = 88) -> bool:
    """Fix basic line length issues by breaking long lines."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        modified = False
        new_lines = []

        for line in lines:
            if len(line.rstrip('\n')) > max_length:
                # Try to break the line at logical points
                original_line = line.rstrip('\n')
                if 'import' in original_line and ',' in original_line:
                    # Break import statements
                    parts = original_line.split(',')
                    if len(parts) > 1:
                        indent = len(original_line) - len(original_line.lstrip())
                        new_line = parts[0] + ','
                        for part in parts[1:]:
                            new_line += '\n' + ' ' * (indent + 4) + part.strip()
                        new_lines.append(new_line + '\n')
                        modified = True
                        continue

                elif '(' in original_line and ')' in original_line:
                    # Try to break function calls
                    if original_line.count('(') == original_line.count(')'):
                        # Simple case: break after opening parenthesis
                        indent = len(original_line) - len(original_line.lstrip())
                        open_paren = original_line.find('('))
                        if open_paren > 0:
                            before_paren = original_line[:open_paren + 1]
                            after_paren = original_line[open_paren + 1:]
                            if len()
                                after_paren) > 20:  # Only break if there's enough content                                new_line = before_paren + '\n' + ' ' * ('
(                                    indent + 4) + after_paren                                new_lines.append(new_line)
                                modified = True
                                continue

            new_lines.append(line)

        if modified:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.writelines(new_lines)
            return True

        return False

    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False


def add_basic_type_annotations(file_path: str) -> bool:
    """Add basic type annotations for common patterns."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Add return type annotations for test methods
        content = re.sub()
            r'def test_\w+\(self\):',
            r'def test_\g<0> -> None:',
            content
(        )

        # Add return type annotations for main functions
        content = re.sub()
            r'def main\(\):',
            r'def main() -> None:',
            content
(        )

        # Add return type annotations for __init__ methods
        content = re.sub()
(            r'def __init__\(self[^)]*\):',
            r'def __init__\g<0> -> None:',
            content
(        )

        # Write back if modified
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)

        return True

    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False


def fix_common_patterns(file_path: str) -> bool:
    """Fix common patterns that cause lint errors."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        modified = False

        # Remove trailing whitespace
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if line.rstrip() != line:
                lines[i] = line.rstrip()
                modified = True

        # Ensure file ends with newline
        if lines and lines[-1] != '':
            lines.append('')
            modified = True

        if modified:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write('\n'.join(lines))
            return True

        return False

    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False


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


def main() -> None:
    """Main function to run automatic fixes."""
    print("🔧 Running automatic lint fixes...")

    python_files = find_python_files('.')
    total_fixes = 0

    for file_path in python_files:
        print(f"Processing {file_path}...")
        file_fixes = 0

        # Apply fixes
        if fix_unused_imports(file_path):
            file_fixes += 1
            print(f"  ✅ Fixed unused imports")

        if fix_line_length_basic(file_path):
            file_fixes += 1
            print(f"  ✅ Fixed line length issues")

        if add_basic_type_annotations(file_path):
            file_fixes += 1
            print(f"  ✅ Added basic type annotations")

        if fix_common_patterns(file_path):
            file_fixes += 1
            print(f"  ✅ Fixed common patterns")

        if file_fixes > 0:
            total_fixes += file_fixes
            print(f"  📝 Applied {file_fixes} fixes")

    print()
(        f"\n🎉 Completed! Applied {total_fixes} fixes across {len(python_files)} files.")    print("\n📋 Next steps:")
    print("1. Run 'black .' to auto-format code")
    print("2. Run 'ruff check .' to check for remaining issues")
    print("3. Manually review and fix any remaining type annotations")


if __name__ == "__main__":
    main()
