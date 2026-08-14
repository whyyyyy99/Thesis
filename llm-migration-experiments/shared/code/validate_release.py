#!/usr/bin/env python3
"""Validate the canonical release counts without rerunning generation or tests."""

from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DATASET = (
    ROOT.parent
    / "pandas-to-polars-migration-dataset"
    / "data"
    / "final"
    / "migration_pairs.csv"
)

RESULT_FILES = {
    "Baseline": ROOT / "baseline" / "results" / "test_results_v3.csv",
    "Exp1": ROOT / "exp1" / "results" / "test_results_v3.csv",
    "Exp2": ROOT / "exp2" / "results" / "test_results_v3.csv",
    "Exp3": ROOT / "exp3" / "results" / "test_results_v3.csv",
}

EXPECTED = {
    "Baseline": {"pass": 170, "L1": 26, "L2": 26, "L3": 9},
    "Exp1": {"pass": 172, "L1": 26, "L2": 27, "L3": 6},
    "Exp2": {"pass": 174, "L1": 32, "L2": 21, "L3": 4},
    "Exp3": {"pass": 170, "L1": 31, "L2": 25, "L3": 5},
}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def is_true(value: str) -> bool:
    return str(value).strip().lower() in {"1", "true", "yes"}


def primary_outcome(row: dict[str, str]) -> str:
    if row["l1_raw"] == "fail":
        return "L1"
    if row["l2_raw"] == "fail":
        return "L2"
    if row["l3_raw"] == "fail":
        return "L3"
    if is_true(row["all_pass"]):
        return "pass"
    raise ValueError(f"Unresolved primary outcome for {row['snippet_id']}")


def main() -> None:
    dataset = read_csv(DATASET)
    assert len(dataset) == 238
    valid_ids = {
        row["snippet_id"] for row in dataset if is_true(row["evaluation_valid"])
    }
    assert len(valid_ids) == 231

    for condition, path in RESULT_FILES.items():
        rows = read_csv(path)
        assert len(rows) == 238
        valid = [row for row in rows if not is_true(row["excluded"])]
        assert {row["snippet_id"] for row in valid} == valid_ids
        counts = Counter(primary_outcome(row) for row in valid)
        assert counts == Counter(EXPECTED[condition]), (condition, counts)
        print(f"{condition}: {dict(counts)}")

    combined = read_csv(
        ROOT / "shared" / "results" / "all_conditions_test_results_v3.csv"
    )
    assert len(combined) == 952
    assert Counter(row["condition"] for row in combined) == Counter(
        {condition: 238 for condition in RESULT_FILES}
    )

    taxonomy = read_csv(
        ROOT
        / "shared"
        / "results"
        / "all_conditions_taxonomy_classification_final.csv"
    )
    assert Counter(row["experiment"] for row in taxonomy) == Counter(
        {"baseline": 61, "exp1": 59, "exp2": 57, "exp3": 61}
    )

    profiles = read_csv(
        ROOT / "shared" / "results" / "knowledge_profile_outcomes.csv"
    )
    profile_totals = {
        condition: {
            field: sum(int(row[field]) for row in profiles if row["condition"] == condition)
            for field in ("snippets", "baseline_pass", "augmented_pass", "rescued", "regressed")
        }
        for condition in ("Exp1", "Exp2", "Exp3")
    }
    assert profile_totals == {
        "Exp1": {
            "snippets": 231,
            "baseline_pass": 170,
            "augmented_pass": 172,
            "rescued": 18,
            "regressed": 16,
        },
        "Exp2": {
            "snippets": 231,
            "baseline_pass": 170,
            "augmented_pass": 174,
            "rescued": 23,
            "regressed": 19,
        },
        "Exp3": {
            "snippets": 231,
            "baseline_pass": 170,
            "augmented_pass": 170,
            "rescued": 17,
            "regressed": 17,
        },
    }
    print("Release validation passed.")


if __name__ == "__main__":
    main()
