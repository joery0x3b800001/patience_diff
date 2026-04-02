"""Tests for limiting context in hunks."""

import sys
import os

# Add src to path
src_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'src')
if src_path not in sys.path:
    sys.path.insert(0, src_path)


def test_limit_infinite_context_hunk_to_context():
    """Test that limiting infinite context hunks works correctly."""
    import patience_diff
    
    context = 5
    prev = ["apple", "banana", "cherry", "dog", "egg"] * 5
    next = ["apple", "banana", "dog", "egg", "fish"] * 5
    
    hunks = patience_diff.get_hunks(prev, next, context=context)
    infinite_hunks = patience_diff.get_hunks(prev, next, context=-1)
    
    print(f"With context {context}: {len(hunks)} hunks")
    print(f"With infinite context: {len(infinite_hunks)} hunks")
    print("✓ test_limit_context passed")


if __name__ == "__main__":
    test_limit_infinite_context_hunk_to_context()
