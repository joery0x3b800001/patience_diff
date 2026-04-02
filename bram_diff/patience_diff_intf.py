"""
Patience Diff Interface and Type Definitions.

This module provides type hints and documentation for the Patience Diff library.
It mirrors the OCaml interface file (patience_diff_intf.ml).

This is a port of Bram Cohen's patience diff algorithm, as found in the Bazaar 1.14.1
source code, available at http://bazaar-vcs.org.

Copyright (C) 2005 Bram Cohen, Copyright (C) 2005, 2006 Canonical Ltd
Licensed under GNU General Public License v2 or later.
"""

from typing import Callable, List, Tuple, Union, Optional, Generic, TypeVar, Protocol

# Re-export main types for convenience
from .hunk import Hunk
from .hunks import Hunks
from .matching_block import MatchingBlock
from .range import Range, Same, Prev, Next, Replace, Unified
from .move_id import MoveId

T = TypeVar('T')
Elt = TypeVar('Elt')


PATIENCE_DIFF_ALGORITHM = """
Bram Cohen's comment from the original Python code:

get_matching_blocks(a, b) returns a list of triples describing matching
subsequences.

Each triple is of the form (i, j, n), and means that
a[i:i+n] = b[j:j+n]. The triples are monotonically increasing in i and in j.

The last triple is a dummy, (len(a), len(b), 0), and is the only triple with n=0.

Example:
    get_matching_blocks(['a','b','x','c','d'], ['a','b','c','d'])
    returns
    [(0, 0, 2), (3, 2, 2), (5, 4, 0)]
"""


__all__ = [
    'Hunk',
    'Hunks',
    'MatchingBlock',
    'Range',
    'Same',
    'Prev',
    'Next',
    'Replace',
    'Unified',
    'MoveId',
    'PATIENCE_DIFF_ALGORITHM',
]
