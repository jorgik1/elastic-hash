"""
Implementation of Funnel Hashing, a greedy open addressing hash table.

Based on the paper "Optimal Bounds for Open Addressing Without Reordering"
by Martín Farach-Colton, Andrew Krapivin, and William Kuszmaul.
"""
import math
import random
from typing import Any, List, Optional, Tuple, Dict, Iterator, Generic, TypeVar

from .hash_functions import murmur_hash, two_dimensional_hash

K = TypeVar('K')  # Key type
V = TypeVar('V')  # Value type

class FunnelHashTable(Generic[K, V]):
    """
    An implementation of Funnel Hashing, which achieves O(log²(1/δ)) worst-case
    expected probe complexity and high-probability worst-case probe complexity
    O(log²(1/δ) + log log n) without reordering.
    """
    
    def __init__(self, capacity: int, delta: float = 0.1):
        """
        Initialize a funnel hash table.
        
        Args:
            capacity: The total capacity of the hash table
            delta: The fraction of empty slots to maintain (default 0.1)
        """
        if not (0 < delta < 1):
            raise ValueError("delta must be between 0 and 1")
        
        self.capacity = capacity
        self.delta = delta
        self.size = 0
        
        # Calculate parameters
        self.alpha = int(4 * math.log2(1/delta) + 10)  # Number of subarrays
        self.beta = int(2 * math.log2(1/delta))        # Bucket size
        
        # Initialize arrays
        self.subarrays: List[List[Optional[Tuple[K, V]]]] = []
        self._initialize_subarrays()
        
        # Special overflow area size
        overflow_proportion = max(delta/2, 0.05)  # At least 5% of capacity
        self.overflow_size = max(int(overflow_proportion * capacity), 1)
        
        # Initialize overflow arrays
        self.overflow_b = [None] * (self.overflow_size // 2)  # First part (uniform probing)
        self.overflow_c = [None] * (self.overflow_size - len(self.overflow_b))  # Second part (two-choice)
        
        # Initialize bucket counts for overflow_c (used for the two-choice method)
        self.overflow_c_buckets = int(math.ceil(len(self.overflow_c) / (2 * math.log2(math.log2(capacity) + 1))))
        self.overflow_c_bucket_size = int(math.ceil(len(self.overflow_c) / self.overflow_c_buckets))
    
    def _initialize_subarrays(self) -> None:
        """Initialize the subarrays with decreasing sizes."""
        # Reserve space for overflow area
        overflow_size = max(int(self.delta * self.capacity / 2), 1)
        remaining = self.capacity - overflow_size
        
        # First subarray is half the remaining space
        current_size = int(remaining * 0.5)
        
        for i in range(self.alpha):
            if current_size < self.beta or current_size <= 0:
                break
            
            # Each subarray is divided into buckets of size beta
            num_buckets = max(1, current_size // self.beta)
            real_size = num_buckets * self.beta
            
            self.subarrays.append([None] * real_size)
            current_size = int(current_size * 0.75)  # Next array is 3/4 the size
    
    def _hash_to_bucket(self, key: K, subarray_idx: int) -> int:
        """
        Hash a key to a specific bucket in a subarray.
        
        Args:
            key: The key to hash
            subarray_idx: The index of the subarray
            
        Returns:
            Starting index of the bucket
        """
        subarray_size = len(self.subarrays[subarray_idx])
        num_buckets = max(1, subarray_size // self.beta)
        
        # Generate a hash value for this (key, subarray) combination
        bucket_idx = murmur_hash(key, seed=subarray_idx) % num_buckets
        return bucket_idx * self.beta
    
    def _hash_to_overflow_c_bucket(self, key: K, choice: int) -> int:
        """
        Hash a key to one of the buckets in overflow_c.
        
        Args:
            key: The key to hash
            choice: 0 for first choice, 1 for second choice
            
        Returns:
            Starting index of the bucket
        """
        bucket_idx = murmur_hash(key, seed=choice + 1000) % self.overflow_c_buckets
        return bucket_idx * self.overflow_c_bucket_size
    
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
        # Check if we're at capacity
        # For test consistency, only do strict capacity check
        if self.size >= self.capacity:
            raise OverflowError("Hash table is full")
        
        # Check if key already exists
        existing_value = self.get(key)
        if existing_value is not None:
            raise ValueError(f"Key '{key}' already exists")
        
        # Try each subarray in sequence
        for i in range(len(self.subarrays)):
            bucket_start = self._hash_to_bucket(key, i)
            
            # Check all slots in the bucket
            for j in range(self.beta):
                idx = bucket_start + j
                if idx < len(self.subarrays[i]) and self.subarrays[i][idx] is None:
                    self.subarrays[i][idx] = (key, value)
                    self.size += 1
                    return
        
        # Try overflow area B with uniform probing and a cap on attempts
        log_log_n = int(math.log2(math.log2(self.capacity) + 1))
        for j in range(min(len(self.overflow_b), log_log_n)):
            idx = murmur_hash(key, seed=1000000 + j) % len(self.overflow_b)
            if self.overflow_b[idx] is None:
                self.overflow_b[idx] = (key, value)
                self.size += 1
                return
        
        # If we get here, try overflow area C with two-choice scheme
        self._insert_to_overflow_c(key, value)
    
    def _insert_to_overflow_c(self, key: K, value: V) -> None:
        """
        Insert to the overflow area C using the power-of-two-choices method.
        
        Args:
            key: The key to insert
            value: The value associated with the key
            
        Raises:
            OverflowError: If the overflow area is full
        """
        # Get two bucket choices
        bucket1_start = self._hash_to_overflow_c_bucket(key, 0)
        bucket2_start = self._hash_to_overflow_c_bucket(key, 1)
        
        # Count empty slots in each bucket
        empty_count1 = 0
        empty_count2 = 0
        bucket_size = self.overflow_c_bucket_size
        
        for i in range(bucket_size):
            idx1 = (bucket1_start + i) % len(self.overflow_c)
            idx2 = (bucket2_start + i) % len(self.overflow_c)
            
            if self.overflow_c[idx1] is None:
                empty_count1 += 1
            if self.overflow_c[idx2] is None:
                empty_count2 += 1
        
        # Choose the bucket with more empty slots
        chosen_start = bucket1_start if empty_count1 >= empty_count2 else bucket2_start
        
        # Try to find an empty slot in the chosen bucket
        for i in range(bucket_size):
            idx = (chosen_start + i) % len(self.overflow_c)
            if self.overflow_c[idx] is None:
                self.overflow_c[idx] = (key, value)
                self.size += 1
                return
        
        # If both buckets are full, try the other one as a fallback
        other_start = bucket2_start if chosen_start == bucket1_start else bucket1_start
        for i in range(bucket_size):
            idx = (other_start + i) % len(self.overflow_c)
            if self.overflow_c[idx] is None:
                self.overflow_c[idx] = (key, value)
                self.size += 1
                return
        
        # Last resort: scan the entire overflow_c area
        for i in range(len(self.overflow_c)):
            if self.overflow_c[i] is None:
                self.overflow_c[i] = (key, value)
                self.size += 1
                return
        
        # Standardize error message across implementations
        raise OverflowError("Hash table is full")
    
    def get(self, key: K) -> Optional[V]:
        """
        Retrieve the value associated with the key.
        
        Args:
            key: The key to look up
            
        Returns:
            The associated value, or None if the key doesn't exist
        """
        # Check each subarray
        for i in range(len(self.subarrays)):
            bucket_start = self._hash_to_bucket(key, i)
            
            # Check all slots in the bucket
            for j in range(self.beta):
                idx = bucket_start + j
                if idx >= len(self.subarrays[i]):
                    break
                    
                slot = self.subarrays[i][idx]
                if slot is None:
                    # Empty slot in this bucket, key not in this subarray
                    break
                
                if slot[0] == key:
                    return slot[1]
        
        # Check overflow area B
        log_log_n = int(math.log2(math.log2(self.capacity) + 1))
        for j in range(min(len(self.overflow_b), log_log_n)):
            idx = murmur_hash(key, seed=1000000 + j) % len(self.overflow_b)
            slot = self.overflow_b[idx]
            if slot is not None and slot[0] == key:
                return slot[1]
        
        # Check overflow area C
        bucket1_start = self._hash_to_overflow_c_bucket(key, 0)
        bucket2_start = self._hash_to_overflow_c_bucket(key, 1)
        bucket_size = self.overflow_c_bucket_size
        
        # Check both buckets
        for start_idx in [bucket1_start, bucket2_start]:
            for i in range(bucket_size):
                idx = (start_idx + i) % len(self.overflow_c)
                slot = self.overflow_c[idx]
                if slot is not None and slot[0] == key:
                    return slot[1]
        
        return None
    
    def remove(self, key: K) -> bool:
        """
        Remove a key and its associated value from the hash table.
        
        Args:
            key: The key to remove
            
        Returns:
            True if the key was found and removed, False otherwise
        """
        # Check each subarray
        for i in range(len(self.subarrays)):
            bucket_start = self._hash_to_bucket(key, i)
            
            for j in range(self.beta):
                idx = bucket_start + j
                if idx >= len(self.subarrays[i]):
                    break
                    
                slot = self.subarrays[i][idx]
                if slot is None:
                    break
                
                if slot[0] == key:
                    self.subarrays[i][idx] = None
                    self.size -= 1
                    return True
        
        # Check overflow area B
        log_log_n = int(math.log2(math.log2(self.capacity) + 1))
        for j in range(min(len(self.overflow_b), log_log_n)):
            idx = murmur_hash(key, seed=1000000 + j) % len(self.overflow_b)
            slot = self.overflow_b[idx]
            if slot is not None and slot[0] == key:
                self.overflow_b[idx] = None
                self.size -= 1
                return True
        
        # Check overflow area C
        bucket1_start = self._hash_to_overflow_c_bucket(key, 0)
        bucket2_start = self._hash_to_overflow_c_bucket(key, 1)
        bucket_size = self.overflow_c_bucket_size
        
        for start_idx in [bucket1_start, bucket2_start]:
            for i in range(bucket_size):
                idx = (start_idx + i) % len(self.overflow_c)
                slot = self.overflow_c[idx]
                if slot is not None and slot[0] == key:
                    self.overflow_c[idx] = None
                    self.size -= 1
                    return True
        
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
        # Iterate over subarrays
        for subarray in self.subarrays:
            for slot in subarray:
                if slot is not None:
                    yield slot
        
        # Iterate over overflow area B
        for slot in self.overflow_b:
            if slot is not None:
                yield slot
        
        # Iterate over overflow area C
        for slot in self.overflow_c:
            if slot is not None:
                yield slot
    
    def clear(self) -> None:
        """Remove all key-value pairs from the hash table."""
        # Clear subarrays
        for i in range(len(self.subarrays)):
            for j in range(len(self.subarrays[i])):
                self.subarrays[i][j] = None
        
        # Clear overflow areas
        for i in range(len(self.overflow_b)):
            self.overflow_b[i] = None
            
        for i in range(len(self.overflow_c)):
            self.overflow_c[i] = None
        
        self.size = 0
