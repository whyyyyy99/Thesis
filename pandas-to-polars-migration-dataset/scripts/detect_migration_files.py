#!/usr/bin/env python3
"""Detect file-level commits that remove pandas code and add Polars code."""

from __future__ import annotations

import argparse
import re
import subprocess
from pathlib import Path

import pandas as pd


PANDAS_SIGNAL = re.compile(
    r"(?:\bimport\s+pandas\b|\bfrom\s+pandas\b|\bpd\.|\bpandas\.)",
    re.IGNORECASE,
)
POLARS_SIGNAL = re.compile(
    r"(?:\bimport\s+polars\b|\bfrom\s+polars\b|\bpl\.|\bpolars\.)",
    re.IGNORECASE,
)


def git(repository: Path, *arguments: str) -> str:
    result = subprocess.run(
        ["git", *arguments],
        cwd=repository,
        check=True,
        capture_output=True,
        text=True,
        errors="replace",
    )
    return result.stdout


def changed_python_files(repository: Path, sha: str) -> list[str]:
    output = git(repository, "diff-tree", "--no-commit-id", "--name-only", "-r", sha)
    return [line for line in output.splitlines() if line.endswith(".py")]


def added_deleted_text(patch: str) -> tuple[str, str]:
    added = []
    deleted = []
    for line in patch.splitlines():
        if line.startswith("+++") or line.startswith("---"):
            continue
        if line.startswith("+"):
            added.append(line[1:])
        elif line.startswith("-"):
            deleted.append(line[1:])
    return "\n".join(added), "\n".join(deleted)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repositories", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--since", default="2023-01-01")
    parser.add_argument("--until", default="2025-12-31")
    parser.add_argument("--max-commits", type=int, default=2000)
    args = parser.parse_args()

    rows: list[dict] = []
    for repository in sorted(args.repositories.iterdir()):
        if not (repository / ".git").exists():
            continue
        log = git(
            repository,
            "log",
            "--no-merges",
            f"--since={args.since}",
            f"--until={args.until}",
            f"--max-count={args.max_commits}",
            "--format=%H%x09%s",
            "--regexp-ignore-case",
            "--grep=pandas|polars",
            "--extended-regexp",
        )
        for record in log.splitlines():
            sha, subject = record.split("\t", 1)
            for file_path in changed_python_files(repository, sha):
                patch = git(repository, "show", "--format=", sha, "--", file_path)
                added, deleted = added_deleted_text(patch)
                if not (PANDAS_SIGNAL.search(deleted) and POLARS_SIGNAL.search(added)):
                    continue
                rows.append(
                    {
                        "repository": repository.name.replace("__", "/", 1),
                        "commit_sha": sha,
                        "commit_subject": subject,
                        "file_path": file_path,
                        "added_lines": len(added.splitlines()),
                        "deleted_lines": len(deleted.splitlines()),
                        "patch": patch,
                    }
                )

    result = pd.DataFrame(rows)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    result.to_csv(args.output, index=False)
    print(f"Wrote {len(result)} candidate migration files")


if __name__ == "__main__":
    main()
