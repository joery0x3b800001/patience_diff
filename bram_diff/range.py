"""Range - Represents different types of ranges in a diff."""

from typing import TypeVar, Generic, List, Union, Optional, Tuple
from dataclasses import dataclass

try:
    from .move_kind import Move, WithinMove
    from .move_id import MoveId
except ImportError:
    from move_kind import Move, WithinMove
    from move_id import MoveId

T = TypeVar('T')


@dataclass(frozen=True)
class Same(Generic[T]):
    """Represents identical lines in both versions."""
    lines: Tuple


@dataclass(frozen=True)
class Prev(Generic[T]):
    """Represents lines only in the previous version."""
    lines: Tuple
    move_kind: Optional[Union[Move, WithinMove]] = None


@dataclass(frozen=True)
class Next(Generic[T]):
    """Represents lines only in the next version."""
    lines: Tuple
    move_kind: Optional[Union[Move, WithinMove]] = None


@dataclass(frozen=True)
class Replace(Generic[T]):
    """Represents lines that are different."""
    prev_lines: Tuple
    next_lines: Tuple
    move_id: Optional[MoveId] = None


@dataclass(frozen=True)
class Unified(Generic[T]):
    """Represents lines in unified format."""
    lines: Tuple
    move_id: Optional[MoveId] = None


Range = Union[Same, Prev, Next, Replace, Unified]
