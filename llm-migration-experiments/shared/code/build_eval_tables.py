"""
Build evaluation tables for the current Experiments 1, 2 V2, and 3 V2.

One CSV per experiment, one row per snippet.

Columns:
  snippet_id, pandas_code, detected_pandas_apis,
  chunks_used,                          ← experiment-specific knowledge injected
  generated_polars_code,
  reference_polars_code,
  gold_target_polars_apis,
  generated_polars_apis,
  syntactically_valid, has_polars_import, no_pandas_leakage, code_not_empty,
  api_recall, api_precision, api_f1,
  silver_score, silver_label,
  exclude

Run from data/ root:
    python3 experiments/scripts/build_eval_tables.py

Use --include-legacy to also rebuild the archived EXP2/EXP3 tables.
"""

import argparse
import ast
import csv
import json
import re
from pathlib import Path

EXP_ROOT  = Path(__file__).parent.parent
DATA_ROOT = EXP_ROOT.parent
RESULTS   = EXP_ROOT / "results"


# ── Code quality helpers ──────────────────────────────────────────────────

def is_syntactically_valid(code: str) -> int:
    if not code or not code.strip():
        return 0
    # strip markdown fences if present
    cleaned = re.sub(r"^```[^\n]*\n", "", code.strip())
    cleaned = re.sub(r"\n```$", "", cleaned)
    try:
        ast.parse(cleaned)
        return 1
    except SyntaxError:
        return 0


def has_polars_import(code: str) -> int:
    return int(bool(re.search(r"\bimport polars\b", code or "")))


def no_pandas_leakage(code: str) -> int:
    return int(not bool(re.search(r"\bimport pandas\b|\bpd\.", code or "")))


def extract_generated_apis(code: str) -> list:
    """Extract unique polars.X / pl.X tokens from generated code."""
    if not code:
        return []
    hits = re.findall(r"\bpl\.([A-Za-z_][A-Za-z0-9_]*)", code)
    hits += re.findall(r"\bpolars\.([A-Za-z_][A-Za-z0-9_]*)", code)
    seen, result = set(), []
    for h in hits:
        key = f"polars.{h}"
        if key not in seen:
            seen.add(key)
            result.append(key)
    return result


def _leaf(api: str) -> str:
    return api.split(".")[-1].lower()


def compute_metrics(generated_apis: list, gold_apis: list):
    """Precision / recall / F1 at method-name level vs gold_target_polars_apis."""
    if not gold_apis:
        return 1.0, 1.0, 1.0
    gen_set  = {_leaf(a) for a in generated_apis}
    gold_set = {_leaf(a) for a in gold_apis}
    if not gen_set:
        return 0.0, 0.0, 0.0
    tp        = len(gen_set & gold_set)
    recall    = round(tp / len(gold_set), 3) if gold_set else 1.0
    precision = round(tp / len(gen_set),  3) if gen_set  else 0.0
    denom     = recall + precision
    f1        = round(2 * recall * precision / denom, 3) if denom else 0.0
    return recall, precision, f1


def silver_score(valid, pol_imp, no_leak, not_empty, recall):
    base = (valid + pol_imp + no_leak + not_empty) / 4
    return round((base + recall) / 2, 3)


def silver_label(score: float) -> str:
    if score >= 0.75:
        return "pass"
    elif score >= 0.4:
        return "partial"
    return "fail"


def write_csv(path: Path, rows: list, fieldnames: list) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    print(f"  Saved {len(rows)} rows → {path}")


# ── Load gold_labels_review (shared across experiments) ───────────────────

def load_gold(exp_dir: Path) -> dict:
    """Return dict keyed by snippet_id with gold columns."""
    df_path = exp_dir / "gold_labels_review.csv"
    gold = {}
    with open(df_path, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            gold[row["snippet_id"]] = row
    return gold


def load_jsonl(path: Path) -> list:
    records = []
    with open(path, encoding="utf-8") as f:
        for line_number, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError as exc:
                raise ValueError(f"Invalid JSON in {path}:{line_number}: {exc}") from exc
    return records


def index_records(records: list, source: Path) -> dict:
    """Index records by snippet_id and reject ambiguous experiment output."""
    indexed = {}
    for record in records:
        sid = record.get("snippet_id", "")
        if not sid:
            raise ValueError(f"Record without snippet_id in {source}")
        if sid in indexed:
            raise ValueError(f"Duplicate snippet_id {sid!r} in {source}")
        indexed[sid] = record
    return indexed


def validate_pair_set(records: dict, gold: dict, source: Path) -> None:
    missing = sorted(set(gold) - set(records))
    extra = sorted(set(records) - set(gold))
    if missing or extra:
        details = []
        if missing:
            details.append(f"missing={len(missing)} ({', '.join(missing[:5])})")
        if extra:
            details.append(f"extra={len(extra)} ({', '.join(extra[:5])})")
        raise ValueError(f"Pair mismatch for {source}: {'; '.join(details)}")


def detected_api_names(record: dict) -> list:
    return [
        item.get("api_name", "") if isinstance(item, dict) else str(item)
        for item in record.get("detected_apis", [])
        if (item.get("api_name", "") if isinstance(item, dict) else str(item))
    ]


def retrieved_chunk_names(record: dict, include_mapping: bool) -> list:
    """Return unique API-document identifiers actually placed in the prompt."""
    names = []
    for api_result in record.get("api_results", []):
        if include_mapping:
            target = api_result.get("confirmed_target_api", "")
            if target:
                names.append(f"{target}[mapping]")
        for candidate in api_result.get("top_candidates", []):
            name = candidate.get("polars_api", "") if isinstance(candidate, dict) else str(candidate)
            if name:
                names.append(f"{name}[candidate]" if include_mapping else name)
    return list(dict.fromkeys(names))


FIELDNAMES = [
    "snippet_id",
    "pandas_code",
    "detected_pandas_apis",
    "chunks_used",
    "generated_polars_code",
    "reference_polars_code",
    "gold_target_polars_apis",
    "generated_polars_apis",
    "syntactically_valid",
    "has_polars_import",
    "no_pandas_leakage",
    "code_not_empty",
    "api_recall",
    "api_precision",
    "api_f1",
    "silver_score",
    "silver_label",
    "exclude",
]


def _build_row(snippet_id, pandas_code, detected_apis, chunks_used,
               gen_code, ref_code, gold_apis_str, exclude):
    gold_apis = [a.strip() for a in gold_apis_str.split(",") if a.strip()] if gold_apis_str else []
    gen_apis  = extract_generated_apis(gen_code)
    recall, precision, f1 = compute_metrics(gen_apis, gold_apis)
    valid     = is_syntactically_valid(gen_code)
    pol_imp   = has_polars_import(gen_code)
    no_leak   = no_pandas_leakage(gen_code)
    not_empty = int(bool((gen_code or "").strip()))
    score     = silver_score(valid, pol_imp, no_leak, not_empty, recall)
    return {
        "snippet_id":            snippet_id,
        "pandas_code":           pandas_code,
        "detected_pandas_apis":  detected_apis,
        "chunks_used":           chunks_used,
        "generated_polars_code": gen_code,
        "reference_polars_code": ref_code,
        "gold_target_polars_apis": gold_apis_str,
        "generated_polars_apis": ",".join(gen_apis),
        "syntactically_valid":   valid,
        "has_polars_import":     pol_imp,
        "no_pandas_leakage":     no_leak,
        "code_not_empty":        not_empty,
        "api_recall":            recall,
        "api_precision":         precision,
        "api_f1":                f1,
        "silver_score":          score,
        "silver_label":          silver_label(score),
        "exclude":               exclude,
    }


# ── EXP1 ──────────────────────────────────────────────────────────────────

def process_exp1():
    exp_dir = RESULTS / "exp1_ast_guided"
    gold    = load_gold(exp_dir)

    with open(exp_dir / "ast_guided_outputs.json", encoding="utf-8") as f:
        records = json.load(f)

    rows = []
    for r in records:
        # ast_guided_outputs.json's snippet_id is a full extracted_snippets/
        # path (e.g. ".../05afd878_evaluate_coassembly_edges_before.py"), not
        # the bare snippet_id gold_labels_review.csv is keyed by. Without this
        # normalization every gold lookup silently misses, gold_apis is always
        # empty, and every row gets the trivial "no gold APIs" perfect score.
        sid       = re.sub(r"_before\.py$", "", Path(r["snippet_id"]).name)
        g         = gold.get(sid, {})
        det_apis  = r.get("detected_apis", [])
        # chunks = which mapping records were actually matched
        chunks    = ",".join(r.get("matched_source_apis", []))
        gen_code  = r.get("generated_polars_code", "")
        ref_code  = g.get("reference_polars_code", "")
        gold_apis = g.get("gold_target_polars_apis", "")
        exclude   = g.get("exclude", "")
        pandas_code = g.get("pandas_code", r.get("source_code", ""))

        rows.append(_build_row(
            sid, pandas_code, ",".join(det_apis), chunks,
            gen_code, ref_code, gold_apis, exclude,
        ))

    write_csv(exp_dir / "eval_table.csv", rows, FIELDNAMES)
    return rows


# ── EXP2 ──────────────────────────────────────────────────────────────────

def process_exp2():
    exp_dir = RESULTS / "exp2_doc_rag"
    gold    = load_gold(exp_dir)

    records = []
    with open(exp_dir / "experiment2_outputs.jsonl", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                records.append(json.loads(line))

    rows = []
    for r in records:
        sid       = r["snippet_id"]
        g         = gold.get(sid, {})
        det_apis  = [e["api_name"] if isinstance(e, dict) else e
                     for e in r.get("detected_apis", [])]
        # chunks = top embedding-retrieved Polars documentation candidates
        chunks = ",".join(r.get("top_embedding_candidates", []))
        gen_code  = r.get("generated_polars_code", "")
        ref_code  = g.get("reference_polars_code", "")
        gold_apis = g.get("gold_target_polars_apis", "")
        exclude   = g.get("exclude", "")
        pandas_code = g.get("pandas_code", "")

        rows.append(_build_row(
            sid, pandas_code, ",".join(det_apis), chunks,
            gen_code, ref_code, gold_apis, exclude,
        ))

    write_csv(exp_dir / "eval_table.csv", rows, FIELDNAMES)
    return rows


# ── EXP3 ──────────────────────────────────────────────────────────────────

def process_exp3():
    exp_dir = RESULTS / "exp3_hybrid_vb"
    gold    = load_gold(exp_dir)

    records = []
    with open(exp_dir / "experiment3_outputs.jsonl", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                records.append(json.loads(line))

    # Load hybrid knowledge records for chunk details
    knowledge = {}
    kr_path = exp_dir / "hybrid_knowledge_records.jsonl"
    if kr_path.exists():
        with open(kr_path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    kr = json.loads(line)
                    sid = kr.get("snippet_id", "")
                    knowledge.setdefault(sid, [])
                    role    = kr.get("role", "")
                    api     = kr.get("source_api") or kr.get("target_api") or kr.get("polars_api_name", "")
                    if api:
                        knowledge[sid].append(f"{api}[{role}]" if role else api)

    rows = []
    for r in records:
        sid       = r["snippet_id"]
        g         = gold.get(sid, {})
        det_apis  = [e["api_name"] if isinstance(e, dict) else e
                     for e in r.get("detected_apis", [])]
        # chunks = hybrid knowledge: static mapping + RAG docs
        chunks    = ",".join(knowledge.get(sid, r.get("mapping_found", [])))
        gen_code  = r.get("generated_polars_code", "")
        ref_code  = g.get("reference_polars_code", "")
        gold_apis = g.get("gold_target_polars_apis", "")
        exclude   = g.get("exclude", "")
        pandas_code = g.get("pandas_code", "")

        rows.append(_build_row(
            sid, pandas_code, ",".join(det_apis), chunks,
            gen_code, ref_code, gold_apis, exclude,
        ))

    write_csv(exp_dir / "eval_table.csv", rows, FIELDNAMES)
    return rows


# ── Current V2 pipelines ─────────────────────────────────────────────────

def process_exp2_v2():
    exp_dir = RESULTS / "exp2_v2"
    gold = load_gold(RESULTS / "exp2_doc_rag")
    output_path = exp_dir / "experiment2_outputs.jsonl"
    retrieval_path = exp_dir / "retrieval_results.jsonl"

    outputs = index_records(load_jsonl(output_path), output_path)
    retrieval = index_records(load_jsonl(retrieval_path), retrieval_path)
    validate_pair_set(outputs, gold, output_path)
    validate_pair_set(retrieval, gold, retrieval_path)

    rows = []
    for sid, g in gold.items():
        output = outputs[sid]
        context = retrieval[sid]
        rows.append(_build_row(
            sid,
            g.get("pandas_code", context.get("pandas_code", "")),
            ",".join(detected_api_names(output)),
            ",".join(retrieved_chunk_names(context, include_mapping=False)),
            output.get("generated_polars_code", ""),
            g.get("reference_polars_code", ""),
            g.get("gold_target_polars_apis", ""),
            g.get("exclude", ""),
        ))

    write_csv(exp_dir / "eval_table.csv", rows, FIELDNAMES)
    return rows


def process_exp3_v2():
    exp_dir = RESULTS / "exp3_v2"
    gold = load_gold(RESULTS / "exp2_doc_rag")
    retrieval_path = exp_dir / "retrieval_results.jsonl"
    records = index_records(load_jsonl(retrieval_path), retrieval_path)
    validate_pair_set(records, gold, retrieval_path)

    rows = []
    for sid, g in gold.items():
        record = records[sid]
        rows.append(_build_row(
            sid,
            g.get("pandas_code", record.get("pandas_code", "")),
            ",".join(detected_api_names(record)),
            ",".join(retrieved_chunk_names(record, include_mapping=True)),
            record.get("generated_polars_code", ""),
            g.get("reference_polars_code", ""),
            g.get("gold_target_polars_apis", ""),
            g.get("exclude", ""),
        ))

    write_csv(exp_dir / "eval_table.csv", rows, FIELDNAMES)
    return rows


# ── Main ──────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--include-legacy",
        action="store_true",
        help="also rebuild archived exp2_doc_rag and exp3_hybrid_vb tables",
    )
    args = parser.parse_args()

    print("Building EXP1 eval table...")
    r1 = process_exp1()

    print("Building EXP2 V2 eval table...")
    r2 = process_exp2_v2()

    print("Building EXP3 V2 eval table...")
    r3 = process_exp3_v2()

    result_sets = [("EXP1", r1), ("EXP2 V2", r2), ("EXP3 V2", r3)]
    if args.include_legacy:
        print("Building legacy EXP2 eval table...")
        legacy_r2 = process_exp2()
        print("Building legacy EXP3 eval table...")
        legacy_r3 = process_exp3()
        result_sets.extend([("EXP2 legacy", legacy_r2), ("EXP3 legacy", legacy_r3)])

    print()
    for name, rows in result_sets:
        total     = len(rows)
        excluded  = [r for r in rows if str(r.get("exclude", "")).strip()]
        included  = [r for r in rows if not str(r.get("exclude", "")).strip()]
        excl      = len(excluded)
        n_incl    = len(included)
        passes    = sum(1 for r in included if r["silver_label"] == "pass")
        partials  = sum(1 for r in included if r["silver_label"] == "partial")
        fails     = sum(1 for r in included if r["silver_label"] == "fail")
        avg_f1    = round(sum(r["api_f1"] for r in included) / max(n_incl, 1), 3)
        print(f"{name}: total={total}  exclude={excl}  scored={n_incl}  pass={passes}  partial={partials}  fail={fails}  avg_f1={avg_f1}")


if __name__ == "__main__":
    main()
