#!/usr/bin/env python3
"""Create path-sanitised source, intermediate, and audit release files."""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


PATH_COLUMNS = {
    "before_path",
    "after_path",
    "patch_path",
    "source_json",
    "before_file",
    "after_file",
    "patch_file",
}


def read_csv(path: Path) -> pd.DataFrame:
    for encoding in ("utf-8-sig", "utf-8", "cp1252", "latin1"):
        try:
            return pd.read_csv(path, encoding=encoding)
        except UnicodeDecodeError:
            continue
    raise UnicodeDecodeError("unknown", b"", 0, 1, f"Cannot decode {path}")


def sanitise_path(value: object, workspace: Path) -> object:
    if not isinstance(value, str) or not value:
        return value
    normalised = value.replace("\\", "/")
    workspace_text = str(workspace).replace("\\", "/").rstrip("/") + "/"
    if normalised.startswith(workspace_text):
        return normalised[len(workspace_text) :]
    return normalised


def sanitise_frame(frame: pd.DataFrame, workspace: Path) -> pd.DataFrame:
    result = frame.copy()
    if {"repo", "sha"}.issubset(result.columns):
        repeated_header = result["repo"].astype(str).eq("repo") & result["sha"].astype(
            str
        ).eq("sha")
        result = result.loc[~repeated_header].copy()
    for column in PATH_COLUMNS.intersection(result.columns):
        result[column] = result[column].map(lambda value: sanitise_path(value, workspace))
    return result


def write_clean_workbook(source: Path, target: Path, workspace: Path) -> None:
    sheets = pd.read_excel(source, sheet_name=None)
    with pd.ExcelWriter(target, engine="openpyxl") as writer:
        for name, frame in sheets.items():
            sanitise_frame(frame, workspace).to_excel(writer, sheet_name=name[:31], index=False)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workspace", type=Path, required=True)
    parser.add_argument("--release-dir", type=Path, required=True)
    parser.add_argument("--legacy-scripts-dir", type=Path)
    args = parser.parse_args()
    workspace = args.workspace.resolve()
    release = args.release_dir.resolve()

    source_dir = release / "data/source"
    intermediate_dir = release / "data/intermediate"
    audit_dir = release / "audit"
    for directory in (source_dir, intermediate_dir, audit_dir):
        directory.mkdir(parents=True, exist_ok=True)

    pull_requests = read_csv(workspace / "source/pandas-to-polars-PRs-quickview.csv")
    pull_requests.to_csv(source_dir / "candidate_pull_requests_round1.csv", index=False)
    if args.legacy_scripts_dir:
        legacy = args.legacy_scripts_dir.resolve()
        source_files = {
            "second——pandas-to-polars-PRs-quickview.csv": (
                "candidate_pull_requests_round2.csv"
            ),
            "pandas-to-polars-repos-quickview.csv": "candidate_repositories_round1.csv",
            "second——pandas-to-polars-repos-quickview.csv": (
                "candidate_repositories_round2.csv"
            ),
        }
        for source_name, target_name in source_files.items():
            read_csv(legacy / source_name).to_csv(source_dir / target_name, index=False)

    intermediate_files = {
        "first_migration_commits_summary.csv": "migration_commits_round1.csv",
        "second_migration_commits_summary.csv": "migration_commits_round2.csv",
        "first_isolated_migrations_by_file.csv": "candidate_files_round1.csv",
        "second_isolated_migrations_by_file.csv": "candidate_files_round2.csv",
        "first_pair_inventory_test_yes.csv": "pair_inventory_round1.csv",
        "second_pair_inventory_test_yes.csv": "pair_inventory_round2.csv",
    }
    for source_name, target_name in intermediate_files.items():
        frame = read_csv(workspace / "pipeline_data" / source_name)
        sanitise_frame(frame, workspace).to_csv(intermediate_dir / target_name, index=False)

    workbooks = {
        workspace / "reviewed/first_pair_review_queue_v1_reviewed.xlsx": (
            audit_dir / "pair_review_round1.xlsx"
        ),
        workspace / "reviewed/pair_inventory_test_yes_reviewed_1.xlsx": (
            audit_dir / "pair_review_round2.xlsx"
        ),
        workspace / "reviewed/snippet_master_table.xlsx": (
            audit_dir / "snippet_metadata_review.xlsx"
        ),
    }
    for source, target in workbooks.items():
        write_clean_workbook(source, target, workspace)

    supplemental = read_csv(
        workspace / "reviewed/remaining_54_snippet_classifications.csv"
    )
    supplemental.to_csv(audit_dir / "supplemental_category_review.csv", index=False)

    print(f"Prepared release files under {release}")


if __name__ == "__main__":
    main()
