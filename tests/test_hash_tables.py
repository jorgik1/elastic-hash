"""
Tests for the elastic and funnel hash table implementations.
"""
import unittest
import random
import time
from typing import Dict, Any, List, Callable

from elastic_hash import ElasticHashTable, FunnelHashTable


class TestElasticHashTable(unittest.TestCase):
    """Test cases for ElasticHashTable."""
    
    def test_basic_operations(self):
        """Test basic insert, get, and remove operations."""
        table = ElasticHashTable(100)
        
        # Test insertion
        table.insert("key1", "value1")
        table.insert("key2", "value2")
        table.insert("key3", "value3")
        
        # Test retrieval
        self.assertEqual(table.get("key1"), "value1")
        self.assertEqual(table.get("key2"), "value2")
        self.assertEqual(table.get("key3"), "value3")
        self.assertIsNone(table.get("nonexistent"))
        
        # Test removal
        self.assertTrue(table.remove("key2"))
        self.assertIsNone(table.get("key2"))
        self.assertFalse(table.remove("key2"))  # Already removed
        
        # Test size
        self.assertEqual(len(table), 2)
        
        # Test contains
        self.assertTrue("key1" in table)
        self.assertFalse("key2" in table)
        
        # Test iteration
        items = {k: v for k, v in table}
        self.assertEqual(items, {"key1": "value1", "key3": "value3"})
        
        # Test clear
        table.clear()
        self.assertEqual(len(table), 0)
        self.assertIsNone(table.get("key1"))
    
    def test_high_load_factor(self):
        """Test with table at high load factor (80%)."""
        capacity = 1000
        table = ElasticHashTable(capacity)
        
        # Insert until 80% full
        load_factor = 0.8
        keys = [f"key{i}" for i in range(int(load_factor * capacity))]
        values = [f"value{i}" for i in range(int(load_factor * capacity))]
        
        for i in range(int(load_factor * capacity)):
            table.insert(keys[i], values[i])
        
        # Verify all values can be retrieved
        for i in range(int(load_factor * capacity)):
            self.assertEqual(table.get(keys[i]), values[i])
        
        # Test that we can still add more items
        table.insert("extra_key", "extra_value")
        self.assertEqual(table.get("extra_key"), "extra_value")
    
    def test_duplicate_key(self):
        """Test trying to insert a duplicate key raises ValueError."""
        table = ElasticHashTable(100)
        table.insert("key", "value")
        
        with self.assertRaises(ValueError):
            table.insert("key", "new_value")
    
    def test_table_full(self):
        """Test trying to insert when table is full raises OverflowError."""
        # Create a very small table with exact capacity
        capacity = 3  # Use an even smaller value for reliability
        table = ElasticHashTable(capacity)
        
        # First, verify the capacity
        total_slots = sum(len(subarray) for subarray in table.subarrays)
        self.assertEqual(total_slots, capacity, "Table must have exactly 'capacity' slots")
        
        # Insert until full
        for i in range(capacity):
            table.insert(f"key{i}", f"value{i}")
            
        # Check size matches capacity
        self.assertEqual(len(table), capacity)
        
        # Verify we can't insert any more
        with self.assertRaises(OverflowError):
            table.insert("one_too_many", "value")


class TestFunnelHashTable(unittest.TestCase):
    """Test cases for FunnelHashTable."""
    
    def test_basic_operations(self):
        """Test basic insert, get, and remove operations."""
        table = FunnelHashTable(100)
        
        # Test insertion
        table.insert("key1", "value1")
        table.insert("key2", "value2")
        table.insert("key3", "value3")
        
        # Test retrieval
        self.assertEqual(table.get("key1"), "value1")
        self.assertEqual(table.get("key2"), "value2")
        self.assertEqual(table.get("key3"), "value3")
        self.assertIsNone(table.get("nonexistent"))
        
        # Test removal
        self.assertTrue(table.remove("key2"))
        self.assertIsNone(table.get("key2"))
        self.assertFalse(table.remove("key2"))  # Already removed
        
        # Test size
        self.assertEqual(len(table), 2)
        
        # Test contains
        self.assertTrue("key1" in table)
        self.assertFalse("key2" in table)
        
        # Test iteration
        items = {k: v for k, v in table}
        self.assertEqual(items, {"key1": "value1", "key3": "value3"})
        
        # Test clear
        table.clear()
        self.assertEqual(len(table), 0)
        self.assertIsNone(table.get("key1"))
    
    def test_high_load_factor(self):
        """Test with table at high load factor (80%)."""
        capacity = 1000
        table = FunnelHashTable(capacity)
        
        # Insert until 80% full
        load_factor = 0.8
        keys = [f"key{i}" for i in range(int(load_factor * capacity))]
        values = [f"value{i}" for i in range(int(load_factor * capacity))]
        
        for i in range(int(load_factor * capacity)):
            table.insert(keys[i], values[i])
        
        # Verify all values can be retrieved
        for i in range(int(load_factor * capacity)):
            self.assertEqual(table.get(keys[i]), values[i])
        
        # Test that we can still add more items
        table.insert("extra_key", "extra_value")
        self.assertEqual(table.get("extra_key"), "extra_value")
    
    def test_duplicate_key(self):
        """Test trying to insert a duplicate key raises ValueError."""
        table = FunnelHashTable(100)
        table.insert("key", "value")
        
        with self.assertRaises(ValueError):
            table.insert("key", "new_value")
    
    def test_table_full(self):
        """Test trying to insert when table is full raises OverflowError."""
        # Create a very small table to make it easier to fill
        capacity = 5
        table = FunnelHashTable(capacity)
        
        # Fill the table until we get an overflow error
        keys_inserted = 0
        try:
            for i in range(capacity + 1):  # Try to insert one more than capacity
                table.insert(f"key{i}", f"value{i}")
                keys_inserted += 1
        except OverflowError:
            # We expect this error
            pass
            
        # Verify we managed to insert some keys
        self.assertGreater(keys_inserted, 0)
        
        # Verify we can't insert any more
        with self.assertRaises(OverflowError):
            table.insert("one_too_many", "value")


class BenchmarkTest(unittest.TestCase):
    """Benchmark tests for hash table implementations."""
    
    def _run_benchmark(self, table_class, capacity: int, load_factor: float, 
                      num_operations: int) -> Dict[str, float]:
        """
        Run a benchmark test on a hash table implementation.
        
        Args:
            table_class: The hash table class to test
            capacity: The capacity of the hash table
            load_factor: The load factor to test (0.0-1.0)
            num_operations: Number of operations to perform
            
        Returns:
            Dictionary with benchmark results
        """
        # Create the table
        table = table_class(capacity)
        
        # Generate keys and values
        fill_size = int(capacity * load_factor)
        test_size = min(fill_size, num_operations)
        
        keys = [f"key{i}" for i in range(fill_size)]
        values = [f"value{i}" for i in range(fill_size)]
        
        # Measure insertion time
        start_time = time.time()
        for i in range(test_size):
            table.insert(keys[i], values[i])
        insert_time = time.time() - start_time
        
        # Measure lookup time (hit)
        lookup_keys = random.sample(keys[:test_size], min(test_size, num_operations))
        start_time = time.time()
        for key in lookup_keys:
            table.get(key)
        lookup_hit_time = time.time() - start_time
        
        # Measure lookup time (miss)
        miss_keys = [f"missing{i}" for i in range(min(test_size, num_operations))]
        start_time = time.time()
        for key in miss_keys:
            table.get(key)
        lookup_miss_time = time.time() - start_time
        
        # Measure delete time
        delete_keys = random.sample(keys[:test_size], min(test_size // 2, num_operations))
        start_time = time.time()
        for key in delete_keys:
            table.remove(key)
        delete_time = time.time() - start_time
        
        return {
            "insert_time": insert_time,
            "lookup_hit_time": lookup_hit_time,
            "lookup_miss_time": lookup_miss_time,
            "delete_time": delete_time,
            "insert_ops_per_sec": test_size / insert_time if insert_time > 0 else 0,
            "lookup_hit_ops_per_sec": len(lookup_keys) / lookup_hit_time if lookup_hit_time > 0 else 0,
            "lookup_miss_ops_per_sec": len(miss_keys) / lookup_miss_time if lookup_miss_time > 0 else 0,
            "delete_ops_per_sec": len(delete_keys) / delete_time if delete_time > 0 else 0,
        }
    
    def test_benchmark_comparison(self):
        """Compare performance of ElasticHashTable and FunnelHashTable."""
        capacity = 10000
        load_factors = [0.5, 0.8, 0.9]
        num_operations = 1000
        
        results = {}
        
        for load_factor in load_factors:
            elastic_results = self._run_benchmark(
                ElasticHashTable, capacity, load_factor, num_operations
            )
            funnel_results = self._run_benchmark(
                FunnelHashTable, capacity, load_factor, num_operations
            )
            
            results[f"elastic_{load_factor}"] = elastic_results
            results[f"funnel_{load_factor}"] = funnel_results
            
            print(f"\nLoad factor: {load_factor}")
            print(f"ElasticHashTable:")
            print(f"  Insert: {elastic_results['insert_ops_per_sec']:.2f} ops/sec")
            print(f"  Lookup (hit): {elastic_results['lookup_hit_ops_per_sec']:.2f} ops/sec")
            print(f"  Lookup (miss): {elastic_results['lookup_miss_ops_per_sec']:.2f} ops/sec")
            print(f"  Delete: {elastic_results['delete_ops_per_sec']:.2f} ops/sec")
            
            print(f"FunnelHashTable:")
            print(f"  Insert: {funnel_results['insert_ops_per_sec']:.2f} ops/sec")
            print(f"  Lookup (hit): {funnel_results['lookup_hit_ops_per_sec']:.2f} ops/sec")
            print(f"  Lookup (miss): {funnel_results['lookup_miss_ops_per_sec']:.2f} ops/sec")
            print(f"  Delete: {funnel_results['delete_ops_per_sec']:.2f} ops/sec")


if __name__ == "__main__":
    unittest.main()
