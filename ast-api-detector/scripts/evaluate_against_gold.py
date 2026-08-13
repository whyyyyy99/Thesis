#!/usr/bin/env python3
"""Compare detector output with manually annotated API sets."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


def normalize_api(value: str) -> str:
    value = value.strip()
    if value == "detected_pandas_apis =":
        return ""
    return re.sub(r"^pandas\.(DataFrameGroupBy|SeriesGroupBy)\.", r"\1.", value)


def parse_set(value: str) -> set[str]:
    return {
        normalized
        for item in re.split(r"[,\n]+", value or "")
        if (normalized := normalize_api(item))
    }


def ratio(numerator: int, denominator: int) -> float:
    return numerator / denominator if denominator else 0.0


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--gold", type=Path, required=True)
    parser.add_argument("--detections", type=Path, required=True)
    parser.add_argument("--details", type=Path, required=True)
    parser.add_argument("--summary", type=Path, required=True)
    args = parser.parse_args()

    with args.gold.open(newline="", encoding="utf-8") as handle:
        gold_rows = list(csv.DictReader(handle))
    detections = {
        row["snippet_id"]: row
        for line in args.detections.read_text(encoding="utf-8").splitlines()
        if line.strip()
        for row in [json.loads(line)]
    }

    if {row["snippet_id"] for row in gold_rows} != set(detections):
        raise ValueError("Gold and detector snippet identifiers differ")

    details = []
    for row in gold_rows:
        snippet_id = row["snippet_id"]
        gold = parse_set(row["gold_detected_pandas_apis"])
        detected = {
            normalized
            for item in detections[snippet_id]["normalized_apis"]
            if (normalized := normalize_api(item))
        }
        tp, fp, fn = gold & detected, detected - gold, gold - detected
        if gold == detected:
            status = "exact"
        elif tp:
            status = "partial"
        elif gold and not detected:
            status = "false-negative only"
        elif detected and not gold:
            status = "false-positive only"
        else:
            status = "disjoint"
        details.append({
            "snippet_id": snippet_id,
            "parse_success": detections[snippet_id]["parse_success"],
            "match_status": status,
            "gold_api_count": len(gold),
            "detected_api_count": len(detected),
            "tp_count": len(tp),
            "fp_count": len(fp),
            "fn_count": len(fn),
            "gold_detected_pandas_apis": "\n".join(sorted(gold)),
            "detected_pandas_apis": "\n".join(sorted(detected)),
            "true_positives": "\n".join(sorted(tp)),
            "false_positives": "\n".join(sorted(fp)),
            "false_negatives": "\n".join(sorted(fn)),
        })

    args.details.parent.mkdir(parents=True, exist_ok=True)
    with args.details.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(details[0]))
        writer.writeheader()
        writer.writerows(details)

    tp = sum(row["tp_count"] for row in details)
    fp = sum(row["fp_count"] for row in details)
    fn = sum(row["fn_count"] for row in details)
    precision = ratio(tp, tp + fp)
    recall = ratio(tp, tp + fn)
    f1 = ratio(2 * precision * recall, precision + recall)
    summary = [{
        "snippets": len(details),
        "parse_success": sum(row["parse_success"] for row in details),
        "exact_matches": sum(row["match_status"] == "exact" for row in details),
        "tp": tp,
        "fp": fp,
        "fn": fn,
        "precision": round(precision, 6),
        "recall": round(recall, 6),
        "f1": round(f1, 6),
    }]
    with args.summary.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(summary[0]))
        writer.writeheader()
        writer.writerows(summary)
    print(summary[0])


if __name__ == "__main__":
    main()
