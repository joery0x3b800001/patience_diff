"""Move Kind - Classifies moves in diffs.

A Move Kind represents how a block of code moved or stayed in place.
"""

from dataclasses import dataclass
from typing import Union

try:
    from .move_id import MoveId
except ImportError:
    from move_id import MoveId


@dataclass(frozen=True)
class Move:
    """Represents a code block that moved from one location to another."""
    move_id: MoveId
    
    def __repr__(self) -> str:
        return f"Move({self.move_id})"


@dataclass(frozen=True)
class WithinMove:
    """Represents code that is within a move (part of a larger move operation)."""
    move_id: MoveId
    
    def __repr__(self) -> str:
        return f"WithinMove({self.move_id})"


# Type alias for move kind
MoveKind = Union[Move, WithinMove]

