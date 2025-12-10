
import unittest
from elastic_hash import ElasticHashTable, FunnelHashTable, elastic_table, funnel_table
from elastic_hash import hash_functions
from elastic_hash.utils import TOMBSTONE

class TestCorrectness(unittest.TestCase):
    """
    Tests to verify correctness of hash table operations,
    specifically focusing on collision handling and removal (Tombstones).
    """

    def test_elastic_collision_remove_chain(self):
        """
        Verify that removing an element does not break the probe chain for other elements
        that collided with it (ElasticHashTable).
        """
        print("\nTesting ElasticHashTable remove chain correctness...")
        table = ElasticHashTable(30)

        # Monkey patch probe limit to ensure we search deep enough
        old_limit = table._calculate_probe_limit
        table._calculate_probe_limit = lambda eps: 100

        # Monkey patch hash function to force collisions
        original_hash_func = elastic_table.two_dimensional_hash

        def forced_collision_hash(key, i, j, max_value):
            res = hash_functions.two_dimensional_hash(key, i, j, max_value)
            if i == 0 and j == 0 and max_value == len(table.subarrays[0]):
                if key in ["key1", "key2"]: return 2 # Force collision
            return res

        elastic_table.two_dimensional_hash = forced_collision_hash

        try:
            table.insert("key1", "val1")
            table.insert("key2", "val2")

            # Verify both are present
            self.assertEqual(table.get("key1"), "val1")
            self.assertEqual(table.get("key2"), "val2")

            # Remove the first one
            table.remove("key1")
            self.assertIsNone(table.get("key1"))

            # Verify the second one is STILL present
            val2 = table.get("key2")
            self.assertEqual(val2, "val2", "key2 should be found after removing key1")

            # Verify we can fill the tombstone
            table.insert("key3", "val3") # Should potentially reuse the slot?
            # Note: insert logic might pick a different slot depending on hash of key3.
            # But "key1" slot is now Tombstone.

        finally:
            elastic_table.two_dimensional_hash = original_hash_func
            table._calculate_probe_limit = old_limit

    def test_funnel_collision_remove_chain(self):
        """
        Verify that removing an element does not break the search in a bucket (FunnelHashTable).
        """
        print("\nTesting FunnelHashTable remove chain correctness...")
        table = FunnelHashTable(100)

        # FunnelHashTable uses murmur_hash to find bucket.
        # We need to force two keys to hash to the same bucket AND same sequence.

        # Actually, Funnel Hashing tries bucket slots sequentially: base, base+1, ...
        # If we fill base, base+1. Remove base. Search for base+1.
        # It relies on checking slots sequentially.
        # If slot at base is None, it stops.

        # We need to force collision in the bucket hash.
        original_hash_func = funnel_table.murmur_hash

        # We target subarray 0.
        target_bucket = 0

        def forced_bucket_hash(key, seed=0):
            # Seed 0 is used for subarray 0 bucket choice in `_hash_to_bucket`
            # `bucket_idx = murmur_hash(key, seed=subarray_idx) % num_buckets`
            # So if seed == 0 (subarray_idx), we force return 0 (bucket 0)
            if seed == 0:
                 if key in ["keyA", "keyB"]: return 0

            return hash_functions.murmur_hash(key, seed)

        funnel_table.murmur_hash = forced_bucket_hash

        try:
            # We need to make sure they fall into the same bucket.
            # Subarray 0 size is usually large.
            # We patched the hash to return 0 for seed 0.
            # `bucket_idx = 0 % num_buckets = 0`.
            # So `bucket_start` = 0.

            table.insert("keyA", "valA") # Should go to slot 0 of sub 0?
            table.insert("keyB", "valB") # Should go to slot 1 of sub 0?

            # Verify locations (whitebox check)
            sub0 = table.subarrays[0]
            # keyA should be at 0 (or wherever first slot empty is)
            # keyB should be at 1

            # Note: we need to ensure they actually go to sub0.
            # Funnel hashing tries sub0, sub1...
            # First insert keyA. It goes to sub0.

            self.assertEqual(table.get("keyA"), "valA")
            self.assertEqual(table.get("keyB"), "valB")

            # Remove keyA
            table.remove("keyA")
            self.assertIsNone(table.get("keyA"))

            # Verify keyB is still there
            valB = table.get("keyB")
            self.assertEqual(valB, "valB", "keyB should be found after removing keyA in same bucket")

        finally:
            funnel_table.murmur_hash = original_hash_func

    def test_tombstone_reuse(self):
        """
        Verify that tombstones are reused for insertion.
        """
        table = ElasticHashTable(10)
        # Fill a specific slot
        table.insert("a", 1)
        # Remove it
        table.remove("a")

        # Insert new item, it should preferably use the tombstone (if it hashes there)
        # This is hard to guarantee without mocking hash, but we can verify size and capacity behavior.
        # If we insert/remove repeatedly, we shouldn't run out of space if we reuse tombstones.

        for i in range(100):
            table.insert("a", 1)
            table.remove("a")
            self.assertEqual(len(table), 0)

        # If we didn't reuse tombstones, we might have filled the table with tombstones
        # (though this implementation doesn't fail on tombstones, it just searches past them).
        # But for insert, we MUST reuse them or we will overflow.
        # Because we only have capacity=10. 100 inserts would definitely overflow if not reused.

    def test_tombstones_iter(self):
        """Verify iteration skips tombstones."""
        table = ElasticHashTable(10)
        table.insert("a", 1)
        table.insert("b", 2)
        table.remove("a")

        items = list(table)
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0], ("b", 2))

if __name__ == "__main__":
    unittest.main()
