"""
Patience Diff - A Python port of the OCaml Patience Diff library.

This is a comprehensive port of Bram Cohen's patience diff algorithm, as found in the Bazaar 1.14.1
source code, available at http://bazaar-vcs.org.

Copyright (C) 2005 Bram Cohen, Copyright (C) 2005, 2006 Canonical Ltd
Licensed under GNU General Public License v2 or later.
"""

__version__ = "1.0.0"

# Import all public modules for convenience
from . import (
    hunk,
    hunks,
    matching_block,
    move_id,
    move_kind,
    patience_diff,
    plain_diff,
    range,
)

# Export commonly used classes and functions
from .hunk import Hunk
from .hunks import Hunks
from .matching_block import MatchingBlock
from .move_id import MoveId
from .move_kind import Move, WithinMove
from .range import Same, Prev, Next, Replace, Unified, Range
from .patience_diff import (
    get_matching_blocks,
    get_hunks,
    matches,
    match_ratio,
)

# Create module-level exports similar to OCaml
class PatienceDiff:
    """Patience Diff algorithm module."""
    get_matching_blocks = staticmethod(patience_diff.get_matching_blocks)
    get_hunks = staticmethod(patience_diff.get_hunks)
    matches = staticmethod(patience_diff.matches)
    match_ratio = staticmethod(patience_diff.match_ratio)

class PlainDiff:
    """Plain (Myers) diff algorithm module."""
    get_matching_blocks = staticmethod(plain_diff.get_matching_blocks)
    get_hunks = staticmethod(plain_diff.get_hunks)
    matches = staticmethod(plain_diff.matches)
    match_ratio = staticmethod(plain_diff.match_ratio)

__all__ = [
    'hunk',
    'hunks',
    'matching_block',
    'move_id',
    'move_kind',
    'patience_diff',
    'plain_diff',
    'range',
    'Hunk',
    'Hunks',
    'MatchingBlock',
    'MoveId',
    'Move',
    'WithinMove',
    'Same',
    'Prev',
    'Next',
    'Replace',
    'Unified',
    'Range',
    'get_matching_blocks',
    'get_hunks',
    'matches',
    'match_ratio',
    'PatienceDiff',
    'PlainDiff',
]
