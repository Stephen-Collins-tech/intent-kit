#!/usr/bin/env python3pt to fix trailing whitespace in test files."""

import os
import re

def fix_trailing_whitespace(file_path):
 ix trailing whitespace in a file."""
    with open(file_path, rf:
        content = f.read()
    
    # Remove trailing whitespace from lines
    lines = content.split('\n)
    fixed_lines = [line.rstrip() for line in lines]
    fixed_content = '\n.join(fixed_lines)
    
    with open(file_path, w) asf:
        f.write(fixed_content)

def main():
 ix trailing whitespace in all test files.   test_files = [
       tests/intent_kit/graph/test_registry.py',
       tests/intent_kit/node/test_base.py',
       tests/intent_kit/node/test_types.py',
       tests/intent_kit/node/test_enums.py',
       tests/intent_kit/test_core_types.py'
    ]
    
    for file_path in test_files:
        if os.path.exists(file_path):
            print(fFixing {file_path})
            fix_trailing_whitespace(file_path)
        else:
            print(fFile not found: {file_path})if __name__ == "__main__":
    main()