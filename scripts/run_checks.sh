#!/bin/bash
# Run development checks before committing

set -e  # Exit on error

echo "Running code formatting checks..."
if command -v black &> /dev/null; then
    black --check elastic_hash tests examples
else
    echo "black not found. Install with 'pip install black'"
    exit 1
fi

echo "Running import sorting checks..."
if command -v isort &> /dev/null; then
    isort --check-only elastic_hash tests examples
else
    echo "isort not found. Install with 'pip install isort'"
    exit 1
fi

echo "Running linting checks..."
if command -v flake8 &> /dev/null; then
    flake8 elastic_hash tests examples
else
    echo "flake8 not found. Install with 'pip install flake8'"
    exit 1
fi

echo "Running tests..."
python run_all_tests.py

echo "All checks passed!"
