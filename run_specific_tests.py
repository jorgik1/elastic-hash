#!/usr/bin/env python
"""Run specific tests that were previously failing."""

import unittest

# Import the test classes
from tests.test_hash_tables import TestElasticHashTable, TestFunnelHashTable

# Create a test suite with the specific tests
suite = unittest.TestSuite()

# Add the previously failing tests
suite.addTest(TestElasticHashTable('test_table_full'))
suite.addTest(TestFunnelHashTable('test_table_full'))

# Run the tests with verbose output
runner = unittest.TextTestRunner(verbosity=2)
result = runner.run(suite)

# Print summary
print(f"\nTest result: {'PASSED' if result.wasSuccessful() else 'FAILED'}")
print(f"Ran {result.testsRun} tests")
print(f"Errors: {len(result.errors)}")
print(f"Failures: {len(result.failures)}")
