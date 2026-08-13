# AST-Based pandas API Detector

This directory contains the AST detector, input snapshot, manually annotated gold labels, and stored evaluation outputs used for the thesis evaluation of pandas API detection.

## Contents

- `src/ast_api_locator.py`: detector implementation.
- `data/input/snippets.csv`: the 238 pandas snippets evaluated by the detector.
- `data/mapping/api_mapping.json`: mapping records used to construct receiver-specific API maps.
- `data/gold/ast_gold_labels.csv`: manually annotated pandas API sets.
- `results/ast_detections.jsonl`: AST fields extracted from the previously stored experiment output. This file was not regenerated for this release.
- `results/ast_gold_comparison.csv`: stored snippet-level comparison with the gold labels.
- `results/ast_gold_summary.csv`: stored aggregate and receiver-family metrics.
- `results/ast_gold_summary.md`: readable summary of the stored metrics.
- `docs/METHOD.md`: detector and evaluation methodology.
- `docs/RESULTS.md`: verified headline results.
- `docs/DATA_DICTIONARY.md`: field definitions.
- `docs/thesis_tables.tex`: LaTeX tables corresponding to the reported results.
- `scripts/`: reusable detector and evaluation utilities.
- `tests/`: focused regression tests, including a non-pandas negative case.

## Stored Results

The primary evaluation covers all 238 snippets, including 21 snippets that could not be parsed as complete Python syntax units. The stored results contain 457 true positives, 89 false positives, and 105 false negatives, giving a micro-averaged precision of 83.7%, recall of 81.3%, and F1 score of 82.5%.

The successfully parsed subset contains 217 snippets. Its precision is 83.7%, recall is 89.8%, and F1 score is 86.6%.

## Reproduction Utilities

The repository includes scripts that can rerun the detector and recompute the comparison if independent reproduction is desired. The files under `results/` are the previously stored formal outputs rather than outputs generated while preparing this release.

```bash
python3 -m unittest discover -s tests
```

```bash
python3 scripts/run_detector.py \
  --input data/input/snippets.csv \
  --mapping data/mapping/api_mapping.json \
  --output results/reproduced_ast_detections.jsonl
```

```bash
python3 scripts/evaluate_against_gold.py \
  --gold data/gold/ast_gold_labels.csv \
  --detections results/reproduced_ast_detections.jsonl \
  --details results/reproduced_ast_gold_comparison.csv \
  --summary results/reproduced_ast_summary.csv
```

## Version Note

The mapping snapshot included here contains 765 JSON records. This is the actual count in the archived file used for this release.
