#!/usr/bin/env python3
"""Reproduce the latest four-condition thesis taxonomy.

The classifier deliberately excludes the snippet identifier from rule evidence.
Rules with insufficient evidence return ``manual review required`` rather than a
substantive default category.  Only the earliest observed failing layer is used
for the primary classification; raw downstream failures are retained for a
separate causal (cascade-versus-independent) review.

The deterministic rules provide the initial classification. Final categories
are then loaded from the condition-specific manual-adjudication files, matching
the classification procedure used in the thesis. Outputs are written under
``shared/results/reproduced`` so the canonical reviewed files are not replaced.
"""

from __future__ import annotations

import csv
import json
import re
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
RESULTS = ROOT / "shared" / "results" / "reproduced"
OUTPUT = RESULTS / "all_conditions_taxonomy_classification.csv"
SUMMARY = RESULTS / "all_conditions_taxonomy_summary.csv"

NOTEBOOK_ROOTS = {
    "baseline": ROOT / "baseline" / "tests",
    "exp1": ROOT / "exp1" / "tests",
    "exp2": ROOT / "exp2" / "tests",
    "exp3": ROOT / "exp3" / "tests",
}

RESULT_FILES = {
    "baseline": ROOT / "baseline" / "results" / "test_results_v3.csv",
    "exp1": ROOT / "exp1" / "results" / "test_results_v3.csv",
    "exp2": ROOT / "exp2" / "results" / "test_results_v3.csv",
    "exp3": ROOT / "exp3" / "results" / "test_results_v3.csv",
}

REVIEW_FILES = {
    condition: ROOT / condition / "results" / "taxonomy_classification_final.csv"
    for condition in NOTEBOOK_ROOTS
}

EVALUATION_CATEGORIES = {
    "oracle mismatch",
    "overly strict schema or type comparison",
    "object-type comparison issue",
    "test-harness issue",
    "harness-introduced helper input-type mismatch",
    "environment or configuration issue",
}

EXECUTION_CATEGORIES = {
    "import or unresolved-reference error",
    "invalid target API usage",
    "lazy/eager misuse",
    "type or runtime error",
    "incomplete runnable code",
    "timeout, non-termination, or memory issue",
}

STANDARD_BEHAVIOURAL_CATEGORIES = {
    "wrong logical direction",
    "incorrect condition",
    "missing one or more steps",
    "wrong aggregation, filtering, or join logic",
    "return-type mismatch",
    "schema mismatch",
    "column-order mismatch",
    "index or datetime contract mismatch",
    "helper input-type mismatch",
    "exception-semantics mismatch",
}

EDGE_CASE_CATEGORIES = {
    "null- or missing-value handling",
    "empty-input handling",
    "dtype-sensitive behaviour",
    "ordering stability",
    "groupby or aggregation edge cases",
    "join or merge edge cases",
    "index-related edge behaviour",
}

TAXONOMY_CATEGORIES = (
    EVALUATION_CATEGORIES
    | EXECUTION_CATEGORIES
    | STANDARD_BEHAVIOURAL_CATEGORIES
    | EDGE_CASE_CATEGORIES
)

# Source/test-context decisions for payloads that do not contain enough
# semantic information for a keyword rule.  These entries were assigned only
# after inspecting the generated implementation and the target test contract;
# the identifier is a lookup key, not classification evidence.
MANUAL_PRIMARY_OVERRIDES = {
    ("baseline", "29097c0c_to_dataset_read_wrap"): "missing one or more steps",
    ("baseline", "8017f91b_pairwise_cosine_loc"): "index or datetime contract mismatch",
    ("baseline", "8017f91b_pairwise_loc_filter"): "index or datetime contract mismatch",
    ("baseline", "8017f91b_precompute_cross_join"): "wrong aggregation, filtering, or join logic",
    ("baseline", "8c71f3c7_citation_models_rank"): "ordering stability",
    ("baseline", "8c71f3c7_hybrid_scorer_citation_index"): "index or datetime contract mismatch",
    ("baseline", "8c71f3c7_hybrid_scorer_language_index"): "index or datetime contract mismatch",
    ("baseline", "8c71f3c7_pairwise_loc_colname"): "index or datetime contract mismatch",
    ("baseline", "a52cebfe_common_summary_filter"): "index-related edge behaviour",
    ("baseline", "ed3b46c0_base_pattern_pred_concat"): "wrong aggregation, filtering, or join logic",
    ("exp1", "05afd878_evaluate_coassembly_edges"): "wrong aggregation, filtering, or join logic",
    ("exp1", "29097c0c_to_dataset_read_wrap"): "missing one or more steps",
    ("exp1", "3c49cad1_bench_interp_time_rmse"): "wrong aggregation, filtering, or join logic",
    ("exp1", "3c49cad1_timeseries_gain"): "missing one or more steps",
    ("exp1", "8017f91b_pairwise_cosine_loc"): "index or datetime contract mismatch",
    ("exp1", "8017f91b_pairwise_loc_filter"): "index or datetime contract mismatch",
    ("exp1", "8017f91b_precompute_cross_join"): "wrong aggregation, filtering, or join logic",
    ("exp1", "8c71f3c7_hybrid_scorer_citation_index"): "index or datetime contract mismatch",
    ("exp1", "8c71f3c7_pairwise_loc_colname"): "index or datetime contract mismatch",
    ("exp1", "8c71f3c7_pairwise_loc_item"): "index or datetime contract mismatch",
    ("exp1", "ed3b46c0_base_pattern_pred_concat"): "wrong aggregation, filtering, or join logic",
    ("exp2", "287a28d8_col_starts_with"): "incorrect condition",
    ("exp2", "3c49cad1_timeseries_gain"): "missing one or more steps",
    ("exp2", "73a39d90_metrics_groupby_partition"): "wrong aggregation, filtering, or join logic",
    ("exp2", "8017f91b_pairwise_loc_filter"): "index or datetime contract mismatch",
    ("exp2", "8c71f3c7_hybrid_scorer_citation_index"): "index or datetime contract mismatch",
    ("exp2", "efc0581f_dedup_redundant_filter"): "ordering stability",
    ("exp2", "efc0581f_ident_from_dicts_cross"): "wrong aggregation, filtering, or join logic",
    ("exp2", "img2table_cells_redundant_removal_migration"): "ordering stability",
    ("exp2", "pheval_parse_hgnc_data"): "missing one or more steps",
    ("exp3", "287a28d8_col_starts_with"): "incorrect condition",
    ("exp3", "3c49cad1_mosmix_access_datetime"): "missing one or more steps",
    ("exp3", "3c49cad1_timeseries_gain"): "missing one or more steps",
    ("exp3", "73a39d90_metrics_groupby_partition"): "wrong aggregation, filtering, or join logic",
    ("exp3", "8017f91b_pairwise_cosine_loc"): "index or datetime contract mismatch",
    ("exp3", "8017f91b_pairwise_loc_filter"): "index or datetime contract mismatch",
    ("exp3", "8017f91b_precompute_cross_join"): "wrong aggregation, filtering, or join logic",
    ("exp3", "8c71f3c7_pairwise_loc_colname"): "index or datetime contract mismatch",
    ("exp3", "a52cebfe_common_summary_filter"): "index-related edge behaviour",
    ("exp3", "efc0581f_ident_from_dicts_cross"): "wrong aggregation, filtering, or join logic",
    ("exp3", "portfolio_momentum_rsi"): "wrong aggregation, filtering, or join logic",
    # The harness supplied Polars objects correctly in these two cases; the
    # generated code incorrectly retained a pandas-only conversion helper.
    ("exp3", "3c49cad1_bench_precip_regular"): "invalid target API usage",
    ("exp3", "adjacency_read_file_to_polars"): "invalid target API usage",
    # The generated helper converts the result of a migrated HybridScore
    # method with pl.from_pandas even though that method now returns Polars.
    ("exp1", "readnext_hybrid_score_compare_scores_migration"): "helper input-type mismatch",
    # The comparator attempted to sort an Object column. The generated output
    # itself was not shown to violate the migration contract.
    ("exp3", "1f8af3a3_target_elusive_sample_pairs"): "object-type comparison issue",
    # These DuplicateErrors are caused by adding a pandas-style index column
    # when the generated frame already contains that column.
    ("baseline", "8017f91b_eval_hybrid_concat_sort"): "invalid target API usage",
    ("exp1", "adjacency_create_matrix_loop"): "invalid target API usage",
    ("exp2", "a52cebfe_es_update_scaling_factors"): "invalid target API usage",
    # The edge fixture preserves pandas index fields that the generated CSV
    # path drops. This is an index contract divergence, not a generic schema
    # category outside the Layer 3 taxonomy.
    ("baseline", "a52cebfe_rft_concat_write"): "index-related edge behaviour",
    ("exp1", "a52cebfe_rft_concat_write"): "index-related edge behaviour",
    ("exp2", "a52cebfe_rft_concat_write"): "index-related edge behaviour",
    ("exp3", "a52cebfe_rft_concat_write"): "index-related edge behaviour",
}


def output_lines(path: Path) -> list[str]:
    notebook = json.loads(path.read_text(encoding="utf-8"))
    lines: list[str] = []
    for cell in notebook.get("cells", []):
        for output in cell.get("outputs", []):
            if output.get("output_type") == "stream":
                text = "".join(output.get("text", []))
            else:
                text = ""
            lines.extend(text.splitlines())
    return [re.sub(r"\x1b\[[0-9;]*m", "", line).strip() for line in lines]


def layer_evidence(path: Path, function: str, layer: str) -> list[str]:
    marker = re.compile(rf"^❌\s+{layer}\b", re.IGNORECASE)
    function_token = re.compile(
        rf"(?<![A-Za-z0-9_])(?:gen_|generated_)?{re.escape(function)}(?![A-Za-z0-9_])"
    )
    return [
        line
        for line in output_lines(path)
        if marker.search(line)
        and function_token.search(line)
        and f"before_{function}" not in line
    ]


def payload(evidence: list[str], function: str) -> str:
    """Remove marker metadata and the function identifier from rule evidence."""
    cleaned: list[str] = []
    for line in evidence:
        line = re.sub(r"^❌\s+L[123]\s+", "", line, flags=re.IGNORECASE)
        line = re.sub(
            rf"(?<![A-Za-z0-9_])(?:gen_|generated_)?{re.escape(function)}(?![A-Za-z0-9_])",
            " ",
            line,
        )
        cleaned.append(re.sub(r"\s+", " ", line).strip())
    return " | ".join(cleaned).lower()


def evaluation_category(text: str) -> str | None:
    if any(term in text for term in ("before code failed", "oracle failed", "oracle mismatch")):
        return "oracle mismatch"
    if any(term in text for term in ("comparison helper", "_same_scalar", "picklingerror")):
        return "test-harness issue"
    if any(term in text for term in ("modulenotfounderror", "filenotfounderror", "no such file or directory", "kernel died")):
        return "environment or configuration issue"
    return None


def classify_l1(text: str) -> str:
    evaluation = evaluation_category(text)
    if evaluation:
        return evaluation
    if any(term in text for term in ("lazyframe", "lazy/eager", "eager/lazy", "unresolved polars expr", "'expr' object")):
        return "lazy/eager misuse"
    invalid_api = (
        "has no attribute", "unexpected keyword argument", "unsupported keyword",
        "no method", "non-existent", "does not support `series` assignment",
        "must specify `on`", "only supports 'vertical' concat strategy",
        "cannot return empty fold", "requires either `fields`", "can only be used on numeric types",
        "index(...) must be called", "col.__call__() missing", "schema_overrides` should be",
        "should be a single byte", "cannot select elements using sequence",
    )
    if any(term in text for term in invalid_api):
        return "invalid target API usage"
    if any(term in text for term in (
        "syntaxerror", "indentationerror", "unboundlocalerror", "unfixable syntax",
        "not syntactically valid", "ellipsis was passed", "trailing line continuation",
        "_wrapped", "generated wrapper", "nonetype object is not callable",
    )):
        return "incomplete runnable code"
    if any(term in text for term in ("nameerror", "modulenotfounderror", "importerror", "not defined")):
        return "import or unresolved-reference error"
    if any(term in text for term in ("timeout", "timed out", "memoryerror", "killed")):
        return "timeout, non-termination, or memory issue"
    return "type or runtime error"


def classify_l2(text: str) -> str:
    evaluation = evaluation_category(text)
    if evaluation:
        return evaluation
    if any(term in text for term in (
        "lazyframe", "lazy/eager", "eager/lazy", "unresolved polars expr", "'expr' object",
    )):
        return "lazy/eager misuse"
    if any(term in text for term in (
        "has no attribute", "unexpected keyword argument", "unsupported keyword",
        "non-existent", "no method named", "does not support", "must specify `on`",
    )):
        return "invalid target API usage"
    if any(term in text for term in (
        "syntaxerror", "indentationerror", "unboundlocalerror", "unfixable syntax",
        "not syntactically valid", "_wrapped", "generated wrapper",
    )):
        return "incomplete runnable code"
    if any(term in text for term in ("nameerror", "importerror", "not defined")):
        return "import or unresolved-reference error"
    if any(term in text for term in ("timeout", "timed out", "memoryerror", "killed")):
        return "timeout, non-termination, or memory issue"
    if "setup error" in text:
        return "type or runtime error"
    if any(term in text for term in (
        "one side returned", "return contract", "before_return=", "gen_return=",
        "returned method", "returned an unresolved", "before=list, gen=dataframe",
        "before=none", "gen=none",
    )):
        return "return-type mismatch"
    if any(term in text for term in (
        "column sets differ", "missing column", "before-only=", "gen-only=",
        "headers", "column names", "schema mismatch", "schemaerror",
        "has a dtype", "dtype of '",
    )):
        return "schema mismatch"
    if any(term in text for term in (
        "column order", "columns are in a different order", "ordered columns",
    )):
        return "column-order mismatch"
    if any(term in text for term in (
        "index mismatch", "index values", "datetime", "date contract", "timezone",
    )):
        return "index or datetime contract mismatch"
    if any(term in text for term in (
        "helper input", "helper expected", "incompatible helper",
    )):
        return "helper input-type mismatch"
    if any(term in text for term in (
        "exception mismatch", "mismatch exception", "before_error=", "gen_error=",
        "different exception", "one side raised",
    )):
        return "exception-semantics mismatch"
    if any(term in text for term in ("opposite", "reversed", "ascending", "descending", "wrong direction")):
        return "wrong logical direction"
    if any(term in text for term in ("condition", "predicate", "mask", "incorrect membership")):
        return "incorrect condition"
    if any(term in text for term in (
        "groupby", "group_by", "aggregation", "filtering", " join ", "merge",
        "concat", "pivot", "intersection", "side effect", "row count",
    )):
        return "wrong aggregation, filtering, or join logic"
    if any(term in text for term in (
        "generated=none", "gen=None", "missing step", "omitted", "not produced",
    )):
        return "missing one or more steps"
    return "manual review required"


def classify_l3(text: str) -> str:
    evaluation = evaluation_category(text)
    if evaluation:
        return evaluation
    if any(term in text for term in ("null", "missing value", "all-null", "nan", "none value")):
        return "null- or missing-value handling"
    if any(term in text for term in ("empty", "zero-row", "zero row", "no rows")):
        return "empty-input handling"
    if any(term in text for term in ("dtype", "type-sensitive", "schema/null/category", "date objects", "polars input")):
        return "dtype-sensitive behaviour"
    if any(term in text for term in ("ordering", "order", "sort", "stable", "duplicate", "dedup", "kwargs not mutated")):
        return "ordering stability"
    if any(term in text for term in ("groupby", "group_by", "aggregation", "singleton group", "partition")):
        return "groupby or aggregation edge cases"
    if any(term in text for term in ("join", "merge", "non-matching key", "cross")):
        return "join or merge edge cases"
    if any(term in text for term in ("index", "iloc", "reindex", "mismatched lengths", "row position")):
        return "index-related edge behaviour"
    return "manual review required"


def classify(layer: str, text: str) -> str:
    return {"L1": classify_l1, "L2": classify_l2, "L3": classify_l3}[layer](text)


def top_level_category(category: str) -> str:
    if category in EVALUATION_CATEGORIES:
        return "evaluation-induced error"
    if category in EXECUTION_CATEGORIES:
        return "execution failure"
    if category in STANDARD_BEHAVIOURAL_CATEGORIES:
        return "standard behavioural mismatch"
    if category in EDGE_CASE_CATEGORIES:
        return "edge-case failure"
    raise ValueError(f"Category is not part of the thesis taxonomy: {category!r}")


def load_reviewed_categories() -> dict[tuple[str, str], str]:
    """Load the final manual adjudications preserved with each condition."""
    reviewed: dict[tuple[str, str], str] = {}
    for condition, path in REVIEW_FILES.items():
        with path.open(newline="", encoding="utf-8") as handle:
            for row in csv.DictReader(handle):
                category = row.get("final_primary_category") or row.get("primary_category")
                if category:
                    reviewed[(condition, row["snippet_id"])] = category
    return reviewed


def main() -> None:
    RESULTS.mkdir(parents=True, exist_ok=True)
    reviewed_categories = load_reviewed_categories()
    rows: list[dict[str, str]] = []
    for condition, root in NOTEBOOK_ROOTS.items():
        result_path = RESULT_FILES[condition]
        with result_path.open(newline="", encoding="utf-8") as handle:
            results = list(csv.DictReader(handle))
        for result in results:
            snippet = result["snippet_id"]
            if result["l1_raw"] == "fail":
                primary = "L1"
            elif result["l2_raw"] == "fail":
                primary = "L2"
            elif result["l2_raw"] == "pass" and result["l3_raw"] == "fail":
                primary = "L3"
            else:
                primary = None
            if primary is None:
                continue
            notebook = root / result["notebook"]
            evidence = layer_evidence(notebook, result["func_name"], primary)
            rule_text = payload(evidence, result["func_name"])
            category = classify(primary, rule_text)
            category = MANUAL_PRIMARY_OVERRIDES.get((condition, snippet), category)
            category = reviewed_categories.get((condition, snippet), category)
            top = None if category == "manual review required" else top_level_category(category)
            downstream = [
                layer for layer in ("L2", "L3")
                if (primary == "L1" or (primary == "L2" and layer == "L3"))
                and result[f"{layer.lower()}_raw"] == "fail"
            ]
            rows.append({
                "experiment": condition,
                "snippet_id": snippet,
                "primary_layer": primary,
                "top_level_category": top or "manual review required",
                "primary_category": category,
                "downstream_failed_layers": ",".join(downstream),
                "downstream_causal_status": "causal review required" if downstream else "none",
                "evidence": " | ".join(evidence),
                "classification_payload": rule_text,
            })

    unresolved = [
        row for row in rows if row["primary_category"] == "manual review required"
    ]
    if unresolved:
        examples = ", ".join(
            f"{row['experiment']}:{row['snippet_id']}" for row in unresolved[:10]
        )
        raise ValueError(
            f"{len(unresolved)} classifications still require manual review: {examples}"
        )

    fields = list(rows[0])
    with OUTPUT.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)

    summary_rows: list[dict[str, str | int]] = []
    for condition in NOTEBOOK_ROOTS:
        selected = [row for row in rows if row["experiment"] == condition]
        counts = Counter((row["primary_layer"], row["primary_category"]) for row in selected)
        for (layer, category), count in sorted(counts.items()):
            summary_rows.append({
                "experiment": condition,
                "primary_layer": layer,
                "primary_category": category,
                "count": count,
            })
    with SUMMARY.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(summary_rows[0]))
        writer.writeheader()
        writer.writerows(summary_rows)

    print(f"classified={len(rows)}")
    print(f"manual_review={sum(row['primary_category'] == 'manual review required' for row in rows)}")
    print(OUTPUT)
    print(SUMMARY)


if __name__ == "__main__":
    main()
