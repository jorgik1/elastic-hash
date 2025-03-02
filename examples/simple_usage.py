"""Simple usage examples for elastic-hash library.

This script demonstrates the basic functionality and advantages of both
ElasticHashTable and FunnelHashTable implementations, including:
- Basic operations (insert, get, remove)
- Membership testing and iteration
- Performance at high load factors

Run this script directly to see the demonstrations in action:
    python simple_usage.py
"""
from elastic_hash import ElasticHashTable, FunnelHashTable


def demo_elastic_hash_table():
    """Demonstrate basic usage of ElasticHashTable."""
    print("\n=== ElasticHashTable Demo ===")
    
    # Create a new table with capacity 100
    table = ElasticHashTable(100)
    
    # Insert some values
    table.insert("name", "John Doe")
    table.insert("email", "john@example.com")
    table.insert("age", 30)
    
    # Retrieve values
    print(f"Name: {table.get('name')}")           # John Doe
    print(f"Email: {table.get('email')}")         # john@example.com
    print(f"Age: {table.get('age')}")             # 30
    print(f"Phone: {table.get('phone')}")         # None (not found)
    
    # Check if keys exist
    print(f"Contains 'name': {'name' in table}")  # True
    print(f"Contains 'phone': {'phone' in table}")  # False
    
    # Get the current size
    print(f"Size: {len(table)}")                  # 3
    
    # Remove a key
    table.remove("email")
    print(f"After removal - Email: {table.get('email')}")  # None
    print(f"Size after removal: {len(table)}")    # 2
    
    # Iterate over all items
    print("All items:")
    for key, value in table:
        print(f"  {key}: {value}")


def demo_funnel_hash_table():
    """Demonstrate basic usage of FunnelHashTable."""
    print("\n=== FunnelHashTable Demo ===")
    
    # Create a new table with capacity 100
    table = FunnelHashTable(100)
    
    # Insert some values
    table.insert("name", "Jane Smith")
    table.insert("email", "jane@example.com")
    table.insert("age", 28)
    
    # Retrieve values
    print(f"Name: {table.get('name')}")           # Jane Smith
    print(f"Email: {table.get('email')}")         # jane@example.com
    print(f"Age: {table.get('age')}")             # 28
    print(f"Phone: {table.get('phone')}")         # None (not found)
    
    # Check if keys exist
    print(f"Contains 'name': {'name' in table}")  # True
    print(f"Contains 'phone': {'phone' in table}")  # False
    
    # Get the current size
    print(f"Size: {len(table)}")                  # 3
    
    # Remove a key
    table.remove("email")
    print(f"After removal - Email: {table.get('email')}")  # None
    print(f"Size after removal: {len(table)}")    # 2
    
    # Iterate over all items
    print("All items:")
    for key, value in table:
        print(f"  {key}: {value}")


def demo_high_load_factor():
    """Demonstrate behavior at high load factors."""
    print("\n=== High Load Factor Demo ===")
    
    capacity = 1000
    load_factor = 0.9  # 90% full
    
    elastic_table = ElasticHashTable(capacity)
    funnel_table = FunnelHashTable(capacity)
    
    # Insert items up to the load factor
    items_to_insert = int(capacity * load_factor)
    print(f"Inserting {items_to_insert} items into both tables (load factor: {load_factor})")
    
    for i in range(items_to_insert):
        key = f"key{i}"
        value = f"value{i}"
        elastic_table.insert(key, value)
        funnel_table.insert(key, value)
    
    # Test retrievals at high load
    import random
    import time
    
    # Select 100 random keys
    test_keys = [f"key{random.randint(0, items_to_insert-1)}" for _ in range(100)]
    
    # Time ElasticHashTable lookups
    start_time = time.time()
    for key in test_keys:
        elastic_table.get(key)
    elastic_time = time.time() - start_time
    
    # Time FunnelHashTable lookups
    start_time = time.time()
    for key in test_keys:
        funnel_table.get(key)
    funnel_time = time.time() - start_time
    
    print(f"ElasticHashTable: 100 lookups took {elastic_time:.6f} seconds")
    print(f"FunnelHashTable:  100 lookups took {funnel_time:.6f} seconds")


if __name__ == "__main__":
    demo_elastic_hash_table()
    demo_funnel_hash_table()
    demo_high_load_factor()
