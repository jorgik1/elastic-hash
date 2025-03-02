"""
Hash functions for the elastic and funnel hash table implementations.
"""
import hashlib
from typing import Any, Tuple


def murmur_hash(key: Any, seed: int = 0) -> int:
    """
    A MurmurHash-inspired hash function with good distribution properties.
    
    Args:
        key: The key to hash
        seed: A seed value to generate different hash values for the same key
        
    Returns:
        An integer hash value
    """
    # Convert key to bytes if it's not already
    if isinstance(key, str):
        key_bytes = key.encode('utf-8')
    elif isinstance(key, bytes):
        key_bytes = key
    else:
        key_bytes = str(key).encode('utf-8')
    
    # Add the seed to the key
    key_with_seed = key_bytes + seed.to_bytes(4, byteorder='little')
    
    # Use hashlib for a high-quality hash
    hash_obj = hashlib.md5(key_with_seed)
    hash_bytes = hash_obj.digest()
    
    # Convert to integer
    hash_int = int.from_bytes(hash_bytes[:8], byteorder='little')
    return hash_int


def two_dimensional_hash(key: Any, i: int, j: int, max_value: int) -> int:
    """
    Generate a hash value for a two-dimensional hash function.
    
    Args:
        key: The key to hash
        i: The first dimension (typically subarray index)
        j: The second dimension (typically position within subarray)
        max_value: The maximum hash value (typically subarray size)
        
    Returns:
        An integer hash value in range [0, max_value-1]
    """
    # Use different seeds for different dimensions
    seed = (i * 31337 + j * 17 + 12345) & 0xFFFFFFFF
    hash_val = murmur_hash(key, seed)
    return hash_val % max_value


def hash_sequence(key: Any, length: int, seed: int = 0) -> Tuple[int, ...]:
    """
    Generate a sequence of hash values for a key.
    
    Args:
        key: The key to hash
        length: The number of hash values to generate
        seed: A seed value for the hash function
        
    Returns:
        A tuple of hash values
    """
    return tuple(murmur_hash(key, seed + i) for i in range(length))
