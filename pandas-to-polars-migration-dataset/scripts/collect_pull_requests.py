#!/usr/bin/env python3
"""Collect merged GitHub pull requests that may describe pandas-to-Polars migrations."""

from __future__ import annotations

import argparse
import os
import time
from pathlib import Path

import pandas as pd
import requests


API_ROOT = "https://api.github.com"
BOT_EXCLUSIONS = (
    "-author:dependabot -author:dependabot[bot] "
    "-author:renovate -author:renovate[bot] "
    "-author:pre-commit-ci -author:github-actions -author:github-actions[bot]"
)
QUERY_PATTERNS = (
    "pandas polars (replace OR switch OR migrate OR convert) in:title",
    '"replace pandas with polars" in:title',
    '"pandas to polars" in:title',
    '"migration to polars" pandas in:title',
    '"switch to polars" pandas in:title',
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--start-year", type=int, default=2023)
    parser.add_argument("--end-year", type=int, default=2025)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--sleep", type=float, default=0.25)
    return parser.parse_args()


def request_json(session: requests.Session, url: str, params: dict) -> dict:
    for attempt in range(6):
        response = session.get(url, params=params, timeout=60)
        if response.status_code == 200:
            return response.json()
        if response.status_code in {403, 429}:
            time.sleep(min(60, 2 ** attempt))
            continue
        response.raise_for_status()
    raise RuntimeError(f"GitHub request failed after retries: {url}")


def main() -> None:
    args = parse_args()
    token = os.environ.get("GITHUB_TOKEN", "").strip()
    if not token:
        raise RuntimeError("Set the GITHUB_TOKEN environment variable")

    session = requests.Session()
    session.headers.update(
        {
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }
    )

    rows: list[dict] = []
    for year in range(args.start_year, args.end_year + 1):
        for pattern in QUERY_PATTERNS:
            query = (
                f"{pattern} is:pr is:merged -is:draft {BOT_EXCLUSIONS} "
                f"merged:{year}-01-01..{year}-12-31"
            )
            for page in range(1, 11):
                payload = request_json(
                    session,
                    f"{API_ROOT}/search/issues",
                    {"q": query, "per_page": 100, "page": page},
                )
                items = payload.get("items", [])
                for item in items:
                    repository = item["repository_url"].split("/repos/", 1)[-1]
                    rows.append(
                        {
                            "repository": repository,
                            "pr_number": item["number"],
                            "pr_title": item["title"],
                            "pr_url": item["html_url"],
                            "author": item.get("user", {}).get("login", ""),
                            "created_at": item.get("created_at", ""),
                            "updated_at": item.get("updated_at", ""),
                            "query_year": year,
                            "query_pattern": pattern,
                        }
                    )
                if len(items) < 100:
                    break
                time.sleep(args.sleep)

    result = pd.DataFrame(rows).drop_duplicates(["repository", "pr_number"])
    args.output.parent.mkdir(parents=True, exist_ok=True)
    result.to_csv(args.output, index=False)
    print(f"Wrote {len(result)} pull requests from {result['repository'].nunique()} repositories")


if __name__ == "__main__":
    main()
