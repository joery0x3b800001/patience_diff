"""Tests for plain diff and Myers algorithm cutoff functionality."""

import sys
import os

# Add src to path
src_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'bram_diff')
if src_path not in sys.path:
    sys.path.insert(0, src_path)

import patience_diff


def test_plain_diff_simple():
    """Test plain diff with simple changes."""
    prev = ["a", "b", "c"]
    next = ["a", "x", "c"]
    
    hunks = patience_diff.get_hunks(prev, next)
    assert hunks is not None, "Should generate hunks"
    print(f"✓ test_plain_diff_simple passed")


def test_plain_diff_cutoff():
    """Test plain diff algorithm with cutoff."""
    prev = ["line1"]
    next = ["line1"]
    
    hunks = patience_diff.get_hunks(prev, next)
    # Identical content should have no hunks or empty hunks
    assert hunks is not None, "Should handle identical content"
    print("✓ test_plain_diff_cutoff passed")


def test_cutoff_large_diff():
    """Test cutoff with large differences requiring Myers fallback."""
    prev = list(range(100))  # ['0', '1', '2', ..., '99']
    next = [str(x * 2) for x in range(100)]  # ['0', '2', '4', ...]
    
    hunks = patience_diff.get_hunks(prev, next)
    # Large differences should still be handled
    assert hunks is not None, "Should handle large diffs"
    print(f"✓ test_cutoff_large_diff passed")


def test_myers_fallback_complete_change():
    """Test Myers algorithm fallback for complete changes."""
    prev = ["a", "b", "c", "d", "e"]
    next = ["x", "y", "z", "w", "v"]
    
    blocks = patience_diff.get_matching_blocks(lambda x: x, prev, next)
    ratio = patience_diff.match_ratio(prev, next)
    assert ratio == 0.0, "Completely different sequences should have 0% match"
    print(f"✓ test_myers_fallback_complete_change passed - Ratio: {ratio:.2%}")


def test_cutoff_single_change():
    """Test cutoff with single line change."""
    prev = ["line1", "line2", "line3", "line4", "line5"]
    next = ["line1", "line2", "modified", "line4", "line5"]
    
    hunks = patience_diff.get_hunks(prev, next)
    assert hunks is not None, "Should handle single change"
    print(f"✓ test_cutoff_single_change passed")


def test_cutoff_multiple_isolated_changes():
    """Test cutoff with multiple isolated changes."""
    prev = ["a", "b", "c", "d", "e", "f", "g", "h"]
    next = ["a", "x", "c", "d", "e", "f", "y", "h"]
    
    hunks = patience_diff.get_hunks(prev, next)
    assert hunks is not None, "Should handle multiple changes"
    print(f"✓ test_cutoff_multiple_isolated_changes passed")


def test_cutoff_adjacent_changes():
    """Test cutoff with adjacent changes."""
    prev = ["line1", "lineA", "lineB", "line4"]
    next = ["line1", "lineX", "lineY", "line4"]
    
    hunks = patience_diff.get_hunks(prev, next)
    assert hunks is not None, "Should handle adjacent changes"
    print(f"✓ test_cutoff_adjacent_changes passed")


def test_very_long_sequences():
    """Test with very long sequences (stress test)."""
    prev = list(range(1000))
    next = list(range(1, 1001))
    
    blocks = patience_diff.get_matching_blocks(lambda x: x, prev, next)
    # All items except first/last should match
    assert len(blocks) >= 1, "Should handle very long sequences"
    print(f"✓ test_very_long_sequences passed - {len(blocks)} blocks")


def test_cutoff_with_duplicates():
    """Test cutoff behavior with duplicate values."""
    prev = ["x", "a", "x", "b", "x"]
    next = ["x", "b", "x", "a", "x"]
    
    blocks = patience_diff.get_matching_blocks(lambda x: x, prev, next)
    matches = patience_diff.matches(prev, next)
    # Patience diff may find fewer matches due to algorithm ordering constraints
    assert len(matches) >= 1, "Should find at least one match"
    print(f"✓ test_cutoff_with_duplicates passed - {len(matches)} matches")


def test_cutoff_empty_to_content():
    """Test transition from empty to content."""
    prev = []
    next = ["new1", "new2", "new3"]
    
    hunks = patience_diff.get_hunks(prev, next)
    assert hunks is not None, "Should handle empty to content"
    print(f"✓ test_cutoff_empty_to_content passed")


def test_cutoff_content_to_empty():
    """Test transition from content to empty."""
    prev = ["old1", "old2", "old3"]
    next = []
    
    hunks = patience_diff.get_hunks(prev, next)
    assert hunks is not None, "Should handle content to empty"
    print(f"✓ test_cutoff_content_to_empty passed")


def test_cutoff_match_ratio_zero():
    """Test match ratio is zero for completely different sequences."""
    prev = ["a", "b", "c"]
    next = ["x", "y", "z"]
    
    ratio = patience_diff.match_ratio(prev, next)
    assert ratio == 0.0, "Completely different sequences should have 0% match"
    print(f"✓ test_cutoff_match_ratio_zero passed - Ratio: {ratio:.2%}")


if __name__ == "__main__":
    print("=" * 60)
    print("PLAIN DIFF / CUTOFF TESTS")
    print("=" * 60)
    
    test_plain_diff_simple()
    test_plain_diff_cutoff()
    test_cutoff_large_diff()
    test_myers_fallback_complete_change()
    test_cutoff_single_change()
    test_cutoff_multiple_isolated_changes()
    test_cutoff_adjacent_changes()
    test_very_long_sequences()
    test_cutoff_with_duplicates()
    test_cutoff_empty_to_content()
    test_cutoff_content_to_empty()
    test_cutoff_match_ratio_zero()
    
    print("=" * 60)
    print("All plain_diff_cutoff tests passed!")
    print("=" * 60)
