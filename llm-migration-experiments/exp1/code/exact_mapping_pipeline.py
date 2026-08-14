"""
AST-guided exact API mapping injection for pandas-to-Polars migration.

Method: AST-guided exact API mapping injection
  1. Detect pandas APIs in source code via AST analysis.
  2. Exact-match detected API names against api_mapping.json (no embeddings, no vector search).
  3. Inject matched records into a structured prompt.
  4. Optionally call an LLM to generate migrated Polars code.
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

sys.path.insert(0, str(Path(__file__).parent.parent))
from ast_api_locator import APIMaps, build_maps_from_json, extract_pandas_api_details

DEFAULT_PROMPT_TEMPLATE = Path(__file__).parent / "prompt_template.txt"


# ── Mapping helpers ────────────────────────────────────────────────────

def load_mapping(json_path: str) -> List[Dict]:
    """Load all records from api_mapping.json."""
    with open(json_path, encoding="utf-8") as f:
        return json.load(f)


def exact_match(
    detected_apis: List[str],
    mapping_records: List[Dict],
) -> Tuple[List[Dict], List[str], List[str]]:
    """Exact-match detected API names against mapping records.

    Returns (matched_records, matched_source_apis, unmatched_apis).
    """
    index = {
        r["source_api"]: r
        for r in mapping_records
        if r.get("source_api")
    }
    matched_records: List[Dict] = []
    matched_source_apis: List[str] = []
    unmatched_apis: List[str] = []

    for api in detected_apis:
        if api in index:
            matched_records.append(index[api])
            matched_source_apis.append(api)
        else:
            unmatched_apis.append(api)

    return matched_records, matched_source_apis, unmatched_apis


# ── Formatting ─────────────────────────────────────────────────────────

def format_mapping_records(records: List[Dict]) -> str:
    """Format matched mapping records for prompt injection."""
    if not records:
        return "(none)"
    lines = []
    for i, r in enumerate(records, 1):
        lines.append(f"[{i}] Source API: {r.get('source_api', '')}")
        if r.get("target_api"):
            lines.append(f"    Target API: {r['target_api']}")
        if r.get("functional_description"):
            lines.append(f"    Description: {r['functional_description']}")
        if r.get("usage_limitations"):
            lines.append(f"    Usage Limitations: {r['usage_limitations']}")
        if r.get("discrepancies"):
            lines.append(f"    Discrepancies: {r['discrepancies']}")
        lines.append("")
    return "\n".join(lines).strip()


# ── Prompt builder ─────────────────────────────────────────────────────

def build_prompt(
    source_code: str,
    detected_apis: List[str],
    matched_records: List[Dict],
    unmatched_apis: List[str],
    unknown_methods: List[str],
    template: str,
) -> str:
    """Fill the prompt template with AST-derived content."""
    detected_str = (
        "\n".join(f"  - {a}" for a in detected_apis)
        if detected_apis else "  (none detected)"
    )
    matched_str = format_mapping_records(matched_records)

    unmatched_all = sorted(set(unmatched_apis) | set(unknown_methods))
    unmatched_str = (
        "\n".join(f"  - {m}" for m in unmatched_all)
        if unmatched_all else "  (none)"
    )

    return template.format(
        source_code=source_code,
        detected_apis=detected_str,
        matched_mapping_records=matched_str,
        unmatched_or_unknown_apis=unmatched_str,
    )


# ── Per-snippet processor ──────────────────────────────────────────────

def process_snippet(
    snippet_id: str,
    source_code: str,
    maps: APIMaps,
    mapping_records: List[Dict],
    template: str,
    llm=None,
    precomputed_apis: List[str] = None,
) -> Dict:
    """Run the full AST-guided pipeline for one snippet.

    Returns a dict with all intermediate results and the generated code
    (empty string when no LLM is provided).
    """
    details = extract_pandas_api_details(source_code, maps=maps)
    detected_apis   = precomputed_apis if precomputed_apis is not None else details["normalized_apis"]
    # Note: precomputed_apis=[] means AST found nothing (valid result), not missing data
    op_keywords     = details["operation_keywords"]
    unknown_methods = details["unknown_methods"]

    matched_records, matched_source_apis, unmatched_apis = exact_match(
        detected_apis, mapping_records
    )

    prompt = build_prompt(
        source_code=source_code,
        detected_apis=detected_apis,
        matched_records=matched_records,
        unmatched_apis=unmatched_apis,
        unknown_methods=unknown_methods,
        template=template,
    )

    generated_code = ""
    if llm is not None:
        try:
            response = llm.invoke([{"role": "user", "content": prompt}])
            generated_code = response.content
        except Exception as exc:
            generated_code = f"# LLM ERROR: {exc}"

    return {
        "snippet_id":          snippet_id,
        "source_code":         source_code,
        "parse_success":       details["parse_success"],
        "detected_apis":       detected_apis,
        "operation_keywords":  op_keywords,
        "unknown_methods":     unknown_methods,
        "matched_records":     matched_records,
        "matched_source_apis": matched_source_apis,
        "unmatched_apis":      unmatched_apis,
        "prompt":              prompt,
        "generated_polars_code": generated_code,
    }


# ── Coverage report ────────────────────────────────────────────────────

def build_coverage_report(results: List[Dict]) -> Dict:
    """Aggregate per-snippet results into a coverage summary."""
    from collections import Counter

    total = len(results)
    parse_ok  = sum(1 for r in results if r["parse_success"])
    with_det  = sum(1 for r in results if r["detected_apis"])
    with_mat  = sum(1 for r in results if r["matched_records"])

    det_counter  = Counter()
    mat_counter  = Counter()
    unmat_counter = Counter()
    unk_counter   = Counter()

    for r in results:
        for a in r["detected_apis"]:
            det_counter[a] += 1
        for a in r["matched_source_apis"]:
            mat_counter[a] += 1
        for a in r["unmatched_apis"]:
            unmat_counter[a] += 1
        for m in r["unknown_methods"]:
            unk_counter[m] += 1

    avg_det = sum(len(r["detected_apis"]) for r in results) / max(total, 1)
    avg_mat = sum(len(r["matched_records"]) for r in results) / max(total, 1)

    zero_det_examples = [
        {"snippet_id": r["snippet_id"], "parse_success": r["parse_success"],
         "unknown_methods": r["unknown_methods"]}
        for r in results if not r["detected_apis"]
    ][:10]

    zero_mat_examples = [
        {"snippet_id": r["snippet_id"], "detected_apis": r["detected_apis"],
         "unmatched_apis": r["unmatched_apis"]}
        for r in results if not r["matched_records"]
    ][:10]

    return {
        "total_snippets":                    total,
        "parse_success_count":               parse_ok,
        "parse_failed_count":                total - parse_ok,
        "snippets_with_detected_apis":       with_det,
        "snippets_with_zero_detected_apis":  total - with_det,
        "snippets_with_matched_records":     with_mat,
        "snippets_with_zero_matched_records": total - with_mat,
        "average_detected_apis_per_snippet": round(avg_det, 3),
        "average_matched_records_per_snippet": round(avg_mat, 3),
        "top_detected_apis":   det_counter.most_common(20),
        "top_matched_apis":    mat_counter.most_common(20),
        "top_unmatched_apis":  unmat_counter.most_common(20),
        "top_unknown_methods": unk_counter.most_common(20),
        "examples_zero_detected_apis":   zero_det_examples,
        "examples_zero_matched_records": zero_mat_examples,
    }
