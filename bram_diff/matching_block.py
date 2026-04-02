"""Matching Block - Represents a block of matching lines between two arrays."""

from dataclasses import dataclass


@dataclass(frozen=True)
class MatchingBlock:
    """
    A matching block represents a region of matching content between two arrays.
    
    Attributes:
        prev_start: Starting index in the "previous" array
        next_start: Starting index in the "next" array
        length: Number of matching elements in this block
    """
    prev_start: int
    next_start: int
    length: int
    
    def __repr__(self) -> str:
        return f"MatchingBlock({self.prev_start}, {self.next_start}, {self.length})"
    
    def __str__(self) -> str:
        return f"({self.prev_start}, {self.next_start}, {self.length})"
