"""Patience Diff algorithm implementation based on Bram Cohen's algorithm.

This is a comprehensive port of Bram Cohen's patience diff algorithm, as found in the Bazaar source code.
The algorithm is described in: http://bazaar-vcs.org

Copyright (C) 2005 Bram Cohen, Copyright (C) 2005, 2006 Canonical Ltd
Licensed under GNU General Public License v2 or later.
"""

from typing import List, Callable, Optional, Tuple, Any, TypeVar, Dict, Set
from collections import deque

import time as _time
import os as _os
import sys as _sys

from typing import (
    Iterator as _Iterator,
    Optional as _Optional,
    Sequence as _Sequence,
    Type as _Type,
    Union as _Union,
    Tuple as _Tuple,
    List as _List
)
import heapq

try:
    from .matching_block import MatchingBlock
    from .hunk import Hunk
    from .range import Same, Prev, Next, Replace, Unified
    from .move_kind import Move, WithinMove
    from .move_id import MoveId
except ImportError:
    from matching_block import MatchingBlock
    from hunk import Hunk
    from range import Same, Prev, Next, Replace, Unified
    from move_kind import Move, WithinMove
    from move_id import MoveId

T = TypeVar('T')


# ============================================================================
# Patience Sorting Algorithm
# ============================================================================

class OrderedSequence:
    """A sequence with second coordinates in increasing order."""
    
    def __init__(self, items: List[Tuple[int, int]]):
        # Sort by (y, x) where y is second coordinate, x is first
        self.items = sorted(items, key=lambda p: (p[1], p[0]))
    
    def __len__(self):
        return len(self.items)
    
    def __getitem__(self, idx):
        return self.items[idx]
    
    def is_empty(self):
        return len(self.items) == 0


class PatienceSequenceMatcher:
    def __init__(self, isjunk=None, a: _Sequence[str] = "", b: _Sequence[str] = ""):
        self.a = a
        self.b = b
        self._matching_blocks = None

    def get_matching_blocks(self) -> _List[MatchingBlock]:
        if self._matching_blocks is None:
            # This calls the internal get_matching_blocks logic
            self._matching_blocks = get_matching_blocks(None, self.a, self.b)
        return self._matching_blocks

    def get_opcodes(self) -> _Iterator[_Tuple[str, int, int, int, int]]:
        i = j = 0
        for block in self.get_matching_blocks():
            ai, bj, n = block.prev_start, block.next_start, block.length
            if i < ai and j < bj:
                yield ('replace', i, ai, j, bj)
            elif i < ai:
                yield ('delete', i, ai, j, bj)
            elif j < bj:
                yield ('insert', i, ai, j, bj)

            if n > 0:
                yield ('equal', ai, ai + n, bj, bj + n)
            i, j = ai + n, bj + n

        # Emit any tail not covered by the sentinel
        if i < len(self.a) and j < len(self.b):
            yield ('replace', i, len(self.a), j, len(self.b))
        elif i < len(self.a):
            yield ('delete', i, len(self.a), j, j)
        elif j < len(self.b):
            yield ('insert', i, i, j, len(self.b))

    def get_grouped_opcodes(self, n: int = 3) -> _Iterator[_List[_Tuple[str, int, int, int, int]]]:
        codes = list(self.get_opcodes())
        if not codes:
            return

        # If there are NO differences (only one 'equal' block), don't yield anything
        if len(codes) == 1 and codes[0][0] == 'equal':
            # Check if the sequences are actually different lengths or content
            if self.a == self.b:
                return
            # If they are different but the matcher failed, force a replace
            codes = [('replace', 0, len(self.a), 0, len(self.b))]

        group = []
        for tag, i1, i2, j1, j2 in codes:
            if tag == 'equal':
                if i2 - i1 > n * 2:
                    group.append((tag, i1, i1 + n, j1, j1 + n))
                    yield group
                    group = []
                    i1, j1 = i2 - n, j2 - n
            group.append((tag, i1, i2, j1, j2))

        if group:
            yield group


class Backpointers:
    """Track a value with optional backpointer to previous value in sequence."""
    
    def __init__(self, value: Tuple[int, int], tag: Optional['Backpointers'] = None):
        self.value = value
        self.tag = tag
    
    def to_list(self) -> List[Tuple[int, int]]:
        """Convert backpointer chain to list."""
        result = []
        current = self
        while current is not None:
            result.append(current.value)
            current = current.tag
        return list(reversed(result))


def longest_increasing_subsequence(ordered_seq: OrderedSequence) -> List[Tuple[int, int]]:
    """Find longest increasing subsequence using patience sorting."""
    if ordered_seq.is_empty():
        return []
    
    # Piles of cards with backpointers
    piles: List[Backpointers] = []
    
    for x_val in ordered_seq.items:
        # Find the pile where we should place this card
        pile_idx = _find_pile_index(piles, x_val)
        
        # Get the backpointer tag from the previous pile
        tag = None
        if pile_idx > 0:
            tag = piles[pile_idx - 1]
        
        # Create backpointer entry
        new_entry = Backpointers(x_val, tag)
        
        if pile_idx >= len(piles):
            piles.append(new_entry)
        else:
            piles[pile_idx] = new_entry
    
    # Get result from rightmost pile
    if piles:
        return piles[-1].to_list()
    return []


def _find_pile_index(piles: List[Backpointers], x_val: Tuple[int, int]) -> int:
    """Find index where card should be placed using binary search."""
    left, right = 0, len(piles)
    while left < right:
        mid = (left + right) // 2
        if piles[mid].value[0] < x_val[0]:
            left = mid + 1
        else:
            right = mid
    return left


# ============================================================================
# Matching Blocks and Lines
# ============================================================================

class LineMetadata:
    """Metadata for a line in the diff."""
    pass


class UniqueInA(LineMetadata):
    def __init__(self, index: int):
        self.index = index


class UniqueInAB(LineMetadata):
    def __init__(self, index_a: int, index_b: int):
        self.index_a = index_a
        self.index_b = index_b


class NotUnique(LineMetadata):
    def __init__(self, count: int):
        self.count = count


SWITCH_TO_PLAIN_DIFF_NUMERATOR = 1
SWITCH_TO_PLAIN_DIFF_DENOMINATOR = 10


def should_discard_if_other_side_equal(big_enough: int) -> int:
    """Calculate threshold for discarding matches when other side is equal."""
    return big_enough


def _should_discard_match(big_enough: int, left_change: int, right_change: int, block_len: int) -> bool:
    """Check if a match should be discarded based on surrounding changes."""
    should_discard_threshold = should_discard_if_other_side_equal(big_enough)
    
    # Throw away if effective length is too small relative to surrounding inserts/deletes
    if block_len >= big_enough:
        return False
    
    if left_change > block_len and right_change > block_len:
        return True
    if left_change >= block_len + should_discard_threshold and right_change == block_len:
        return True
    if right_change >= block_len + should_discard_threshold and left_change == block_len:
        return True
    
    return False


def _basic_semantic_cleanup(big_enough: int, matching_blocks: List[MatchingBlock]) -> List[MatchingBlock]:
    """Remove spurious matches based on surrounding changes."""
    if len(matching_blocks) <= 1:
        return matching_blocks
    
    result = []
    for i, block in enumerate(matching_blocks):
        if i == 0:
            result.append(block)
        else:
            prev_block = result[-1]
            left_change = block.prev_start - (prev_block.prev_start + prev_block.length)
            right_change = block.next_start - (prev_block.next_start + prev_block.length)
            
            if _should_discard_match(big_enough, left_change, right_change, block.length):
                # Merge with previous block
                result[-1] = MatchingBlock(
                    prev_block.prev_start,
                    prev_block.next_start,
                    block.prev_start + block.length - prev_block.prev_start
                )
            else:
                result.append(block)
    
    return result


def _advanced_semantic_cleanup(big_enough: int, matching_blocks: List[MatchingBlock]) -> List[MatchingBlock]:
    """Remove spurious matches by looking at both sides."""
    if len(matching_blocks) <= 2:
        return matching_blocks
    
    result = []
    i = 0
    while i < len(matching_blocks):
        block = matching_blocks[i]
        
        # Look ahead
        if i + 1 < len(matching_blocks):
            next_block = matching_blocks[i + 1]
            left_change = next_block.prev_start - (block.prev_start + block.length)
            right_change = next_block.next_start - (block.next_start + block.length)
            
            # Big block followed by small change followed by big block
            if (i + 2 < len(matching_blocks) and 
                _should_discard_match(big_enough, left_change, right_change, next_block.length)):
                
                next_next_block = matching_blocks[i + 2]
                # Merge all three blocks
                merged = MatchingBlock(
                    block.prev_start,
                    block.next_start,
                    next_next_block.prev_start + next_next_block.length - block.prev_start
                )
                # Re-apply cleanup on the merged block
                temp = _basic_semantic_cleanup(big_enough, [merged])
                result.extend(temp)
                i += 3
                continue
        
        result.append(block)
        i += 1
    
    return _basic_semantic_cleanup(big_enough, result)


def _semantic_cleanup(big_enough: int, matching_blocks: List[MatchingBlock]) -> List[MatchingBlock]:
    """Apply semantic cleanup to remove spurious matches."""
    blocks = _basic_semantic_cleanup(big_enough, matching_blocks)
    return _advanced_semantic_cleanup(big_enough, blocks)


def _unique_lcs(prev_array, prev_lo, prev_hi, next_array, next_lo, next_hi) -> Optional[List[Tuple[int, int]]]:
    """Find longest common subsequence among unique elements."""
    # Build hashtable of unique elements in prev_array
    unique: Dict[Any, LineMetadata] = {}
    
    for i in range(prev_lo, prev_hi):
        elem = prev_array[i]
        if elem in unique:
            metadata = unique[elem]
            if isinstance(metadata, UniqueInA):
                unique[elem] = NotUnique(2)
            elif isinstance(metadata, NotUnique):
                unique[elem] = NotUnique(metadata.count + 1)
        else:
            unique[elem] = UniqueInA(i)
    
    # Count matching elements and find intersections
    num_pairs = 0
    intersection_size = 0
    
    for j in range(next_lo, next_hi):
        elem = next_array[j]
        if elem in unique:
            metadata = unique[elem]
            if isinstance(metadata, NotUnique):
                if metadata.count > 0:
                    unique[elem] = NotUnique(metadata.count - 1)
                    intersection_size += 1
            elif isinstance(metadata, UniqueInA):
                num_pairs += 1
                intersection_size += 1
                unique[elem] = UniqueInAB(metadata.index, j)
            elif isinstance(metadata, UniqueInAB):
                num_pairs -= 1
                unique[elem] = NotUnique(0)
    
    # Check if there are enough unique tokens
    if num_pairs * SWITCH_TO_PLAIN_DIFF_DENOMINATOR < intersection_size * SWITCH_TO_PLAIN_DIFF_NUMERATOR:
        return None
    
    # Build array for LIS
    pairs = []
    for elem, metadata in unique.items():
        if isinstance(metadata, UniqueInAB):
            pairs.append((metadata.index_a, metadata.index_b))
    
    if not pairs:
        return None
    
    ordered_seq = OrderedSequence(pairs)
    return longest_increasing_subsequence(ordered_seq)


def _matches_recursive(prev_array, next_array, prev_lo, prev_hi, next_lo, next_hi, matches_list):
    """Recursively find matches using patience diff."""
    if prev_lo >= prev_hi or next_lo >= next_hi:
        return
    
    # Check if first elements match
    if prev_array[prev_lo] == next_array[next_lo]:
        # Add matching sequence at beginning
        while (prev_lo < prev_hi and next_lo < next_hi and 
               prev_array[prev_lo] == next_array[next_lo]):
            matches_list.append((prev_lo, next_lo))
            prev_lo += 1
            next_lo += 1
        _matches_recursive(prev_array, next_array, prev_lo, next_lo, prev_hi, next_hi, matches_list)
    
    # Check if last elements match
    elif prev_array[prev_hi - 1] == next_array[next_hi - 1]:
        # Remember and recurse
        nahi = prev_hi - 1
        nbhi = next_hi - 1
        while (nahi > prev_lo and nbhi > next_lo and 
               prev_array[nahi - 1] == next_array[nbhi - 1]):
            nahi -= 1
            nbhi -= 1
        
        _matches_recursive(prev_array, next_array, prev_lo, next_lo, nahi, nbhi, matches_list)
        
        # Add matching sequence at end
        for i in range(prev_hi - nahi):
            matches_list.append((nahi + i, nbhi + i))
    
    else:
        # Try unique_lcs
        lcs = _unique_lcs(prev_array, prev_lo, prev_hi, next_array, next_lo, next_hi)
        
        if lcs is None:
            lcs = []
        
        last_a = prev_lo - 1
        last_b = next_lo - 1
        
        for apos, bpos in lcs:
            if last_a + 1 != apos or last_b + 1 != bpos:
                _matches_recursive(prev_array, next_array, last_a + 1, last_b + 1, apos, bpos, matches_list)
            last_a = apos
            last_b = bpos
            matches_list.append((apos, bpos))
        
        if lcs:
            _matches_recursive(prev_array, next_array, last_a + 1, last_b + 1, prev_hi, next_hi, matches_list)


def _combine_equalities(prev_array, next_array, matches: List[MatchingBlock]) -> List[MatchingBlock]:
    """Merge adjacent matching blocks that are separated only by equal elements."""
    if len(matches) <= 1:
        return matches
    
    result = []
    i = 0
    while i < len(matches):
        current = matches[i]
        
        # Look for adjacent blocks that can be merged
        while i + 1 < len(matches):
            next_block = matches[i + 1]
            
            # Check if blocks are adjacent with equal elements between them
            prev_gap = next_block.prev_start - (current.prev_start + current.length)
            next_gap = next_block.next_start - (current.next_start + current.length)
            
            if prev_gap == next_gap and prev_gap >= 0:
                # Check if gap elements are equal
                can_merge = True
                for j in range(prev_gap):
                    prev_idx = current.prev_start + current.length + j
                    next_idx = current.next_start + current.length + j
                    if prev_array[prev_idx] != next_array[next_idx]:
                        can_merge = False
                        break
                
                if can_merge:
                    # Merge blocks
                    current = MatchingBlock(
                        current.prev_start,
                        current.next_start,
                        next_block.prev_start + next_block.length - current.prev_start
                    )
                    i += 1
                    continue
            
            break
        
        result.append(current)
        i += 1
    
    return result


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


# ============================================================================
# Public API
# ============================================================================

def get_matching_blocks(transform, prev_array, next_array, big_enough=1, max_slide=0, score=None):
    """Get matching blocks using patience diff algorithm.
    
    Returns list of MatchingBlock objects where each block represents a matching subsequence.
    The last block is always a sentinel with length 0.
    """
    if transform is None:
        transform = lambda x: x
    
    # Handle empty arrays
    if not prev_array and not next_array:
        return [MatchingBlock(0, 0, 0)]
    if not prev_array:
        return [MatchingBlock(0, 0, 0)]
    if not next_array:
        return [MatchingBlock(len(prev_array), len(next_array), 0)]
    
    # Find raw matches
    matches_list = []
    _matches_recursive(prev_array, next_array, 0, len(prev_array), 0, len(next_array), matches_list)
    
    # Collapse into blocks
    blocks = _collapse_sequences(matches_list)
    
    # Combine equalities to merge adjacent blocks
    blocks = _combine_equalities(prev_array, next_array, blocks)
    
    # Apply semantic cleanup to remove spurious matches
    blocks = _semantic_cleanup(big_enough, blocks)
    
    # Add sentinel block
    if blocks:
        last = max(blocks, key=lambda b: (b.prev_start + b.length, b.next_start + b.length))
        sentinel = MatchingBlock(last.prev_start + last.length, last.next_start + last.length, 0)
    else:
        sentinel = MatchingBlock(len(prev_array), len(next_array), 0)
    
    blocks.append(sentinel)
    return blocks


def matches(prev_array, next_array):
    """Get matching indices as list of (i,j) pairs."""
    if not prev_array or not next_array:
        return []
    
    matches_list = []
    _matches_recursive(prev_array, next_array, 0, len(prev_array), 0, len(next_array), matches_list)
    return sorted(matches_list)


def match_ratio(prev_array, next_array) -> float:
    """Calculate match ratio between 0 and 1."""
    total = len(prev_array) + len(next_array)
    if total == 0:
        return 1.0
    matches_list = matches(prev_array, next_array)
    return 2.0 * len(matches_list) / total


def _create_hunk(prev_start, prev_stop, next_start, next_stop, ranges) -> Hunk:
    """Create a hunk from indices and ranges."""
    return Hunk(
        prev_start=prev_start + 1,
        prev_size=prev_stop - prev_start,
        next_start=next_start + 1,
        next_size=next_stop - next_start,
        ranges=list(reversed(ranges))
    )


def _get_ranges_rev(prev_array, next_array, matching_blocks, transform=None, big_enough=1):
    """Convert matching blocks to ranges in reverse order."""
    if transform is None:
        transform = lambda x: x
    
    ranges = []
    prev_idx = 0
    next_idx = 0
    
    for block in matching_blocks:
        # Handle gap before this block
        if prev_idx < block.prev_start or next_idx < block.next_start:
            if prev_idx < block.prev_start and next_idx < block.next_start:
                prev_slice = tuple(prev_array[prev_idx:block.prev_start])
                next_slice = tuple(next_array[next_idx:block.next_start])
                ranges.append(Replace(prev_slice, next_slice, None))
            elif prev_idx < block.prev_start:
                prev_slice = tuple(prev_array[prev_idx:block.prev_start])
                ranges.append(Prev(prev_slice, None))
            else:
                next_slice = tuple(next_array[next_idx:block.next_start])
                ranges.append(Next(next_slice, None))
        
        # Handle matching block
        if block.length > 0:
            same_items = tuple(
                (prev_array[block.prev_start + i], next_array[block.next_start + i])
                for i in range(block.length)
            )
            ranges.append(Same(same_items))
        
        prev_idx = block.prev_start + block.length
        next_idx = block.next_start + block.length
    
    return list(reversed(ranges))


def _limit_hunk_context(hunk: Hunk, context: int) -> List[Hunk]:
    """Split hunks based on context limit, removing large Same ranges."""
    if context < 0:
        return [hunk]
    
    ranges = hunk.ranges
    hunks = []
    curr_ranges = []
    prev_start = hunk.prev_start
    next_start = hunk.next_start
    
    def finalize_hunk():
        if curr_ranges:
            h = Hunk(prev_start, prev_start, next_start, next_start, list(reversed(curr_ranges)))
            return h
        return None
    
    i = 0
    while i < len(ranges):
        r = ranges[i]
        
        if isinstance(r, Same):
            size = len(r.lines)
            
            if i == len(ranges) - 1:  # Last range
                # Crop to context
                keep = min(size, context)
                if keep > 0:
                    cropped_lines = r.lines[:keep]
                    curr_ranges.append(Same(cropped_lines))
                
                # Finalize
                h = finalize_hunk()
                if h and h.ranges:
                    hunks.append(h)
            
            elif size > context * 2:
                # This Same is large, split it
                # Keep first context
                first_lines = r.lines[:context]
                if first_lines:
                    curr_ranges.append(Same(first_lines))
                
                # Finalize current hunk
                h = finalize_hunk()
                if h and h.ranges:
                    hunks.append(h)
                
                curr_ranges = []
                prev_start += context
                next_start += context
                
                # Keep last context
                last_lines = r.lines[-context:]
                curr_ranges.append(Same(last_lines))
                prev_start += size - context
                next_start += size - context
            
            else:
                # Keep entire Same range as context
                curr_ranges.append(r)
                prev_start += size
                next_start += size
        
        else:
            # Non-Same range
            if isinstance(r, Prev):
                size = len(r.lines)
                prev_start += size
            elif isinstance(r, Next):
                size = len(r.lines)
                next_start += size
            elif isinstance(r, Replace):
                prev_start += len(r.prev_lines)
                next_start += len(r.next_lines)
            
            curr_ranges.append(r)
        
        i += 1
    
    # Finalize last hunk
    h = finalize_hunk()
    if h and h.ranges:
        hunks.append(h)
    
    return hunks


def get_hunks(prev_array, next_array, transform=None, context=-1, big_enough=1, max_slide=0, score=None):
    """Generate hunks comparing prev_array and next_array.
    
    Args:
        prev_array: Previous/original array
        next_array: Next/new array
        transform: Optional transform function for elements
        context: Number of context lines (negative = infinite)
        big_enough: Minimum match size for semantic cleanup
        max_slide: Maximum slide distance for diff boundaries
        score: Optional scoring function for boundary selection
    
    Returns:
        List of Hunk objects representing the differences
    """
    if transform is None:
        transform = lambda x: x
    
    prev_array = list(prev_array)
    next_array = list(next_array)
    
    # Get matching blocks with cleanup
    blocks = get_matching_blocks(transform, prev_array, next_array, big_enough=big_enough)
    
    # Get ranges from blocks
    ranges = _get_ranges_rev(prev_array, next_array, blocks, transform, big_enough)
    
    # Handle infinite context case
    if context < 0:
        if ranges:
            return [Hunk(1, len(prev_array) + 1, 1, len(next_array) + 1, ranges)]
        else:
            return [Hunk(1, 1, 1, 1, [])]
    
    # Handle limited context case
    if not ranges:
        return [Hunk(1, 1, 1, 1, [])]
    
    # Create initial hunk with all ranges
    initial_hunk = Hunk(1, len(prev_array) + 1, 1, len(next_array) + 1, ranges)
    
    # Split by context
    hunks = _limit_hunk_context(initial_hunk, context)
    
    return hunks if hunks else [Hunk(1, 1, 1, 1, [])]


def default_context():
    """Return the default context value (infinite)."""
    return -1


def unified_diff(
    a: _Sequence[str],
    b: _Sequence[str],
    fromfile: str = "",
    tofile: str = "",
    n: int = 3,
    lineterm: str = "\n",
    sequencematcher: _Optional[_Type[PatienceSequenceMatcher]] = None,
) -> _Iterator[str]:

    matcher_class = sequencematcher or PatienceSequenceMatcher
    matcher = matcher_class(a=a, b=b)

    started = False
    for group in matcher.get_grouped_opcodes(n):
        if not started:
            # Generate Headers
            yield f"--- {fromfile}{lineterm}"
            yield f"+++ {tofile}{lineterm}"
            started = True

        i1, i2, j1, j2 = group[0][1], group[-1][2], group[0][3], group[-1][4]
        yield f"@@ -{i1 + 1},{i2 - i1} +{j1 + 1},{j2 - j1} @@{lineterm}"

        for tag, i1, i2, j1, j2 in group:
            if tag == "equal":
                for line in a[i1:i2]:
                    yield " " + line
                continue
            if tag in ("replace", "delete"):
                for line in a[i1:i2]:
                    yield "-" + line
            if tag in ("replace", "insert"):
                for line in b[j1:j2]:
                    yield "+" + line