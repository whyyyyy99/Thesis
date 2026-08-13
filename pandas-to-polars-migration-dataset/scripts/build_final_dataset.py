#!/usr/bin/env python3
"""Build the public 238-pair pandas-to-Polars dataset table."""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


CATEGORY_RULES = {
    "Core dataframe transformations": ("core dataframe transform", "dataframe"),
    "Index and row semantics": ("index / row semantics",),
    "Aggregation and combination": ("aggregation & combine",),
    "IO boundaries": ("io boundary",),
    "Types, schemas, and temporal operations": ("types / schema / temporal",),
    "UDF and custom-logic rewrites": ("udf / custom logic rewrite",),
    "Lazy execution and evaluation strategy": ("lazy execution",),
    "Missing and null semantics": ("missing / null semantics", "missing values"),
    "Import and setup only": ("import / setup-only",),
    "Reshaping": ("reshape",),
    "Other/manual": ("other / manual", "other/manual"),
}

CATEGORY_COLUMNS = {
    "Core dataframe transformations": "category_core_dataframe_transformations",
    "Index and row semantics": "category_index_and_row_semantics",
    "Aggregation and combination": "category_aggregation_and_combination",
    "IO boundaries": "category_io_boundaries",
    "Types, schemas, and temporal operations": "category_types_schemas_temporal",
    "UDF and custom-logic rewrites": "category_udf_and_custom_logic",
    "Lazy execution and evaluation strategy": "category_lazy_execution",
    "Missing and null semantics": "category_missing_and_null_semantics",
    "Import and setup only": "category_import_and_setup_only",
    "Reshaping": "category_reshaping",
    "Other/manual": "category_other_manual",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workspace", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    return parser.parse_args()


def fill_supplemental_labels(master: pd.DataFrame, supplemental: pd.DataFrame) -> None:
    supplemental = supplemental.set_index("snippet_id")
    columns = [
        "pandas_label_all",
        "polars_label_all",
        "macro_all",
        "migration_pattern_note",
    ]
    for column in columns:
        missing = master[column].fillna("").astype(str).str.strip().eq("")
        values = master.loc[missing, "snippet_id"].map(supplemental[column])
        master.loc[missing, column] = values.fillna(master.loc[missing, column])


def normalise_categories(raw_value: object) -> list[str]:
    text = str(raw_value).lower()
    return [
        category
        for category, markers in CATEGORY_RULES.items()
        if any(marker in text for marker in markers)
    ]


def load_extracted_snippets(workspace: Path) -> pd.DataFrame:
    root = workspace / "extracted_snippets"
    rows: dict[str, dict[str, str]] = {}
    suffixes = {
        "_before.py": "pandas_code",
        "_after.py": "polars_code",
        ".patch": "migration_diff",
    }
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        for suffix, column in suffixes.items():
            if path.name.endswith(suffix):
                snippet_id = path.name[: -len(suffix)]
                rows.setdefault(snippet_id, {})[column] = path.read_text(
                    encoding="utf-8", errors="replace"
                )
                break
    return pd.DataFrame(
        [{"snippet_id": snippet_id, **values} for snippet_id, values in rows.items()]
    )


def main() -> None:
    args = parse_args()
    workspace = args.workspace.resolve()
    output_dir = args.output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    master = pd.read_excel(
        workspace / "reviewed/snippet_master_table.xlsx",
        sheet_name="Sheet1",
    ).fillna("")
    supplemental = pd.read_csv(
        workspace / "reviewed/remaining_54_snippet_classifications.csv"
    ).fillna("")
    final_ids = pd.read_csv(
        workspace / "experiments/results/exp1_ast_guided/gold_labels_review.csv"
    )[["snippet_id"]]
    evaluation = pd.read_csv(
        workspace / "experiments/results/manual_harness_line_audit.csv"
    ).fillna("")

    fill_supplemental_labels(master, supplemental)
    master = master.rename(columns={"snippet_id": "review_record_id"})
    master["final_snippet_id"] = master["source_json_name"].str.replace(
        r"\.json$", "", regex=True
    )

    selected = final_ids.merge(
        master,
        left_on="snippet_id",
        right_on="final_snippet_id",
        how="left",
        validate="one_to_one",
    )
    selected = selected.merge(
        evaluation[["snippet_id", "verdict", "evidence", "action"]],
        on="snippet_id",
        how="left",
        validate="one_to_one",
    )
    extracted = load_extracted_snippets(workspace)
    selected = selected.drop(
        columns=["before_snippet", "after_snippet", "patch_snippet"]
    ).merge(extracted, on="snippet_id", how="left", validate="one_to_one")

    selected["migration_categories"] = selected["macro_all"].map(
        lambda value: "; ".join(normalise_categories(value))
    )
    for category, column in CATEGORY_COLUMNS.items():
        selected[column] = selected["macro_all"].map(
            lambda value, category=category: category in normalise_categories(value)
        )

    selected["evaluation_valid"] = selected["verdict"].ne("evaluation_invalid")
    selected["evaluation_status"] = selected["verdict"].replace(
        {"clean": "valid", "repair": "valid_after_harness_audit"}
    )
    selected["repository_url"] = "https://github.com/" + selected["repo"].str.replace(
        "__", "/", n=1, regex=False
    )
    selected["commit_url"] = (
        selected["repository_url"] + "/commit/" + selected["commit_sha"]
    )

    output_columns = [
        "snippet_id",
        "repo",
        "repository_url",
        "commit_sha",
        "commit_url",
        "code_folder",
        "pandas_code",
        "polars_code",
        "migration_diff",
        "snippet_note",
        "pandas_label_all",
        "polars_label_all",
        "migration_categories",
        *CATEGORY_COLUMNS.values(),
        "migration_pattern_note",
        "evaluation_valid",
        "evaluation_status",
        "evidence",
        "action",
    ]
    result = selected[output_columns].rename(
        columns={
            "repo": "repository",
            "code_folder": "source_file",
            "pandas_label_all": "pandas_api_labels",
            "polars_label_all": "polars_api_labels",
            "evidence": "evaluation_audit_evidence",
            "action": "evaluation_audit_action",
        }
    )

    if len(result) != 238 or result["snippet_id"].nunique() != 238:
        raise ValueError("Expected 238 unique final snippets")
    required = [
        "repository",
        "commit_sha",
        "source_file",
        "pandas_code",
        "polars_code",
        "migration_categories",
    ]
    missing = {
        column: int(result[column].fillna("").astype(str).str.strip().eq("").sum())
        for column in required
    }
    if any(missing.values()):
        raise ValueError(f"Missing required values: {missing}")
    if int(result["evaluation_valid"].sum()) != 231:
        raise ValueError("Expected 231 evaluation-valid snippets")

    result.to_csv(output_dir / "migration_pairs.csv", index=False)
    result.to_excel(output_dir / "migration_pairs.xlsx", index=False)

    counts = {
        category: int(result[column].sum())
        for category, column in CATEGORY_COLUMNS.items()
    }
    summary = pd.DataFrame(
        [{"migration_category": key, "pairs": value} for key, value in counts.items()]
    )
    summary.to_csv(output_dir / "migration_category_counts.csv", index=False)

    print(f"Wrote {len(result)} migration pairs to {output_dir}")
    print(f"Evaluation-valid pairs: {int(result['evaluation_valid'].sum())}")
    print(summary.to_string(index=False))


if __name__ == "__main__":
    main()
