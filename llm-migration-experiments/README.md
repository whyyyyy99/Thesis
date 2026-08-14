# LLM-Assisted pandas-to-Polars Migration Experiments

This repository snapshot contains the generation code, prompt material, stored outputs, three-layer tests, and review records for four experimental conditions evaluated on 238 migration snippets. Seven snippets lacked a defensible behavioural contract, leaving a common evaluation set of 231 snippets.

## Conditions

| Directory | Condition | Knowledge supplied |
|---|---|---|
| `baseline/` | Zero-shot Baseline | No external mapping or documentation knowledge |
| `exp1/` | AST-guided exact API mapping | Exact pandas-to-Polars mapping records |
| `exp2/` | Embedding-based documentation retrieval | Top-5 Polars documentation candidates per detected pandas API |
| `exp3/` | Mapping-guided hybrid retrieval | Static mappings, exact documentation lookup, and fallback retrieval |

All conditions used `gpt-5.4-mini` with low reasoning effort. The Baseline used a 4,000-token maximum output allowance; the augmented conditions used 6,000. The latest Exp2 rerun is the `reasoning_low_20260810` run. Older Exp2 generation and test results are intentionally excluded.

## Directory Layout

Each condition contains:

- `code/`: generation or retrieval implementation.
- `prompts/`: fixed template and rendered per-snippet prompts.
- `results/`: stored generation records, generated Python, and final test results.
- `tests/`: the isolated, manually reviewed notebooks used for the final test pass.
- `audit/`: condition-specific review material where available.

Files under `results/generated_py/` are preserved model outputs. Some are fragments that depend on enclosing code, and some contain syntax or indentation failures observed during evaluation. They are evidence, not a clean installable Python package, and have intentionally not been repaired.

The `shared/` directory contains the AST helper, documentation corpora, common evaluation scripts, the fixed seven-snippet exclusion list, review material, and a rebuilt 952-row cross-condition result table. The full static mapping table is stored under both `exp1/knowledge/` and `exp3/knowledge/`, the two conditions that use it. The source-only registry used for shared AST normalisation is stored in the separate `ast-api-detector/` package.

Each condition's `results/taxonomy_classification_final.csv` contains one row for every primary migration failure in that condition. `shared/results/all_conditions_taxonomy_classification_final.csv` combines the four conditions using the latest Exp2 rerun, while `shared/results/all_conditions_taxonomy_summary.csv` contains the corresponding category counts.

## Final End-to-End Results

| Condition | Passes | Pass rate | Rescued | Regressed |
|---|---:|---:|---:|---:|
| Baseline | 170/231 | 73.6% | -- | -- |
| Exp1 | 172/231 | 74.5% | 18 | 16 |
| Exp2 | 174/231 | 75.3% | 23 | 19 |
| Exp3 | 170/231 | 73.6% | 17 | 17 |

The paired comparisons did not identify a statistically significant improvement over the Baseline after Holm correction.

## Latest Exp2

The Exp2 package contains 238 rendered prompts, 238 raw Responses API objects, 238 generated Python files, and the final manually reviewed test and taxonomy outputs. `exp2/results/exp2_final_summary.json` is the concise final result summary, `exp2_test_results_reviewed_238.csv` contains the reviewed per-snippet outcomes, and `taxonomy_classification_final.csv` contains the 57 final primary-failure classifications. The run manifest records:

- requested model: `gpt-5.4-mini`
- actual model snapshot: `gpt-5.4-mini-2026-03-17`
- API: Responses API
- reasoning effort: `low`
- maximum output tokens: 6,000
- retrieval depth: top 5
- completed responses: 238/238

## Important Data Note

The previously stored combined CSV excluded 27 snippets and contained only Exp2 rows. It is not included. `shared/results/all_conditions_test_results_v3.csv` was rebuilt from the four authoritative condition-specific V3 tables while applying the same seven dataset-level exclusions to every condition. No model generation or test execution was performed during this rebuild.

## Credentials

No API keys are included. Generation scripts read `OPENAI_API_KEY` from the environment.

Machine-specific paths were replaced with `<PROJECT_ROOT>` in archived notebooks and manifests. Configure these placeholders before rerunning the notebooks.
