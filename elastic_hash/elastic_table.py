"""
Implementation of Elastic Hashing, a non-greedy open addressing hash table.

Based on the paper "Optimal Bounds for Open Addressing Without Reordering"
by Martín Farach-Colton, Andrew Krapivin, and William Kuszmaul.
"""
import math
from typing import Any, List, Optional, Tuple, Dict, Iterator, Generic, TypeVar

from .hash_functions import two_dimensional_hash

K = TypeVar('K')  # Key type
V = TypeVar('V')  # Value type

class ElasticHashTable(Generic[K, V]):
    """
    An implementation of Elastic Hashing, which achieves O(1) amortized expected 
    probe complexity and O(log 1/δ) worst-case expected probe complexity without 
    reordering elements.
    """
    
    def __init__(self, capacity: int, delta: float = 0.1):
        """
        Initialize an elastic hash table.
        
        Args:
            capacity: The total capacity of the hash table
            delta: The fraction of empty slots to maintain (default 0.1)
        """
        if not (0 < delta < 1):
            raise ValueError("delta must be between 0 and 1")
        
        self.capacity = capacity
        self.delta = delta
        self.size = 0
        
        # Calculate number of subarrays and their sizes
        self.num_subarrays = math.ceil(math.log2(capacity)) + 1
        self.subarrays: List[List[Optional[Tuple[K, V]]]] = []
        
        # Initialize subarrays with decreasing sizes
        # Ensure we have enough total slots to fit the capacity
        total_slots = 0
        remaining = capacity
        current_size = capacity // 2
        
        for i in range(self.num_subarrays):
            if current_size < 1 or remaining <= 0:
                break
            
            # Ensure we don't exceed the total capacity
            actual_size = min(current_size, remaining)
            self.subarrays.append([None] * actual_size)
            
            total_slots += actual_size
            remaining -= actual_size
            current_size = current_size // 2
            
        # Ensure we have exactly capacity slots
        if total_slots < capacity:
            # Add one more array if needed
            extra_needed = capacity - total_slots
            self.subarrays.append([None] * extra_needed)
        
        # Batch tracking variables
        self.current_batch = 0
        self.batch_targets = self._calculate_batch_targets()
    
    def _calculate_batch_targets(self) -> List[Dict[str, int]]:
        """
        Calculate target fill levels for each batch.
        
        Returns:
            A list of dictionaries containing target fill levels for each subarray
        """
        targets = []
        
        # Batch 0: Fill subarray 0 to 75%
        batch0 = {
            "end_idx": 0,  # Last subarray to be filled in this batch
            "targets": {0: int(0.75 * len(self.subarrays[0]))}
        }
        targets.append(batch0)
        
        # Subsequent batches
        for i in range(1, len(self.subarrays)):
            if i >= len(self.subarrays):
                break
                
            # Target is to fill subarray i-1 to (1-delta/2) and subarray i to 75%
            target_prev = int((1 - self.delta/2) * len(self.subarrays[i-1]))
            target_curr = int(0.75 * len(self.subarrays[i])) if i < len(self.subarrays) else 0
            
            batch = {
                "end_idx": i,
                "targets": {
                    i-1: target_prev,
                    i: target_curr
                }
            }
            targets.append(batch)
        
        return targets
    
    def _get_free_slots_ratio(self, subarray_idx: int) -> float:
        """
        Calculate the ratio of free slots in a subarray.
        
        Args:
            subarray_idx: Index of the subarray
            
        Returns:
            Ratio of free slots (0.0 = full, 1.0 = empty)
        """
        if subarray_idx >= len(self.subarrays):
            return 0.0
            
        subarray = self.subarrays[subarray_idx]
        filled = sum(1 for slot in subarray if slot is not None)
        return (len(subarray) - filled) / len(subarray)
    
    def _calculate_probe_limit(self, epsilon: float) -> int:
        """
        Calculate the probe limit based on the free slots ratio.
        
        Args:
            epsilon: The ratio of free slots
            
        Returns:
            The number of probes to attempt
        """
        if epsilon <= self.delta/2:
            return 0
        
        # c * min(log^2(1/epsilon), log(1/delta))
        c = 32  # Constant factor, can be tuned
        log_factor = min(math.log2(1/epsilon)**2, math.log2(1/self.delta))
        return max(1, int(c * log_factor))
    
    def _get_insertion_arrays(self) -> Tuple[int, int]:
        """
        Determine which subarrays to use for the current insertion.
        
        Returns:
            A tuple of (primary_array_idx, secondary_array_idx)
        """
        batch_info = self.batch_targets[min(self.current_batch, len(self.batch_targets)-1)]
        end_idx = batch_info["end_idx"]
        
        # Primary array is the one we're currently filling to (1-delta/2)
        primary_idx = end_idx
        
        # Secondary array is the next one we're filling to 75%
        secondary_idx = end_idx + 1
        
        # Handle edge cases
        if secondary_idx >= len(self.subarrays):
            secondary_idx = primary_idx
        
        return primary_idx, secondary_idx
    
    def _update_batch_if_needed(self) -> None:
        """Check if we need to move to the next batch and update if necessary."""
        if self.current_batch >= len(self.batch_targets):
            return
            
        batch_info = self.batch_targets[self.current_batch]
        targets = batch_info["targets"]
        
        # Check if all targets for the current batch are met
        all_targets_met = True
        for idx, target in targets.items():
            if idx >= len(self.subarrays):
                continue
                
            filled = sum(1 for slot in self.subarrays[idx] if slot is not None)
            if filled < target:
                all_targets_met = False
                break
        
        if all_targets_met:
            self.current_batch += 1
    
    def insert(self, key: K, value: V) -> None:
        """
        Insert a key-value pair into the hash table.
        
        Args:
            key: The key to insert
            value: The value associated with the key
            
        Raises:
            ValueError: If the key already exists
            OverflowError: If the table is full
        """
        # For consistent testing, always check for capacity
        # We need to reliably throw OverflowError when the table is full
        if self.size >= self.capacity:
            raise OverflowError("Hash table is full")
        
        # Check if key already exists
        existing_value = self.get(key)
        if existing_value is not None:
            raise ValueError(f"Key '{key}' already exists")
        
        # Determine which subarrays to use
        primary_idx, secondary_idx = self._get_insertion_arrays()
        
        # Try primary array with limited probes if it's not too full
        epsilon1 = self._get_free_slots_ratio(primary_idx)
        probe_limit = self._calculate_probe_limit(epsilon1)
        
        if probe_limit > 0:
            for j in range(probe_limit):
                pos = two_dimensional_hash(key, primary_idx, j, len(self.subarrays[primary_idx]))
                if self.subarrays[primary_idx][pos] is None:
                    self.subarrays[primary_idx][pos] = (key, value)
                    self.size += 1
                    self._update_batch_if_needed()
                    return
        
        # Try secondary array with unlimited probes
        if secondary_idx < len(self.subarrays):
            j = 0
            while True:
                if j >= len(self.subarrays[secondary_idx]):
                    break  # Safeguard against infinite loops
                
                pos = two_dimensional_hash(key, secondary_idx, j, len(self.subarrays[secondary_idx]))
                if self.subarrays[secondary_idx][pos] is None:
                    self.subarrays[secondary_idx][pos] = (key, value)
                    self.size += 1
                    self._update_batch_if_needed()
                    return
                j += 1
        
        # If we reach here, we couldn't find a slot despite the table not being full
        # This should be very rare but we handle it by searching all arrays
        for i, subarray in enumerate(self.subarrays):
            for j in range(len(subarray)):
                pos = two_dimensional_hash(key, i, j, len(subarray))
                if subarray[pos] is None:
                    subarray[pos] = (key, value)
                    self.size += 1
                    self._update_batch_if_needed()
                    return
        
        # This happens when all slots are actually filled despite capacity check
        raise OverflowError("Hash table is full")
    
    def get(self, key: K) -> Optional[V]:
        """
        Retrieve the value associated with the key.
        
        Args:
            key: The key to look up
            
        Returns:
            The associated value, or None if the key doesn't exist
        """
        # Search each subarray
        for i, subarray in enumerate(self.subarrays):
            j = 0
            while j < len(subarray):
                pos = two_dimensional_hash(key, i, j, len(subarray))
                slot = subarray[pos]
                
                if slot is None:
                    # In a properly implemented hash table, we can stop
                    # searching this subarray once we find an empty slot
                    break
                    
                if slot[0] == key:
                    return slot[1]
                
                j += 1
        
        return None
    
    def remove(self, key: K) -> bool:
        """
        Remove a key and its associated value from the hash table.
        
        Note: In this implementation, we mark slots as None when removed,
        which can lead to early termination of searches. A more sophisticated
        implementation would use tombstones or other techniques.
        
        Args:
            key: The key to remove
            
        Returns:
            True if the key was found and removed, False otherwise
        """
        # Search each subarray
        for i, subarray in enumerate(self.subarrays):
            j = 0
            while j < len(subarray):
                pos = two_dimensional_hash(key, i, j, len(subarray))
                slot = subarray[pos]
                
                if slot is None:
                    # Empty slot, key not in this subarray
                    break
                    
                if slot[0] == key:
                    subarray[pos] = None
                    self.size -= 1
                    return True
                
                j += 1
        
        return False
    
    def __contains__(self, key: K) -> bool:
        """
        Check if a key exists in the hash table.
        
        Args:
            key: The key to check
            
        Returns:
            True if the key exists, False otherwise
        """
        return self.get(key) is not None
    
    def __len__(self) -> int:
        """
        Get the number of key-value pairs in the hash table.
        
        Returns:
            The number of key-value pairs
        """
        return self.size
    
    def __iter__(self) -> Iterator[Tuple[K, V]]:
        """
        Iterate over all key-value pairs in the hash table.
        
        Returns:
            An iterator over all key-value pairs
        """
        for subarray in self.subarrays:
            for slot in subarray:
                if slot is not None:
                    yield slot
    
    def clear(self) -> None:
        """Remove all key-value pairs from the hash table."""
        for i, subarray in enumerate(self.subarrays):
            for j in range(len(subarray)):
                subarray[j] = None
        
        self.size = 0
        self.current_batch = 0
