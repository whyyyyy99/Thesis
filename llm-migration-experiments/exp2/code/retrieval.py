"""Embedding-only Polars documentation retrieval used by Exp2 and Exp3."""

import logging
from typing import Dict, List, Set, Tuple

logger = logging.getLogger(__name__)


# Generic conversion APIs were frequent false positives during pilot retrieval.
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

# No source APIs in the final experiment bypassed the conversion-noise filter.
CONVERSION_INTENT_APIS: Set[str] = set()


def is_conversion_intent(source_api: str) -> bool:
    """Return whether a source API represents an explicit conversion operation."""
    return source_api in CONVERSION_INTENT_APIS


def filter_conversion_candidates(
    candidates: List[Dict],
    source_api: str,
    conversion_intent: bool,
) -> Tuple[List[Dict], List[Dict]]:
    """Split embedding candidates into retained and filtered records."""
    if conversion_intent:
        return list(candidates), []

    kept: List[Dict] = []
    filtered: List[Dict] = []
    for candidate in candidates:
        api_name = candidate.get("polars_api_name", "")
        if api_name in RETRIEVAL_NOISE_APIS:
            filtered.append(
                {
                    **candidate,
                    "filter_reason": (
                        f"{api_name} is a retrieval noise API; "
                        f"{source_api} is not a conversion-intent source"
                    ),
                }
            )
        else:
            kept.append(candidate)
    return kept, filtered


class EmbeddingRetriever:
    """Dense cosine retriever using all-mpnet-base-v2."""

    def __init__(self, docs: List[Dict], model_name: str = "all-mpnet-base-v2"):
        import os

        os.environ.setdefault("HF_HUB_OFFLINE", "1")
        import numpy as np
        from sentence_transformers import SentenceTransformer

        self._docs = docs
        self._np = np
        self._model = SentenceTransformer(model_name)

        texts = [self._text(doc) for doc in docs]
        logger.info("Embedding %d Polars docs with %s", len(docs), model_name)
        self._vecs = self._model.encode(
            texts,
            convert_to_numpy=True,
            show_progress_bar=False,
        ).astype("float32")
        norms = np.linalg.norm(self._vecs, axis=1, keepdims=True)
        norms[norms == 0] = 1.0
        self._vecs /= norms
        logger.info("Embedding index ready (dim=%d)", self._vecs.shape[1])

    @staticmethod
    def _text(doc: Dict) -> str:
        return " ".join(
            filter(
                None,
                [
                    doc.get("api_name", ""),
                    doc.get("functional_description", "")[:400],
                    doc.get("examples", "")[:100],
                ],
            )
        )

    def retrieve(self, query: str, top_k: int = 20) -> List[Dict]:
        """Return the highest-cosine documentation records."""
        query_vector = self._model.encode(
            [query],
            convert_to_numpy=True,
            show_progress_bar=False,
        )[0].astype("float32")
        query_vector /= max(float(self._np.linalg.norm(query_vector)), 1e-9)
        scores = self._vecs @ query_vector
        ranked = self._np.argsort(scores)[::-1][:top_k]

        results: List[Dict] = []
        for rank, index in enumerate(ranked, 1):
            index = int(index)
            doc = self._docs[index]
            results.append(
                {
                    "chunk_id": f"polars_{index}",
                    "polars_api_name": doc.get("api_name", ""),
                    "retriever_type": "embedding_cosine",
                    "rank": rank,
                    "score": round(float(scores[index]), 6),
                    "signature": doc.get("functional_description", "")[:300],
                    "functional_description": doc.get(
                        "functional_description", ""
                    ),
                    "examples": doc.get("examples", ""),
                    "source_file": doc.get("source_file", ""),
                }
            )
        return results
