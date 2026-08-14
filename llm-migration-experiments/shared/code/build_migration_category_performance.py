#!/usr/bin/env python3
"""Build end-to-end performance by migration category."""

import csv
from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parents[3]
EXPERIMENT_ROOT = REPOSITORY_ROOT / "llm-migration-experiments"
DATASET = (
    REPOSITORY_ROOT
    / "pandas-to-polars-migration-dataset"
    / "data"
    / "final"
    / "migration_pairs.csv"
)
TEST_RESULTS = (
    EXPERIMENT_ROOT
    / "shared"
    / "results"
    / "all_conditions_test_results_v3.csv"
)
OUTPUT = (
    EXPERIMENT_ROOT
    / "shared"
    / "results"
    / "migration_category_performance.csv"
)

CATEGORIES = [
    ("Core dataframe transformations", "category_core_dataframe_transformations"),
    ("Index and row semantics", "category_index_and_row_semantics"),
    ("Aggregation and combination", "category_aggregation_and_combination"),
    ("IO boundaries", "category_io_boundaries"),
    (
        "Types, schemas, and temporal operations",
        "category_types_schemas_temporal",
    ),
    ("UDF and custom-logic rewrites", "category_udf_and_custom_logic"),
    ("Lazy execution and evaluation strategy", "category_lazy_execution"),
    ("Missing and null semantics", "category_missing_and_null_semantics"),
    ("Import and setup only", "category_import_and_setup_only"),
    ("Reshaping", "category_reshaping"),
    ("Other/manual", "category_other_manual"),
]
CONDITIONS = ["Baseline", "Exp1", "Exp2", "Exp3"]


def is_true(value: str) -> bool:
    """Interpret the boolean and numeric encodings used by the CSV artifacts."""
    try:
        return float(value) == 1.0
    except (TypeError, ValueError):
        return str(value).strip().lower() in {"true", "yes", "pass"}


def main() -> None:
    with DATASET.open(encoding="utf-8-sig", newline="") as file:
        pairs = list(csv.DictReader(file))
    with TEST_RESULTS.open(encoding="utf-8", newline="") as file:
        tests = list(csv.DictReader(file))

    outcomes = {
        (row["condition"], row["snippet_id"]): is_true(row["all_pass"])
        for row in tests
        if not is_true(row["excluded"])
    }

    rows = []
    for category, flag_column in CATEGORIES:
        snippet_ids = [
            row["snippet_id"]
            for row in pairs
            if is_true(row["evaluation_valid"]) and is_true(row[flag_column])
        ]
        result = {"migration_category": category, "n": len(snippet_ids)}
        for condition in CONDITIONS:
            passes = sum(outcomes[(condition, snippet_id)] for snippet_id in snippet_ids)
            result[f"{condition.lower()}_passes"] = passes
            result[f"{condition.lower()}_pass_rate"] = round(
                100 * passes / len(snippet_ids), 1
            )
        baseline_proportion = result["baseline_passes"] / len(snippet_ids)
        for condition in CONDITIONS[1:]:
            result[f"{condition.lower()}_difference_pp"] = round(
                100
                * (
                    result[f"{condition.lower()}_passes"] / len(snippet_ids)
                    - baseline_proportion
                ),
                1,
            )
        rows.append(result)

    fieldnames = ["migration_category", "n"]
    for condition in CONDITIONS:
        fieldnames.extend(
            [f"{condition.lower()}_passes", f"{condition.lower()}_pass_rate"]
        )
        if condition != "Baseline":
            fieldnames.append(f"{condition.lower()}_difference_pp")

    with OUTPUT.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    main()
