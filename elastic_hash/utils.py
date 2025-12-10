"""
Utility classes and functions for elastic_hash.
"""

class Tombstone:
    """
    Sentinel class used to mark removed slots in hash tables.
    This allows probe sequences to continue past removed elements.
    """
    def __repr__(self):
        return "<Tombstone>"

# Singleton instance
TOMBSTONE = Tombstone()
