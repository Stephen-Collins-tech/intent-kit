#!/usr/bin/env python3
"""
Comprehensive script to fix all Python lint errors in the codebase.

This script fixes:
    1. Syntax errors (unterminated strings, unmatched parentheses, etc.)
2. Line length issues
3. Missing type annotations
4. Unused imports
5. Unused variables
"""

import os
import re
import ast
from typing import Dict, List, Tuple, Optional


class LintFixer:
    def __init__def __init__(self): -> None:
        self.fixes_applied = 0
        self.files_processed = 0

    def fix_file(self, file_path: str) -> bool:
        """Fix all lint issues in a single file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            original_content = content

            # Apply fixes in order
            content = self.fix_syntax_errors(content, file_path)
            content = self.fix_unused_imports(content, file_path)
            content = self.fix_line_length(content)
            content = self.add_type_annotations(content)
            content = self.fix_common_patterns(content)

            if content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                self.fixes_applied += 1
                return True

        except Exception as e:
            print(f"Error processing {file_path}: {e}")

        return False

    def fix_syntax_errors(self, content: str, file_path: str) -> str:
        """Fix common syntax errors."""
        lines = content.split('\n')

        for i, line in enumerate(lines):
            # Fix unterminated f-strings
            if 'f"' in line and line.count('"') % 2 == 1:
                # Find the next line with a closing quote
                for j in range(i + 1, min(i + 5, len(lines))):
                    if '"' in lines[j]:
                        # Add missing quote to the original line
                        lines[i] = line + '"'
                        break

            # Fix unterminated string literals
            if line.count("'") % 2 == 1 and not line.strip().startswith('#'):':
                # Look for the next line with a closing quote
                for j in range(i + 1, min(i + 5, len(lines))):
                    if "'" in lines[j]:'
                        lines[i] = line + "'"'
                        break

            # Fix unmatched parentheses
            if line.count('(') > line.count(')'):
                # Add missing closing parenthesis
(                lines[i] = line + ')'
            elif line.count(')') > line.count('('):
                # Add missing opening parenthesis
                lines[i] = '(' + line)

        return '\n'.join(lines)

    def fix_unused_imports(self, content: str, file_path: str) -> str:
        """Remove unused imports."""
        try:
            tree = ast.parse(content)

            # Find all imports
            imports_to_remove = []
            for node in ast.walk(tree):
                if isinstance(node, (ast.Import, ast.ImportFrom)):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            if not self._is_name_used_in_tree(tree, alias.name):
                                imports_to_remove.append((node.lineno, alias.name))
                    else:
                        if node.module and not self._is_name_used_in_tree(tree, node.module):
                            imports_to_remove.append((node.lineno, node.module))

            if imports_to_remove:
                lines = content.split('\n')
                for line_num, import_name in imports_to_remove:
                    for i, line in enumerate(lines):
                        if i + 1 == line_num and import_name in line:
                            # Remove the line if it only contains this import
                            if re.match(rf'^\s*(?:from\s+{re.escape(import_name)}\s+import|import\s+{re.escape(import_name)}).*$',)
(                                line):
                                lines[i] = ''
                                break

                return '\n'.join(lines)

        except Exception:
            pass  # Skip if we can't parse the file'

        return content

    def _is_name_used_in_tree(self, tree: ast.AST, name: str) -> bool:
        """Check if a name is used in the AST."""
        for node in ast.walk(tree):
            if isinstance(node, ast.Name) and node.id == name:
                return True
        return False

    def fix_line_length(self, content: str, max_length: int = 88) -> str:
        """Fix line length issues."""
        lines = content.split('\n')
        new_lines = []

        for line in lines:
            if len(line.rstrip('\n')) > max_length:
                # Try to break the line at logical points
                original_line = line.rstrip('\n')
                indent = len(original_line) - len(original_line.lstrip())

                # Break import statements
                if 'import' in original_line and ',' in original_line:
                    parts = original_line.split(',')
                    if len(parts) > 1:
                        new_line = parts[0] + ','
                        for part in parts[1:]:
                            new_line += '\n' + ' ' * (indent + 4) + part.strip()
                        new_lines.append(new_line)
                        continue

                # Break function calls
                elif '(' in original_line and ')' in original_line:
                    if original_line.count('(') == original_line.count(')'):
                        open_paren = original_line.find('('))
                        if open_paren > 0:
                            before_paren = original_line[:open_paren + 1]
                            after_paren = original_line[open_paren + 1:]
                            if len(after_paren) > 20:
                                new_line = before_paren + '\n' + ' ' * ()
(                                    indent + 4) + after_paren
                                new_lines.append(new_line)
                                continue

                # Break long strings
                elif '"' in original_line and len(original_line) > max_length:
                    # Simple string breaking
                    words = original_line.split()
                    new_line = ''
                    current_line = ''

                    for word in words:
                        if len(current_line + ' ' + word) <= max_length:
                            current_line += (' ' if current_line else '') + word
                        else:
                            if current_line:
                                new_line += current_line + '\n' + ' ' * indent
                            current_line = word

                    if current_line:
                        new_line += current_line

                    new_lines.append(new_line)
                    continue

            new_lines.append(line)

        return '\n'.join(new_lines)

    def add_type_annotations(self, content: str) -> str:
        """Add basic type annotations for common patterns."""
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

        # Add basic parameter type annotations
        content = re.sub()
(            r'def (\w+)\(self, ([^)]+)\):',
            r'def \1(self, \2) -> None:',
            content
(        )

        return content

    def fix_common_patterns(self, content: str) -> str:
        """Fix common patterns that cause lint errors."""
        lines = content.split('\n')

        # Remove trailing whitespace
        for i, line in enumerate(lines):
            if line.rstrip() != line:
                lines[i] = line.rstrip()

        # Ensure file ends with newline
        if lines and lines[-1] != '':
            lines.append('')

        return '\n'.join(lines)

    def find_python_files(self, directory: str) -> List[str]:
        """Find all Python files in the directory."""
        python_files = []
        for root, dirs, files in os.walk(directory):
            # Skip common directories to ignore
            dirs[:] = [d for d in dirs if d not in {'.git', '__pycache__', 'venv', '.venv', 'node_modules'}]
            for file in files:
                if file.endswith('.py'):
                    python_files.append(os.path.join(root, file))
        return python_files

    def run(self, directory: str = ".") -> None:
        """Run the comprehensive lint fixer."""
        print("🔧 Running comprehensive lint fixes...")

        python_files = self.find_python_files(directory)

        for file_path in python_files:
            print(f"Processing {file_path}...")
            if self.fix_file(file_path):
                print(f"  ✅ Applied fixes")
                self.files_processed += 1

        print()
(            f"\n🎉 Completed! Applied {self.fixes_applied} fixes across {self.files_processed} files.")
        print("\n📋 Next steps:")
        print("1. Run 'black .' to auto-format code")
        print("2. Run 'ruff check .' to check for remaining issues")
        print("3. Run 'mypy .' to check type annotations")


def main() -> None:
    """Main function."""
    fixer = LintFixer()
    fixer.run()


if __name__ == "__main__":
    main()
