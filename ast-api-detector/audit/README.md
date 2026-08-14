# Audit Material

`ast_detection_gold_review.xlsx` is the human-readable AST evaluation workbook. Its `per_snippet` sheet contains all 238 source snippets, AST-detected pandas APIs, manually annotated gold pandas APIs, parse and set-match status, TP/FP/FN assignments, and per-snippet precision, recall, and F1. Its `summary` sheet contains the formal aggregate and receiver-family metrics. It intentionally contains no Polars APIs or generated migration outputs.

`parse_failures.csv` is a filtered view of the stored formal comparison table. It identifies the 21 snippets for which AST construction failed and records their gold-set size, false-negative count, set-comparison outcome, and gold APIs.

The thesis groups the observed syntax problems into retained indentation, missing initial receivers in method chains, dangling continuations, incomplete compound statements, and malformed multiline expressions. Those causes were established through manual inspection. The archived comparison table does not contain a row-level reason field, so this release does not assign an undocumented reason label to individual snippets.
