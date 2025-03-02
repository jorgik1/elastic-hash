#!/usr/bin/env python
"""
Run tests for the elastic_hash package.

This script discovers and runs all tests in the tests directory.

Usage:
    python run_tests.py               # Run all tests
    python run_tests.py -v            # Run with verbose output
    python run_tests.py specific_test  # Run a specific test module/class/function
    
Examples:
    python run_tests.py tests.test_hash_tables.TestElasticHashTable
    python run_tests.py tests.test_hash_tables.TestElasticHashTable.test_high_load_factor
"""
import sys
import unittest


def run_tests(test_names=None):
    """
    Run tests and return the exit code.
    
    Args:
        test_names: Optional list of specific test names to run
        
    Returns:
        int: 0 if all tests pass, 1 otherwise
    """
    # Handle verbosity
    verbosity = 1
    if '-v' in sys.argv or '--verbose' in sys.argv:
        verbosity = 2
        if '-v' in sys.argv:
            sys.argv.remove('-v')
        if '--verbose' in sys.argv:
            sys.argv.remove('--verbose')
    
    # Check for specific tests to run
    if len(sys.argv) > 1:
        specific_tests = sys.argv[1:]
        suite = unittest.TestLoader().loadTestsFromNames(specific_tests)
    else:
        # Discover and run all tests
        suite = unittest.TestLoader().discover('tests')
    
    # Run tests with specified verbosity
    runner = unittest.TextTestRunner(verbosity=verbosity)
    result = runner.run(suite)
    
    # Print summary
    print(f"\nTest result: {'PASSED' if result.wasSuccessful() else 'FAILED'}")
    print(f"Ran {result.testsRun} tests")
    if result.errors:
        print(f"Errors: {len(result.errors)}")
    if result.failures:
        print(f"Failures: {len(result.failures)}")
    
    # Return 0 if successful, 1 otherwise
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    sys.exit(run_tests())
