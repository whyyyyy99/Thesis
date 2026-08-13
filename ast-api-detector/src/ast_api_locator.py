"""
AST-based pandas API extractor.

Extracts normalized pandas API names from source code snippets,
handling import aliases, data flow tracking, call chains, Series-level
calls, accessor patterns (.str / .dt / .cat), and window chains
(.rolling / .resample / .expanding / .ewm).

Maps are built dynamically from a knowledge base JSON (recommended).
A minimal hardcoded fallback is used when no JSON is provided.

Usage:
    from ast_api_locator import build_maps_from_json, extract_pandas_api_details

    maps = build_maps_from_json("path/to/api_mapping.json")
    details = extract_pandas_api_details(code, maps=maps)
    apis = details["normalized_apis"]
"""

import ast
import json
import textwrap
from typing import Dict, List, Optional, Set, Tuple


# ── APIMaps ────────────────────────────────────────────────────────────

class APIMaps:
    """Normalization maps derived from a knowledge base."""

    def __init__(
        self,
        top_level: Dict[str, str],
        df_method: Dict[str, str],
        df_groupby_method: Dict[str, str],
        series_method: Optional[Dict[str, str]] = None,
        series_groupby_method: Optional[Dict[str, str]] = None,
        index_method: Optional[Dict[str, str]] = None,
        accessor_map: Optional[Dict[str, str]] = None,
    ):
        self.top_level = top_level                          # pd.xxx        → canonical
        self.df_method = df_method                          # df.xxx        → canonical
        self.df_groupby_method = df_groupby_method          # df.groupby(…).xxx → canonical
        self.series_method = series_method or {}             # df["c"].xxx  → canonical
        self.series_groupby_method = series_groupby_method or {}  # df["c"].groupby(…).xxx → canonical
        self.index_method = index_method or {}               # df.columns/.index.xxx → canonical
        self.accessor_map = accessor_map or {}               # "str.lower"  → canonical


# ── Build maps from knowledge base ────────────────────────────────────

def _parse_api_entry(
    api: str,
    top_level: Dict[str, str],
    df_method: Dict[str, str],
    df_groupby_method: Dict[str, str],
    series_method: Dict[str, str],
    series_groupby_method: Dict[str, str],
    index_method: Dict[str, str],
    accessor_map: Dict[str, str],
) -> None:
    """Classify one source_api string into the appropriate map."""
    api = api.split("(")[0].strip()   # strip parameters
    if not api:
        return

    # GroupBy entries (with or without pandas. prefix)
    if "GroupBy" in api:
        method = api.split(".")[-1]
        # DataFrameGroupBy vs SeriesGroupBy are tracked separately so that
        # e.g. df.groupby(...).agg(...) and df["c"].groupby(...).agg(...)
        # resolve to different canonical APIs instead of whichever the JSON
        # happened to list first.
        target = series_groupby_method if "SeriesGroupBy" in api else df_groupby_method
        if method and method not in target:
            target[method] = api
        return

    if not api.startswith("pandas."):
        return

    parts = api[len("pandas."):].split(".")

    if len(parts) == 1:
        # pandas.read_csv, pandas.DataFrame, pandas.merge …
        method = parts[0]
        if method:
            top_level[method] = api

    elif len(parts) == 2:
        obj_type, method = parts[0], parts[1]
        if obj_type == "DataFrame":
            # DataFrame always wins over a previously stored Series entry
            df_method[method] = api
        elif obj_type == "Series":
            series_method[method] = api
            # Keep df_method for this method only if DataFrame version already present
        elif obj_type in ("Index", "MultiIndex"):
            index_method[method] = api
        # Other object types (ExcelFile, …) – skip method tracking

    elif len(parts) == 3:
        obj_type, accessor, method = parts[0], parts[1], parts[2]
        if obj_type == "Series" and accessor in ("str", "dt", "cat"):
            # pandas.Series.str.lower → accessor_map["str.lower"]
            accessor_map[f"{accessor}.{method}"] = api


def build_maps_from_json(json_path: str) -> "APIMaps":
    """
    Build APIMaps from api_mapping.json, then merge with fallback maps.

    JSON-derived values override fallback for the same method name.
    Exact source_api strings from the JSON are preserved.
    Combined entries ("DataFrameGroupBy.agg / DataFrameGroupBy.aggregate")
    are split on " / " and each part is handled separately.
    """
    top_level: Dict[str, str] = {}
    df_method: Dict[str, str] = {}
    df_groupby_method: Dict[str, str] = {}
    series_method: Dict[str, str] = {}
    series_groupby_method: Dict[str, str] = {}
    index_method: Dict[str, str] = {}
    accessor_map: Dict[str, str] = {}

    with open(json_path, encoding="utf-8") as f:
        records = json.load(f)

    for record in records:
        source_api = record.get("source_api", "")
        for part in source_api.split("/"):
            _parse_api_entry(
                part.strip(),
                top_level, df_method, df_groupby_method,
                series_method, series_groupby_method, index_method, accessor_map,
            )

    # Inject historical aliases so old API names resolve to their canonical entries.
    # Each tuple: (old_name, new_name, map_dict) — only added if new_name exists.
    _ALIASES: List[tuple] = [
        ("tolist",     "to_list",   series_method),   # pandas.Series.tolist → to_list
        ("tolist",     "to_list",   index_method),     # pandas.Index.tolist → to_list
        ("iteritems",  "items",     df_method),        # deprecated in 1.5, removed in 2.0
        ("iteritems",  "items",     series_method),
    ]
    for old, new, m in _ALIASES:
        if new in m and old not in m:
            m[old] = m[new]

    json_maps = APIMaps(
        top_level, df_method, df_groupby_method,
        series_method, series_groupby_method, index_method, accessor_map,
    )
    return merge_api_maps(json_maps)


def merge_api_maps(
    primary: "APIMaps", fallback: Optional["APIMaps"] = None
) -> "APIMaps":
    """
    Merge two APIMaps.  primary overrides fallback for the same method name.
    When called from build_maps_from_json the fallback defaults to _FALLBACK_MAPS.
    """
    if fallback is None:
        fallback = _FALLBACK_MAPS

    def _merge(p: dict, f: dict) -> dict:
        merged = dict(f)   # start with fallback baseline
        merged.update(p)   # primary (JSON) overrides
        return merged

    return APIMaps(
        top_level=_merge(primary.top_level, fallback.top_level),
        df_method=_merge(primary.df_method, fallback.df_method),
        df_groupby_method=_merge(primary.df_groupby_method, fallback.df_groupby_method),
        series_method=_merge(primary.series_method, fallback.series_method),
        series_groupby_method=_merge(primary.series_groupby_method, fallback.series_groupby_method),
        index_method=_merge(primary.index_method, fallback.index_method),
        accessor_map=_merge(primary.accessor_map, fallback.accessor_map),
    )


# ── Minimal fallback maps ──────────────────────────────────────────────

_FALLBACK_MAPS = APIMaps(
    top_level={
        "read_csv": "pandas.read_csv", "read_excel": "pandas.read_excel",
        "read_json": "pandas.read_json", "read_parquet": "pandas.read_parquet",
        "read_feather": "pandas.read_feather", "read_hdf": "pandas.read_hdf",
        "read_sql": "pandas.read_sql", "read_pickle": "pandas.read_pickle",
        "read_table": "pandas.read_table", "read_html": "pandas.read_html",
        "DataFrame": "pandas.DataFrame", "Series": "pandas.Series",
        "Index": "pandas.Index", "MultiIndex": "pandas.MultiIndex",
        "merge": "pandas.merge", "concat": "pandas.concat",
        "pivot_table": "pandas.pivot_table", "get_dummies": "pandas.get_dummies",
        "to_datetime": "pandas.to_datetime", "to_numeric": "pandas.to_numeric",
        "isna": "pandas.isna", "notna": "pandas.notna",
        "cut": "pandas.cut", "qcut": "pandas.qcut",
        "melt": "pandas.melt", "crosstab": "pandas.crosstab",
    },
    df_method={m: f"pandas.DataFrame.{m}" for m in [
        "groupby", "agg", "reset_index", "set_index", "sort_values",
        "drop", "dropna", "fillna", "rename", "astype", "apply",
        "merge", "join", "pivot", "melt", "stack", "unstack",
        "value_counts", "describe", "copy", "to_csv", "to_parquet",
        "ffill", "bfill", "replace", "assign", "query", "explode",
        "rolling", "expanding", "ewm", "resample",
    ]},
    df_groupby_method={m: f"DataFrameGroupBy.{m}" for m in [
        "sum", "mean", "count", "size", "min", "max", "std", "var",
        "median", "nunique", "first", "last", "agg", "apply", "transform",
    ]},
    series_method={m: f"pandas.Series.{m}" for m in [
        "value_counts", "map", "apply", "astype", "fillna", "dropna",
        "sort_values", "head", "tail", "unique", "nunique", "str",
        "dt", "cat", "isin", "between", "replace", "cumsum",
    ]},
    series_groupby_method={m: f"SeriesGroupBy.{m}" for m in [
        "sum", "mean", "count", "size", "min", "max", "std", "var",
        "median", "nunique", "first", "last", "agg", "apply", "transform",
    ]},
    index_method={m: f"pandas.Index.{m}" for m in [
        "to_list", "astype", "isin", "unique", "nunique",
        "get_loc", "difference", "union", "intersection", "drop",
        "drop_duplicates", "sort_values", "to_numpy", "map", "values",
    ]},
    accessor_map={},
)


# ── Internal sets ──────────────────────────────────────────────────────

_DF_CONSTRUCTORS: Set[str] = {
    "DataFrame", "read_csv", "read_excel", "read_json", "read_parquet",
    "read_feather", "read_orc", "read_stata", "read_sas", "read_html",
    "read_xml", "read_hdf", "read_sql", "read_sql_table", "read_sql_query",
    "read_clipboard", "read_table", "read_fwf", "read_pickle",
    "merge", "merge_asof", "merge_ordered", "concat", "crosstab",
    "pivot_table", "get_dummies", "from_dummies", "json_normalize",
    "wide_to_long",
}

_DF_RETURNING: Set[str] = {
    "reset_index", "set_index", "sort_values", "sort_index",
    "drop", "drop_duplicates", "dropna", "fillna", "ffill", "bfill",
    "rename", "astype", "assign", "query", "merge", "join", "pivot",
    "pivot_table", "melt", "stack", "unstack", "explode", "apply",
    "transform", "replace", "where", "mask", "clip", "head", "tail",
    "sample", "nlargest", "nsmallest", "copy", "transpose", "diff",
    "cumsum", "cumprod", "cummax", "cummin", "shift",
    "eval", "reindex", "select_dtypes", "convert_dtypes",
    "compare", "combine", "combine_first", "filter",
    "add_prefix", "add_suffix", "round", "abs", "pipe",
    "pct_change", "rolling", "expanding", "ewm", "resample",
    "xs", "swaplevel", "reorder_levels",
}

_COMMON_DF_NAMES: Set[str] = {
    "df", "data", "frame", "table", "result", "results", "output",
    "merged", "filtered", "cleaned", "grouped", "pivoted", "joined",
    "df1", "df2", "df3", "left", "right", "tmp", "temp",
}

_WINDOW_STARTERS: Set[str] = {"rolling", "expanding", "ewm", "resample"}
_ACCESSOR_NAMES: Set[str] = {"str", "dt", "cat"}

# Methods whose result has the same DataFrame-vs-Series "shape" as their receiver
# (df.method() -> DataFrame, series.method() -> Series). Used to propagate an
# inferred type through a chain of calls (e.g. df.pop("c").map(...).apply(...)).
_TYPE_PRESERVING: Set[str] = _DF_RETURNING | {
    "map", "isin", "between", "value_counts", "unique", "nunique",
    "to_list", "tolist", "items", "keys", "duplicated",
    "idxmax", "idxmin", "mode", "interpolate", "notna", "isna",
}

# DataFrame methods that return a Series (change shape rather than preserve it).
_DF_TO_SERIES: Set[str] = {"pop", "squeeze"}

# Method/property names distinctive enough on their own to be trusted as
# pandas even when the receiver is an untracked bare Name (e.g. a function
# parameter, or a variable from an unrecognized call/attribute chain like
# `self.get_lookup()`). These are essentially never defined on non-pandas
# objects, so `some_untracked_var.groupby(...)` is still worth detecting
# rather than silently dropped - as long as the receiver isn't itself a
# plain imported module (see `_collect_module_aliases`), which rules out
# stdlib false-positives like `itertools.groupby(...)` / `os.rename(...)`.
_DISTINCTIVE_DF_METHODS: Set[str] = {
    "groupby", "sort_values", "set_index", "merge", "drop_duplicates",
    "itertuples", "iterrows", "pivot_table", "value_counts",
    "to_csv", "to_parquet", "to_excel", "to_sql", "to_frame",
    "drop", "rename",
}
_DISTINCTIVE_DF_PROPERTIES: Set[str] = {"columns", "loc", "iloc", "index"}

# Names recognized as real DataFrame methods/properties. Anything else
# accessed as `df.<attr>` (not a call, not one of these) is - per pandas'
# own semantics - dot-notation column access (`df.value` <=> df["value"]),
# which returns a Series. Used by `_infer_type` below.
_KNOWN_DF_ATTRS: Set[str] = (
    _TYPE_PRESERVING | _DISTINCTIVE_DF_PROPERTIES | _DISTINCTIVE_DF_METHODS
    | {"values", "shape", "dtypes", "empty", "ndim", "size", "at", "iat", "T"}
)


# ── Parsing helpers ────────────────────────────────────────────────────

def _dedent_body(code: str) -> str:
    lines = code.split("\n")
    import_lines, body_lines = [], []
    for line in lines:
        stripped = line.lstrip()
        if stripped.startswith(("import ", "from ")) or not stripped:
            import_lines.append(line)
        else:
            body_lines.append(line)
    if not body_lines:
        return code
    min_indent = min(
        (len(l) - len(l.lstrip()) for l in body_lines if l.strip()), default=0
    )
    dedented = [l[min_indent:] if len(l) >= min_indent else l for l in body_lines]
    return "\n".join(import_lines + dedented)


def _safe_parse(code: str) -> Optional[ast.Module]:
    def _variants(src: str) -> List[str]:
        base = [textwrap.dedent(src), src, _dedent_body(src)]
        padded = src + "\n    pass"
        base += [textwrap.dedent(padded), padded, _dedent_body(padded)]
        return base

    for v in _variants(code) + _variants(code.replace("...", "pass")):
        try:
            return ast.parse(v)
        except SyntaxError:
            pass
    return None


# ── Import collection ─────────────────────────────────────────────────

def _collect_pandas_aliases(tree: ast.Module) -> Set[str]:
    aliases: Set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name == "pandas" or alias.name.startswith("pandas."):
                    aliases.add(alias.asname or alias.name.split(".")[0])
    return aliases or {"pd"}


def _collect_module_aliases(tree: ast.Module) -> Set[str]:
    """All `import X [as Y]` module names/aliases (any module, not just pandas)."""
    aliases: Set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                aliases.add(alias.asname or alias.name.split(".")[0])
    return aliases


def _collect_from_pandas(tree: ast.Module) -> Set[str]:
    names: Set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            module = node.module or ""
            if module == "pandas" or module.startswith("pandas."):
                for alias in node.names:
                    names.add(alias.asname or alias.name)
    return names


# ── Data flow tracker ─────────────────────────────────────────────────

def _annotation_kind(ann) -> Optional[str]:
    """Classify a type annotation node as 'df' | 'series' | None."""
    if ann is None:
        return None
    if isinstance(ann, ast.Attribute):
        name = ann.attr
    elif isinstance(ann, ast.Name):
        name = ann.id
    elif isinstance(ann, ast.Constant) and isinstance(ann.value, str):
        name = ann.value.split(".")[-1].strip("'\"")   # quoted forward refs
    else:
        return None
    if name == "DataFrame":
        return "df"
    if name == "Series":
        return "series"
    return None


def _track_df_vars(
    tree: ast.Module, pd_aliases: Set[str], from_pandas: Set[str]
) -> Tuple[Set[str], Set[str], Set[str]]:
    df_vars: Set[str] = set()
    series_vars: Set[str] = set()
    gb_vars: Set[str] = set()

    def _is_df_call(node) -> bool:
        if not isinstance(node, ast.Call):
            return False
        func = node.func
        if isinstance(func, ast.Name):
            return func.id in from_pandas and func.id in _DF_CONSTRUCTORS
        # Delegate to `_infer_type`, which (unlike the old hand-rolled checks
        # here) also recurses through a Subscript in the middle of a chain -
        # e.g. `X.set_index(...)[["a","b"]].join(...)` - so the assigned
        # variable is still recognized as a DataFrame even when a column
        # subset selection sits between two chained calls.
        return _infer_type(node, pd_aliases, df_vars, gb_vars, series_vars) == "df"

    def _is_gb_call(node) -> bool:
        if not isinstance(node, ast.Call):
            return False
        func = node.func
        return isinstance(func, ast.Attribute) and func.attr == "groupby"

    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            # Type-annotated parameters (def f(x: pd.DataFrame, y: pd.Series))
            # are a strong, cheap signal that a bare-Name receiver can't be
            # recovered from local data flow alone (e.g. it's just a param).
            args = node.args
            all_args = [*args.posonlyargs, *args.args, *args.kwonlyargs]
            for a in all_args:
                kind = _annotation_kind(a.annotation)
                if kind == "df":
                    df_vars.add(a.arg)
                elif kind == "series":
                    series_vars.add(a.arg)
        elif isinstance(node, ast.Assign):
            val = node.value
            for target in node.targets:
                if isinstance(target, ast.Name):
                    if _is_df_call(val):
                        df_vars.add(target.id)
                    elif _infer_type(val, pd_aliases, df_vars, gb_vars, series_vars) == "series":
                        # Symmetric to _is_df_call above, but for the Series
                        # side: `diff = (a - b).dropna()` should make `diff`
                        # resolve as Series for later uses like `diff.size`,
                        # the same way a DataFrame-producing chain would.
                        series_vars.add(target.id)
                    if _is_gb_call(val):
                        gb_vars.add(target.id)
        elif isinstance(node, ast.AnnAssign):
            if isinstance(node.target, ast.Name):
                kind = _annotation_kind(node.annotation)
                if kind == "df":
                    df_vars.add(node.target.id)
                elif kind == "series":
                    series_vars.add(node.target.id)
                elif node.value:
                    if _is_df_call(node.value):
                        df_vars.add(node.target.id)
                    if _is_gb_call(node.value):
                        gb_vars.add(node.target.id)

    return df_vars, series_vars, gb_vars


# ── Chain inspection ──────────────────────────────────────────────────

def _is_pandas_receiver(
    node, pd_aliases: Set[str], df_vars: Set[str], gb_vars: Set[str],
    series_vars: Set[str] = frozenset(),
) -> bool:
    if isinstance(node, ast.Name):
        return (
            node.id in pd_aliases
            or node.id in df_vars
            or node.id in gb_vars
            or node.id in series_vars
            or node.id in _COMMON_DF_NAMES
        )
    # BinOp/Compare/BoolOp/UnaryOp cover arithmetic and boolean-mask
    # expressions between pandas objects, e.g. `(s1 - s2).abs()`,
    # `(x >= y).astype(int)`, `(~mask).sum()` - the result is only ever a
    # meaningful receiver for a further method call in a pandas context.
    return isinstance(
        node,
        (ast.Call, ast.Subscript, ast.Attribute, ast.BinOp, ast.Compare, ast.BoolOp, ast.UnaryOp),
    )


def _has_groupby_in_chain(node) -> bool:
    while True:
        if isinstance(node, ast.Call):
            func = node.func
            if isinstance(func, ast.Attribute) and func.attr == "groupby":
                return True
            node = func
        elif isinstance(node, ast.Attribute):
            node = node.value
        elif isinstance(node, ast.Subscript):
            node = node.value
        else:
            return False


def _receiver_is_groupby(node, gb_vars: Set[str]) -> bool:
    if isinstance(node, ast.Name) and node.id in gb_vars:
        return True
    if isinstance(node, ast.Subscript):
        return _receiver_is_groupby(node.value, gb_vars)
    return _has_groupby_in_chain(node)


def _get_window_in_chain(node) -> Tuple[bool, str]:
    """Return (True, window_type) if the receiver chain contains a window call."""
    while True:
        if isinstance(node, ast.Call):
            func = node.func
            if isinstance(func, ast.Attribute) and func.attr in _WINDOW_STARTERS:
                return True, func.attr
            node = func
        elif isinstance(node, ast.Attribute):
            node = node.value
        elif isinstance(node, ast.Subscript):
            node = node.value
        else:
            return False, ""


def _subscript_key_type(node: ast.Subscript) -> str:
    """Classify a Subscript's key shape: 'list' | 'mask' | 'str' | 'slice' | 'other'."""
    key = node.slice
    if isinstance(key, ast.Index):  # Python <3.9 wraps the key in ast.Index
        key = key.value
    if isinstance(key, (ast.List, ast.Tuple)):
        return "list"          # df[["a", "b"]]        -> DataFrame
    if isinstance(key, (ast.Compare, ast.BoolOp, ast.UnaryOp, ast.Subscript)):
        return "mask"           # df[df["a"] > 0] / df[df["flag"]] -> DataFrame
    if isinstance(key, ast.BinOp) and isinstance(key.op, (ast.BitAnd, ast.BitOr, ast.BitXor)):
        return "mask"           # df[mask1 & mask2] -> DataFrame (pandas masks combine with &/|/^)
    if isinstance(key, ast.Constant) and isinstance(key.value, str):
        return "str"            # df["a"]                -> Series
    if isinstance(key, ast.Slice):
        return "slice"           # df[1:5]                -> preserves receiver type
    return "other"                # df[var], df[f(...)]    -> ambiguous from AST alone


def _infer_type(
    node,
    pd_aliases: Set[str],
    df_vars: Set[str],
    gb_vars: Set[str],
    series_vars: Set[str] = frozenset(),
) -> Optional[str]:
    """
    Best-effort static type inference for a pandas expression node.

    Returns one of "df", "series", "dfgb", "seriesgb", "index", or None when
    the AST shape doesn't give enough signal (e.g. `df[some_var]`, a bare
    Name that isn't tracked, or a call to code outside pandas). None means
    "unknown" — callers should fall back to their pre-existing heuristic
    rather than treat it as an error.
    """
    if isinstance(node, ast.Name):
        if node.id in gb_vars:
            return "dfgb"
        if node.id in df_vars or node.id in _COMMON_DF_NAMES:
            return "df"
        if node.id in series_vars:
            return "series"
        return None

    if isinstance(node, (ast.BinOp, ast.Compare, ast.BoolOp, ast.UnaryOp)):
        # Arithmetic/comparison between columns overwhelmingly happens at
        # the Series level in this dataset (`df["a"] - df["b"]`,
        # `df["a"] >= 0`, `~mask`), so this is the useful default even
        # though a DataFrame-vs-DataFrame op is technically possible too.
        return "series"

    if isinstance(node, ast.Attribute):
        recv = _infer_type(node.value, pd_aliases, df_vars, gb_vars, series_vars)
        if node.attr in ("columns", "index") and recv in ("df", "series"):
            return "index"     # df.columns / df.index / series.index -> Index
        if node.attr == "T" and recv in ("df", "series"):
            return recv         # .T preserves the receiver's shape
        if recv == "df" and node.attr not in _KNOWN_DF_ATTRS:
            return "series"     # df.value <=> df["value"] - dot-notation column access
        return None

    if isinstance(node, ast.Subscript):
        base = _infer_type(node.value, pd_aliases, df_vars, gb_vars, series_vars)
        shape = _subscript_key_type(node)
        if base in ("dfgb", "seriesgb"):
            if shape == "list":
                return "dfgb"        # gb[["a","b"]] -> DataFrameGroupBy (subset)
            if shape in ("str", "other"):
                # gb["col"] or gb[col_var] -> single-column selection is the
                # idiomatic way to get a SeriesGroupBy, whether the column
                # name is a literal or a variable.
                return "seriesgb"
            return base
        if shape in ("list", "mask"):
            return "df"
        if shape == "str":
            return "series"
        if shape == "slice":
            return base   # row slices preserve the receiver's type
        return None        # unresolved key shape (Name/computed) - let caller fall back

    if isinstance(node, ast.Call):
        func = node.func
        if isinstance(func, ast.Name):
            return "df" if func.id in _DF_CONSTRUCTORS else None
        if not isinstance(func, ast.Attribute):
            return None

        attr = func.attr
        obj = func.value

        if isinstance(obj, ast.Name) and obj.id in pd_aliases:
            return "df" if attr in _DF_CONSTRUCTORS else None

        if attr == "groupby":
            base = _infer_type(obj, pd_aliases, df_vars, gb_vars, series_vars)
            return "seriesgb" if base == "series" else "dfgb"

        recv = _infer_type(obj, pd_aliases, df_vars, gb_vars, series_vars)
        if recv in ("dfgb", "seriesgb"):
            return None  # post-aggregation calls are handled by the groupby branch
        if attr in _DF_TO_SERIES and recv == "df":
            return "series"
        if attr in _TYPE_PRESERVING and recv in ("df", "series", "index"):
            return recv
        return None

    return None


# ── Extraction context ────────────────────────────────────────────────

class _Ctx:
    """Accumulates extraction results for one snippet."""
    __slots__ = ("normalized", "keywords", "unknown")

    def __init__(self):
        self.normalized: Set[str] = set()
        self.keywords: Set[str] = set()
        self.unknown: Set[str] = set()


# ── Core extraction ───────────────────────────────────────────────────

def _process_node(
    node,
    pd_aliases: Set[str],
    from_pandas: Set[str],
    df_vars: Set[str],
    gb_vars: Set[str],
    maps: APIMaps,
    ctx: _Ctx,
    series_vars: Set[str] = frozenset(),
    module_aliases: Set[str] = frozenset(),
) -> None:
    # ── Call nodes ──────────────────────────────────────────────────
    if isinstance(node, ast.Call):
        func = node.func

        # Direct name call: DataFrame(...), Series(...) from direct import
        if not isinstance(func, ast.Attribute):
            if isinstance(func, ast.Name) and func.id in from_pandas:
                api = maps.top_level.get(func.id, f"pandas.{func.id}")
                ctx.normalized.add(api)
                ctx.keywords.add(func.id)
            return

        attr = func.attr
        obj = func.value

        # ── Top-level pandas call: pd.read_csv(…), pd.merge(…) ──────
        if isinstance(obj, ast.Name) and obj.id in pd_aliases:
            api = maps.top_level.get(attr, f"pandas.{attr}")
            ctx.normalized.add(api)
            ctx.keywords.add(attr)
            return

        # ── Accessor pattern: df["col"].str.lower() ──────────────────
        if isinstance(obj, ast.Attribute) and obj.attr in _ACCESSOR_NAMES:
            accessor = obj.attr
            kw = f"{accessor}.{attr}"
            ctx.keywords.add(kw)
            ctx.keywords.add(attr)
            api = maps.accessor_map.get(kw)
            if api:
                ctx.normalized.add(api)
            return

        # Skip non-pandas receivers, unless the method name is distinctive
        # enough on its own (e.g. `.groupby()`) and the receiver isn't a
        # plain imported module (rules out stdlib `itertools.groupby(...)`).
        if not _is_pandas_receiver(obj, pd_aliases, df_vars, gb_vars, series_vars):
            is_distinctive = attr in _DISTINCTIVE_DF_METHODS and not (
                isinstance(obj, ast.Name) and obj.id in module_aliases
            )
            if not is_distinctive:
                return

        # ── GroupBy chain: df.groupby(…).sum() ──────────────────────
        if _receiver_is_groupby(obj, gb_vars):
            # df.groupby(x).agg(...) -> DataFrameGroupBy; df.groupby(x)["c"].agg(...)
            # or a Series grouped directly -> SeriesGroupBy.
            kind = _infer_type(obj, pd_aliases, df_vars, gb_vars, series_vars)
            if kind == "seriesgb":
                api = maps.series_groupby_method.get(attr) or maps.df_groupby_method.get(attr)
            else:
                api = maps.df_groupby_method.get(attr) or maps.series_groupby_method.get(attr)
            if api:
                ctx.normalized.add(api)
            else:
                # Method not in either groupby map; may be a post-agg DataFrame call
                # (e.g. .reset_index() after .sum())
                df_api = maps.df_method.get(attr) or maps.series_method.get(attr)
                if df_api:
                    ctx.normalized.add(df_api)
                else:
                    ctx.unknown.add(attr)
            ctx.keywords.add(attr)
            return

        # ── Window chain: df.rolling(3).mean() ──────────────────────
        in_window, window_type = _get_window_in_chain(obj)
        if in_window:
            kw = f"{window_type}.{attr}"
            ctx.keywords.add(window_type)
            ctx.keywords.add(kw)
            ctx.keywords.add(attr)
            # The window starter (rolling/expanding/…) is captured when its
            # own Call node is processed as a df_method call; no extra normalized
            # API is added here since the knowledge base has no Rolling.mean etc.
            return

        # ── DataFrame vs Series vs Index call: df.method() / df["col"].method() /
        #    df[mask].method() / df.pop("c").method() / df.columns.tolist() … ──
        # `_infer_type` resolves subscript key shape (str -> Series,
        # list/mask -> DataFrame), property results (.columns/.index -> Index),
        # and propagates the type through chains of type-preserving calls;
        # when it can't resolve anything (e.g. the key is a variable), fall
        # back to the old per-shape default.
        kind = _infer_type(obj, pd_aliases, df_vars, gb_vars, series_vars)
        if kind == "series":
            api = maps.series_method.get(attr) or maps.df_method.get(attr)
        elif kind == "df":
            api = maps.df_method.get(attr) or maps.series_method.get(attr)
        elif kind == "index":
            api = maps.index_method.get(attr) or maps.series_method.get(attr)
        elif isinstance(obj, ast.Subscript):
            api = maps.series_method.get(attr) or maps.df_method.get(attr)
        else:
            api = maps.df_method.get(attr) or maps.series_method.get(attr)

        if api:
            ctx.normalized.add(api)
            ctx.keywords.add(attr)
        else:
            ctx.unknown.add(attr)
            ctx.keywords.add(attr)

    # ── Attribute nodes (property access) ───────────────────────────
    elif isinstance(node, ast.Attribute):
        attr = node.attr
        obj = node.value

        # Accessor property: df["col"].dt.year (attribute, not a call)
        if isinstance(obj, ast.Attribute) and obj.attr in _ACCESSOR_NAMES:
            accessor = obj.attr
            kw = f"{accessor}.{attr}"
            ctx.keywords.add(kw)
            ctx.keywords.add(attr)
            api = maps.accessor_map.get(kw)
            if api:
                ctx.normalized.add(api)
            return

        # The bare accessor node itself (the "str" in df["c"].str.lower()) is
        # an intermediate step, not an API call in its own right - skip it so
        # it isn't double-counted alongside the accessor_map entry above.
        if attr in _ACCESSOR_NAMES:
            return

        if isinstance(obj, ast.Name) and obj.id in pd_aliases:
            api = maps.top_level.get(attr, f"pandas.{attr}")
            ctx.normalized.add(api)
            ctx.keywords.add(attr)
            return

        # Property access on any pandas-shaped receiver: self.df.columns,
        # data[mask].index, func().values, … not just a bare tracked Name.
        if not _is_pandas_receiver(obj, pd_aliases, df_vars, gb_vars, series_vars):
            is_distinctive = attr in _DISTINCTIVE_DF_PROPERTIES and not (
                isinstance(obj, ast.Name) and obj.id in module_aliases
            )
            if not is_distinctive:
                return

        kind = _infer_type(obj, pd_aliases, df_vars, gb_vars, series_vars)
        if kind == "series":
            api = maps.series_method.get(attr) or maps.df_method.get(attr)
        elif kind == "index":
            api = maps.index_method.get(attr) or maps.series_method.get(attr)
        else:
            # "df" or unresolved - properties are overwhelmingly accessed on
            # DataFrames in this dataset, so default to df_method as before.
            api = maps.df_method.get(attr) or maps.series_method.get(attr)

        if api:
            ctx.normalized.add(api)
            ctx.keywords.add(attr)


# ── Public API ─────────────────────────────────────────────────────────

def extract_pandas_api_details(
    code: str, maps: Optional[APIMaps] = None
) -> dict:
    """
    Extract pandas API information from a source code snippet.

    Returns a dict with:
      normalized_apis   – canonical API strings (matching knowledge base)
      operation_keywords – raw method names and accessor keywords
      pandas_aliases    – aliases found for the pandas module
      from_pandas       – names imported directly from pandas
      df_vars           – tracked DataFrame variable names
      groupby_vars      – tracked GroupBy variable names
      unknown_methods   – methods on pandas receivers not found in any map
      parse_success     – whether the snippet parsed successfully
    """
    if maps is None:
        maps = _FALLBACK_MAPS

    tree = _safe_parse(code)
    if tree is None:
        return {
            "normalized_apis": [],
            "operation_keywords": [],
            "pandas_aliases": [],
            "from_pandas": [],
            "df_vars": [],
            "series_vars": [],
            "groupby_vars": [],
            "unknown_methods": [],
            "parse_success": False,
        }

    pd_aliases = _collect_pandas_aliases(tree)
    from_pandas = _collect_from_pandas(tree)
    module_aliases = _collect_module_aliases(tree)
    df_vars, series_vars, gb_vars = _track_df_vars(tree, pd_aliases, from_pandas)

    # ast.walk() yields a Call's `.func` Attribute node separately from the
    # Call node itself. The Call branch already fully resolves `x.method()`;
    # without this guard the property-access branch would independently
    # reprocess the same `.method` Attribute node as if it were a bare
    # property read, double-counting (and sometimes misclassifying, since it
    # doesn't know about GroupBy chains) every method call in the snippet.
    call_func_ids = {
        id(node.func) for node in ast.walk(tree)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
    }

    ctx = _Ctx()
    for node in ast.walk(tree):
        if isinstance(node, ast.Attribute) and id(node) in call_func_ids:
            continue
        _process_node(node, pd_aliases, from_pandas, df_vars, gb_vars, maps, ctx, series_vars, module_aliases)

    return {
        "normalized_apis": sorted(ctx.normalized),
        "operation_keywords": sorted(ctx.keywords),
        "pandas_aliases": sorted(pd_aliases),
        "from_pandas": sorted(from_pandas),
        "df_vars": sorted(df_vars),
        "series_vars": sorted(series_vars),
        "groupby_vars": sorted(gb_vars),
        "unknown_methods": sorted(ctx.unknown),
        "parse_success": True,
    }


def extract_pandas_apis(
    code: str, maps: Optional[APIMaps] = None
) -> List[str]:
    """Return only the normalized API list (backward-compatible wrapper)."""
    return extract_pandas_api_details(code, maps)["normalized_apis"]
