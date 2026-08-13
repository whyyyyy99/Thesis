# LLMs for Data Engineering Library Migration

This repository contains the dataset, AST-based API detector, and experimental artifacts accompanying a thesis on LLM-assisted pandas-to-Polars migration.

## Repository Contents

- `pandas-to-polars-migration-dataset/`: 238 migration pairs collected from open-source GitHub repositories, category labels, audit records, and dataset-construction scripts.
- `ast-api-detector/`: detector implementation, manually reviewed labels, evaluation outputs, and documentation.
- `llm-migration-experiments/`: generation code, rendered prompts, generated migrations, three-layer tests, manual review files, and final results for the Baseline and three knowledge-augmented conditions.

The migration experiments generated outputs for all 238 snippets. Seven snippets lacked a defensible executable and behavioural contract, leaving a common evaluation set of 231 snippets. The latest Exp2 rerun is included.

Each directory contains its own README and provenance information. No API credentials are included; generation scripts expect `OPENAI_API_KEY` to be supplied through the environment.
