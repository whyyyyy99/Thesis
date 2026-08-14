# Exp2 Audit Material

- `all_238_manual_review.csv`: final per-snippet manual review of the rerun tests, including the primary layer, category, cascade assessment, evidence, and action.
- `structural_audit.csv`: structural checks confirming notebook alignment, generated wrappers, cleared outputs, and L1--L3 markers.
- `preparation_manifest.json`: provenance for constructing the isolated rerun workspace.
- `taxonomy_manual_overrides.csv`: cases in which manual review replaced the initial rule-based category.
- `taxonomy_summary_before_manual_review.csv`: intermediate category counts before the manual overrides. This file is retained as audit history and is not the final taxonomy summary.

The final reviewed results are stored under `../results/`. Earlier gold/silver API scoring and RRF document-retrieval workbooks were removed because they do not describe the latest all-mpnet cosine-retrieval rerun.
