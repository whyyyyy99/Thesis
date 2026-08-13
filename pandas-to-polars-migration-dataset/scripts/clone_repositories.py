#!/usr/bin/env python3
"""Clone unique repositories listed in the pull-request candidate table."""

from __future__ import annotations

import argparse
import subprocess
from pathlib import Path

import pandas as pd


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()

    candidates = pd.read_csv(args.input)
    column = "repository" if "repository" in candidates else "repo"
    repositories = candidates[column].dropna().astype(str).drop_duplicates()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    for repository in repositories:
        destination = args.output_dir / repository.replace("/", "__")
        if (destination / ".git").exists():
            continue
        subprocess.run(
            [
                "git",
                "clone",
                "--filter=blob:none",
                f"https://github.com/{repository}.git",
                str(destination),
            ],
            check=True,
        )


if __name__ == "__main__":
    main()
