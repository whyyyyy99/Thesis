"""Static-mapping lookup and mapping-aware query construction for Exp3."""

import json
import re
from typing import Dict, Optional, Tuple


def load_static_mapping_index(json_path: str) -> Dict[str, Dict]:
    """Load static mappings and index exact and normalized source API names."""
    with open(json_path, encoding="utf-8") as file:
        records = json.load(file)
    index: Dict[str, Dict] = {}
    for record in records:
        source_api = record.get("source_api", "").strip()
        if not source_api:
            continue
        index[source_api] = record
        index.setdefault(re.sub(r"^pandas\.", "", source_api), record)
        index.setdefault(source_api.lower(), record)
    return index


def lookup_static_mapping(
    api_name: str,
    mapping_index: Dict[str, Dict],
) -> Tuple[Optional[Dict], str]:
    """Return a mapping using exact, stripped, then lowercase lookup."""
    if api_name in mapping_index:
        return mapping_index[api_name], "exact"
    stripped = re.sub(r"^pandas\.", "", api_name)
    if stripped in mapping_index:
        return mapping_index[stripped], "stripped"
    lower = api_name.lower()
    if lower in mapping_index:
        return mapping_index[lower], "lowercase"
    return None, "not_found"


def build_query_case_a(
    api_entry: Dict,
    pandas_doc: Dict,
    static_mapping: Dict,
    pandas_code: str,
) -> str:
    """Build a mapping-aware query for supplementary documentation."""
    api_name = api_entry.get("api_name", "")
    target_api = static_mapping.get("target_api", "")
    description = pandas_doc.get("functional_description", "")[:250].strip()
    method = api_name.split(".")[-1]
    context_lines = [
        line.strip()
        for line in pandas_code.splitlines()
        if method in line and not line.strip().startswith("#")
    ][:3]

    parts = [
        f"Source pandas API: {api_name}",
        f"Pandas description: {description}" if description else "",
        f"Confirmed static mapping: {api_name} maps to {target_api}",
        f"Target Polars API: {target_api}",
        "Code context: " + " | ".join(context_lines) if context_lines else "",
        "Migration need: retrieve Polars documentation that explains how to use "
        "the mapped target API and related APIs to preserve the pandas behavior.",
    ]
    return "\n".join(part for part in parts if part)
