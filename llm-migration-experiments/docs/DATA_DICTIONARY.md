# Data Dictionary

## Generation Records

Generation or retrieval records are keyed by `snippet_id`. Depending on the condition, records include the source code, rendered prompt or prompt context, detected pandas APIs, retrieved or mapped knowledge, generated Polars code, model metadata, and retrieval diagnostics.

Exp2 additionally stores the raw Responses API object. The public copy retains response metadata, output text, and reasoning-token counts. Opaque `encrypted_content` fields were removed because they cannot be interpreted and can trigger false-positive secret scans; no plaintext chain-of-thought was available or removed.

## Test Results

| Field | Description |
|---|---|
| `condition` | Experimental condition. |
| `notebook` | Test notebook filename. |
| `snippet_id` | Stable migration snippet identifier. |
| `func_name` | Function or fragment identifier used by the harness. |
| `l1_raw`, `l2_raw`, `l3_raw` | Raw pass, fail, skip, or unassessed state. |
| `l1_pass`, `l2_pass`, `l3_pass` | Numeric layer result where assessed. |
| `all_pass` | Whether all required evaluation layers passed. |
| `excluded` | Dataset-level exclusion indicator. |
| `notes` | Harness or review notes. |

## Combined Results

`shared/results/all_conditions_test_results_v3.csv` contains 952 rows: 238 snippets for each of four conditions. Exactly seven rows per condition have `excluded = 1`; analyses use the remaining 231 rows per condition.
