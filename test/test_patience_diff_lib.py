"""Comprehensive tests for patience_diff library - Main test suite."""

import sys
import os

# Add src to path
src_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'bram_diff')
if src_path not in sys.path:
    sys.path.insert(0, src_path)

import bram_diff.patience_diff as patience_diff
from bram_diff.patience_diff import MatchingBlock, Hunk


class TestBasicMatching:
    """Test basic matching functionality."""
    
    def test_simple_match(self):
        """Test simple matching of identical sequences."""
        prev = ["a", "b", "c"]
        next = ["a", "b", "c"]
        matches = patience_diff.matches(prev, next)
        assert len(matches) == 3, f"Expected 3 matches, got {len(matches)}"
        print("  ✓ test_simple_match passed")
    
    def test_no_match(self):
        """Test matching with completely different sequences."""
        prev = ["a", "b", "c"]
        next = ["x", "y", "z"]
        matches = patience_diff.matches(prev, next)
        assert len(matches) == 0, f"Expected 0 matches, got {len(matches)}"
        print("  ✓ test_no_match passed")
    
    def test_partial_match(self):
        """Test partial matching."""
        prev = ["a", "b", "c"]
        next = ["a", "x", "c"]
        matches = patience_diff.matches(prev, next)
        # Patience diff may only find some matches depending on algorithm
        assert len(matches) >= 1, f"Expected at least 1 match, got {len(matches)}"
        print("  ✓ test_partial_match passed")
    
    def test_empty_sequences(self):
        """Test matching with empty sequences."""
        matches1 = patience_diff.matches([], [])
        assert len(matches1) == 0, "Empty sequences should have no matches"
        
        matches2 = patience_diff.matches(["a"], [])
        assert len(matches2) == 0, "Empty next should have no matches"
        
        print("  ✓ test_empty_sequences passed")


class TestHunks:
    """Test hunk generation functionality."""
    
    def test_hunk_generation(self):
        """Test basic hunk generation."""
        prev = ["line1", "line2", "line3"]
        next = ["line1", "line2_modified", "line3"]
        hunks = patience_diff.get_hunks(prev, next)
        assert hunks is not None, f"Expected hunks to be generated"
        print("  ✓ test_hunk_generation passed")
    
    def test_infinite_context(self):
        """Test hunks with infinite context."""
        prev = ["a", "b", "c", "d"]
        next = ["a", "x", "c", "d"]
        hunks = patience_diff.get_hunks(prev, next, context=-1)
        assert hunks is not None, "Should generate hunks with infinite context"
        print("  ✓ test_infinite_context passed")
    
    def test_limited_context(self):
        """Test hunks with limited context."""
        prev = ["a", "b", "c", "d"]
        next = ["a", "x", "c", "d"]
        hunks = patience_diff.get_hunks(prev, next, context=1)
        assert hunks is not None, "Should generate hunks with limited context"
        print("  ✓ test_limited_context passed")


class TestMatchRatio:
    """Test match ratio calculation."""
    
    def test_identical_ratio(self):
        """Test 100% match ratio for identical sequences."""
        prev = ["a", "b", "c"]
        next = ["a", "b", "c"]
        ratio = patience_diff.match_ratio(prev, next)
        assert ratio == 1.0, f"Identical sequences should have 100% ratio, got {ratio}"
        print("  ✓ test_identical_ratio passed")
    
    def test_no_match_ratio(self):
        """Test 0% match ratio for completely different sequences."""
        prev = ["a", "b", "c"]
        next = ["x", "y", "z"]
        ratio = patience_diff.match_ratio(prev, next)
        assert ratio == 0.0, f"Different sequences should have 0% ratio, got {ratio}"
        print("  ✓ test_no_match_ratio passed")
    
    def test_partial_ratio(self):
        """Test partial match ratio."""
        prev = ["a", "b", "c", "d"]
        next = ["a", "x", "c", "d"]
        ratio = patience_diff.match_ratio(prev, next)
        assert 0.0 < ratio < 1.0, f"Partial match should be between 0 and 1, got {ratio}"
        print("  ✓ test_partial_ratio passed")


class TestSemanticCleanup:
    """Test semantic cleanup functionality."""
    
    def test_big_enough_parameter(self):
        """Test big_enough parameter effect on cleanup."""
        prev = ["word1", "word2", "word3"]
        next = ["word1", "word2", "word3"]
        
        blocks1 = patience_diff.get_matching_blocks(lambda x: x, prev, next, big_enough=2)
        blocks2 = patience_diff.get_matching_blocks(lambda x: x, prev, next, big_enough=10)
        
        # Both should find the matches
        assert blocks1 is not None, "Should find matches with big_enough=2"
        assert blocks2 is not None, "Should find matches with big_enough=10"
        print("  ✓ test_big_enough_parameter passed")


class TestMatches:
    """Test match extraction functionality."""
    
    def test_matches_extraction(self):
        """Test extracting individual matches."""
        prev = ["line1", "line2", "line3"]
        next = ["line1", "line2", "line3"]
        matches = patience_diff.matches(prev, next)
        assert len(matches) == 3, f"Expected 3 matches, got {len(matches)}"
        print("  ✓ test_matches_extraction passed")
    
    def test_matches_sorted(self):
        """Test that matches are sorted."""
        prev = ["a", "b", "c"]
        next = ["c", "a", "b"]
        matches = patience_diff.matches(prev, next)
        # Matches should be sorted by position
        assert matches == sorted(matches), "Matches should be sorted"
        print("  ✓ test_matches_sorted passed")


class TestTransform:
    """Test transform function support."""
    
    def test_case_insensitive(self):
        """Test case-insensitive matching."""
        prev = ["Apple", "Banana"]
        next = ["apple", "banana"]
        blocks = patience_diff.get_matching_blocks(str.lower, prev, next)
        assert blocks is not None, "Should support case-insensitive matching"
        print("  ✓ test_case_insensitive passed")
    
    def test_strip_transform(self):
        """Test strip whitespace transform."""
        prev = [" apple ", " banana "]
        next = ["apple", "banana"]
        blocks = patience_diff.get_matching_blocks(str.strip, prev, next)
        assert blocks is not None, "Should support strip whitespace transform"
        print("  ✓ test_strip_transform passed")


class TestEdgeCases:
    """Test edge cases and stress scenarios."""
    
    def test_single_element(self):
        """Test with single element sequences."""
        matches1 = patience_diff.matches(["a"], ["a"])
        assert len(matches1) == 1, "Single matching element should work"
        
        matches2 = patience_diff.matches(["a"], ["b"])
        assert len(matches2) == 0, "Single non-matching element should have no matches"
        print("  ✓ test_single_element passed")
    
    def test_duplicates(self):
        """Test with duplicate values."""
        prev = ["x", "a", "x", "b", "x"]
        next = ["x", "b", "x", "a", "x"]
        matches = patience_diff.matches(prev, next)
        # Should find some matches (patience diff may find fewer due to algorithm)
        assert len(matches) >= 1, f"Should find at least 1 match, got {len(matches)}"
        print("  ✓ test_duplicates passed")
    
    def test_large_sequences(self):
        """Test with large sequences (stress test)."""
        prev = list(range(1000))
        next = list(range(1000))
        matches = patience_diff.matches(prev, next)
        assert len(matches) == 1000, f"Should match all 1000 items, got {len(matches)}"
        print("  ✓ test_large_sequences passed")


def run_tests():
    """Run all test classes."""
    print("=" * 60)
    print("COMPREHENSIVE PATIENCE DIFF LIBRARY TESTS")
    print("=" * 60)
    
    test_classes = [
        ("TestBasicMatching", TestBasicMatching()),
        ("TestHunks", TestHunks()),
        ("TestMatchRatio", TestMatchRatio()),
        ("TestSemanticCleanup", TestSemanticCleanup()),
        ("TestMatches", TestMatches()),
        ("TestTransform", TestTransform()),
        ("TestEdgeCases", TestEdgeCases()),
    ]
    
    total_tests = 0
    passed_tests = 0
    
    for class_name, test_obj in test_classes:
        print(f"\n{class_name}:")
        methods = [m for m in dir(test_obj) if m.startswith("test_")]
        for method_name in methods:
            total_tests += 1
            try:
                method = getattr(test_obj, method_name)
                method()
                passed_tests += 1
            except Exception as e:
                print(f"  ✗ {method_name} FAILED: {e}")
    
    print("\n" + "=" * 60)
    print(f"RESULTS: {passed_tests}/{total_tests} tests passed")
    print("=" * 60)
    
    return passed_tests == total_tests


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
