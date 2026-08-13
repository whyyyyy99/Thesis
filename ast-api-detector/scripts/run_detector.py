#!/usr/bin/env python3
"""Run the AST-based pandas API detector over a CSV snippet corpus."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from ast_api_locator import build_maps_from_json, extract_pandas_api_details


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--mapping", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--id-column", default="snippet_id")
    parser.add_argument("--code-column", default="pandas_code")
    args = parser.parse_args()

    maps = build_maps_from_json(str(args.mapping))
    with args.input.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))

    args.output.parent.mkdir(parents=True, exist_ok=True)
    parsed = 0
    with args.output.open("w", encoding="utf-8") as handle:
        for row in rows:
            details = extract_pandas_api_details(row[args.code_column], maps=maps)
            parsed += int(details["parse_success"])
            record = {"snippet_id": row[args.id_column], **details}
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")

    print(f"Wrote {len(rows)} detections to {args.output}; parse success: {parsed}/{len(rows)}")


if __name__ == "__main__":
    main()
