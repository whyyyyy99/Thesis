# Method

## Detection

The detector parses each snippet with Python's standard `ast` module. It collects pandas import aliases, tracks DataFrame, Series, and GroupBy variables, recursively infers receiver families, and normalises recognised calls against receiver-specific maps derived from `api_mapping.json`.

The supported receiver families are top-level pandas functions, DataFrame methods, Series methods, DataFrameGroupBy methods, SeriesGroupBy methods, and Index or MultiIndex methods. The detector also records accessor and window-operation keywords and methods whose receiver can be followed but whose canonical API cannot be resolved.

Calls on explicitly imported non-pandas modules are excluded. A parsing failure returns an empty detected API set and `parse_success = false`.

## Evaluation Unit

For snippet `i`, `G_i` is the manually annotated set of canonical pandas APIs and `D_i` is the detected set. Repeated calls to the same canonical API within one snippet count once. The same API in different snippets counts as a separate snippet--API assignment.

Micro-averaged counts are calculated as:

```text
TP = sum_i |G_i intersect D_i|
FP = sum_i |D_i minus G_i|
FN = sum_i |G_i minus D_i|
```

Precision, recall, and F1 are calculated from these aggregate assignment counts. The primary evaluation includes all 238 snippets. A separate parse-success diagnostic reports performance for the 217 snippets for which an AST was constructed.

## Snippet-Level Outcomes

Each snippet is assigned to one of five mutually exclusive outcomes:

- `exact`: detected and gold sets are equal, including empty--empty sets.
- `partial`: the sets overlap but are not equal.
- `false-negative only`: the gold set is non-empty and the detected set is empty.
- `false-positive only`: the gold set is empty and the detected set is non-empty.
- `disjoint`: both sets are non-empty but have no API in common.

Canonical-name comparison removes a historical `pandas.` prefix from DataFrameGroupBy and SeriesGroupBy records so that mapping-derived detector names and gold labels use the same representation.
