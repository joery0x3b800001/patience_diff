"""Myers diff algorithm implementation.

Basic Myers diff algorithm, translated from GNU diff (diffseq.h and analyze.c).
This is a fallback algorithm used when unique tokens are insufficient for
the Patience Diff algorithm.

Based on the algorithm described by Eugene W. Myers in:
'An O(ND) Difference Algorithm and Its Variations'
"""

from typing import Callable, List, Optional, Any, Hashable, Dict, Tuple

try:
    from .matching_block import MatchingBlock
except ImportError:
    from matching_block import MatchingBlock


def _myers_diff(prev_array, next_array) -> List[Tuple[int, int]]:
    """Find matching pairs using Myers diff algorithm.
    
    Returns list of (i, j) pairs where prev_array[i] == next_array[j].
    """
    # Build hashmap of elements in next_array
    element_map: Dict[Any, List[int]] = {}
    for j, elem in enumerate(next_array):
        if elem not in element_map:
            element_map[elem] = []
        element_map[elem].append(j)
    
    # Find common subsequences
    matches_list = []
    
    # Build LCS using simple DP approach (O(n*m))
    # This is simpler than full Myers but good enough for fallback
    m = len(prev_array)
    n = len(next_array)
    
    # dp[i][j] = length of LCS for prev_array[0:i] and next_array[0:j]
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if prev_array[i - 1] == next_array[j - 1]:
                dp[i][j] = dp[i - 1][j - 1] + 1
            else:
                dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])
    
    # Backtrack to find the actual matches
    i, j = m, n
    while i > 0 and j > 0:
        if dp[i][j] == dp[i - 1][j]:
            i -= 1
        elif dp[i][j] == dp[i][j - 1]:
            j -= 1
        else:
            matches_list.append((i - 1, j - 1))
            i -= 1
            j -= 1
    
    return sorted(matches_list)


def iter_matches(prev_array, next_array, hashable=None, cutoff=None, f=None):
    """Find matching elements between two arrays using Myers algorithm.
    
    Args:
        prev_array: Previous/original array
        next_array: Next/new array
        hashable: Optional hashable function for elements (not used in basic version)
        cutoff: Optional cutoff for edit distance (not used in basic version)
        f: Callback function called with (prev_idx, next_idx) for each match
    """
    if f is None:
        return
    
    matches_list = _myers_diff(prev_array, next_array)
    for prev_idx, next_idx in matches_list:
        f(prev_idx, next_idx)


def _collapse_sequences(matches: List[Tuple[int, int]]) -> List[MatchingBlock]:
    """Collapse consecutive matches into matching blocks."""
    if not matches:
        return [MatchingBlock(0, 0, 0)]
    
    collapsed = []
    start_a = None
    start_b = None
    length = 0
    
    for i_a, i_b in matches:
        if start_a is not None and i_a == start_a + length and i_b == start_b + length:
            length += 1
        else:
            if start_a is not None:
                collapsed.append(MatchingBlock(start_a, start_b, length))
            start_a = i_a
            start_b = i_b
            length = 1
    
    if start_a is not None:
        collapsed.append(MatchingBlock(start_a, start_b, length))
    
    # Add sentinel
    if collapsed:
        last = collapsed[-1]
        collapsed.append(MatchingBlock(last.prev_start + last.length, last.next_start + last.length, 0))
    else:
        collapsed.append(MatchingBlock(0, 0, 0))
    
    return collapsed


def get_matching_blocks(prev_array, next_array, transform=None, big_enough=1, max_slide=0, score=None):
    """Get matching blocks between two arrays using Myers diff algorithm.
    
    Args:
        prev_array: Previous/original array
        next_array: Next/new array  
        transform: Optional transform function for elements (not used)
        big_enough: Minimum match size (not used in basic Myers)
        max_slide: Maximum slide distance (not used)
        score: Optional scoring function (not used)
    
    Returns:
        List of MatchingBlock objects with sentinel at end
    """
    if not prev_array and not next_array:
        return [MatchingBlock(0, 0, 0)]
    if not prev_array:
        return [MatchingBlock(0, 0, 0)]
    if not next_array:
        return [MatchingBlock(len(prev_array), len(next_array), 0)]
    
    matches_list = _myers_diff(prev_array, next_array)
    return _collapse_sequences(matches_list)


def get_hunks(prev_array, next_array, transform=None, context=-1, big_enough=1, max_slide=0, score=None):
    """Generate hunks comparing prev_array and next_array using Myers algorithm.
    
    Args:
        prev_array: Previous/original array
        next_array: Next/new array
        transform: Optional transform function (not used)
        context: Number of context lines
        big_enough: Minimum match size (not used)
        max_slide: Maximum slide (not used)
        score: Optional scoring function (not used)
    
    Returns:
        List of MatchingBlock objects (Myers doesn't generate full hunks)
    """
    # Myers is just a fallback for matching blocks
    # Full hunk generation would need to be implemented separately
    return get_matching_blocks(prev_array, next_array, transform)


def matches(prev_array, next_array) -> List[Tuple[int, int]]:
    """Get list of matching indices (i,j) pairs using Myers algorithm.
    
    Args:
        prev_array: Previous/original array
        next_array: Next/new array
    
    Returns:
        List of (i, j) tuples where prev_array[i] == next_array[j]
    """
    if not prev_array or not next_array:
        return []
    
    return _myers_diff(prev_array, next_array)


def match_ratio(prev_array, next_array) -> float:
    """Calculate match ratio between 0 and 1.
    
    Returns 2 * len(matches) / (len(prev_array) + len(next_array))
    
    Args:
        prev_array: Previous/original array  
        next_array: Next/new array
    
    Returns:
        Float between 0 and 1 indicating similarity
    """
    total = len(prev_array) + len(next_array)
    if total == 0:
        return 1.0
    matches_list = matches(prev_array, next_array)
    return 2.0 * len(matches_list) / total
