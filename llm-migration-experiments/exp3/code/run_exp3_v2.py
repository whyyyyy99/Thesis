"""
Experiment 3 V2 — Static mapping (exact lookup) + Embedding-only retrieval.

4-way case classification per detected pandas API:
  mapping_hit_doc_found       : static mapping hit + doc in corpus → direct lookup
  mapping_hit_doc_missing     : static mapping hit, doc absent → confirmed target kept,
                                embedding used as supplementary
  mapping_no_direct_equivalent: static mapping says no equivalent → embedding supplementary
  mapping_miss                : not in static mapping → pure embedding

Corpus: polars_docs_union.json (polars.Config.* removed upstream)

Usage (from ``llm-migration-experiments``):
    python exp3/code/run_exp3_v2.py --limit 40
    python exp3/code/run_exp3_v2.py                         # all 238
    python exp3/code/run_exp3_v2.py --model gpt-5.4-mini    # with generation
"""

# Must be set before any torch / numpy import to avoid macOS mutex crash
import os
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["TOKENIZERS_PARALLELISM"] = "false"
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

import argparse
import csv
import json
import logging
import sys
from pathlib import Path
from typing import Dict, List, Tuple

RELEASE_ROOT = Path(__file__).resolve().parents[2]

sys.path.insert(0, str(RELEASE_ROOT / "shared" / "code"))
sys.path.insert(0, str(RELEASE_ROOT / "exp2" / "code"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from documentation_retrieval import (
    build_pandas_doc_index,
    lookup_all_pandas_docs,
    build_embedding_query,
)
from retrieval import (
    EmbeddingRetriever,
    filter_conversion_candidates,
    is_conversion_intent,
)
from static_mapping import (
    load_static_mapping_index,
    lookup_static_mapping,
    build_query_case_a,
)
from ast_api_locator import build_maps_from_json, extract_pandas_api_details

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

PREV_RESULTS           = RELEASE_ROOT / "exp3" / "results"
OUTPUT_DIR             = RELEASE_ROOT / "exp3" / "results" / "reproduced"
POLARS_DOCS            = RELEASE_ROOT / "shared" / "knowledge" / "polars_docs_union.json"
PANDAS_DOCS_STRUCTURED = RELEASE_ROOT / "shared" / "knowledge" / "pandas_api_structured.json"
MAPPING_JSON           = RELEASE_ROOT / "exp3" / "knowledge" / "api_mapping.json"
PROMPT_TEMPLATE        = RELEASE_ROOT / "exp3" / "prompts" / "prompt_template.txt"
GOLD_LABELS            = RELEASE_ROOT / "shared" / "input" / "gold_labels_review.csv"

_PANDAS_DOC_ALIASES: Dict[str, str] = {
    "DataFrameGroupBy.cumcount":  "pandas.api.typing.DataFrameGroupBy.cumcount",
    "DataFrameGroupBy.first":     "pandas.api.typing.DataFrameGroupBy.first",
    "DataFrameGroupBy.ngroup":    "pandas.api.typing.DataFrameGroupBy.ngroup",
    "DataFrameGroupBy.sum":       "pandas.api.typing.DataFrameGroupBy.sum",
    "SeriesGroupBy.agg":          "pandas.api.typing.SeriesGroupBy.agg",
    "SeriesGroupBy.apply":        "pandas.api.typing.SeriesGroupBy.apply",
    "pandas.DataFrame.merge":     "pandas.merge",
    "pandas.DataFrame.melt":      "pandas.melt",
    "pandas.DataFrame.pivot":     "pandas.pivot",
}


def write_jsonl(path: Path, records) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")


def _object_type(api_name: str) -> str:
    """Return the receiver category encoded in a normalized pandas API."""
    if api_name.startswith("pandas.DataFrame.") or api_name == "pandas.DataFrame":
        return "DataFrame"
    if api_name.startswith("pandas.Series.") or api_name == "pandas.Series":
        return "Series"
    if api_name.startswith(("pandas.Index.", "pandas.MultiIndex.")):
        return "Index"
    if api_name.startswith("DataFrameGroupBy."):
        return "DataFrameGroupBy"
    if api_name.startswith("SeriesGroupBy."):
        return "SeriesGroupBy"
    if api_name.startswith("pandas."):
        return "pandas"
    return "unknown"


def detect_apis(pandas_code: str, maps) -> Tuple[List[Dict], Dict]:
    """Run the same shared AST detector used by Exp1."""
    details = extract_pandas_api_details(pandas_code, maps=maps)
    entries = [
        {
            "api_name": name,
            "call_text": name,
            "object_type": _object_type(name),
            "detection_source": "AST",
        }
        for name in details["normalized_apis"]
    ]
    return entries, details


def load_gold_labels(
    path: Path,
) -> Dict[str, Dict]:
    """Load the 238 snippet IDs and source texts; API detection runs separately."""
    snippets: Dict[str, Dict] = {}
    with open(path, encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            sid = row["snippet_id"]
            snippets[sid] = {"snippet_id": sid, "pandas_code": row["pandas_code"]}
    return snippets


def load_pandas_index(path: Path) -> Dict[str, Dict]:
    """Build pandas doc index from pandas_api_structured.json (688 docs)."""
    with open(path, encoding="utf-8") as f:
        docs = json.load(f)
    index = build_pandas_doc_index(docs)
    for detected, canonical in _PANDAS_DOC_ALIASES.items():
        if canonical in index and detected not in index:
            index[detected] = index[canonical]
    return index


def build_polars_doc_index(polars_docs: List[Dict]) -> Dict[str, Dict]:
    return {d["api_name"]: d for d in polars_docs if d.get("api_name")}


# ── Text helpers ─────────────────────────────────────────────────────────────

def _to_sentence(text: str, soft_limit: int = 200, max_extend: int = 150) -> str:
    """Return text up to soft_limit chars, extended to the end of the current sentence."""
    if len(text) <= soft_limit:
        return text.strip()
    for sep in (". ", ".\n", "! ", "!\n", "? ", "?\n"):
        pos = text.find(sep, soft_limit)
        if 0 < pos <= soft_limit + max_extend:
            return text[: pos + 1].strip()
    return text[:soft_limit].rstrip() + "…"


# ── Prompt builder ────────────────────────────────────────────────────────────

def _fmt_candidates(candidates: List[Dict]) -> str:
    lines = []
    for c in candidates:
        line = f"  {c['rank']}. {c['polars_api']} (score={c['score']:.4f})"
        if c.get("description"):
            line += f"\n     {c['description']}"
        if c.get("examples"):
            line += f"\n     Example: {c['examples']}"
        lines.append(line)
    return "\n".join(lines)


def _append_mapping_guidance(guidance_lines: List[str], api: str, g: Dict) -> None:
    """Append raw mapping text as supplementary migration guidance for no-doc cases."""
    raw_target = g.get("target_api", "")
    desc       = g.get("functional_description", "")
    limits     = g.get("usage_limitations", "")
    disc       = g.get("discrepancies", "")
    parts = []
    if raw_target:
        parts.append(f"  Suggested migration: {raw_target}")
    if desc:
        parts.append(f"  Notes: {desc[:300]}")
    if limits:
        parts.append(f"  Limitations: {limits[:200]}")
    if disc:
        parts.append(f"  Discrepancies: {disc[:200]}")
    if parts:
        guidance_lines.append(f"\n{api}:\n" + "\n".join(parts))


def build_prompt_exp3(
    snippet:       Dict,
    detected_apis: List[Dict],
    missing:       List[str],
    api_results:   List[Dict],
    template:      str,
) -> str:
    """Fill the EXP3 prompt template using the 4-way case classification."""
    api_list = "\n".join(
        f"  - {e['api_name']} ({e.get('object_type', 'method')})"
        for e in detected_apis
    ) or "  (none detected)"

    confirmed_lines:  List[str] = []
    pd_behavior:      List[str] = []
    supporting_lines: List[str] = []
    guidance_lines:   List[str] = []
    candidate_lines:  List[str] = []
    warning_lines:    List[str] = []

    for res in api_results:
        api       = res["source_pandas_api"]
        case      = res["case"]
        target    = res.get("confirmed_target_api") or ""
        pd_desc   = res.get("pandas_description", "")
        cands     = res.get("top_candidates", [])
        g         = res.get("mapping_guidance") or {}

        if pd_desc:
            pd_behavior.append(f"  {api}: {pd_desc}")

        if case == "mapping_hit_doc_found":
            confirmed_lines.append(f"  {api} → {target}")
            if g.get("functional_description"):
                confirmed_lines.append(f"    Notes: {g['functional_description'][:250]}")
            if g.get("usage_limitations"):
                confirmed_lines.append(f"    Limitations: {g['usage_limitations'][:200]}")
            if g.get("discrepancies"):
                confirmed_lines.append(f"    Discrepancies: {g['discrepancies'][:200]}")
            doc_desc = cands[0].get("description", "") if cands else ""
            if doc_desc:
                supporting_lines.append(f"\n{target}\n  {doc_desc[:300]}")

        elif case == "mapping_hit_doc_missing":
            confirmed_lines.append(
                f"  {api} → {target}  [doc not in corpus — see guidance below]"
            )
            # Pass raw mapping text as supplementary migration guidance
            _append_mapping_guidance(guidance_lines, api, g)
            if cands:
                candidate_lines.append(
                    f"\n{api}  [mapping confirmed: {target}, doc absent — supplementary only]"
                )
                candidate_lines.append(_fmt_candidates(cands))

        elif case == "mapping_no_direct_equivalent":
            confirmed_lines.append(f"  {api} → {target}  [no direct Polars equivalent — see guidance below]")
            # Pass raw mapping text as supplementary migration guidance
            _append_mapping_guidance(guidance_lines, api, g)
            if cands:
                candidate_lines.append(
                    f"\n{api}  [static mapping: no direct equivalent — candidates supplementary only]"
                )
                candidate_lines.append(_fmt_candidates(cands))

        else:  # mapping_miss
            if cands:
                candidate_lines.append(f"\n{api}")
                candidate_lines.append(_fmt_candidates(cands))
            else:
                warning_lines.append(f"  {api}: no static mapping and no retrieval candidates")

    if missing:
        for m in missing:
            warning_lines.append(f"  {m}: pandas doc not found")

    return template.format(
        source_code                = snippet["pandas_code"],
        detected_apis              = api_list,
        confirmed_static_mappings  = "\n".join(confirmed_lines)  or "  (none)",
        pandas_behavior_docs       = "\n".join(pd_behavior)      or "  (none)",
        supporting_polars_docs     = "\n".join(supporting_lines) or "  (none)",
        mapping_migration_guidance = "\n".join(guidance_lines)   or "  (none)",
        candidate_polars_docs      = "\n".join(candidate_lines)  or "  (none)",
        missing_knowledge_warnings = "\n".join(warning_lines)    or "  (none)",
    )


def process_one(
    snippet:             Dict,
    detected_apis:       List[Dict],
    ast_details:         Dict,
    pandas_index:        Dict[str, Dict],
    mapping_index:       Dict[str, Dict],
    polars_doc_index:    Dict[str, Dict],
    embedding_retriever,
    template:            str,
    top_k:               int = 5,
    llm                      = None,
) -> Tuple[Dict, List[Dict]]:
    sid         = snippet["snippet_id"]
    pandas_code = snippet["pandas_code"]

    matched_docs, missing = lookup_all_pandas_docs(
        {"detected_apis": detected_apis}, pandas_index
    )
    missing = sorted(set(missing) | set(ast_details["unknown_methods"]))

    api_results: List[Dict] = []
    diagnostics: List[Dict] = []

    for item in matched_docs:
        api_entry  = item["api_entry"]
        pandas_doc = item["pandas_doc"]
        api_name   = api_entry["api_name"]

        mapping, lookup_key = lookup_static_mapping(api_name, mapping_index)

        # ── 4-way case classification ──────────────────────────────────────
        # mapping_hit_doc_found       : static mapping hit + doc in corpus
        #                               → direct lookup, no retrieval
        # mapping_hit_doc_missing     : static mapping hit, but doc absent from corpus
        #                               → confirmed target kept as primary reference;
        #                                 embedding used as supplementary only
        # mapping_no_direct_equivalent: static mapping hit, target is a prose description
        #                               → no Polars API to retrieve; pass description
        # mapping_miss                : not in static mapping
        #                               → pure embedding retrieval

        confirmed_target = None  # set for mapping_hit_* cases
        emb_filtered     = []

        if mapping:
            target      = mapping.get("target_api", "")
            # Use target_apis list (pre-parsed clean API names) for corpus lookup.
            # Fall back to parsing target_api string if field absent.
            target_apis = mapping.get("target_apis") or []

            # Find first target API that exists in the corpus
            doc         = None
            hit_target  = None
            for t in target_apis:
                d = polars_doc_index.get(t)
                if d:
                    doc        = d
                    hit_target = t
                    break

            confirmed_target = hit_target or (target_apis[0] if target_apis else target)

            if doc:
                case           = "mapping_hit_doc_found"
                top_candidates = [{
                    "polars_api_name":        hit_target,
                    "rank":                   1,
                    "score":                  1.0,
                    "functional_description": doc.get("functional_description", ""),
                    "examples":               doc.get("examples", ""),
                    "is_supplementary":       False,
                }]
                # Also include other target_apis found in corpus as supplementary
                for t in target_apis:
                    if t != hit_target:
                        d2 = polars_doc_index.get(t)
                        if d2:
                            top_candidates.append({
                                "polars_api_name":        t,
                                "rank":                   len(top_candidates) + 1,
                                "score":                  1.0,
                                "functional_description": d2.get("functional_description", ""),
                                "examples":               d2.get("examples", ""),
                                "is_supplementary":       False,
                            })
                query = f"direct_lookup:{confirmed_target}"

            elif any(t.startswith("polars.") for t in target_apis) or target.startswith("polars."):
                case   = "mapping_hit_doc_missing"
                sm_rec = {
                    "source_api":     api_name,
                    "mapping_status": "found",
                    "target_api":     confirmed_target,
                    "lookup_key":     lookup_key,
                }
                query       = build_query_case_a(api_entry, pandas_doc, sm_rec, pandas_code)
                conv_intent = is_conversion_intent(api_name)
                emb_raw     = embedding_retriever.retrieve(query, top_k=top_k)
                emb_kept, emb_filtered = filter_conversion_candidates(emb_raw, api_name, conv_intent)
                top_candidates = [
                    {
                        "polars_api_name":        c["polars_api_name"],
                        "rank":                   c["rank"],
                        "score":                  c["score"],
                        "functional_description": c.get("functional_description", ""),
                        "examples":               c.get("examples", ""),
                        "is_supplementary":       True,
                    }
                    for c in emb_kept[:top_k]
                ]

            else:
                case        = "mapping_no_direct_equivalent"
                query       = build_embedding_query(api_entry, pandas_doc, pandas_code)
                conv_intent = is_conversion_intent(api_name)
                emb_raw     = embedding_retriever.retrieve(query, top_k=top_k)
                emb_kept, emb_filtered = filter_conversion_candidates(emb_raw, api_name, conv_intent)
                top_candidates = [
                    {
                        "polars_api_name":        c["polars_api_name"],
                        "rank":                   c["rank"],
                        "score":                  c["score"],
                        "functional_description": c.get("functional_description", ""),
                        "examples":               c.get("examples", ""),
                        "is_supplementary":       True,
                    }
                    for c in emb_kept[:top_k]
                ]

        else:
            case        = "mapping_miss"
            query       = build_embedding_query(api_entry, pandas_doc, pandas_code)
            conv_intent = is_conversion_intent(api_name)
            emb_raw     = embedding_retriever.retrieve(query, top_k=top_k)
            emb_kept, emb_filtered = filter_conversion_candidates(emb_raw, api_name, conv_intent)
            top_candidates = [
                {
                    "polars_api_name":        c["polars_api_name"],
                    "rank":                   c["rank"],
                    "score":                  c["score"],
                    "functional_description": c.get("functional_description", ""),
                    "examples":               c.get("examples", ""),
                    "is_supplementary":       False,
                }
                for c in emb_kept[:top_k]
            ]

        # Attach raw mapping metadata for all mapping-hit cases
        _mapping_guidance = None
        if mapping:
            _mapping_guidance = {
                "target_api":             mapping.get("target_api", ""),
                "functional_description": mapping.get("functional_description", ""),
                "usage_limitations":      mapping.get("usage_limitations", ""),
                "discrepancies":          mapping.get("discrepancies", ""),
            }

        api_results.append({
            "source_pandas_api":      api_name,
            "pandas_description":     _to_sentence(pandas_doc.get("functional_description", "")),
            "case":                   case,
            "confirmed_target_api":   confirmed_target,
            "mapping_guidance":       _mapping_guidance,
            "query":                  query,
            "top_candidates": [
                {
                    "rank":             i + 1,
                    "polars_api":       c["polars_api_name"],
                    "score":            c["score"],
                    "is_supplementary": c.get("is_supplementary", False),
                    "description":      _to_sentence(c.get("functional_description", "")),
                    "examples":         c.get("examples", ""),
                }
                for i, c in enumerate(top_candidates)
            ],
            "filtered_conversion_apis": [c["polars_api_name"] for c in emb_filtered],
        })

        diagnostics.append({
            "snippet_id":           sid,
            "source_pandas_api":    api_name,
            "case":                 case,
            "confirmed_target_api": confirmed_target,
            "query":                query,
            "embedding_candidates_after_filter": [
                {
                    "api_name":         c["polars_api_name"],
                    "rank":             c["rank"],
                    "score":            c["score"],
                    "is_supplementary": c.get("is_supplementary", False),
                }
                for c in top_candidates
            ],
            "filtered_conversion_candidates": [
                {"api_name": c["polars_api_name"], "rank": c["rank"]}
                for c in emb_filtered
            ],
        })

    prompt_context = build_prompt_exp3(
        snippet, detected_apis, missing, api_results, template
    )
    generated_code = ""
    if llm is not None:
        try:
            resp = llm.invoke([{"role": "user", "content": prompt_context}])
            generated_code = resp.content
        except Exception as exc:
            generated_code = f"# LLM ERROR: {exc}"

    return {
        "snippet_id":            sid,
        "pandas_code":           pandas_code,
        "detected_apis":         [a["api_name"] for a in detected_apis],
        "ast_details":           ast_details,
        "missing_pandas_docs":   missing,
        "api_results":           api_results,
        "prompt_context":        prompt_context,
        "generated_polars_code": generated_code,
    }, diagnostics


def build_readable_summary(results: List[Dict]) -> str:
    lines = ["=" * 80, "EXP3 V2 — Static Mapping (exact lookup) + Embedding Retrieval",
             "=" * 80, ""]
    for r in results:
        sid  = r["snippet_id"]
        lines.append(f"### {sid}")
        lines.append("```python")
        lines.append(r["pandas_code"].strip())
        lines.append("```")
        lines.append("")

        if not r["api_results"]:
            lines.append("_(no pandas APIs detected / no doc matches)_")
            lines.append("")
            lines.append("-" * 60)
            lines.append("")
            continue

        for api_res in r["api_results"]:
            papi  = api_res["source_pandas_api"]
            case  = api_res["case"]
            known = api_res.get("confirmed_target_api")
            tag   = f"[{case}]" + (f" → {known}" if known else "")
            lines.append(f"**Pandas API:** `{papi}`  {tag}")
            for c in api_res["top_candidates"]:
                lines.append(f"  {c['rank']}. `{c['polars_api']}` (score={c['score']:.4f})")
            if api_res["filtered_conversion_apis"]:
                lines.append(
                    f"  _(filtered: {', '.join(api_res['filtered_conversion_apis'])})_"
                )
            lines.append("")

        if r["missing_pandas_docs"]:
            lines.append(f"_(APIs with no pandas doc: {', '.join(r['missing_pandas_docs'])})_")
            lines.append("")
        lines.append("-" * 60)
        lines.append("")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="EXP3 V2 — Static mapping + Embedding-only")
    parser.add_argument("--polars-docs",  default=str(POLARS_DOCS))
    parser.add_argument("--pandas-docs",  default=str(PANDAS_DOCS_STRUCTURED))
    parser.add_argument("--prev-results", default=str(PREV_RESULTS))
    parser.add_argument("--gold-labels",  default=str(GOLD_LABELS))
    parser.add_argument("--mapping",      default=str(MAPPING_JSON))
    parser.add_argument("--output",       default=str(OUTPUT_DIR))
    parser.add_argument("--top-k",        type=int, default=5)
    parser.add_argument("--limit",        type=int, default=None)
    parser.add_argument("--model",        default="",
                        help="OpenAI model for generation; empty = retrieval only")
    args = parser.parse_args()

    prev_dir   = Path(args.prev_results)
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    logger.info("Loading Polars docs (%s) …", args.polars_docs)
    with open(args.polars_docs, encoding="utf-8") as f:
        polars_docs = json.load(f)
    logger.info("  %d Polars docs", len(polars_docs))

    logger.info("Building Embedding retriever …")
    embedding_retriever = EmbeddingRetriever(polars_docs)

    logger.info("Building Polars doc lookup index …")
    polars_doc_index = build_polars_doc_index(polars_docs)

    logger.info("Loading static mapping …")
    mapping_index = load_static_mapping_index(args.mapping)
    ast_maps = build_maps_from_json(args.mapping)
    logger.info("  %d mapping entries indexed", len(mapping_index))

    logger.info("Loading snippet corpus (%s) …", args.gold_labels)
    snippets_by_sid = load_gold_labels(Path(args.gold_labels))
    logger.info("  %d snippets", len(snippets_by_sid))

    logger.info("Loading pandas doc index (%s) …", args.pandas_docs)
    pandas_index = load_pandas_index(Path(args.pandas_docs))

    logger.info("Loading prompt template …")
    template = PROMPT_TEMPLATE.read_text(encoding="utf-8")

    llm = None
    if args.model:
        import openai as _openai
        class _LLM:
            class _R:
                def __init__(self, t): self.content = t
            def __init__(self, model):
                self._c = _openai.OpenAI(); self.model = model
            def invoke(self, messages):
                t = messages[-1]["content"] if isinstance(messages[-1], dict) else messages[-1].content
                r = self._c.responses.create(
                    model=self.model,
                    reasoning={"effort": "low"},
                    input=t,
                    max_output_tokens=6000,
                )
                return self._R(r.output_text)
        if os.environ.get("OPENAI_API_KEY"):
            llm = _LLM(args.model)
            logger.info("LLM: %s", args.model)
        else:
            logger.warning("OPENAI_API_KEY not set — retrieval-only mode")

    sid_order = sorted(snippets_by_sid.keys())
    if args.limit:
        sid_order = sid_order[: args.limit]
    logger.info("Processing %d snippets …", len(sid_order))

    results:     List[Dict] = []
    diagnostics: List[Dict] = []

    for i, sid in enumerate(sid_order, 1):
        detected_apis, ast_details = detect_apis(
            snippets_by_sid[sid]["pandas_code"], ast_maps
        )
        result, diags = process_one(
            snippet             = snippets_by_sid[sid],
            detected_apis       = detected_apis,
            ast_details         = ast_details,
            pandas_index        = pandas_index,
            mapping_index       = mapping_index,
            polars_doc_index    = polars_doc_index,
            embedding_retriever = embedding_retriever,
            template            = template,
            top_k               = args.top_k,
            llm                 = llm,
        )
        results.append(result)
        diagnostics.extend(diags)

        if i % 50 == 0 or i == len(sid_order):
            logger.info("  %d / %d done", i, len(sid_order))

    write_jsonl(output_dir / "retrieval_results.jsonl",     results)
    write_jsonl(output_dir / "retrieval_diagnostics.jsonl", diagnostics)
    (output_dir / "retrieval_summary.txt").write_text(
        build_readable_summary(results), encoding="utf-8"
    )

    total_pairs   = len(diagnostics)
    case_counts   = {}
    for d in diagnostics:
        case_counts[d["case"]] = case_counts.get(d["case"], 0) + 1
    pairs_with_hit = sum(1 for d in diagnostics if d["embedding_candidates_after_filter"])
    conv_filtered  = sum(len(d["filtered_conversion_candidates"]) for d in diagnostics)

    print("\n── EXP3 V2 Stats ───────────────────────────────────")
    print(f"  Snippets processed:                  {len(results)}")
    print(f"  pandas-API pairs:                    {total_pairs}")
    print(f"  mapping_hit_doc_found:               {case_counts.get('mapping_hit_doc_found', 0)}")
    print(f"  mapping_hit_doc_missing:             {case_counts.get('mapping_hit_doc_missing', 0)}")
    print(f"  mapping_no_direct_equivalent:        {case_counts.get('mapping_no_direct_equivalent', 0)}")
    print(f"  mapping_miss:                        {case_counts.get('mapping_miss', 0)}")
    print(f"  Pairs with ≥1 candidate:             {pairs_with_hit} ({100*pairs_with_hit/max(total_pairs,1):.1f}%)")
    print(f"  Conversion APIs filtered out:        {conv_filtered}")
    print(f"  Output directory:                    {output_dir}")


if __name__ == "__main__":
    main()
