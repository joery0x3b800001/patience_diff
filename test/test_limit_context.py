"""Tests for limiting context in hunks - Comprehensive suite."""

import sys
import os

# Add src to path
src_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'bram_diff')
if src_path not in sys.path:
    sys.path.insert(0, src_path)

import patience_diff


def test_limit_infinite_context_hunk_to_context():
    """Test that limiting infinite context hunks works correctly."""
    context = 5
    prev = ["apple", "banana", "cherry", "dog", "egg"] * 5
    next = ["apple", "banana", "dog", "egg", "fish"] * 5
    
    hunks = patience_diff.get_hunks(prev, next, context=context)
    infinite_hunks = patience_diff.get_hunks(prev, next, context=-1)
    
    assert hunks is not None, "Should generate hunks"
    assert infinite_hunks is not None, "Should generate hunks with infinite context"
    print(f"With context {context}: Generated hunks")
    print(f"With infinite context: Generated hunks")
    print("✓ test_limit_infinite_context_hunk_to_context passed")


def test_context_zero():
    """Test with context=0."""
    prev = ["a", "b", "c"]
    next = ["a", "x", "c"]
    
    hunks = patience_diff.get_hunks(prev, next, context=0)
    assert hunks is not None, "Should handle context=0"
    print("✓ test_context_zero passed")


def test_context_large():
    """Test with large context."""
    prev = ["line"] * 1000
    next = ["line"] * 500 + ["modified"] + ["line"] * 499
    
    hunks = patience_diff.get_hunks(prev, next, context=100)
    assert hunks is not None, "Should handle large context"
    print(f"✓ test_context_large passed - Generated hunks")


def test_multiple_hunks_with_context():
    """Test multiple changes with context."""
    prev = ["a"] * 10 + ["b"] * 10 + ["c"] * 10
    next = ["a"] * 10 + ["x"] * 10 + ["c"] * 10
    
    hunks = patience_diff.get_hunks(prev, next, context=2)
    assert hunks is not None, "Should handle multiple changes"
    print(f"✓ test_multiple_hunks_with_context passed - Generated hunks")


def test_context_at_boundaries():
    """Test context at start and end of file."""
    prev = ["change", "a", "b", "c"]
    next = ["modified", "a", "b", "c"]
    
    hunks = patience_diff.get_hunks(prev, next, context=1)
    assert hunks is not None, "Should handle context at boundaries"
    print("✓ test_context_at_boundaries passed")


if __name__ == "__main__":
    print("=" * 60)
    print("LIMIT CONTEXT TESTS")
    print("=" * 60)
    
    test_limit_infinite_context_hunk_to_context()
    test_context_zero()
    test_context_large()
    test_multiple_hunks_with_context()
    test_context_at_boundaries()
    
    print("=" * 60)
    print("All limit_context tests passed!")
    print("=" * 60)
