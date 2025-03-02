# Elastic Hash

[![Python Tests](https://github.com/yourusername/elastic-hash/actions/workflows/python-tests.yml/badge.svg)](https://github.com/yourusername/elastic-hash/actions/workflows/python-tests.yml)
[![PyPI version](https://badge.fury.io/py/elastic-hash.svg)](https://badge.fury.io/py/elastic-hash)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python Versions](https://img.shields.io/pypi/pyversions/elastic-hash.svg)](https://pypi.org/project/elastic-hash/)

A Python implementation of advanced open addressing hash table algorithms from the paper "Optimal Bounds for Open Addressing Without Reordering" by Martín Farach-Colton, Andrew Krapivin, and William Kuszmaul.

## Features

This library provides two cutting-edge hash table implementations:

1. **ElasticHashTable**: Achieves O(1) amortized expected probe complexity and O(log 1/δ) worst-case expected probe complexity without reordering elements.

2. **FunnelHashTable**: A greedy approach that achieves O(log² 1/δ) worst-case expected probe complexity, disproving the longstanding Yao's conjecture that O(1/δ) was optimal for greedy approaches.

Where δ is the fraction of empty slots in the table (e.g., if the table is 90% full, δ = 0.1).

## Installation

```bash
pip install elastic-hash
```

Or install from source:

```bash
git clone https://github.com/yourusername/elastic-hash.git
cd elastic-hash
pip install -e .
```

## Usage

### ElasticHashTable

```python
from elastic_hash import ElasticHashTable

# Create a new table with capacity 100
table = ElasticHashTable(100)

# Insert some values
table.insert("name", "John Doe")
table.insert("email", "john@example.com")
table.insert("age", 30)

# Retrieve values
print(table.get("name"))  # "John Doe"
print(table.get("unknown"))  # None

# Check if key exists
print("name" in table)  # True

# Remove a key
table.remove("email")  # True

# Get size
print(len(table))  # 2

# Iterate over all key-value pairs
for key, value in table:
    print(f"{key}: {value}")
```

### FunnelHashTable

```python
from elastic_hash import FunnelHashTable

# Create a new table with capacity 100
table = FunnelHashTable(100)

# The API is the same as ElasticHashTable
table.insert("key", "value")
value = table.get("key")
exists = "key" in table
success = table.remove("key")
```

## Advantages Over Built-in Dict

1. **Bounded Operations**: Our hash tables provide strong theoretical guarantees on worst-case operation time, which can be critical for real-time applications.

2. **Consistent Performance**: When operating at high load factors (e.g., 90% full), our hash tables maintain better worst-case performance than traditional approaches.

3. **Memory Efficiency**: Our implementations work well even when very full, allowing you to use memory more efficiently.

4. **No Reordering**: Unlike some advanced hash tables, our implementations never move elements after insertion, which can be important for certain applications.

## Benchmarks

We've benchmarked both hash table implementations against Python's built-in dict. Here are some key findings from our tests:

| Implementation | Load Factor | Insert (ops/sec) | Lookup Hit (ops/sec) | Lookup Miss (ops/sec) | Delete (ops/sec) |
|---------------|-------------|-----------------|----------------------|----------------------|-----------------|
| ElasticHashTable | 0.5 | ~6,000 | ~740,000 | ~76,000 | ~620,000 |
| ElasticHashTable | 0.9 | ~6,500 | ~760,000 | ~78,000 | ~570,000 |
| FunnelHashTable | 0.5 | ~26,000 | ~550,000 | ~28,000 | ~160,000 |
| FunnelHashTable | 0.9 | ~27,000 | ~570,000 | ~28,000 | ~120,000 |

Key observations:
- **FunnelHashTable is ~4x faster for insertions** than ElasticHashTable
- **ElasticHashTable has better lookup miss performance** (when key doesn't exist)
- Both implementations maintain consistent performance even at high load factors (90%)
- The performance characteristics match the theoretical guarantees from the paper

The `examples/benchmark.py` script lets you run your own benchmarks across different capacities and load factors:

```bash
python examples/benchmark.py

# For visualization support, install matplotlib:
pip install matplotlib
```

## Implementation Notes

### ElasticHashTable

- Divides the array into subarrays of geometrically decreasing sizes
- Uses a two-dimensional probe sequence for each key
- Implements batch-based insertion to maintain balanced fill levels
- Achieves O(1) amortized expected probe complexity through careful distribution of work
- Excellent negative lookup performance (when key doesn't exist)
- Hash functions are carefully designed to avoid clustering

### FunnelHashTable

- Divides the array into multiple levels with buckets of fixed size
- Uses a greedy approach where elements cascade down through levels
- Implements a special overflow area using the power-of-two-choices method
- Achieves O(log² 1/δ) worst-case expected probe complexity
- Superior insertion performance
- Can handle high load factors with minimal performance degradation

## When to Use

**Use ElasticHashTable when:**
- Your workload is lookup-heavy, especially with many lookups for keys that don't exist
- You need optimal amortized performance
- You need better delete operation performance

**Use FunnelHashTable when:**
- Your workload is insert-heavy
- You want to maximize insertion throughput
- You need a greedy approach with better worst-case guarantees than traditional hash tables

**Both implementations are ideal for:**
- Real-time systems requiring predictable performance
- High load factor scenarios (>80% full)
- Memory-constrained environments
- Applications where elements shouldn't be reordered after insertion

## Running Tests

```bash
# Run all tests
python run_all_tests.py

# Run a specific test
python -m unittest tests.test_hash_tables.TestElasticHashTable.test_high_load_factor
```

Our test suite verifies that both implementations:
- Handle basic operations (insert, get, remove) correctly
- Work at high load factors (up to 80%)
- Handle collisions properly
- Throw appropriate errors when the table is full

## Credits

Based on the paper "Optimal Bounds for Open Addressing Without Reordering" by Martín Farach-Colton, Andrew Krapivin, and William Kuszmaul.

## License

MIT
