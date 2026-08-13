# Final Result Summary

## Conditional Layer Performance

| Condition | L1 pass | L2 pass given L1 | L3 pass given L2 | End-to-end |
|---|---:|---:|---:|---:|
| Baseline | 205/231 (88.7%) | 179/205 (87.3%) | 170/179 (95.0%) | 170/231 (73.6%) |
| Exp1 | 205/231 (88.7%) | 178/205 (86.8%) | 172/178 (96.6%) | 172/231 (74.5%) |
| Exp2 | 199/231 (86.1%) | 178/199 (89.4%) | 174/178 (97.8%) | 174/231 (75.3%) |
| Exp3 | 200/231 (86.6%) | 175/200 (87.5%) | 170/175 (97.1%) | 170/231 (73.6%) |

## Primary Outcomes

| Condition | End-to-end pass | Primary L1 | Primary L2 | Primary L3 |
|---|---:|---:|---:|---:|
| Baseline | 170 | 26 | 26 | 9 |
| Exp1 | 172 | 26 | 27 | 6 |
| Exp2 | 174 | 32 | 21 | 4 |
| Exp3 | 170 | 31 | 25 | 5 |

Each row sums to the 231 evaluation-valid snippets.

## Paired Changes from the Baseline

| Condition | Difference | Rescued | Regressed |
|---|---:|---:|---:|
| Exp1 | +0.9 percentage points | 18 | 16 |
| Exp2 | +1.7 percentage points | 23 | 19 |
| Exp3 | 0.0 percentage points | 17 | 17 |
