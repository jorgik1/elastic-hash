#!/bin/bash
# Run black and isort to format all code

set -e  # Exit on error

echo "Formatting code with black..."
black elastic_hash tests examples

echo "Sorting imports with isort..."
isort elastic_hash tests examples

echo "All code formatted successfully!"
