"""Pandas documentation lookup and embedding-query construction."""

import re
from typing import Dict, List, Optional, Tuple


def build_pandas_doc_index(pandas_docs: List[Dict]) -> Dict[str, Dict]:
    """Build a multi-key lookup index over pandas documentation records."""
    index: Dict[str, Dict] = {}
    for doc in pandas_docs:
        name = doc.get("api_name", "")
        if not name:
            continue
        index[name] = doc
        index.setdefault(name.split(".")[-1], doc)
        index.setdefault(re.sub(r"^pandas\.", "", name), doc)
    return index


def lookup_pandas_doc(api_name: str, index: Dict[str, Dict]) -> Optional[Dict]:
    """Look up a pandas API using the normalized fallbacks used in the study."""
    if api_name in index:
        return index[api_name]
    stripped = re.sub(r"^pandas\.", "", api_name)
    if stripped in index:
        return index[stripped]
    lower = api_name.lower()
    for key, value in index.items():
        if key.lower() == lower:
            return value
    return index.get(api_name.split(".")[-1])


def lookup_all_pandas_docs(
    detection: Dict,
    pandas_index: Dict[str, Dict],
) -> Tuple[List[Dict], List[str]]:
    """Return documentation matches and APIs without a matching record."""
    matched: List[Dict] = []
    missing: List[str] = []
    for api_entry in detection["detected_apis"]:
        doc = lookup_pandas_doc(api_entry["api_name"], pandas_index)
        if doc:
            matched.append({"api_entry": api_entry, "pandas_doc": doc})
        else:
            missing.append(api_entry["api_name"])
    return matched, missing


def build_embedding_query(
    api_entry: Dict,
    pandas_doc: Dict,
    pandas_code: str,
) -> str:
    """Build the semantic query submitted to the embedding retriever."""
    api_name = api_entry.get("api_name", "")
    object_type = api_entry.get("object_type", "")
    description = pandas_doc.get("functional_description", "")[:300].strip()

    parts = [f"Source pandas API: {api_name}"]
    if object_type and object_type != "top_level":
        parts.append(f"Object type: {object_type}")
    if description:
        parts.append(f"Pandas description: {description}")

    method = api_name.split(".")[-1]
    context_lines = [
        line.strip()
        for line in pandas_code.splitlines()
        if method in line and not line.strip().startswith("#")
    ][:3]
    if context_lines:
        parts.append("Code context: " + " | ".join(context_lines))

    parts.append(
        "Migration need: find Polars documentation chunks that can express "
        "the same operation in Polars."
    )
    return "\n".join(parts)
