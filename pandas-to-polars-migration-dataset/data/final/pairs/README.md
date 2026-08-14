# Migration Pair Source Files

This directory contains one subdirectory for each of the 238 migration pairs. Every subdirectory is named with the pair's stable `snippet_id` and contains:

- `pandas.py`: the source pandas code fragment.
- `polars.py`: the corresponding developer-written Polars code fragment.

The files preserve the code stored in `../migration_pairs.csv`. They are extracted fragments rather than standalone programs, so some depend on imports, variables, indentation, functions, classes, or other context from their original repositories.
