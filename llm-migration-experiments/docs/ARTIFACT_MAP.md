# Canonical Artifact Map

This page identifies the files that should be used to reproduce the thesis
tables. Audit and provenance files remain available, but are not interchangeable
with the canonical results below.

## Common inputs

- Final dataset and evaluation status:
  `../pandas-to-polars-migration-dataset/data/final/migration_pairs.csv`
- Shared API labels used by the knowledge-profile analyses:
  `shared/input/gold_labels_review.csv`
- Pandas and Polars documentation corpora: `shared/knowledge/`

The final seven-snippet exclusion is defined only by `evaluation_valid` in the
final migration dataset. The older `exclude` column in
`shared/input/gold_labels_review.csv` describes an earlier screening stage.

## Condition results

| Condition | Canonical test results | Final taxonomy |
|---|---|---|
| Baseline | `baseline/results/test_results_v3.csv` | `baseline/results/taxonomy_classification_final.csv` |
| Exp1 | `exp1/results/test_results_v3.csv` | `exp1/results/taxonomy_classification_final.csv` |
| Exp2 | `exp2/results/test_results_v3.csv` | `exp2/results/taxonomy_classification_final.csv` |
| Exp3 | `exp3/results/test_results_v3.csv` | `exp3/results/taxonomy_classification_final.csv` |

Exp2 is the `reasoning_low_20260810` rerun. Its reviewed 238-row source table is
`exp2/results/exp2_test_results_reviewed_238.csv`; the normalised V3 file in the
table above is the canonical input for cross-condition analysis.

## Cross-condition results

- `shared/results/all_conditions_test_results_v3.csv`: 952 rows, including the
  same seven excluded snippets in each condition.
- `shared/results/all_conditions_taxonomy_classification_final.csv`: 238 primary
  failure classifications.
- `shared/results/all_conditions_taxonomy_summary.csv`: taxonomy counts.
- `shared/results/migration_category_performance.csv`: the migration-category
  table reported in the thesis.
- `shared/results/knowledge_profile_outcomes.csv`: the Exp1 mapping, Exp2
  retrieval, and Exp3 routing profile outcome tables.

## Generation evidence

- Baseline: `baseline/results/generation_records.jsonl`
- Exp1: `exp1/results/generation_records.jsonl` and `exp1/results/generated_py/`
- Exp2: `exp2/results/experiment2_outputs.jsonl`,
  `exp2/results/raw_responses/`, and `exp2/results/generated_py/`
- Exp3: `exp3/results/retrieval_results.jsonl` and
  `exp3/results/generated_py/`

Rendered prompts are stored under each condition's `prompts/rendered/`
directory. Test notebooks are stored under each condition's `tests/` directory.
