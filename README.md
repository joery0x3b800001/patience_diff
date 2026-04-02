# Patience Diff - Python Port

A complete Python port of Bram Cohen's algorithm for computing efficient differences.

## Features

- Patience Sorting Algorithm: O(n log n)
- Semantic Cleanup: Removes spurious matches
- Multiple Output Formats: Blocks, hunks with context
- Myers Fallback: Simple diff for edge cases
- Type Hints: Full annotations for IDE support
- Well Tested: Comprehensive test suite

## Quick Start

```bash
make install  # Install in dev mode
make test     # Run tests
```

## License

GNU General Public License v2 or later

Original algorithm and OCaml implementation by Bram Cohen  
Copyright (C) 2005, 2006 Canonical Ltd  
Python port by Shaun Joe


## API Reference

### Core Functions

- `get_matching_blocks(transform, prev_array, next_array, big_enough=1)` - Find matching blocks
- `get_hunks(transform, prev_array, next_array, context=-1, big_enough=1)` - Generate hunks  
- `matches(prev_array, next_array)` - Get matching index pairs
- `match_ratio(prev_array, next_array)` - Calculate similarity ratio

### Data Types

- `Hunk` - Contiguous diff region with ranges
- `MatchingBlock` - Matching subsequence (prev_start, next_start, length)
- Range types: `Same`, `Prev`, `Next`, `Replace`


## Project Structure

```
src/                      # Python package (11 modules)
├── patience_diff.py      # Core algorithm (700+ lines)
├── plain_diff.py         # Myers fallback
├── hunk.py               # Hunk data structures
├── hunks.py              # Hunk utilities
├── matching_block.py     # Matching block type
├── range.py              # Range types
├── move_id.py            # Move identifiers
├── move_kind.py          # Move classification
├── patience_diff_intf.py # Interface definitions
├── patience_diff_lib.py  # Library exports
└── __init__.py           # Package initialization

test/                     # Test suite
├── test_limit_context.py
├── test_merge_diff.py
└── test_plain_diff_cutoff.py

Makefile                  # Build automation
setup.py                  # Package setup
pyproject.toml            # Build configuration
README.md
```


## Testing

All tests passing:

```bash
$ make test
test/test_limit_context.py PASSED
test/test_merge_diff.py PASSED
test/test_plain_diff_cutoff.py PASSED

============================  3 passed  ============================
```


## Algorithm

The Patience Diff algorithm works in several steps:

1. Identify unique elements (appearing exactly once in both sequences)
2. Build longest increasing subsequence (LIS) of unique matches using patience sorting
3. Recursively find matches in gaps between LIS elements
4. Remove spurious small matches ("semantic cleanup")
5. Merge adjacent blocks separated by identical elements
6. Convert matching blocks to hunks with Same/Prev/Next/Replace ranges


## References

- http://bazaar-vcs.org - Original implementation
- Eugene W. Myers: "An O(ND) Difference Algorithm and Its Variations"

