# Data Dictionary

## `data/input/snippets.csv`

| Field | Description |
|---|---|
| `snippet_id` | Stable identifier for one migration snippet. |
| `pandas_code` | Source pandas snippet supplied to the detector. |

## `data/gold/ast_gold_labels.csv`

| Field | Description |
|---|---|
| `snippet_id` | Stable snippet identifier. |
| `gold_detected_pandas_apis` | Manually annotated canonical pandas APIs, separated by newlines. |

## `results/ast_detections.jsonl`

| Field | Description |
|---|---|
| `snippet_id` | Stable snippet identifier. |
| `normalized_apis` | Sorted canonical pandas APIs detected in the snippet. |
| `operation_keywords` | Accessor, window, or operation keywords collected by the detector. |
| `pandas_aliases` | Module aliases introduced by pandas imports. |
| `from_pandas` | Names imported directly from pandas. |
| `df_vars` | Variables inferred to contain DataFrame receivers. |
| `series_vars` | Variables inferred to contain Series receivers. |
| `groupby_vars` | Variables inferred to contain GroupBy receivers. |
| `unknown_methods` | Methods observed on tracked receivers but not normalised to a known API. |
| `parse_success` | Whether Python's AST parser accepted the snippet. |

## `results/ast_gold_comparison.csv`

This stored table contains one row per snippet, parse status, gold and detected counts, TP/FP/FN counts, exact-match status, set-comparison outcome, canonical API sets, and unresolved methods.

## `results/ast_gold_summary.csv`

This stored table contains the overall micro-average, parse-success and parse-failure diagnostics, and receiver-family assignment metrics.
