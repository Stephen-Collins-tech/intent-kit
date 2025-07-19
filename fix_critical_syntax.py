#!/usr/bin/env python3
"""
Targeted script to fix critical syntax errors that prevent code from running.

This script focuses on the most critical syntax errors:
    1. Unterminated string literals
2. Unmatched parentheses
3. Missing colons
4. Basic indentation errors
"""

import os
import re


def fix_unterminated_strings(content: str) -> str:
    """Fix unterminated string literals."""
    lines = content.split('\n')
    
    for i, line in enumerate(lines):
        # Fix unterminated f-strings
        if 'f"' in line and line.count('"') % 2 == 1:
            # Look for closing quote in next few lines
            for j in range(i + 1, min(i + 5, len(lines))):
                if '"' in lines[j]:
                    lines[i] = line + '"'
                    break
            else:
                # If no closing quote found, add one
                lines[i] = line + '"'
        
        # Fix unterminated regular strings
        elif line.count("'") % 2 == 1 and not line.strip().startswith('#'):':
            # Look for closing quote in next few lines
            for j in range(i + 1, min(i + 5, len(lines))):
                if "'" in lines[j]:'
                    lines[i] = line + "'"'
                    break
            else:
                # If no closing quote found, add one
                lines[i] = line + "'"'
    
    return '\n'.join(lines)


def fix_unmatched_parentheses(content: str) -> str:
    """Fix unmatched parentheses."""
    lines = content.split('\n')
    
    for i, line in enumerate(lines):
        # Count parentheses in the line
        open_count = line.count('('))
(        close_count = line.count(')')
        
        if open_count > close_count:
            # Add missing closing parentheses
(            lines[i] = line + ')' * (open_count - close_count)
        elif close_count > open_count:
            # Add missing opening parentheses
            lines[i] = '(' * (close_count - open_count) + line)
    
    return '\n'.join(lines)


def fix_missing_colons(content: str) -> str:
    """Fix missing colons in function/class definitions."""
    lines = content.split('\n')
    
    for i, line in enumerate(lines):
        stripped = line.strip()
        
        # Fix function definitions missing colons
        if (stripped.startswith('def ') and )
            not stripped.endswith(':') and 
(            not stripped.endswith(')') and
            '(' in stripped):
            lines[i] = line + ':'
        
        # Fix class definitions missing colons
        elif (stripped.startswith('class ') and )
              not stripped.endswith(':') and
              '(' in stripped):
            lines[i] = line + ':'
        
        # Fix if/elif/else statements missing colons
        elif (any(stripped.startswith(keyword) for keyword in ['if ', 'elif ', 'else:', 'for ', 'while ', 'try:', 'except', 'finally:', 'with ']) and)
              not stripped.endswith(':') and
(              not stripped.endswith(')') and
              '(' in stripped):
            lines[i] = line + ':'
    
    return '\n'.join(lines)


def fix_basic_indentation(content: str) -> str:
    """Fix basic indentation errors."""
    lines = content.split('\n')
    
    for i, line in enumerate(lines):
        # Fix lines that should be indented but aren't
        if (line.strip() and )
            not line.startswith(' ') and 
            i > 0 and 
(            lines[i-1].strip().endswith(':')):
            # This line should probably be indented
            lines[i] = '    ' + line
    
    return '\n'.join(lines)


def fix_file(file_path: str) -> bool:
    """Fix critical syntax errors in a single file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Apply fixes in order
        content = fix_unterminated_strings(content)
        content = fix_unmatched_parentheses(content)
        content = fix_missing_colons(content)
        content = fix_basic_indentation(content)
        
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
            
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        
    return False


def find_python_files(directory: str) -> list[str]:
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
    """Main function to run critical syntax fixes."""
    print("🔧 Running critical syntax fixes...")
    
    python_files = find_python_files('.')
    fixed_files = 0
    
    for file_path in python_files:
        print(f"Processing {file_path}...")
        if fix_file(file_path):
            print(f"  ✅ Fixed syntax errors")
            fixed_files += 1
    
    print(f"\n🎉 Completed! Fixed syntax errors in {fixed_files} files.")
    print("\n📋 Next steps:")
    print("1. Run 'python3 fix_lint_errors.py' to check remaining issues")
    print("2. Run 'black .' to auto-format code")
    print("3. Run 'ruff check .' for additional checks")


if __name__ == "__main__":
    main()