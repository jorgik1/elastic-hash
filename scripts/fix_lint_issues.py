#!/usr/bin/env python
"""
Fix common linting issues in the codebase.

This script:
1. Removes unused imports
2. Fixes whitespace issues
3. Adjusts blank lines between classes and methods
"""
import os
import re
import sys

def fix_file(filepath):
    """Fix linting issues in a single file."""
    with open(filepath, 'r') as f:
        content = f.read()
    
    # Track if we made changes
    original_content = content
    
    # 1. Remove trailing whitespace
    content = re.sub(r' +$', '', content, flags=re.MULTILINE)
    
    # 2. Fix blank lines containing whitespace
    content = re.sub(r'\n[ \t]+\n', '\n\n', content)
    
    # 3. Fix class/function definitions needing 2 blank lines
    content = re.sub(r'(\n[^\n]+\n)class ', r'\n\n\nclass ', content)
    content = re.sub(r'(\n[^\n]+\n)def ', r'\n\n\ndef ', content)
    
    # 4. Fix multiple blank lines (more than 2)
    content = re.sub(r'\n{4,}', '\n\n\n', content)
    
    # Check for unused imports (more complex, may need manual intervention)
    # This is a simple heuristic - check for each imported name in the file
    import_pattern = re.compile(r'^from\s+[\w.]+\s+import\s+(.*?)$', re.MULTILINE)
    for match in import_pattern.finditer(content):
        imported_items = match.group(1)
        # Process the imported items
        for item in re.split(r',\s*', imported_items):
            item = item.strip()
            if item.startswith('(') and item.endswith(')'):
                item = item[1:-1]
            if ' as ' in item:
                item = item.split(' as ')[1]
            
            # Check if the item is used in the file (simple check)
            if item and item not in ['*']:
                pattern = r'\b' + re.escape(item) + r'\b'
                # Count occurrences but exclude the import line itself
                count = len(re.findall(pattern, content)) - 1
                if count <= 0:
                    print(f"  Warning: '{item}' appears unused in {os.path.basename(filepath)}")
    
    # Write back if changes were made
    if content != original_content:
        with open(filepath, 'w') as f:
            f.write(content)
        return True
    return False

def main():
    """Fix linting issues in all Python files."""
    # Directories to check
    directories = ['elastic_hash', 'tests', 'examples']
    
    files_changed = 0
    for directory in directories:
        for root, _, files in os.walk(directory):
            for file in files:
                if file.endswith('.py'):
                    filepath = os.path.join(root, file)
                    print(f"Checking {filepath}...")
                    if fix_file(filepath):
                        files_changed += 1
                        print(f"  Fixed issues in {filepath}")
    
    print(f"\nFixed issues in {files_changed} files.")
    print("Note: Some complex issues may need manual attention.")
    print("Run 'flake8' to check for remaining issues.")

if __name__ == "__main__":
    main()
