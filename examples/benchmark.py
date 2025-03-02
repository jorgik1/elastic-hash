"""
Benchmarking script to compare ElasticHashTable, FunnelHashTable, and Python's dict.

This script compares the performance of the hash table implementations across
different capacities and load factors.

Optional Dependencies:
    matplotlib: For visualization support. Install with:
               pip install matplotlib
               or
               pip install elastic-hash[plot]
"""
import time
import random
import sys
import csv
from typing import Dict, List, Tuple, Any, Callable, Type

from elastic_hash import ElasticHashTable, FunnelHashTable

# Try to import matplotlib but make it optional
try:
    import matplotlib.pyplot as plt
    PLOTTING_AVAILABLE = True
except ImportError:
    PLOTTING_AVAILABLE = False
    print("Note: matplotlib not found. Visualizations will be skipped.")
    print("To enable visualizations, install matplotlib: pip install matplotlib")


class DictWrapper:
    """A wrapper for Python's dict with a similar interface to our hash tables."""
    
    def __init__(self, capacity: int, delta: float = 0.1):
        """Initialize the wrapper."""
        self.data = {}
        self.capacity = capacity
        self.delta = delta
    
    def insert(self, key, value):
        """Insert a key-value pair."""
        if len(self.data) >= (1 - self.delta) * self.capacity:
            raise OverflowError("Dict is full")
        if key in self.data:
            raise ValueError(f"Key '{key}' already exists")
        self.data[key] = value
    
    def get(self, key):
        """Get a value by key."""
        return self.data.get(key)
    
    def remove(self, key):
        """Remove a key-value pair."""
        if key in self.data:
            del self.data[key]
            return True
        return False
    
    def __contains__(self, key):
        """Check if key exists."""
        return key in self.data
    
    def __len__(self):
        """Get number of key-value pairs."""
        return len(self.data)
    
    def __iter__(self):
        """Iterate over key-value pairs."""
        return iter(self.data.items())
    
    def clear(self):
        """Clear all key-value pairs."""
        self.data.clear()


def run_benchmark(table_classes: List[Type], capacities: List[int], load_factors: List[float], 
                 operations_per_test: int = 10000) -> Dict[str, Dict[Tuple[int, float], Dict[str, float]]]:
    """
    Run benchmarks on multiple hash table implementations.
    
    Args:
        table_classes: List of hash table classes to benchmark
        capacities: List of capacities to test
        load_factors: List of load factors to test
        operations_per_test: Number of operations per test
        
    Returns:
        Nested dictionary of results
    """
    results = {}
    
    for table_class in table_classes:
        class_name = table_class.__name__
        results[class_name] = {}
        
        for capacity in capacities:
            for load_factor in load_factors:
                print(f"Benchmarking {class_name} with capacity {capacity} at {load_factor:.2f} load factor...")
                
                # Create table
                table = table_class(capacity, delta=1-load_factor)
                
                # Generate keys and values
                items_to_insert = int(capacity * load_factor)
                test_size = min(items_to_insert, operations_per_test)
                
                keys = [f"key{i}" for i in range(items_to_insert)]
                values = [f"value{i}" for i in range(items_to_insert)]
                
                # Insert time
                insert_times = []
                chunk_size = min(1000, test_size)
                
                for j in range(0, test_size, chunk_size):
                    end_idx = min(j + chunk_size, test_size)
                    chunk_keys = keys[j:end_idx]
                    chunk_values = values[j:end_idx]
                    
                    start_time = time.time()
                    for k in range(len(chunk_keys)):
                        table.insert(chunk_keys[k], chunk_values[k])
                    chunk_time = time.time() - start_time
                    insert_times.append(chunk_time / len(chunk_keys))
                
                avg_insert_time = sum(insert_times) / len(insert_times)
                
                # Lookup time (hits)
                lookup_keys = random.sample(keys[:test_size], min(test_size, operations_per_test))
                start_time = time.time()
                for key in lookup_keys:
                    table.get(key)
                lookup_hit_time = time.time() - start_time
                
                # Lookup time (misses)
                missing_keys = [f"missing{i}" for i in range(min(test_size, operations_per_test))]
                start_time = time.time()
                for key in missing_keys:
                    table.get(key)
                lookup_miss_time = time.time() - start_time
                
                # Delete time
                delete_keys = random.sample(keys[:test_size], min(test_size // 2, operations_per_test))
                start_time = time.time()
                for key in delete_keys:
                    table.remove(key)
                delete_time = time.time() - start_time
                
                # Calculate operations per second
                insert_ops_per_sec = 1.0 / avg_insert_time if avg_insert_time > 0 else float('inf')
                lookup_hit_ops_per_sec = len(lookup_keys) / lookup_hit_time if lookup_hit_time > 0 else float('inf')
                lookup_miss_ops_per_sec = len(missing_keys) / lookup_miss_time if lookup_miss_time > 0 else float('inf')
                delete_ops_per_sec = len(delete_keys) / delete_time if delete_time > 0 else float('inf')
                
                # Store results
                results[class_name][(capacity, load_factor)] = {
                    "insert_time": avg_insert_time,
                    "lookup_hit_time": lookup_hit_time / len(lookup_keys),
                    "lookup_miss_time": lookup_miss_time / len(missing_keys),
                    "delete_time": delete_time / len(delete_keys),
                    "insert_ops_per_sec": insert_ops_per_sec,
                    "lookup_hit_ops_per_sec": lookup_hit_ops_per_sec,
                    "lookup_miss_ops_per_sec": lookup_miss_ops_per_sec,
                    "delete_ops_per_sec": delete_ops_per_sec,
                }
    
    return results


def print_results(results: Dict[str, Dict[Tuple[int, float], Dict[str, float]]]) -> None:
    """Print benchmark results in a nice format."""
    for class_name, class_results in results.items():
        print(f"\n=== {class_name} Results ===")
        print(f"{'Capacity':10} {'Load Factor':12} {'Insert (op/s)':15} {'Lookup Hit (op/s)':18} "
              f"{'Lookup Miss (op/s)':18} {'Delete (op/s)':15}")
        print("-" * 90)
        
        for (capacity, load_factor), metrics in sorted(class_results.items()):
            print(f"{capacity:<10d} {load_factor:<12.2f} "
                  f"{metrics['insert_ops_per_sec']:<15.2f} "
                  f"{metrics['lookup_hit_ops_per_sec']:<18.2f} "
                  f"{metrics['lookup_miss_ops_per_sec']:<18.2f} "
                  f"{metrics['delete_ops_per_sec']:<15.2f}")


def save_results_to_csv(results: Dict[str, Dict[Tuple[int, float], Dict[str, float]]], 
                        filename: str) -> None:
    """Save benchmark results to a CSV file."""
    with open(filename, 'w', newline='') as csvfile:
        fieldnames = ['implementation', 'capacity', 'load_factor', 
                     'insert_ops_per_sec', 'lookup_hit_ops_per_sec', 
                     'lookup_miss_ops_per_sec', 'delete_ops_per_sec']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        for class_name, class_results in results.items():
            for (capacity, load_factor), metrics in class_results.items():
                writer.writerow({
                    'implementation': class_name,
                    'capacity': capacity,
                    'load_factor': load_factor,
                    'insert_ops_per_sec': metrics['insert_ops_per_sec'],
                    'lookup_hit_ops_per_sec': metrics['lookup_hit_ops_per_sec'],
                    'lookup_miss_ops_per_sec': metrics['lookup_miss_ops_per_sec'],
                    'delete_ops_per_sec': metrics['delete_ops_per_sec'],
                })
    
    print(f"Results saved to {filename}")


def plot_results(results: Dict[str, Dict[Tuple[int, float], Dict[str, float]]], 
                save_filename: str = None) -> None:
    """Plot benchmark results."""
    if not PLOTTING_AVAILABLE:
        print("Skipping visualization as matplotlib is not available")
        return
        
    # Extract unique capacities and load factors
    capacities = set()
    load_factors = set()
    implementations = list(results.keys())
    
    for class_results in results.values():
        for capacity, load_factor in class_results.keys():
            capacities.add(capacity)
            load_factors.add(load_factor)
    
    capacities = sorted(capacities)
    load_factors = sorted(load_factors)
    
    # Setup plot grid
    fig, axes = plt.subplots(len(capacities), 4, figsize=(16, 4 * len(capacities)))
    fig.suptitle('Hash Table Performance Comparison', fontsize=16)
    
    # If only one capacity, wrap the axes in a list to make it 2D
    if len(capacities) == 1:
        axes = [axes]
    
    # Operations to plot
    operations = [
        ('insert_ops_per_sec', 'Insert Performance'),
        ('lookup_hit_ops_per_sec', 'Lookup (Hit) Performance'),
        ('lookup_miss_ops_per_sec', 'Lookup (Miss) Performance'),
        ('delete_ops_per_sec', 'Delete Performance')
    ]
    
    # Plot for each capacity and operation type
    for i, capacity in enumerate(capacities):
        for j, (op_key, op_title) in enumerate(operations):
            ax = axes[i][j]
            ax.set_title(f"{op_title} (capacity={capacity})")
            ax.set_xlabel("Load Factor")
            ax.set_ylabel("Operations per Second")
            
            # Data for current capacity and operation
            for impl in implementations:
                x_vals = []
                y_vals = []
                
                for (cap, lf), metrics in results[impl].items():
                    if cap == capacity:
                        x_vals.append(lf)
                        y_vals.append(metrics[op_key])
                
                # Sort by load factor
                points = sorted(zip(x_vals, y_vals))
                x_vals = [p[0] for p in points]
                y_vals = [p[1] for p in points]
                
                ax.plot(x_vals, y_vals, marker='o', label=impl)
            
            ax.legend()
            ax.grid(True)
    
    plt.tight_layout(rect=[0, 0, 1, 0.96])  # Adjust for suptitle
    
    if save_filename:
        plt.savefig(save_filename)
        print(f"Plot saved to {save_filename}")
    
    plt.show()


def main():
    """Run the benchmark."""
    # Table classes to benchmark
    table_classes = [ElasticHashTable, FunnelHashTable, DictWrapper]
    
    # Test parameters
    capacities = [10000]
    load_factors = [0.5, 0.7, 0.8, 0.9]
    operations_per_test = 5000
    
    # Run benchmarks
    print("Starting benchmarks...")
    results = run_benchmark(table_classes, capacities, load_factors, operations_per_test)
    
    # Print results
    print_results(results)
    
    # Save results
    csv_filename = "hash_table_benchmark_results.csv"
    save_results_to_csv(results, csv_filename)
    print(f"\nDetailed results saved to {csv_filename}")
    
    # Plot results if matplotlib is available
    if PLOTTING_AVAILABLE:
        try:
            plot_results(results, "hash_table_benchmark_results.png")
        except Exception as e:
            print(f"Error creating plot: {e}")
    else:
        print("\nSkipping plot generation since matplotlib is not installed.")
        print("Install matplotlib for visualizations: pip install matplotlib")


if __name__ == "__main__":
    main()
