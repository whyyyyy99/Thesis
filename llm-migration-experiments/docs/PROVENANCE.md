# File Provenance

## Baseline

- Generation code: cleaned copy of `baseline_zero_shot_generation.ipynb`.
- Prompt: fixed `zero_shot_v1` user template from the generation notebook.
- Generation records: path-normalised view of the stored 238-row `generated_outputs/results.jsonl`.
- Final tests: `baseline_test_results_v3.csv`.

## Exp1

- Generation code: `run_exp1_ast_guided.py`, `exact_mapping_pipeline.py`, and the prompt template.
- Static knowledge source: `exp1/knowledge/api_mapping.json`.
- Generation records: 238 final snippet records selected from the stored historical JSON using the final dataset identifiers; no generation was rerun.
- Generated Python: 238 stored files.
- Final tests: `exp1_test_results_v3.csv`.

## Exp2

- Generation directory: `exp2_v2_reasoning_low_20260810`.
- Final evaluation directory: `test_rerun_exp2_reasoning_low_20260810/outputs/final`.
- Retrieval input fields were recorded as identical to the earlier Exp2 V2 retrieval run; generation was rerun with the Responses API and low reasoning effort.
- Exp2 did not use target-side mapping records for retrieval or prompt augmentation. The release reproduction script uses the source-only API registry in the sibling `ast-api-detector/` directory for shared API normalisation.
- The package includes the run and preparation manifests, validation summary, complete manual review, structural audit, final primary outcomes, and final taxonomy files.

## Exp3

- Generation code: `run_exp3_v2.py`, `hybrid_pipeline.py`, and the stored prompt template.
- Static knowledge source: `exp3/knowledge/api_mapping.json`, an identical copy of the mapping used by Exp1.
- Retrieval/generation records and generated Python: 238 stored entries.
- Final tests: `exp3_test_results_v3.csv`.

## Shared Evaluation

The 952-row combined table was assembled from the four condition-specific V3 files. The 231 evaluation-valid identifiers were taken from the final migration dataset, ensuring that exactly the same seven snippets are excluded in every condition.
