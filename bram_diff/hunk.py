"""Hunk dataclass for representing chunks of differences."""

from dataclasses import dataclass, field
from typing import List


def _get_same_class():
    """Lazy import to avoid circular imports."""
    try:
        from .range import Same
    except ImportError:
        from range import Same
    return Same


@dataclass
class Hunk:
    """A hunk represents a contiguous region of changes in a diff."""
    prev_start: int
    prev_size: int
    next_start: int
    next_size: int
    ranges: List = field(default_factory=list)
    
    def all_same(self):
        """Check if all ranges in this hunk are identical."""
        Same = _get_same_class()
        return all(isinstance(r, Same) for r in self.ranges)
    
    @staticmethod
    def limit_infinite_context_hunk_to_context(hunk: 'Hunk', context: int) -> List['Hunk']:
        """Split a hunk with unlimited context to one with limited context.
        
        Removes large Same ranges from the middle, keeping only 'context' lines
        of context around changes.
        """
        if context < 0:
            return [hunk]
        
        Same = _get_same_class()
        
        ranges = hunk.ranges
        hunks_list = []
        curr_ranges = []
        prev_start = hunk.prev_start
        next_start = hunk.next_start
        
        def finalize_hunk():
            if curr_ranges:
                h = Hunk(prev_start, prev_start, next_start, next_start, list(reversed(curr_ranges)))
                hunks_list.append(h)
                curr_ranges.clear()
            return prev_start, next_start
        
        i = 0
        while i < len(ranges):
            r = ranges[i]
            
            if isinstance(r, Same):
                size = len(r.items)
                
                if i == len(ranges) - 1:  # Last range
                    # Crop to context
                    keep = min(size, context)
                    if keep > 0:
                        cropped_items = r.items[:keep]
                        curr_ranges.append(Same(cropped_items))
                        prev_start += keep
                        next_start += keep
                    
                    # Finalize
                    finalize_hunk()
                
                elif size > context * 2:
                    # This Same is large, split it
                    # Keep first context
                    first_items = r.items[:context]
                    if first_items:
                        curr_ranges.append(Same(first_items))
                        prev_start += context
                        next_start += context
                    
                    # Finalize current hunk
                    finalize_hunk()
                    
                    # Advance by trimmed amount
                    prev_start += size - context
                    next_start += size - context
                    
                    # Keep last context for next hunk
                    last_items = r.items[-context:]
                    if last_items:
                        curr_ranges.append(Same(last_items))
                
                else:
                    # Keep entire Same range as context
                    curr_ranges.append(r)
                    prev_start += size
                    next_start += size
            
            else:
                # Non-Same range
                if hasattr(r, 'items') and not isinstance(r, Same):
                    # Prev or Next
                    size = len(r.items)
                    if hasattr(r, 'lines'):  # For backward compat
                        size = len(r.lines)
                    prev_start += size if hasattr(r, 'prev_items') else 0
                    next_start += size if hasattr(r, 'next_items') else 0
                elif hasattr(r, 'prev_items'):
                    # Replace
                    prev_start += len(r.prev_items)
                    next_start += len(r.next_items)
                
                curr_ranges.append(r)
            
            i += 1
        
        # Finalize last hunk if needed
        if curr_ranges:
            finalize_hunk()
        
        return hunks_list
