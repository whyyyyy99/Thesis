"""
Experiment 2 V2 — Embedding-only documentation retrieval.

Final retrieval design:
  - all-mpnet-base-v2 cosine retrieval
  - Single embedding query per pandas API (rich semantic query)
  - Same retrieval noise filtering (RETRIEVAL_NOISE_APIS)
  - top_k=5 per detected pandas API
  - Optional LLM generation (pass --model to enable)

API detection is recomputed from each source snippet with the same shared AST
detector used by EXP1 and EXP3.  The legacy detected_pandas_apis CSV column is
not used.

Corpus: polars_docs_union.json (polars.Config.* removed upstream)

Usage (from data/ root):
    # Retrieval only (default):
    python experiments/scripts/run_exp2_v2.py

    # Limit to N snippets (smoke test):
    python experiments/scripts/run_exp2_v2.py --limit 30

    # With LLM generation:
    python experiments/scripts/run_exp2_v2.py --model gpt-4.1-mini

    # Custom polars docs:
    python experiments/scripts/run_exp2_v2.py \\
        --polars-docs experiments/results/merged_polars_docs_filtered.json
"""

import argparse
import csv
import json
import logging
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Tuple

RELEASE_ROOT = Path(__file__).resolve().parents[2]

sys.path.insert(0, str(RELEASE_ROOT / "shared" / "code"))
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
from ast_api_locator import build_maps_from_json, extract_pandas_api_details

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

PREV_RESULTS           = RELEASE_ROOT / "exp2" / "results"
OUTPUT_DIR             = RELEASE_ROOT / "exp2" / "results" / "reproduced"
POLARS_DOCS            = RELEASE_ROOT / "shared" / "knowledge" / "polars_docs_union.json"
PANDAS_DOCS_STRUCTURED = RELEASE_ROOT / "shared" / "knowledge" / "pandas_api_structured.json"
SOURCE_API_REGISTRY    = RELEASE_ROOT.parent / "ast-api-detector" / "data" / "registry" / "pandas_source_api_registry.json"
PROMPT_TEMPLATE        = RELEASE_ROOT / "exp2" / "prompts" / "prompt_template.txt"
GOLD_LABELS            = RELEASE_ROOT / "shared" / "input" / "gold_labels_review.csv"

# Aliases: detected API name form → name used in pandas_api_structured.json
# Only safe aliases: GroupBy short-forms and top-level function aliases.
# Removed unsafe DataFrame.X → Series.X / Index.X aliases that cause
# semantic pollution (wrong behavioral description in retrieval query).
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


# ── I/O helpers ───────────────────────────────────────────────────────────────

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
    """Run the same shared AST detector used by EXP1 and EXP3."""
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
    """Load snippet IDs and source texts; API detection runs separately."""
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

def build_prompt_exp2(
    snippet:       Dict,
    detected_apis: List[Dict],
    missing:       List[str],
    api_results:   List[Dict],
    template:      str,
) -> str:
    api_list = "\n".join(
        f"  - {e['api_name']} ({e.get('object_type', 'method')})"
        for e in detected_apis
    ) or "  (none detected)"

    mapping_blocks = []
    for res in api_results:
        lines = [f"\npandas API: {res['source_pandas_api']}"]
        pd_desc = res.get("pandas_description", "")
        if pd_desc:
            lines.append(f"  pandas: {pd_desc}")
        candidates = res.get("top_candidates", [])
        if candidates:
            lines.append("  Retrieved Polars candidates (embedding similarity):")
            for c in candidates:
                line = f"  {c['rank']}. {c['polars_api']} (score={c['score']:.4f})"
                if c.get("description"):
                    line += f"\n     {c['description']}"
                if c.get("examples"):
                    line += f"\n     Example: {c['examples']}"
                lines.append(line)
        else:
            lines.append("  Polars candidates: none found — translate manually")
        mapping_blocks.append("\n".join(lines))

    return template.format(
        source_code             = snippet["pandas_code"],
        detected_apis           = api_list,
        dynamic_mapping_records = "\n".join(mapping_blocks) or "(no mappings)",
        unknown_methods         = "\n".join(f"  - {u}" for u in missing) or "  (none)",
    )


# ── Per-snippet processing ────────────────────────────────────────────────────

def process_one(
    snippet:             Dict,
    detected_apis:       List[Dict],
    pandas_index:        Dict[str, Dict],
    embedding_retriever,
    template:            str,
    top_k:               int = 5,
    llm                      = None,
) -> Dict:
    sid         = snippet["snippet_id"]
    pandas_code = snippet["pandas_code"]

    matched_docs, missing = lookup_all_pandas_docs(
        {"detected_apis": detected_apis}, pandas_index
    )

    api_results: List[Dict] = []
    diagnostics: List[Dict] = []

    for item in matched_docs:
        api_entry  = item["api_entry"]
        pandas_doc = item["pandas_doc"]
        api_name   = api_entry["api_name"]

        emb_q       = build_embedding_query(api_entry, pandas_doc, pandas_code)
        conv_intent = is_conversion_intent(api_name)
        emb_raw     = embedding_retriever.retrieve(emb_q, top_k=top_k)
        emb_kept, emb_filtered = filter_conversion_candidates(emb_raw, api_name, conv_intent)
        top_candidates = emb_kept[:top_k]

        api_results.append({
            "source_pandas_api":  api_name,
            "pandas_description": _to_sentence(pandas_doc.get("functional_description", "")),
            "embedding_query":    emb_q,
            "top_candidates": [
                {
                    "rank":        i + 1,
                    "polars_api":  c["polars_api_name"],
                    "score":       c["score"],
                    "description": _to_sentence(c.get("functional_description", "")),
                    "examples":    c.get("examples", ""),
                }
                for i, c in enumerate(top_candidates)
            ],
            "filtered_conversion_apis": [c["polars_api_name"] for c in emb_filtered],
        })

        diagnostics.append({
            "snippet_id":        sid,
            "source_pandas_api": api_name,
            "embedding_query":   emb_q,
            "conversion_intent": conv_intent,
            "embedding_candidates_after_filter": [
                {"api_name": c["polars_api_name"], "rank": c["rank"], "score": c["score"]}
                for c in top_candidates
            ],
            "filtered_conversion_candidates": [
                {"api_name": c["polars_api_name"], "rank": c["rank"]}
                for c in emb_filtered
            ],
        })

    prompt_context = build_prompt_exp2(
        snippet, detected_apis, missing, api_results, template
    )
    generated_code = ""
    raw_model_response = None
    if llm is not None:
        try:
            resp = llm.invoke([{"role": "user", "content": prompt_context}])
            generated_code = resp.content
            raw_model_response = resp.raw_response
        except Exception as exc:
            generated_code = f"# LLM ERROR: {exc}"
            raw_model_response = {
                "error_type": type(exc).__name__,
                "error_message": str(exc),
            }

    return {
        "snippet_id":            sid,
        "pandas_code":           pandas_code,
        "detected_apis":         [a["api_name"] for a in detected_apis],
        "missing_pandas_docs":   missing,
        "api_results":           api_results,
        "prompt_context":        prompt_context,
        "generated_polars_code": generated_code,
        "raw_model_response":    raw_model_response,
        "_diagnostics":          diagnostics,
    }


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="EXP2 V2 — Embedding-only retrieval")
    parser.add_argument("--polars-docs",    default=str(POLARS_DOCS))
    parser.add_argument("--pandas-docs",   default=str(PANDAS_DOCS_STRUCTURED))
    parser.add_argument("--mapping",       default=str(SOURCE_API_REGISTRY),
                        help="Source-only API registry used by the shared AST detector")
    parser.add_argument("--prev-results",  default=str(PREV_RESULTS))
    parser.add_argument("--gold-labels",   default=str(GOLD_LABELS))
    parser.add_argument("--output",        default=str(OUTPUT_DIR))
    parser.add_argument("--top-k",         type=int, default=5)
    parser.add_argument("--limit",         type=int, default=None,
                        help="Process only first N snippets")
    parser.add_argument("--model",         default="",
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

    logger.info("Loading snippet corpus (%s) …", args.gold_labels)
    snippets_by_sid = load_gold_labels(Path(args.gold_labels))
    logger.info("  %d snippets", len(snippets_by_sid))

    logger.info("Loading shared AST detector metadata (%s) …", args.mapping)
    ast_maps = build_maps_from_json(args.mapping)

    logger.info("Loading pandas doc index (%s) …", args.pandas_docs)
    pandas_index = load_pandas_index(Path(args.pandas_docs))

    logger.info("Loading prompt template …")
    template = PROMPT_TEMPLATE.read_text(encoding="utf-8")

    # Optional LLM
    llm = None
    if args.model:
        import openai as _openai
        class _LLM:
            class _R:
                def __init__(self, text, raw_response):
                    self.content = text
                    self.raw_response = raw_response
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
                return self._R(
                    r.output_text,
                    r.model_dump(mode="json"),
                )
        if os.environ.get("OPENAI_API_KEY"):
            llm = _LLM(args.model)
            logger.info("LLM: %s (responses API, reasoning=low)", args.model)
        else:
            logger.warning("OPENAI_API_KEY not set — retrieval-only mode")

    sid_order = sorted(snippets_by_sid.keys())
    if args.limit:
        sid_order = sid_order[: args.limit]
    logger.info("Processing %d snippets …", len(sid_order))

    results:     List[Dict] = []
    diagnostics: List[Dict] = []
    outputs:     List[Dict] = []

    for i, sid in enumerate(sid_order, 1):
        detected_apis, ast_details = detect_apis(
            snippets_by_sid[sid]["pandas_code"], ast_maps
        )
        r = process_one(
            snippet             = snippets_by_sid[sid],
            detected_apis       = detected_apis,
            pandas_index        = pandas_index,
            embedding_retriever = embedding_retriever,
            template            = template,
            top_k               = args.top_k,
            llm                 = llm,
        )
        diags = r.pop("_diagnostics", [])
        results.append(r)
        diagnostics.extend(diags)
        outputs.append({
            "snippet_id":            r["snippet_id"],
            "detected_apis":         r["detected_apis"],
            "ast_details":           ast_details,
            "missing_pandas_docs":   r["missing_pandas_docs"],
            "generated_polars_code": r["generated_polars_code"],
            "raw_model_response":    r["raw_model_response"],
        })

        if i % 50 == 0 or i == len(sid_order):
            logger.info("  %d / %d done", i, len(sid_order))

    write_jsonl(output_dir / "retrieval_results.jsonl",     results)
    write_jsonl(output_dir / "retrieval_diagnostics.jsonl", diagnostics)
    write_jsonl(output_dir / "experiment2_outputs.jsonl",   outputs)

    prompts_dir = output_dir / "prompts"
    responses_dir = output_dir / "raw_responses"
    generated_dir = output_dir / "generated_py"
    prompts_dir.mkdir(parents=True, exist_ok=True)
    responses_dir.mkdir(parents=True, exist_ok=True)
    generated_dir.mkdir(parents=True, exist_ok=True)
    for result in results:
        sid = result["snippet_id"]
        (prompts_dir / f"{sid}.txt").write_text(
            result["prompt_context"], encoding="utf-8"
        )
        (responses_dir / f"{sid}.json").write_text(
            json.dumps(result["raw_model_response"], ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        (generated_dir / f"{sid}.py").write_text(
            result["generated_polars_code"], encoding="utf-8"
        )

    manifest = {
        "experiment": "exp2_v2",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "model": args.model or None,
        "api": "responses" if llm is not None else None,
        "reasoning_effort": "low" if llm is not None else None,
        "max_output_tokens": 6000 if llm is not None else None,
        "top_k": args.top_k,
        "snippet_count": len(results),
        "prompt_template": str(PROMPT_TEMPLATE),
        "polars_docs": str(args.polars_docs),
        "pandas_docs": str(args.pandas_docs),
        "mapping_metadata": str(args.mapping),
        "source_script": str(Path(__file__).resolve()),
    }
    (output_dir / "run_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    total   = len(diagnostics)
    w_hit   = sum(1 for d in diagnostics if d["embedding_candidates_after_filter"])
    w_gen   = sum(1 for o in outputs if o["generated_polars_code"].strip())
    filtered = sum(len(d["filtered_conversion_candidates"]) for d in diagnostics)

    print(f"\n── EXP2 V2 Stats ──────────────────────────────────")
    print(f"  Snippets processed        : {len(results)}")
    print(f"  pandas-API pairs          : {total}")
    print(f"  Pairs with ≥1 candidate   : {w_hit} ({100*w_hit/max(total,1):.1f}%)")
    print(f"  Conversion APIs filtered  : {filtered}")
    if llm:
        print(f"  With generated code       : {w_gen}")
    print(f"  Output directory          : {output_dir}")


if __name__ == "__main__":
    main()
