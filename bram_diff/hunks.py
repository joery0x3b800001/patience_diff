"""Hunks - list of hunks representing a complete diff."""

from typing import List, Callable

try:
    from .hunk import Hunk
    from .range import Replace, Prev, Next
    from .move_kind import WithinMove
except ImportError:
    from hunk import Hunk
    from range import Replace, Prev, Next
    from move_kind import WithinMove


def unified(hunks: List[Hunk]) -> List[Hunk]:
    """Convert Replace ranges to Prev+Next pairs in unified format."""
    def transform_range(r):
        if isinstance(r, Replace):
            move_kind = WithinMove(r.move_id) if r.move_id else None
            return [Prev(r.prev_items, move_kind), Next(r.next_items, move_kind)]
        else:
            return [r]
    
    result = []
    for hunk in hunks:
        new_ranges = []
        for r in hunk.ranges:
            new_ranges.extend(transform_range(r))
        result.append(Hunk(hunk.prev_start, hunk.prev_size, hunk.next_start, hunk.next_size, new_ranges))
    return result


def ranges(hunks: List[Hunk]) -> List:
    """Get all ranges from all hunks."""
    result = []
    for hunk in hunks:
        result.extend(hunk.ranges)
    return result


def concat_map_ranges(hunks: List[Hunk], f: Callable) -> List[Hunk]:
    """Apply a function to all ranges in all hunks."""
    result = []
    for hunk in hunks:
        new_ranges = []
        for r in hunk.ranges:
            mapped = f(r)
            if isinstance(mapped, list):
                new_ranges.extend(mapped)
            else:
                new_ranges.append(mapped)
        result.append(Hunk(hunk.prev_start, hunk.prev_size, hunk.next_start, hunk.next_size, new_ranges))
    return result
