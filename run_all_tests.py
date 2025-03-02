#!/usr/bin/env python
"""Run all tests for the elastic_hash package."""

import unittest
import sys

def run_tests():
    """
    Run all tests and return the exit code.
    
    Returns:
        int: 0 if all tests pass, 1 otherwise
    """
    # Discover and run tests
    loader = unittest.TestLoader()
    suite = loader.discover('tests')
    
    # Run tests with verbose output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print(f"\nTest result: {'PASSED' if result.wasSuccessful() else 'FAILED'}")
    print(f"Ran {result.testsRun} tests")
    print(f"Errors: {len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    
    # Return 0 if successful, 1 otherwise
    return 0 if result.wasSuccessful() else 1

if __name__ == "__main__":
    sys.exit(run_tests())
