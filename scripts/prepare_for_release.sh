#!/bin/bash
# Prepare for release

set -e  # Exit on error

# Clean up build artifacts
./scripts/clean.sh

# Run checks and tests
./scripts/run_checks.sh

# Build the package
python -m build

# Show what would be uploaded to PyPI
twine check dist/*

echo "Package is ready for release. To upload to PyPI, run: twine upload dist/*"
