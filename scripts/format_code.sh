#!/bin/bash
# Format code with black and isort, then fix linting issues

set -e  # Exit on error

echo "Checking for required packages..."
# Check for black
if ! command -v black &> /dev/null; then
    echo "black not found. Installing..."
    pip install black
fi

# Check for isort
if ! command -v isort &> /dev/null; then
    echo "isort not found. Installing..."
    pip install isort
fi

# Check for flake8
if ! command -v flake8 &> /dev/null; then
    echo "flake8 not found. Installing..."
    pip install flake8
fi

echo "Running isort to sort imports..."
isort elastic_hash tests examples

echo "Running black to format code..."
black elastic_hash tests examples

echo "Running our custom lint fixer script..."
python scripts/fix_lint_issues.py

echo "Checking for remaining issues with flake8..."
flake8 elastic_hash tests examples || true

echo "Formatting complete! Some issues may require manual fixing."
echo "Run 'flake8 elastic_hash tests examples' to see any remaining issues."
