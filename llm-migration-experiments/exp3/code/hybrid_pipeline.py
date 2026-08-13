"""
# DEPRECATED — superseded by experiments/scripts/run_exp3_v2.py
# Changes in v2: 766-entry api_mapping, target_apis list lookup, unsafe alias removal,
# supplementary knowledge injection for no-doc mapping cases.

Experiment 3 VB — Complementary Hybrid RAG pipeline.

Per-API flow:
  If static mapping EXISTS  → confirmed knowledge + retrieve supporting Polars docs
  If static mapping MISSING → retrieve candidate Polars docs (same as Exp 2)

Reuses:
  ast_api_locator          — AST detection (unchanged)
  experiment2.retrieval    — BM25Retriever, EmbeddingRetriever, rrf_merge
  experiment2.doc_rag_pipeline — load_snippets, pandas doc index/lookup, detect_apis
"""

import json
import logging
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "experiment2"))
sys.path.insert(0, str(Path(__file__).parent))

from ast_api_locator import APIMaps, build_maps_from_json
from doc_rag_pipeline import (
    _adapt,
    build_pandas_doc_index,
    detect_apis,
    load_snippets,
    lookup_pandas_doc,
    lookup_all_pandas_docs,
)
from retrieval import BM25Retriever, EmbeddingRetriever, rrf_merge

logger = logging.getLogger(__name__)


# ── Step 3: Static mapping lookup ─────────────────────────────────────────

def load_static_mapping_index(json_path: str) -> Dict[str, Dict]:
    """
    Load api_mapping.json and build a multi-key lookup index.
    Keys: exact source_api, stripped (no 'pandas.' prefix), lowercase.
    Tail-only match removed — 199 collisions caused wrong mapping injection.
    """
    with open(json_path, encoding="utf-8") as f:
        records = json.load(f)
    index: Dict[str, Dict] = {}
    for rec in records:
        src = rec.get("source_api", "").strip()
        if not src:
            continue
        index[src] = rec
        stripped = re.sub(r"^pandas\.", "", src)
        index.setdefault(stripped, rec)
        index.setdefault(src.lower(), rec)
    return index


def lookup_static_mapping(
    api_name: str,
    mapping_index: Dict[str, Dict],
) -> Tuple[Optional[Dict], str]:
    """
    Return (record_or_None, lookup_key_used).
    Tries exact → strip pandas. → lowercase.
    Tail fallback removed — caused silent wrong-mapping with 199 collisions.
    """
    if api_name in mapping_index:
        return mapping_index[api_name], "exact"
    stripped = re.sub(r"^pandas\.", "", api_name)
    if stripped in mapping_index:
        return mapping_index[stripped], "stripped"
    lower = api_name.lower()
    if lower in mapping_index:
        return mapping_index[lower], "lowercase"
    return None, "not_found"


def build_static_mapping_record(
    snippet_id: str,
    api_name:   str,
    mapping:    Optional[Dict],
    lookup_key: str,
) -> Dict:
    if mapping:
        return {
            "snippet_id":        snippet_id,
            "source_api":        api_name,
            "mapping_status":    "found",
            "lookup_key":        lookup_key,
            "target_api":        mapping.get("target_api", ""),
            "functional_description": mapping.get("functional_description", ""),
            "usage_limitations": mapping.get("usage_limitations", ""),
            "discrepancies":     mapping.get("discrepancies", ""),
            "keywords":          mapping.get("keywords", ""),
        }
    return {
        "snippet_id":     snippet_id,
        "source_api":     api_name,
        "mapping_status": "missing",
        "lookup_key":     lookup_key,
        "target_api":     None,
    }


# ── Step 5: Query construction (two cases) ───────────────────────────────

def build_query_case_a(
    api_entry:      Dict,
    pandas_doc:     Dict,
    static_mapping: Dict,
    pandas_code:    str,
) -> str:
    """
    Case A: static mapping exists.
    Goal: retrieve supporting Polars usage docs for the confirmed target API.
    """
    api_name   = api_entry.get("api_name", "")
    target_api = static_mapping.get("target_api", "")
    desc       = pandas_doc.get("functional_description", "")[:250].strip()

    method = api_name.split(".")[-1]
    ctx_lines = [
        ln.strip() for ln in pandas_code.splitlines()
        if method in ln and not ln.strip().startswith("#")
    ][:3]

    parts = [
        f"Source pandas API: {api_name}",
        f"Pandas description: {desc}" if desc else "",
        f"Confirmed static mapping: {api_name} maps to {target_api}",
        f"Target Polars API: {target_api}",
        ("Code context: " + " | ".join(ctx_lines)) if ctx_lines else "",
        "Migration need: retrieve Polars documentation that explains how to use "
        "the mapped target API and related APIs to preserve the pandas behavior.",
    ]
    return "\n".join(p for p in parts if p)


def build_query_case_b(
    api_entry:  Dict,
    pandas_doc: Dict,
    pandas_code: str,
) -> str:
    """
    Case B: static mapping missing.
    Goal: retrieve candidate Polars docs that may express equivalent behavior.
    """
    api_name = api_entry.get("api_name", "")
    desc     = pandas_doc.get("functional_description", "")[:250].strip()

    method = api_name.split(".")[-1]
    ctx_lines = [
        ln.strip() for ln in pandas_code.splitlines()
        if method in ln and not ln.strip().startswith("#")
    ][:3]

    parts = [
        f"Source pandas API: {api_name}",
        f"Pandas description: {desc}" if desc else "",
        ("Code context: " + " | ".join(ctx_lines)) if ctx_lines else "",
        "Migration need: retrieve Polars documentation chunks that may express "
        "equivalent or similar behavior.",
    ]
    return "\n".join(p for p in parts if p)


# ── Step 8: Hybrid knowledge records ─────────────────────────────────────

def build_hybrid_record(
    snippet_id:      str,
    api_entry:       Dict,
    static_mapping_rec: Dict,
    pandas_doc:      Optional[Dict],
    query_text:      str,
    rrf_candidates:  List[Dict],
) -> Dict:
    mapping_status = static_mapping_rec["mapping_status"]
    has_candidates = len(rrf_candidates) > 0

    if mapping_status == "found" and has_candidates:
        knowledge_role = "confirmed_mapping_plus_supporting_docs"
        query_type     = "supporting_docs_for_confirmed_mapping"
    elif mapping_status == "found" and not has_candidates:
        knowledge_role = "confirmed_mapping_no_supporting_docs"
        query_type     = "supporting_docs_for_confirmed_mapping"
    elif mapping_status == "missing" and has_candidates:
        knowledge_role = "candidate_docs_for_missing_mapping"
        query_type     = "candidate_docs_for_unmapped_api"
    else:
        knowledge_role = "missing_mapping_and_no_candidate_docs"
        query_type     = "candidate_docs_for_unmapped_api"

    polars_docs = []
    for cand in rrf_candidates:
        polars_docs.append({
            "target_api":   cand.get("polars_api_name", ""),
            "rank":         cand.get("final_rank", 0),
            "rrf_score":    cand.get("rrf_score", 0.0),
            "bm25_rank":    cand.get("bm25_rank"),
            "bm25_score":   cand.get("bm25_score"),
            "embedding_rank":  cand.get("embedding_rank"),
            "embedding_score": cand.get("embedding_score"),
            "signature":    cand.get("signature", ""),
            "description":  cand.get("functional_description", "")[:400].strip(),
            "examples":     cand.get("examples", "")[:200].strip(),
            "source_file":  cand.get("source_file", ""),
        })

    return {
        "snippet_id":       snippet_id,
        "source_api":       api_entry.get("api_name", ""),
        "source_call_text": api_entry.get("call_text", api_entry.get("api_name", "")),
        "mapping_status":   mapping_status,
        "static_mapping":   static_mapping_rec if mapping_status == "found" else None,
        "pandas_doc": {
            "api_name":    pandas_doc.get("api_name", "") if pandas_doc else "",
            "signature":   pandas_doc.get("functional_description", "")[:200].strip() if pandas_doc else "",
            "description": pandas_doc.get("functional_description", "")[:400].strip() if pandas_doc else "",
        } if pandas_doc else None,
        "query_text":           query_text,
        "query_type":           query_type,
        "retrieved_polars_docs": polars_docs,
        "knowledge_role":       knowledge_role,
    }


# ── Step 9: Coverage-aware selection ─────────────────────────────────────

def coverage_aware_selection(
    hybrid_records:   List[Dict],
    per_api_top_k:    int = 5,
    global_limit:     int = 25,
) -> Tuple[List[Dict], List[str], List[str], bool]:
    """
    Select up to global_limit unique Polars docs for the prompt.

    Rules:
      1. Each pandas API contributes at least its top-1 retrieved doc (if any).
      2. All docs are deduplicated by target_api name.
      3. After min-coverage, remaining budget filled by RRF score desc.
      4. Docs that appear in multiple APIs' results record all supporting APIs.

    Returns (selected_docs, covered_apis, missing_candidate_apis, prompt_truncated)
    """
    # Build per-API candidate pools
    per_api: Dict[str, List[Dict]] = {}
    for rec in hybrid_records:
        candidates = rec.get("retrieved_polars_docs", [])[:per_api_top_k]
        per_api[rec["source_api"]] = candidates

    # Global dedup pool: target_api → enriched doc dict
    pool: Dict[str, Dict] = {}

    def _add(doc: Dict, api_name: str) -> None:
        key = doc.get("target_api", "")
        if not key:
            return
        if key not in pool:
            pool[key] = {**doc, "supporting_apis": [api_name]}
        else:
            if api_name not in pool[key]["supporting_apis"]:
                pool[key]["supporting_apis"].append(api_name)
            if doc.get("rrf_score", 0) > pool[key].get("rrf_score", 0):
                pool[key]["rrf_score"] = doc["rrf_score"]

    for api_name, candidates in per_api.items():
        for doc in candidates:
            _add(doc, api_name)

    # Phase A: at least top-1 per API
    selected_keys: List[str] = []
    covered_apis:  List[str] = []
    missing_candidate_apis: List[str] = []

    for api_name, candidates in per_api.items():
        if not candidates:
            missing_candidate_apis.append(api_name)
            continue
        top1_key = candidates[0].get("target_api", "")
        if top1_key and top1_key not in selected_keys:
            selected_keys.append(top1_key)
        covered_apis.append(api_name)

    # Phase B: fill remaining budget by RRF desc
    not_yet = sorted(
        ((v.get("rrf_score", 0), k) for k, v in pool.items() if k not in selected_keys),
        reverse=True,
    )
    budget    = global_limit - len(selected_keys)
    truncated = len(not_yet) > budget

    for _, key in not_yet[:budget]:
        selected_keys.append(key)

    selected_docs = [pool[k] for k in selected_keys[:global_limit] if k in pool]
    return selected_docs, covered_apis, missing_candidate_apis, truncated


# ── Step 9: Prompt context formatting ────────────────────────────────────

def format_prompt_context(
    snippet:          Dict,
    detection:        Dict,
    hybrid_records:   List[Dict],
    selected_docs:    List[Dict],
    covered_apis:     List[str],
    missing_cand_apis: List[str],
    template:         str,
) -> str:
    pandas_code = snippet["pandas_code"]

    # ── Detected pandas APIs ─────────────────────────────────────────────
    detected_apis_str = "\n".join(
        f"  - {e['api_name']} ({e['object_type']})"
        for e in detection["detected_apis"]
    ) or "  (none detected)"

    # ── Confirmed static mappings ────────────────────────────────────────
    found_records = [r for r in hybrid_records if r["mapping_status"] == "found"]
    if found_records:
        lines = []
        for r in found_records:
            sm = r["static_mapping"]
            lines.append(f"  - {r['source_api']}  →  {sm['target_api']}")
            if sm.get("usage_limitations"):
                lines.append(f"    Note: {sm['usage_limitations'][:150]}")
        confirmed_str = "\n".join(lines)
    else:
        confirmed_str = "  (none — all detected APIs are unmapped)"

    # ── Source pandas behavior ───────────────────────────────────────────
    pd_desc_lines = []
    for r in hybrid_records:
        if r.get("pandas_doc"):
            desc = r["pandas_doc"].get("description", "")[:200].strip()
            if desc:
                pd_desc_lines.append(f"  - {r['source_api']}: {desc}")
    pandas_behavior_str = "\n".join(pd_desc_lines) or "  (no pandas documentation available)"

    # ── Supporting Polars docs (for confirmed mappings) ──────────────────
    # Collect selected docs that support at least one "found" API
    found_api_set = {r["source_api"] for r in found_records}
    supporting = [
        d for d in selected_docs
        if any(a in found_api_set for a in d.get("supporting_apis", []))
    ]
    if supporting:
        lines = []
        for i, d in enumerate(supporting, 1):
            api = d.get("target_api", "?")
            desc = d.get("description", "")[:200].strip()
            supporting_for = [a for a in d.get("supporting_apis", []) if a in found_api_set]
            lines.append(f"  [{i}] {api}  (supports: {', '.join(supporting_for)})")
            if desc:
                lines.append(f"      {desc}")
        supporting_str = "\n".join(lines)
    else:
        supporting_str = "  (none retrieved)"

    # ── Candidate Polars docs (for unmapped APIs) ─────────────────────────
    missing_api_set = {r["source_api"] for r in hybrid_records if r["mapping_status"] == "missing"}
    candidate_docs = [
        d for d in selected_docs
        if any(a in missing_api_set for a in d.get("supporting_apis", []))
        and not any(a in found_api_set for a in d.get("supporting_apis", []))
    ]
    if candidate_docs:
        lines = []
        for i, d in enumerate(candidate_docs, 1):
            api = d.get("target_api", "?")
            desc = d.get("description", "")[:200].strip()
            cand_for = [a for a in d.get("supporting_apis", []) if a in missing_api_set]
            lines.append(f"  [{i}] {api}  (candidate for: {', '.join(cand_for)})")
            if desc:
                lines.append(f"      {desc}")
        candidate_str = "\n".join(lines)
    elif missing_api_set:
        candidate_str = "  (none retrieved for unmapped APIs)"
    else:
        candidate_str = "  (all detected APIs have confirmed static mappings)"

    # ── Missing knowledge warnings ────────────────────────────────────────
    warn_lines = []
    for api in missing_cand_apis:
        warn_lines.append(f"  - {api}: no static mapping and no Polars candidate docs found.")
    for method in detection.get("unknown_methods", []):
        warn_lines.append(f"  - {method}: unrecognised method — translate manually.")
    warnings_str = "\n".join(warn_lines) or "  (none)"

    return template.format(
        source_code               = pandas_code,
        detected_apis             = detected_apis_str,
        confirmed_static_mappings = confirmed_str,
        pandas_behavior_docs      = pandas_behavior_str,
        supporting_polars_docs    = supporting_str,
        candidate_polars_docs     = candidate_str,
        missing_knowledge_warnings = warnings_str,
    )


# ── Full pipeline for one snippet ─────────────────────────────────────────

def process_one(
    snippet:             Dict,
    maps:                APIMaps,
    mapping_index:       Dict[str, Dict],
    pandas_index:        Dict[str, Dict],
    bm25_retriever,
    embedding_retriever,
    template:            str,
    top_k_retrieval:     int = 20,
    per_api_top_k:       int = 5,
    global_prompt_limit: int = 25,
    rrf_k:               int = 60,
    llm                      = None,
) -> Dict:
    # Step 2
    detection = detect_apis(snippet, maps)
    sid       = snippet["snippet_id"]

    # Steps 3 + 4 + 5 + 6 + 7 + 8
    static_mapping_records: List[Dict] = []
    matched_pandas_docs:    List[Dict] = []
    missing_pandas_docs:    List[str]  = []
    queries_out:            List[Dict] = []
    bm25_out:               List[Dict] = []
    embedding_out:          List[Dict] = []
    rrf_out:                List[Dict] = []
    hybrid_records:         List[Dict] = []

    for api_entry in detection["detected_apis"]:
        api_name = api_entry["api_name"]

        # Step 3: static mapping
        mapping, lookup_key = lookup_static_mapping(api_name, mapping_index)
        sm_rec = build_static_mapping_record(sid, api_name, mapping, lookup_key)
        static_mapping_records.append(sm_rec)

        # Step 4: pandas doc
        pd_doc = lookup_pandas_doc(api_name, pandas_index)
        if pd_doc:
            matched_pandas_docs.append({
                "snippet_id": sid,
                "api_name":   api_name,
                "pandas_doc": pd_doc,
            })
        else:
            missing_pandas_docs.append(api_name)

        # Step 5: query construction
        if mapping and pd_doc:
            query = build_query_case_a(api_entry, pd_doc, sm_rec, snippet["pandas_code"])
            q_type = "supporting_docs_for_confirmed_mapping"
        elif pd_doc:
            query = build_query_case_b(api_entry, pd_doc, snippet["pandas_code"])
            q_type = "candidate_docs_for_unmapped_api"
        else:
            # No pandas doc → minimal query
            query  = f"Source pandas API: {api_name}\nMigration need: find Polars equivalent."
            q_type = "candidate_docs_for_unmapped_api"

        queries_out.append({
            "snippet_id":    sid,
            "source_api":    api_name,
            "mapping_status": sm_rec["mapping_status"],
            "target_api":    sm_rec.get("target_api"),
            "query_text":    query,
            "query_type":    q_type,
        })

        # Step 6: dual retrieval
        bm25_cands = bm25_retriever.retrieve(query, top_k=top_k_retrieval)
        emb_cands  = embedding_retriever.retrieve(query, top_k=top_k_retrieval)
        bm25_out.append({"snippet_id": sid, "source_api": api_name,
                         "mapping_status": sm_rec["mapping_status"],
                         "query_type": q_type, "candidates": bm25_cands})
        embedding_out.append({"snippet_id": sid, "source_api": api_name,
                               "mapping_status": sm_rec["mapping_status"],
                               "query_type": q_type, "candidates": emb_cands})

        # Step 7: RRF
        rrf_cands = rrf_merge(bm25_cands, emb_cands, top_k=per_api_top_k, k=rrf_k)
        rrf_out.append({"snippet_id": sid, "source_api": api_name,
                        "mapping_status": sm_rec["mapping_status"],
                        "query_type": q_type, "candidates": rrf_cands})

        # Step 8: hybrid record
        hr = build_hybrid_record(sid, api_entry, sm_rec, pd_doc, query, rrf_cands)
        hybrid_records.append(hr)

    # Step 9: coverage-aware selection + prompt
    selected_docs, covered_apis, missing_cand_apis, truncated = coverage_aware_selection(
        hybrid_records, per_api_top_k=per_api_top_k, global_limit=global_prompt_limit
    )

    prompt_context = format_prompt_context(
        snippet, detection, hybrid_records,
        selected_docs, covered_apis, missing_cand_apis, template,
    )

    # Optional LLM
    generated_code = ""
    if llm is not None:
        try:
            resp = llm.invoke([{"role": "user", "content": prompt_context}])
            generated_code = resp.content
        except Exception as exc:
            generated_code = f"# LLM ERROR: {exc}"

    return {
        "snippet_id":           sid,
        "pandas_code":          snippet["pandas_code"],
        "parse_success":        detection["parse_success"],
        "detected_apis":        detection["detected_apis"],
        "operation_keywords":   detection["operation_keywords"],
        "unknown_methods":      detection["unknown_methods"],
        # Stage outputs
        "static_mapping_records": static_mapping_records,
        "matched_pandas_docs":    matched_pandas_docs,
        "missing_pandas_docs":    missing_pandas_docs,
        "queries":                queries_out,
        "bm25_candidates":        bm25_out,
        "embedding_candidates":   embedding_out,
        "rrf_candidates":         rrf_out,
        "hybrid_records":         hybrid_records,
        # Prompt metadata
        "covered_apis":           covered_apis,
        "missing_candidate_apis": missing_cand_apis,
        "num_prompt_docs":        len(selected_docs),
        "prompt_truncated":       truncated,
        "prompt_context":         prompt_context,
        "generated_polars_code":  generated_code,
    }
