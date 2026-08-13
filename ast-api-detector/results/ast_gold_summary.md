# Latest AST detection versus manual gold labels

The comparison covers all 238 snippets. API order and duplicate mentions are ignored.

| Scope | Gold | Detected | TP | FP | FN | Precision | Recall | F1 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| all APIs (micro) | 562 | 546 | 457 | 89 | 105 | 0.837 | 0.813 | 0.825 |
| parse-success snippets (micro) | 509 | 546 | 457 | 89 | 52 | 0.837 | 0.898 | 0.866 |
| parse-failed snippets (micro) | 53 | 0 | 0 | 0 | 53 | 0.000 | 0.000 | 0.000 |
| DataFrame | 329 | 340 | 285 | 55 | 44 | 0.838 | 0.866 | 0.852 |
| DataFrameGroupBy | 10 | 10 | 9 | 1 | 1 | 0.900 | 0.900 | 0.900 |
| Index/MultiIndex | 13 | 4 | 2 | 2 | 11 | 0.500 | 0.154 | 0.235 |
| Series | 131 | 119 | 93 | 26 | 38 | 0.782 | 0.710 | 0.744 |
| SeriesGroupBy | 6 | 6 | 6 | 0 | 0 | 1.000 | 1.000 | 1.000 |
| top-level pandas | 73 | 67 | 62 | 5 | 11 | 0.925 | 0.849 | 0.886 |

Exact API-set matches: **155/238 (65.1%)**.
AST parse failures: **21**.
