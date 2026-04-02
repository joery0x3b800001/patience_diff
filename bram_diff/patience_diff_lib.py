"""
Patience Diff Library - Main entry point.

This module serves as the main library entry point, re-exporting all core modules.
Equivalent to patience_diff_lib.ml in the OCaml implementation.

This is a port of Bram Cohen's patience diff algorithm, as found in the Bazaar 1.14.1
source code, available at http://bazaar-vcs.org.

Copyright (C) 2005 Bram Cohen, Copyright (C) 2005, 2006 Canonical Ltd
Licensed under GNU General Public License v2 or later.
"""

# Re-export all major modules
from . import (
    patience_diff as PatienceDiff,
    plain_diff as PlainDiff,
)

__all__ = [
    'PatienceDiff',
    'PlainDiff',
]
