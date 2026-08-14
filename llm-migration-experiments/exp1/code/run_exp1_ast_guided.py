"""
Experiment 1 — AST-guided exact API mapping injection.

Method: AST-assisted API-guided prompting
  - Exact static mappings only; no documentation retrieval.
  - Uses AST analysis to detect pandas APIs, exact-matches against
    api_mapping.json, and injects matched records into the prompt.

Usage (from the `llm-migration-experiments/` root):
    # Dry run (no LLM): build prompts and save coverage report only
    python exp1/code/run_exp1_ast_guided.py \\
        --snippets-dir extracted_snippets \\
        --mapping exp1/knowledge/api_mapping.json \\
        --output exp1/results/reproduced_ast_guided_outputs.json \\
        --model ""

    # With LLM (requires OPENAI_API_KEY in environment)
    python exp1/code/run_exp1_ast_guided.py \\
        --snippets-dir extracted_snippets \\
        --mapping exp1/knowledge/api_mapping.json \\
        --output exp1/results/reproduced_ast_guided_outputs.json \\
        --model gpt-5.4-mini
"""

import argparse
import json
import logging
import os
import sys
from pathlib import Path

RELEASE_ROOT = Path(__file__).resolve().parents[2]

sys.path.insert(0, str(RELEASE_ROOT / "shared" / "code"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from ast_api_locator import build_maps_from_json
from exact_mapping_pipeline import (
    build_coverage_report,
    load_mapping,
    process_snippet,
)

PROMPT_TEMPLATE_PATH = RELEASE_ROOT / "exp1" / "prompts" / "prompt_template.txt"

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)


# ── Snippet loaders ────────────────────────────────────────────────────

def load_snippets_from_json(path: str):
    with open(path, encoding="utf-8") as f:
        records = json.load(f)
    snippets = []
    for r in records:
        sid  = r.get("id") or r.get("snippet_id") or str(len(snippets))
        code = r.get("code") or r.get("source_code") or ""
        entry = {"id": sid, "code": code}
        if "detected_apis" in r:
            entry["detected_apis"] = r["detected_apis"]
        snippets.append(entry)
    return snippets


def load_snippets_from_dir(snippets_dir: str):
    snippets = []
    for p in sorted(Path(snippets_dir).rglob("*_before.py")):
        snippets.append({"id": str(p), "code": p.read_text(encoding="utf-8", errors="ignore")})
    return snippets


# ── Console summary ────────────────────────────────────────────────────

def print_summary(report: dict, output_path: str, coverage_path: str) -> None:
    r = report
    total = r["total_snippets"]
    print(f"\n{'='*60}")
    print("  AST-GUIDED MIGRATION — SUMMARY")
    print(f"{'='*60}")
    print(f"Total snippets                  : {total}")
    print(f"Parse success                   : {r['parse_success_count']} / {total}")
    print(f"With detected APIs              : {r['snippets_with_detected_apis']} "
          f"({100*r['snippets_with_detected_apis']/max(total,1):.1f}%)")
    print(f"With matched mapping records    : {r['snippets_with_matched_records']} "
          f"({100*r['snippets_with_matched_records']/max(total,1):.1f}%)")
    print(f"Avg detected APIs / snippet     : {r['average_detected_apis_per_snippet']}")
    print(f"Avg matched records / snippet   : {r['average_matched_records_per_snippet']}")

    print(f"\nTop unmatched APIs:")
    for api, cnt in r["top_unmatched_apis"][:10]:
        print(f"  {cnt:4d}  {api}")

    print(f"\nTop unknown methods:")
    for m, cnt in r["top_unknown_methods"][:10]:
        print(f"  {cnt:4d}  {m}")

    print(f"\nOutputs  : {output_path}")
    print(f"Coverage : {coverage_path}")


# ── Entry point ────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Experiment 1: AST-guided exact API mapping injection."
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--snippets",     help="JSON file with snippet objects (id/code fields)")
    group.add_argument("--snippets-dir", help="Directory to scan for *_before.py files")
    parser.add_argument("--mapping",  required=True, help="Path to api_mapping.json")
    parser.add_argument("--output",   required=True, help="Output JSON path for per-snippet results")
    parser.add_argument("--model",    default="gpt-5.4-mini",  help="OpenAI model name; pass an empty string for dry run")
    parser.add_argument("--limit",    type=int, default=None, help="Process only first N snippets")
    args = parser.parse_args()

    # ── Load resources ─────────────────────────────────────────────
    logger.info(f"Loading mapping from {args.mapping}")
    mapping_records = load_mapping(args.mapping)
    maps = build_maps_from_json(args.mapping)
    logger.info(f"  {len(mapping_records)} mapping records loaded")

    template = PROMPT_TEMPLATE_PATH.read_text(encoding="utf-8")

    if args.snippets:
        logger.info(f"Loading snippets from {args.snippets}")
        snippets = load_snippets_from_json(args.snippets)
    else:
        logger.info(f"Scanning {args.snippets_dir} for *_before.py")
        snippets = load_snippets_from_dir(args.snippets_dir)
    logger.info(f"  {len(snippets)} snippets loaded")

    if args.limit:
        snippets = snippets[:args.limit]
        logger.info(f"  Limiting to first {args.limit} snippets")

    # ── Optional LLM ───────────────────────────────────────────────
    llm = None
    if args.model:
        import openai as _openai
        class _ResponsesLLM:
            class _R:
                def __init__(self, text): self.content = text
            def __init__(self, model):
                self._client = _openai.OpenAI()
                self.model = model
            def invoke(self, messages):
                text = messages[-1]["content"] if isinstance(messages[-1], dict) else messages[-1].content
                r = self._client.responses.create(
                    model=self.model,
                    reasoning={"effort": "low"},
                    input=text,
                    max_output_tokens=6000,
                )
                return self._R(r.output_text)
        api_key = os.environ.get("OPENAI_API_KEY", "")
        if not api_key:
            logger.warning("OPENAI_API_KEY not set — running in dry-run mode")
        else:
            llm = _ResponsesLLM(model=args.model)
            logger.info(f"LLM: {args.model} (responses API, reasoning=low)")
    else:
        logger.info("No --model provided — dry-run mode (prompts built, no LLM calls)")

    # ── Process snippets ───────────────────────────────────────────
    results = []
    for i, s in enumerate(snippets, 1):
        if i % 50 == 0 or i == len(snippets):
            logger.info(f"  [{i}/{len(snippets)}] processed")
        result = process_snippet(
            snippet_id=s["id"],
            source_code=s["code"],
            maps=maps,
            mapping_records=mapping_records,
            template=template,
            llm=llm,
            precomputed_apis=s["detected_apis"] if "detected_apis" in s else None,
        )
        results.append(result)

    # ── Save outputs ───────────────────────────────────────────────
    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    compact_results = []
    for r in results:
        c = dict(r)
        c.pop("matched_records", None)
        compact_results.append(c)

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(compact_results, f, indent=2, ensure_ascii=False)

    # ── Coverage report ────────────────────────────────────────────
    coverage = build_coverage_report(results)
    coverage_path = out_path.parent / "ast_api_mapping_coverage_report.json"
    with open(coverage_path, "w", encoding="utf-8") as f:
        json.dump(coverage, f, indent=2, ensure_ascii=False)

    print_summary(coverage, str(out_path), str(coverage_path))


if __name__ == "__main__":
    main()
