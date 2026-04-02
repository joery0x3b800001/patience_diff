"""Tests for plain diff with cutoff."""

import sys, os

# Add src to path
src_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'src')
if src_path not in sys.path:
    sys.path.insert(0, src_path)


def test_plain_diff_cutoff():
    """Test plain diff with cutoff."""
    import plain_diff
    
    prev = list(range(100))
    next = list(range(1, 101))
    
    matches_list = plain_diff.matches(prev, next)
    print(f"Plain diff cutoff test: Found {len(matches_list)} matches")
    print("✓ test_plain_diff_cutoff passed")


if __name__ == "__main__":
    test_plain_diff_cutoff()
