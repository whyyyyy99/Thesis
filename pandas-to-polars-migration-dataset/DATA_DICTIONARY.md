# Data dictionary

## Identity and provenance

- `snippet_id`: stable identifier used throughout the study.
- `repository`: GitHub repository in `owner/name` form.
- `repository_url`: repository URL.
- `commit_sha`: full migration commit SHA.
- `commit_url`: URL of the migration commit.
- `source_file`: encoded source-file location recorded during extraction.

## Migration pair

- `pandas_code`: pandas source snippet supplied to the migration model.
- `polars_code`: corresponding developer-written Polars implementation.
- `migration_diff`: extracted before/after diff for the pair.
- `snippet_note`: short extraction note from dataset construction.

## Labels

- `pandas_api_labels`: manually reviewed pandas API-family labels.
- `polars_api_labels`: manually reviewed Polars API-family labels.
- `migration_categories`: canonical semicolon-separated migration categories.
- `category_*`: Boolean indicators for each category in the multi-label taxonomy.
- `migration_pattern_note`: manual description of the migration pattern.

## Evaluation eligibility

- `evaluation_valid`: whether the pair entered the 231-pair behavioural evaluation.
- `evaluation_status`: `valid`, `valid_after_harness_audit`, or
  `evaluation_invalid`.
- `evaluation_audit_evidence`: evidence recorded during the shared harness audit.
- `evaluation_audit_action`: corrective action or exclusion decision recorded by
  the audit.

Evaluation eligibility is not a dataset-validity label. All 238 rows are verified
migration pairs. The seven `evaluation_invalid` rows were excluded only because
their isolated fragments did not retain enough context for defensible executable
behavioural scoring.
