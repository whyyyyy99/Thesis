#!/usr/bin/env python3
"""Build an inventory from extracted migration JSON artifacts."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifacts", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    rows = []
    for path in sorted(args.artifacts.rglob("*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        relative = path.relative_to(args.artifacts)
        parts = relative.parts
        rows.append(
            {
                "snippet_id": path.stem,
                "repository": parts[0].replace("__", "/", 1),
                "commit_sha": parts[1] if len(parts) > 1 else "",
                "source_file": parts[2].replace("__", "/") if len(parts) > 2 else "",
                "artifact_path": str(relative),
                "pandas_code": data.get("before_snippet", ""),
                "polars_code": data.get("after_snippet", ""),
                "migration_diff": data.get("patch_snippet", ""),
                "snippet_note": data.get("snippet_note", ""),
            }
        )

    result = pd.DataFrame(rows)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    result.to_csv(args.output, index=False)
    print(f"Wrote {len(result)} artifact records")


if __name__ == "__main__":
    main()
