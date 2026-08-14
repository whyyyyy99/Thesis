# pandas-to-Polars Migration Dataset

This release contains 238 pandas-to-Polars migration pairs extracted from
developer-authored changes in open-source GitHub repositories. Each pair includes
the pandas source snippet, the corresponding developer-written Polars snippet,
repository and commit provenance, API labels, and one or more migration-category
labels. Of the 238 pairs, 231 support the executable behavioural evaluation used
in the thesis.

## Layout

- `data/final/migration_pairs.csv`: canonical 238-pair table.
- `data/final/migration_pairs.xlsx`: Excel version of the canonical table.
- `data/final/pairs/`: 238 directories containing the paired `pandas.py` and
  `polars.py` source fragments.
- `data/final/migration_category_counts.csv`: full-dataset category counts.
- `data/source/`: candidate pull-request records used to identify repositories.
- `data/intermediate/`: selected commit, file, and pair inventories.
- `audit/`: manual pair-validation and category-review workbooks.
- `scripts/`: cleaned scripts for collection, detection, inventory construction,
  and final-table assembly.

## Rebuilding the final table

Run from the thesis data workspace:

```bash
python github_release/dataset/scripts/build_final_dataset.py \
  --workspace . \
  --output-dir github_release/dataset/data/final
```

GitHub API access is read from the `GITHUB_TOKEN` environment variable. No
credentials are stored in this release.

The two mining rounds can be reproduced structurally with:

```bash
python scripts/collect_pull_requests.py \
  --start-year 2023 --end-year 2024 \
  --output data/source/candidate_pull_requests_round1_new.csv

python scripts/collect_pull_requests.py \
  --start-year 2025 --end-year 2025 \
  --output data/source/candidate_pull_requests_round2_new.csv
```

The checked-in source tables are the archived records used by the study. A new
GitHub API run may return different records because repositories, pull requests,
and search indexing can change over time.

## Category labels

The migration taxonomy is multi-label. A pair can therefore belong to more than
one of the following categories:

- Core dataframe transformations
- Index and row semantics
- Aggregation and combination
- IO boundaries
- Types, schemas, and temporal operations
- UDF and custom-logic rewrites
- Lazy execution and evaluation strategy
- Missing and null semantics
- Import and setup only
- Reshaping
- Other/manual

The `migration_categories` column contains a semicolon-separated canonical list.
The corresponding Boolean columns support direct filtering and aggregation.

## Evaluation status

`evaluation_valid` identifies the 231 pairs included in the final behavioural
evaluation. The remaining seven pairs remain part of the 238-pair dataset but
were excluded from behavioural scoring because their isolated snippets did not
retain a defensible executable and observable contract.
