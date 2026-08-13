"""
Experiment 2 retrieval utilities.

Retrievers
----------
BM25Retriever       — rank_bm25 (lexical)
EmbeddingRetriever  — all-mpnet-base-v2 cosine (dense)

Fusion
------
rrf_merge           — Reciprocal Rank Fusion  RRF(d) = Σ 1/(k + rank_r(d))

v2 additions (separated-query mode)
------------------------------------
RETRIEVAL_NOISE_APIS      — polars APIs that are systematic embedding false positives
CONVERSION_INTENT_APIS    — pandas APIs that legitimately need conversion candidates
filter_conversion_candidates — removes retrieval noise APIs unless source has conversion intent
"""

import logging
import re
import string
from typing import Dict, List, Optional, Set, Tuple

logger = logging.getLogger(__name__)

# ── Shared tokeniser (used by BM25 index + queries) ───────────────────────

_PUNCT = str.maketrans("", "", string.punctuation)
_COMPOUND: Dict[str, str] = {
    "groupby":        "group by",
    "sort_values":    "sort values",
    "reset_index":    "reset index",
    "set_index":      "set index",
    "fillna":         "fill null na",
    "dropna":         "drop null na",
    "isna":           "is null na",
    "notna":          "not null na",
    "value_counts":   "value counts",
    "to_datetime":    "to datetime parse",
    "read_csv":       "read csv",
    "to_csv":         "write csv",
    "drop_duplicates": "drop duplicates unique",
    "merge":          "join merge",
    "concat":         "concat append",
    "pivot":          "pivot reshape",
    "melt":           "melt unpivot",
    "astype":         "cast type",
    "apply":          "apply map elements",
    "agg":            "aggregate agg",
    "aggregate":      "aggregate agg",
    "rename":         "rename columns",
    "nunique":        "count distinct unique",
}


def tokenise(text: str) -> List[str]:
    text = text.lower().translate(_PUNCT)
    text = re.sub(r"[_.]", " ", text)
    tokens = text.split()
    expanded: List[str] = []
    for t in tokens:
        expanded.append(t)
        if t in _COMPOUND:
            expanded.extend(_COMPOUND[t].split())
    return expanded


# ── v2: Conversion API filtering ──────────────────────────────────────────

# Polars APIs that are generic pandas↔polars object converters.
# These dominate BM25 results because they mention "pandas" heavily.
RETRIEVAL_NOISE_APIS: Set[str] = {
    "polars.from_pandas",
    "polars.from_dataframe",
    "polars.from_repr",
    "polars.DataFrame.to_pandas",
    "polars.Series.to_pandas",
    "polars.DataFrame.to_arrow",
    "polars.Series.to_arrow",
    "polars.DataFrame.to_init_repr",
    "polars.DataFrame.__dataframe__",
}

# Pandas source APIs where a noise candidate is actually relevant
# (e.g., the snippet explicitly constructs a polars object from pandas data).
# All other source APIs will have noise candidates filtered out.
# Conservative by design: when in doubt, filter rather than allow.
CONVERSION_INTENT_APIS: Set[str] = {}

# Keyword argument names too generic to add signal to a BM25 query.
_SKIP_KW_NAMES: Set[str] = {
    "self", "df", "data", "result", "output", "value", "values",
    "col", "cols", "column", "columns", "axis", "inplace",
    "x", "y", "i", "j", "k", "n", "s",
}

# String literal argument values worth including in a BM25 query.
_KEEP_ARG_VALUES: Set[str] = {
    "first", "last", "any", "all",
    "left", "right", "inner", "outer", "cross", "full", "semi", "anti",
    "ascending", "descending",
    "forward", "backward", "ffill", "bfill",
    "drop", "raise", "ignore",
    "sum", "mean", "min", "max", "count", "std", "var",
}


def is_conversion_intent(source_api: str) -> bool:
    """Return True when source_api is a genuine pandas-to-polars conversion context."""
    return source_api in CONVERSION_INTENT_APIS


def filter_conversion_candidates(
    candidates: List[Dict],
    source_api: str,
    conversion_intent: bool,
) -> Tuple[List[Dict], List[Dict]]:
    """
    Split candidates into (kept, filtered).

    Retrieval noise APIs are removed unless the source pandas operation is
    explicitly a conversion/construction context (CONVERSION_INTENT_APIS).
    Filtered list carries a 'filter_reason' key for diagnostics.
    """
    if conversion_intent:
        return list(candidates), []

    kept: List[Dict] = []
    filtered: List[Dict] = []
    for c in candidates:
        api = c.get("polars_api_name", "")
        if api in RETRIEVAL_NOISE_APIS:
            filtered.append({
                **c,
                "filter_reason": (
                    f"{api} is a retrieval noise API; "
                    f"{source_api} is not a conversion-intent source"
                ),
            })
        else:
            kept.append(c)
    return kept, filtered


# ── BM25 Retriever ─────────────────────────────────────────────────────────

class BM25Retriever:
    """Lexical BM25 retriever over Polars doc corpus (rank_bm25)."""

    def __init__(self, docs: List[Dict]):
        from rank_bm25 import BM25Okapi
        self._docs = docs
        corpus = [tokenise(self._text(d)) for d in docs]
        self._bm25 = BM25Okapi(corpus)
        logger.info("BM25 index built: %d documents", len(docs))

    @staticmethod
    def _text(doc: Dict) -> str:
        return " ".join(filter(None, [
            doc.get("api_name", ""),
            doc.get("functional_description", ""),
            doc.get("examples", ""),
        ]))

    def retrieve(self, query: str, top_k: int = 20) -> List[Dict]:
        scores = self._bm25.get_scores(tokenise(query))
        ranked = sorted(enumerate(scores), key=lambda x: x[1], reverse=True)[:top_k]
        results = []
        for rank_i, (idx, score) in enumerate(ranked, 1):
            results.append({
                "chunk_id":               f"polars_{idx}",
                "polars_api_name":        self._docs[idx].get("api_name", ""),
                "retriever_type":         "bm25",
                "rank":                   rank_i,
                "score":                  round(float(score), 6),
                "signature":              self._docs[idx].get("functional_description", "")[:300],
                "functional_description": self._docs[idx].get("functional_description", ""),
                "examples":               self._docs[idx].get("examples", ""),
                "source_file":            self._docs[idx].get("source_file", ""),
            })
        return results


# ── Embedding Cosine Retriever ─────────────────────────────────────────────

class EmbeddingRetriever:
    """Dense cosine retriever using all-mpnet-base-v2 (offline-safe)."""

    def __init__(self, docs: List[Dict], model_name: str = "all-mpnet-base-v2"):
        import os
        import numpy as np
        os.environ.setdefault("HF_HUB_OFFLINE", "1")
        from sentence_transformers import SentenceTransformer

        self._docs = docs
        self._np   = np
        self._model = SentenceTransformer(model_name)

        texts = [self._text(d) for d in docs]
        logger.info("Embedding %d Polars docs with %s …", len(docs), model_name)
        self._vecs = self._model.encode(texts, convert_to_numpy=True, show_progress_bar=False).astype("float32")
        # L2-normalise once so cosine = dot product at query time
        norms = np.linalg.norm(self._vecs, axis=1, keepdims=True)
        norms[norms == 0] = 1.0
        self._vecs /= norms
        logger.info("Embedding index ready (dim=%d)", self._vecs.shape[1])

    @staticmethod
    def _text(doc: Dict) -> str:
        return " ".join(filter(None, [
            doc.get("api_name", ""),
            doc.get("functional_description", "")[:400],
            doc.get("examples", "")[:100],
        ]))

    def retrieve(self, query: str, top_k: int = 20) -> List[Dict]:
        q = self._model.encode([query], convert_to_numpy=True, show_progress_bar=False)[0].astype("float32")
        q /= max(float(self._np.linalg.norm(q)), 1e-9)
        scores = self._vecs @ q
        ranked = self._np.argsort(scores)[::-1][:top_k]
        results = []
        for rank_i, idx in enumerate(ranked, 1):
            idx = int(idx)
            results.append({
                "chunk_id":               f"polars_{idx}",
                "polars_api_name":        self._docs[idx].get("api_name", ""),
                "retriever_type":         "embedding_cosine",
                "rank":                   rank_i,
                "score":                  round(float(scores[idx]), 6),
                "signature":              self._docs[idx].get("functional_description", "")[:300],
                "functional_description": self._docs[idx].get("functional_description", ""),
                "examples":               self._docs[idx].get("examples", ""),
                "source_file":            self._docs[idx].get("source_file", ""),
            })
        return results


# ── RRF Fusion ─────────────────────────────────────────────────────────────

def rrf_merge(
    bm25_results:      List[Dict],
    embedding_results: List[Dict],
    top_k: int = 5,
    k: int = 60,
) -> List[Dict]:
    """
    Reciprocal Rank Fusion.

        RRF(d) = Σ_r  1 / (k + rank_r(d))

    k=60 is the standard value from Cormack et al. 2009.
    Scores from different retrievers are NOT added — only ranks are used.
    """
    pool: Dict[str, Dict] = {}

    def _accumulate(results: List[Dict], rank_key: str, score_key: str) -> None:
        for entry in results:
            cid = entry["chunk_id"]
            if cid not in pool:
                pool[cid] = {
                    "chunk_id":               cid,
                    "polars_api_name":        entry["polars_api_name"],
                    "signature":              entry.get("signature", ""),
                    "functional_description": entry.get("functional_description", ""),
                    "examples":               entry.get("examples", ""),
                    "source_file":            entry.get("source_file", ""),
                    "bm25_rank":              None,
                    "bm25_score":             None,
                    "embedding_rank":         None,
                    "embedding_score":        None,
                    "rrf_score":              0.0,
                }
            pool[cid][rank_key]  = entry["rank"]
            pool[cid][score_key] = entry["score"]
            pool[cid]["rrf_score"] += 1.0 / (k + entry["rank"])

    _accumulate(bm25_results,      "bm25_rank",      "bm25_score")
    _accumulate(embedding_results, "embedding_rank",  "embedding_score")

    ranked = sorted(pool.values(), key=lambda x: x["rrf_score"], reverse=True)
    for final_rank, entry in enumerate(ranked[:top_k], 1):
        entry["final_rank"] = final_rank
        entry["rrf_score"]  = round(entry["rrf_score"], 8)

    return ranked[:top_k]
