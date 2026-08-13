# Stored Evaluation Results

## API-Level Performance

| Metric | Result |
|---|---:|
| Snippets | 238 |
| Gold API assignments | 562 |
| Detected API assignments | 546 |
| True positives | 457 |
| False positives | 89 |
| False negatives | 105 |
| Precision | 83.7% |
| Recall | 81.3% |
| F1 | 82.5% |

## Parsing Diagnostics

| Metric | Result |
|---|---:|
| Successfully parsed | 217 (91.2%) |
| Parse failures | 21 (8.8%) |
| Parse-success precision | 83.7% |
| Parse-success recall | 89.8% |
| Parse-success F1 | 86.6% |

Fourteen parse-failed snippets had non-empty gold sets containing 53 API assignments. The remaining seven parse-failed snippets had empty gold and detected sets.

## Snippet-Level Set Comparison

| Outcome | Snippets | Percentage |
|---|---:|---:|
| Exact match | 155 | 65.1% |
| Partial match | 52 | 21.8% |
| False-negative only | 17 | 7.1% |
| False-positive only | 13 | 5.5% |
| Disjoint | 1 | 0.4% |
| Total | 238 | 100.0% |

Twenty-three exact matches were empty--empty comparisons. Seven of these occurred in parse-failed snippets and therefore indicate set equality rather than successful parsing.

## Receiver Families

| Family | Gold | Detected | TP | FP | FN | Precision | Recall | F1 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| DataFrame | 329 | 340 | 285 | 55 | 44 | 0.838 | 0.866 | 0.852 |
| DataFrameGroupBy | 10 | 10 | 9 | 1 | 1 | 0.900 | 0.900 | 0.900 |
| Index/MultiIndex | 13 | 4 | 2 | 2 | 11 | 0.500 | 0.154 | 0.235 |
| Series | 131 | 119 | 93 | 26 | 38 | 0.782 | 0.710 | 0.744 |
| SeriesGroupBy | 6 | 6 | 6 | 0 | 0 | 1.000 | 1.000 | 1.000 |
| Top-level pandas | 73 | 67 | 62 | 5 | 11 | 0.925 | 0.849 | 0.886 |
