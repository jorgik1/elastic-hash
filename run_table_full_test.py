#!/usr/bin/env python
"""Run only the table_full test for the ElasticHashTable."""

import unittest
from tests.test_hash_tables import TestElasticHashTable

if __name__ == "__main__":
    # Run just the test_table_full test
    suite = unittest.TestSuite()
    suite.addTest(TestElasticHashTable('test_table_full'))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print(f"Test passed: {result.wasSuccessful()}")
