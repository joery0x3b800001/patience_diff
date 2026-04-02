"""Tests for merge diff functionality - Comprehensive suite."""

import sys
import os

# Add src to path
src_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'src')
if src_path not in sys.path:
    sys.path.insert(0, src_path)

import patience_diff


def test_merge_diff():
    """Test basic merge diff operations."""
    prev = ["line1", "line2", "line3"]
    next = ["line1", "line2_modified", "line3"]
    
    hunks = patience_diff.get_hunks(prev, next)
    assert hunks is not None, "Should generate hunks"
    print("✓ test_merge_diff passed")


def test_simple_insert():
    """Test simple line insertion."""
    prev = ["line1", "line2", "line3"]
    next = ["line1", "line1.5", "line2", "line3"]
    
    hunks = patience_diff.get_hunks(prev, next)
    blocks = patience_diff.get_matching_blocks(lambda x: x, prev, next)
    assert len(blocks) >= 1, "Should find matching blocks"
    print(f"✓ test_simple_insert passed - {len(blocks)} blocks")


def test_simple_delete():
    """Test simple line deletion."""
    prev = ["line1", "line1.5", "line2", "line3"]
    next = ["line1", "line2", "line3"]
    
    blocks = patience_diff.get_matching_blocks(lambda x: x, prev, next)
    assert len(blocks) >= 1, "Should find matching blocks"
    print(f"✓ test_simple_delete passed - {len(blocks)} blocks")


def test_multiple_changes():
    """Test multiple insertions and deletions."""
    prev = ["a", "b", "c", "d", "e"]
    next = ["a", "x", "c", "y", "e", "z"]
    
    hunks = patience_diff.get_hunks(prev, next)
    assert hunks is not None, "Should handle multiple changes"
    print(f"✓ test_multiple_changes passed")


def test_complete_replacement():
    """Test replacing one block with another."""
    prev = ["old1", "old2", "old3"]
    next = ["new1", "new2", "new3"]
    
    blocks = patience_diff.get_matching_blocks(lambda x: x, prev, next)
    ratio = patience_diff.match_ratio(prev, next)
    assert ratio < 0.3, "Should have low match ratio for complete replacement"
    print(f"✓ test_complete_replacement passed - Match ratio: {ratio:.2%}")


def test_reordering():
    """Test line reordering."""
    prev = ["a", "b", "c"]
    next = ["c", "a", "b"]
    
    blocks = patience_diff.get_matching_blocks(lambda x: x, prev, next)
    # Should still find individual matches even though order changed
    assert len(blocks) >= 2, "Should find some matching blocks"
    print(f"✓ test_reordering passed - {len(blocks)} blocks")


def test_mixed_operations():
    """Test mixed insert, delete, modify operations."""
    prev = ["func1()", "param=5", "return x", "func2()"]
    next = ["func1()", "param=10", "debug_print()", "return x", "func2()"]
    
    hunks = patience_diff.get_hunks(prev, next)
    assert hunks is not None, "Should handle mixed operations"
    print(f"✓ test_mixed_operations passed - {len(hunks)} hunks")


def test_matches_extraction():
    """Test extracting individual match pairs."""
    prev = ["line1", "line2", "line3"]
    next = ["line1", "line2", "line3"]
    
    matches = patience_diff.matches(prev, next)
    assert len(matches) == 3, f"Expected 3 matches, got {len(matches)}"
    print(f"✓ test_matches_extraction passed - Found {len(matches)} matches")


def test_match_ratio_full():
    """Test match ratio calculation."""
    prev = ["a", "b", "c"]
    next = ["a", "b", "c"]
    
    ratio = patience_diff.match_ratio(prev, next)
    assert ratio == 1.0, f"Identical sequences should have 100% ratio"
    print(f"✓ test_match_ratio_full passed - Ratio: {ratio:.2%}")


def test_match_ratio_partial():
    """Test partial match ratio."""
    prev = ["a", "b", "c", "d", "e", "f"]
    next = ["a", "b", "c", "x", "y", "z"]
    
    ratio = patience_diff.match_ratio(prev, next)
    assert 0.0 < ratio < 1.0, "Partial match should be between 0 and 1"
    print(f"✓ test_match_ratio_partial passed - Ratio: {ratio:.2%}")


if __name__ == "__main__":
    print("=" * 60)
    print("MERGE DIFF TESTS")
    print("=" * 60)
    
    test_merge_diff()
    test_simple_insert()
    test_simple_delete()
    test_multiple_changes()
    test_complete_replacement()
    test_reordering()
    test_mixed_operations()
    test_matches_extraction()
    test_match_ratio_full()
    test_match_ratio_partial()
    
    print("=" * 60)
    print("All merge_diff tests passed!")
    print("=" * 60)
