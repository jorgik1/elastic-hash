#!/usr/bin/env python
"""
Format code across the project using black and isort.

This script:
1. Runs black for code formatting
2. Runs isort for import sorting
"""
import os
import subprocess
import sys

def run_command(command):
    """Run a shell command and return output."""
    print(f"Running: {' '.join(command)}")
    result = subprocess.run(command, capture_output=True, text=True)
    
    if result.stdout:
        print(result.stdout)
    
    if result.stderr:
        print(result.stderr, file=sys.stderr)
    
    return result.returncode == 0

def main():
    """Format all code in the project."""
    # Directories to format
    directories = ['elastic_hash', 'tests', 'examples']
    
    # Check for required tools
    try:
        subprocess.run(["black", "--version"], capture_output=True)
    except FileNotFoundError:
        print("Black not found. Installing...")
        if not run_command([sys.executable, "-m", "pip", "install", "black"]):
            print("Failed to install black.")
            return 1
    
    try:
        subprocess.run(["isort", "--version"], capture_output=True)
    except FileNotFoundError:
        print("isort not found. Installing...")
        if not run_command([sys.executable, "-m", "pip", "install", "isort"]):
            print("Failed to install isort.")
            return 1
    
    # Run black on all directories
    print("\n============ Running Black ============")
    if not run_command(["black"] + directories):
        print("Black failed to format some files.")
    
    # Run isort on all directories
    print("\n============ Running isort ============")
    if not run_command(["isort"] + directories):
        print("isort failed to sort imports in some files.")
    
    print("\nFormatting complete.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
