#!/bin/bash
# Clean up script for development

# Remove build artifacts
find . -name "*.pyc" -delete
find . -name "__pycache__" -delete
find . -name "*.so" -delete
find . -name "*.dylib" -delete
find . -name "*.egg-info" -type d -exec rm -rf {} +
find . -name ".eggs" -type d -exec rm -rf {} +
find . -name ".pytest_cache" -type d -exec rm -rf {} +
find . -name ".coverage" -delete
find . -name "htmlcov" -type d -exec rm -rf {} +
find . -name "dist" -type d -exec rm -rf {} +
find . -name "build" -type d -exec rm -rf {} +

# Remove benchmark results
find . -name "hash_table_benchmark_results.csv" -delete
find . -name "hash_table_benchmark_results.png" -delete

echo "Cleanup complete!"
