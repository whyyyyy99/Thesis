"""
# DEPRECATED — superseded by experiments/scripts/run_exp2_v2.py
# Unsafe pandas doc aliases removed; use run_exp2_v2.py for all new runs.

Experiment 2 — AST + Documentation RAG pipeline.

Flow (per snippet):
  Step 1  load_snippets()
  Step 2  detect_apis()              — reuses existing AST API locator
  Step 3  lookup_all_pandas_docs()   — pandas doc exact + normalised lookup
  Step 4  build_query()              — enriched retrieval query per API
  Step 5  BM25 retrieve top-20       — called in runner
  Step 5  Embedding retrieve top-20  — called in runner
  Step 6  rrf_merge()               — RRF fusion → final top-5
  Step 7  build_dynamic_mapping()    — candidate mapping record
  Step 8  build_prompt_context()     — migration prompt context

No predefined pandas-to-Polars mapping table is used.
No gold Polars solutions are accessed at any point during generation.
"""

import json
import logging
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(Path(__file__).parent))

from ast_api_locator import APIMaps, build_maps_from_json, extract_pandas_api_details
from retrieval import (
    rrf_merge,
    _COMPOUND,
    _SKIP_KW_NAMES,
    _KEEP_ARG_VALUES,
    RETRIEVAL_NOISE_APIS,
    CONVERSION_INTENT_APIS,
    is_conversion_intent,
    filter_conversion_candidates,
)

logger = logging.getLogger(__name__)


# ── Step 1: Load snippets ──────────────────────────────────────────────────

def load_snippets(source) -> List[Dict]:
    """
    Accept:
      - str / Path to a directory  (scans *_before.py)
      - str / Path to a .jsonl file
      - str / Path to a .json file  (list or single object)
      - list of dicts               (pass-through)

    Returns list of {"snippet_id": str, "pandas_code": str}.
    """
    if isinstance(source, list):
        return [_adapt(r) for r in source]

    path = Path(source)
    if path.is_dir():
        snippets = []
        for p in sorted(path.rglob("*_before.py")):
            snippets.append({
                "snippet_id": str(p),
                "pandas_code": p.read_text(encoding="utf-8", errors="ignore"),
            })
        return snippets

    if path.suffix == ".jsonl":
        snippets = []
        with open(path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    snippets.append(_adapt(json.loads(line)))
        return snippets

    if path.suffix in {".json"}:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, list):
            return [_adapt(r) for r in data]
        return [_adapt(data)]

    raise ValueError(f"Unsupported snippet source: {source!r}")


def _adapt(record: Dict) -> Dict:
    """Normalise field names from different dataset formats."""
    sid  = (record.get("snippet_id") or record.get("id") or
            record.get("pair_id")    or str(id(record)))
    code = (record.get("pandas_code") or record.get("code") or
            record.get("source_code") or "")
    out = {"snippet_id": str(sid), "pandas_code": code, "_raw": record}
    if "detected_apis" in record:
        out["detected_apis"] = record["detected_apis"]
    return out


# ── Step 2: AST detection ──────────────────────────────────────────────────

def detect_apis(snippet: Dict, maps: APIMaps) -> Dict:
    """Call AST API locator; return structured detection record.
    If snippet contains 'detected_apis' (pre-computed), use those instead."""
    details = extract_pandas_api_details(snippet["pandas_code"], maps=maps)
    if "detected_apis" in snippet:
        api_list = snippet["detected_apis"]
    else:
        api_list = details["normalized_apis"]
    return {
        "snippet_id":        snippet["snippet_id"],
        "pandas_code":       snippet["pandas_code"],
        "parse_success":     details["parse_success"],
        "detected_apis": [
            {
                "api_name":        api,
                "call_text":       api,
                "object_type":     _infer_object_type(api),
                "detection_source": "AST",
            }
            for api in api_list
        ],
        "operation_keywords": details["operation_keywords"],
        "unknown_methods":    details["unknown_methods"],
        "df_vars":            details["df_vars"],
        "groupby_vars":       details["groupby_vars"],
    }


def _infer_object_type(api_name: str) -> str:
    for token in ("GroupBy", "DataFrame", "Series", "Index",
                  "Resampler", "Rolling", "Expanding"):
        if token in api_name:
            return token
    return "top_level"


# ── Step 3: Pandas doc lookup ──────────────────────────────────────────────

def build_pandas_doc_index(pandas_docs: List[Dict]) -> Dict[str, Dict]:
    """Build a multi-key lookup index over pandas documentation records."""
    index: Dict[str, Dict] = {}
    for doc in pandas_docs:
        name = doc.get("api_name", "")
        if not name:
            continue
        index[name] = doc
        # Short form: pandas.DataFrame.groupby → groupby
        short = name.split(".")[-1]
        index.setdefault(short, doc)
        # Strip leading "pandas.": pandas.DataFrame.groupby → DataFrame.groupby
        stripped = re.sub(r"^pandas\.", "", name)
        index.setdefault(stripped, doc)
    return index


def lookup_pandas_doc(api_name: str, index: Dict[str, Dict]) -> Optional[Dict]:
    """Exact lookup, then normalised fallbacks (never silently ignores)."""
    if api_name in index:
        return index[api_name]
    # Variant 1: strip "pandas."
    stripped = re.sub(r"^pandas\.", "", api_name)
    if stripped in index:
        return index[stripped]
    # Variant 2: case-insensitive
    lower = api_name.lower()
    for k, v in index.items():
        if k.lower() == lower:
            return v
    # Variant 3: tail method name (low-priority)
    tail = api_name.split(".")[-1]
    if tail in index:
        return index[tail]
    return None


def lookup_all_pandas_docs(
    detection: Dict,
    pandas_index: Dict[str, Dict],
) -> Tuple[List[Dict], List[str]]:
    """
    Returns (matched, missing).
    matched: list of {"api_entry": ..., "pandas_doc": ...}
    missing: list of api_name strings with no match
    """
    matched, missing = [], []
    for api_entry in detection["detected_apis"]:
        doc = lookup_pandas_doc(api_entry["api_name"], pandas_index)
        if doc:
            matched.append({"api_entry": api_entry, "pandas_doc": doc})
        else:
            missing.append(api_entry["api_name"])
    return matched, missing


# ── Step 4: Build retrieval queries ───────────────────────────────────────

def build_query(api_entry: Dict, pandas_doc: Dict, pandas_code: str) -> str:
    """
    Build an enriched retrieval query combining:
      - pandas API name + object type
      - pandas signature
      - pandas functional description (first 300 chars)
      - key parameters and returns (from functional_description)
      - local call context from the code snippet
      - explicit migration goal statement
    """
    api_name = api_entry.get("api_name", "")
    obj_type = api_entry.get("object_type", "")
    desc     = pandas_doc.get("functional_description", "")
    desc_short = desc[:300].strip()

    parts = [f"Source pandas API: {api_name}"]
    if obj_type and obj_type != "top_level":
        parts.append(f"Object type: {obj_type}")
    if desc_short:
        parts.append(f"Pandas description: {desc_short}")

    method = api_name.split(".")[-1]
    context_lines = [
        ln.strip() for ln in pandas_code.splitlines()
        if method in ln and not ln.strip().startswith("#")
    ][:3]
    if context_lines:
        parts.append("Code context: " + " | ".join(context_lines))

    parts.append(
        "Migration need: find Polars documentation chunks that can express "
        "the same operation in Polars."
    )
    return "\n".join(parts)


# ── Step 7: Build dynamic mapping records ─────────────────────────────────

def build_dynamic_mapping(
    snippet_id:         str,
    api_entry:          Dict,
    pandas_doc:         Dict,
    query:              str,
    rrf_candidates:     List[Dict],
) -> Dict:
    """
    Build a dynamic documentation-RAG mapping record.

    mapping_type is always "documentation_rag_candidate" (or
    "no_candidate_found" when rrf_candidates is empty).
    These are *retrieved candidates*, not confirmed one-to-one mappings.
    """
    mapping_type = (
        "no_candidate_found" if not rrf_candidates
        else "documentation_rag_candidate"
    )

    target_candidates = []
    for cand in rrf_candidates:
        target_candidates.append({
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
        "pandas_doc": {
            "api_name":   pandas_doc.get("api_name", ""),
            "signature":  pandas_doc.get("functional_description", "")[:200].strip(),
            "description": pandas_doc.get("functional_description", "")[:400].strip(),
        },
        "query":            query,
        "target_candidates": target_candidates,
        "mapping_type":     mapping_type,
        "notes": (
            "These Polars documentation chunks are retrieved candidates and are "
            "not guaranteed one-to-one mappings. Use them only if they preserve "
            "the behavior of the original pandas code."
        ),
    }


# ── Step 8: Build migration prompt context ────────────────────────────────

def format_candidate_for_prompt(cand: Dict, rank: int) -> str:
    api  = cand.get("target_api", "?")
    desc = cand.get("description", "")[:150].strip()
    rrf  = cand.get("rrf_score", 0)
    bm25_rank = cand.get("bm25_rank")
    emb_rank  = cand.get("embedding_rank")
    rank_info = []
    if bm25_rank is not None:
        rank_info.append(f"BM25 rank {bm25_rank}")
    if emb_rank is not None:
        rank_info.append(f"embedding rank {emb_rank}")
    rank_str = f" ({', '.join(rank_info)}, RRF={rrf:.4f})" if rank_info else f" (RRF={rrf:.4f})"
    line = f"{rank}. {api}{rank_str}"
    if desc:
        line += f"\n   {desc}"
    return line


def build_prompt_context(
    snippet:          Dict,
    detection:        Dict,
    dynamic_mappings: List[Dict],
    template:         str,
) -> Dict:
    """Assemble the per-snippet prompt context ready for LLM injection."""
    api_list = "\n".join(
        f"  - {e['api_name']} ({e['object_type']})"
        for e in detection["detected_apis"]
    ) or "  (none detected)"

    mapping_blocks = []
    for dm in dynamic_mappings:
        lines = [f"\npandas API: {dm['source_api']}"]
        pd_desc = dm["pandas_doc"].get("description", "")[:200].strip()
        if pd_desc:
            lines.append(f"  pandas: {pd_desc}")
        candidates = dm.get("target_candidates", [])
        if candidates:
            lines.append("  Retrieved Polars candidates (BM25 + embedding + RRF):")
            for i, c in enumerate(candidates[:5], 1):
                lines.append("  " + format_candidate_for_prompt(c, i))
        else:
            lines.append("  Polars candidates: none found — migrate manually")
        mapping_blocks.append("\n".join(lines))

    mappings_str = "\n".join(mapping_blocks) if mapping_blocks else "(no mappings)"

    unknown_str = (
        "\n".join(f"  - {u}" for u in detection["unknown_methods"])
        or "  (none)"
    )

    prompt_context = template.format(
        source_code            = snippet["pandas_code"],
        detected_apis          = api_list,
        dynamic_mapping_records = mappings_str,
        unknown_methods        = unknown_str,
    )

    return {
        "snippet_id":           snippet["snippet_id"],
        "pandas_code":          snippet["pandas_code"],
        "detected_pandas_apis": detection["detected_apis"],
        "dynamic_mappings":     dynamic_mappings,
        "prompt_context":       prompt_context,
    }


# ── v2: Separated BM25 / embedding query builders ────────────────────────

def _extract_call_context(method: str, pandas_code: str, max_lines: int = 3) -> List[str]:
    """Return up to max_lines of code that contain the method name."""
    return [
        ln.strip() for ln in pandas_code.splitlines()
        if method in ln and not ln.strip().startswith("#")
    ][:max_lines]


def build_bm25_query(
    api_entry: Dict,
    pandas_doc: Dict,
    pandas_code: str,
) -> str:
    """
    Short, lexically-focused BM25 query.
    Includes method name, synonym expansion, and call-site argument signals.
    Avoids generic migration/documentation vocabulary.
    """
    api_name = api_entry.get("api_name", "")
    method   = api_name.split(".")[-1]   # e.g. "drop_duplicates"

    tokens: List[str] = []

    # 1. Full method token and underscore parts
    tokens.append(method)
    tokens.extend(p for p in method.split("_") if len(p) > 2)

    # 2. Synonym expansion from shared _COMPOUND table
    expansion = _COMPOUND.get(method, "")
    if expansion:
        tokens.extend(expansion.split())

    # 3. Argument names and key values from the actual call site.
    # Only look at text AFTER the method name to avoid capturing assignment LHS.
    for line in _extract_call_context(method, pandas_code):
        pos = line.find(method)
        if pos < 0:
            continue
        call_text = line[pos + len(method):]   # ".drop_duplicates(keep='first')" etc.
        for kw in re.findall(r"\b(\w+)\s*=", call_text):
            if kw.lower() not in _SKIP_KW_NAMES and len(kw) > 1:
                tokens.append(kw.lower())
        for val in re.findall(r'["\']([a-z_]+)["\']', call_text):
            if val in _KEEP_ARG_VALUES:
                tokens.append(val)

    # Deduplicate preserving order
    seen: set = set()
    result: List[str] = []
    for t in tokens:
        if t and t not in seen:
            seen.add(t)
            result.append(t)

    return " ".join(result)


def build_embedding_query(
    api_entry: Dict,
    pandas_doc: Dict,
    pandas_code: str,
) -> str:
    """
    Semantic embedding query — same rich structure as the legacy build_query().
    Separated from BM25 query so BM25 no longer receives migration boilerplate.
    """
    return build_query(api_entry, pandas_doc, pandas_code)


# ── v2: per-API pipeline with filtering and diagnostics ──────────────────

def process_one_v2(
    snippet:             Dict,
    detected_apis:       List[Dict],          # pre-computed, list of api_entry dicts
    pandas_index:        Dict[str, Dict],
    bm25_retriever,
    embedding_retriever,
    template:            str,
    top_k_retrieval:     int = 25,            # slightly larger to buffer filtering
    top_k_final:         int = 5,
    rrf_k:               int = 60,
    llm                      = None,
) -> Dict:
    """
    Experiment 2 v2: separated BM25/embedding queries + conversion-API filtering.
    Accepts pre-computed detected_apis so AST is not re-run.
    Returns result dict with diagnostics appended.
    """
    sid          = snippet["snippet_id"]
    pandas_code  = snippet["pandas_code"]

    diagnostics:     List[Dict] = []
    dynamic_mappings: List[Dict] = []
    rrf_out:          List[Dict] = []

    matched_docs, missing = lookup_all_pandas_docs(
        {"detected_apis": detected_apis}, pandas_index
    )

    for item in matched_docs:
        api_entry  = item["api_entry"]
        pandas_doc = item["pandas_doc"]
        api_name   = api_entry["api_name"]

        bm25_q = build_bm25_query(api_entry, pandas_doc, pandas_code)
        emb_q  = build_embedding_query(api_entry, pandas_doc, pandas_code)

        bm25_raw = bm25_retriever.retrieve(bm25_q, top_k=top_k_retrieval)
        emb_raw  = embedding_retriever.retrieve(emb_q, top_k=top_k_retrieval)

        conv_intent = is_conversion_intent(api_name)
        bm25_kept, bm25_filtered = filter_conversion_candidates(bm25_raw, api_name, conv_intent)
        emb_kept,  emb_filtered  = filter_conversion_candidates(emb_raw,  api_name, conv_intent)

        rrf_candidates = rrf_merge(bm25_kept, emb_kept, top_k=top_k_final, k=rrf_k)
        rrf_out.append({"api_name": api_name, "candidates": rrf_candidates})

        dm = build_dynamic_mapping(sid, api_entry, pandas_doc, emb_q, rrf_candidates)
        dynamic_mappings.append(dm)

        diagnostics.append({
            "snippet_id":             sid,
            "source_pandas_api":      api_name,
            "query_mode":             "separated",
            "bm25_query":             bm25_q,
            "embedding_query":        emb_q,
            "conversion_intent_detected": conv_intent,
            "bm25_candidates_before_filter": [
                {"api_name": c["polars_api_name"], "rank": c["rank"], "score": c["score"]}
                for c in bm25_raw
            ],
            "bm25_candidates_after_filter": [
                {"api_name": c["polars_api_name"], "rank": c["rank"], "score": c["score"]}
                for c in bm25_kept
            ],
            "embedding_candidates_before_filter": [
                {"api_name": c["polars_api_name"], "rank": c["rank"], "score": c["score"]}
                for c in emb_raw
            ],
            "embedding_candidates_after_filter": [
                {"api_name": c["polars_api_name"], "rank": c["rank"], "score": c["score"]}
                for c in emb_kept
            ],
            "filtered_conversion_candidates": [
                {
                    "api_name":    c["polars_api_name"],
                    "from":        c["retriever_type"],
                    "rank":        c["rank"],
                    "filter_reason": c.get("filter_reason", ""),
                }
                for c in bm25_filtered + emb_filtered
            ],
            "rrf_candidates": [
                {
                    "api_name":       c["polars_api_name"],
                    "rrf_score":      c["rrf_score"],
                    "bm25_rank":      c.get("bm25_rank"),
                    "embedding_rank": c.get("embedding_rank"),
                    "final_rank":     c.get("final_rank"),
                }
                for c in rrf_candidates
            ],
        })

    # Build generation prompt
    detection_stub = {
        "detected_apis":      detected_apis,
        "unknown_methods":    [],
        "operation_keywords": [],
    }
    migration_context = build_prompt_context(
        snippet, detection_stub, dynamic_mappings, template
    )

    generated_code = ""
    if llm is not None:
        try:
            resp = llm.invoke([
                {"role": "user", "content": migration_context["prompt_context"]}
            ])
            generated_code = resp.content
        except Exception as exc:
            generated_code = f"# LLM ERROR: {exc}"

    return {
        "snippet_id":            sid,
        "pandas_code":           pandas_code,
        "detected_apis":         detected_apis,
        "missing_pandas_docs":   missing,
        "dynamic_mappings":      dynamic_mappings,
        "rrf_candidates":        rrf_out,
        "prompt_context":        migration_context["prompt_context"],
        "generated_polars_code": generated_code,
        "diagnostics":           diagnostics,
    }


# ── Full pipeline for one snippet ─────────────────────────────────────────

def process_one(
    snippet:             Dict,
    maps:                APIMaps,
    pandas_index:        Dict[str, Dict],
    bm25_retriever,
    embedding_retriever,
    template:            str,
    top_k_retrieval:     int = 20,
    top_k_final:         int = 5,
    rrf_k:               int = 60,
    llm                      = None,
) -> Dict:
    """
    Run the full Experiment 2 pipeline for one snippet.

    Returns a result dict with all intermediate stages plus the
    optional generated Polars code.
    """
    # Step 2
    detection = detect_apis(snippet, maps)

    # Steps 3–7
    matched_docs, missing = lookup_all_pandas_docs(detection, pandas_index)

    queries_out:     List[Dict] = []
    bm25_out:        List[Dict] = []
    embedding_out:   List[Dict] = []
    rrf_out:         List[Dict] = []
    dynamic_mappings: List[Dict] = []

    for item in matched_docs:
        api_entry  = item["api_entry"]
        pandas_doc = item["pandas_doc"]
        api_name   = api_entry["api_name"]

        # Step 4
        query = build_query(api_entry, pandas_doc, snippet["pandas_code"])
        queries_out.append({"api_name": api_name, "query": query})

        # Step 5 — dual retrieval
        bm25_candidates = bm25_retriever.retrieve(query, top_k=top_k_retrieval)
        emb_candidates  = embedding_retriever.retrieve(query, top_k=top_k_retrieval)

        bm25_out.append({"api_name": api_name, "candidates": bm25_candidates})
        embedding_out.append({"api_name": api_name, "candidates": emb_candidates})

        # Step 6 — RRF fusion
        rrf_candidates = rrf_merge(
            bm25_candidates, emb_candidates,
            top_k=top_k_final, k=rrf_k,
        )
        rrf_out.append({"api_name": api_name, "candidates": rrf_candidates})

        # Step 7 — dynamic mapping record
        dm = build_dynamic_mapping(
            snippet["snippet_id"], api_entry, pandas_doc, query, rrf_candidates
        )
        dynamic_mappings.append(dm)

    # Step 8
    migration_context = build_prompt_context(
        snippet, detection, dynamic_mappings, template
    )

    # Optional LLM call (Step 9)
    generated_code = ""
    if llm is not None:
        try:
            resp = llm.invoke([
                {"role": "user", "content": migration_context["prompt_context"]}
            ])
            generated_code = resp.content
        except Exception as exc:
            generated_code = f"# LLM ERROR: {exc}"

    return {
        "snippet_id":         snippet["snippet_id"],
        "pandas_code":        snippet["pandas_code"],
        "parse_success":      detection["parse_success"],
        # Stage exports
        "detected_apis":      detection["detected_apis"],
        "operation_keywords": detection["operation_keywords"],
        "unknown_methods":    detection["unknown_methods"],
        "missing_pandas_docs": missing,
        "queries":            queries_out,
        "bm25_candidates":    bm25_out,
        "embedding_candidates": embedding_out,
        "rrf_candidates":     rrf_out,
        "dynamic_mappings":   dynamic_mappings,
        "prompt_context":     migration_context["prompt_context"],
        "generated_polars_code": generated_code,
    }
