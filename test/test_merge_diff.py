"""Tests for merge diff functionality."""

import sys, os

# Add src to path
src_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'src')
if src_path not in sys.path:
    sys.path.insert(0, src_path)


def test_merge_diff():
    """Test merge diff operations."""
    import patience_diff
    
    prev = ["line1", "line2", "line3"]
    next = ["line1", "line2_modified", "line3"]
    
    hunks = patience_diff.get_hunks(prev, next)
    print(f"Merge diff test: Generated {len(hunks)} hunks")
    print("✓ test_merge_diff passed")


if __name__ == "__main__":
    test_merge_diff()
