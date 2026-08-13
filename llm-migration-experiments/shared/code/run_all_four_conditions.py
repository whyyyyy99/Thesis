"""
Run test notebooks for all 4 conditions in parallel and collect L1/L2/L3 results.

Conditions:
  baseline   – generated_outputs/*/test/**/*.ipynb  (excl. legacy/)
  exp1       – experiments/results/exp1_ast_guided/test_notebooks_v2/*.ipynb
  exp2       – experiments/results/exp2_v2/test_notebooks_v2/*.ipynb
  exp3       – experiments/results/exp3_v2/test_notebooks_v2/*.ipynb

Run from data/ root:
  /opt/anaconda3/envs/my_nlp_env/bin/python3 experiments/scripts/run_all_four_conditions.py
"""

import argparse
import csv
import json
import re
import subprocess
import shutil
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

ROOT    = Path(__file__).resolve().parents[2]
PYTHON  = sys.executable
JUPYTER = shutil.which("jupyter") or "jupyter"
PIP     = [sys.executable, "-m", "pip"]

GOLD_LABELS_CSV = ROOT / "shared/input/gold_labels_review.csv"

NOTEBOOK_ROOTS = {
    "baseline": ROOT / "baseline/tests",
    "exp1": ROOT / "exp1/tests",
    "exp2": ROOT / "exp2/tests",
    "exp3": ROOT / "exp3/tests",
}


def _load_excluded_snippet_ids() -> set[str]:
    """snippet_ids flagged 'unsuitable' in the gold-label review (curated once,
    shared across all 4 conditions since it reflects the snippet, not the
    generated code)."""
    if not GOLD_LABELS_CSV.exists():
        return set()
    with open(GOLD_LABELS_CSV, newline="", encoding="utf-8") as f:
        return {
            row["snippet_id"]
            for row in csv.DictReader(f)
            if row.get("exclude", "").strip()
        }


EXCLUDED_SNIPPET_IDS = _load_excluded_snippet_ids()

WORKERS  = 6     # parallel notebook executions
TIMEOUT  = 120   # seconds per notebook
MAX_INSTALL_RETRIES = 1

# ── regex patterns ───────────────────────────────────────────────────────────
_PASS_RE  = re.compile(r"✅\s+L(\d)\s+\S+\s+(\S+?)(?::|$)")
_FAIL_RE  = re.compile(r"❌\s+L(\d)\s+\S+\s+(\S+?)(?::|$)")
_SKIP_RE  = re.compile(r"⚠️\s+L(\d)\s+\S+\s+(\S+?)(?::|$)")
_MODERR_RE = re.compile(r"ModuleNotFoundError: No module named '([^']+)'")
_PRIORITY  = {"fail": 3, "pass": 2, "skip": 1}

FIELDNAMES = [
    "condition", "notebook", "snippet_id", "func_name",
    "l1_raw", "l2_raw", "l3_raw",
    "l1_pass", "l2_pass", "l3_pass",
    "all_pass", "excluded", "notes",
]


def _collect_notebooks(condition: str, only_snippets: set[str] | None = None) -> list[Path]:
    notebooks = sorted(NOTEBOOK_ROOTS[condition].glob("*_test.ipynb"))
    if not only_snippets:
        return notebooks
    return [
        path for path in notebooks
        if path.name.removesuffix("_test.ipynb") in only_snippets
    ]


def _extract_module(error_text: str) -> str | None:
    m = _MODERR_RE.search(error_text)
    if not m:
        return None
    return m.group(1).split(".")[0]


def _pip_install(pkg: str) -> bool:
    r = subprocess.run(
        [*PIP, "install", pkg, "-q"],
        capture_output=True, text=True, timeout=120
    )
    return r.returncode == 0


def _execute_notebook(nb_path: Path, timeout: int = TIMEOUT) -> tuple[bool, str]:
    result = subprocess.run(
        [JUPYTER, "nbconvert", "--to", "notebook",
         "--execute", "--inplace",
         f"--ExecutePreprocessor.timeout={timeout}",
         "--ExecutePreprocessor.kernel_name=python3",
         str(nb_path)],
        capture_output=True, text=True, timeout=timeout + 30,
    )
    log = result.stdout + result.stderr
    return result.returncode == 0, log


_LOOSE_LINE_RE = re.compile(r"^([✅❌⚠️])\s+L(\d)\s+(.*)$")


def _parse_outputs(nb_path: Path, primary_fn: str | None = None) -> dict[str, dict]:
    """Parse ✅/❌/⚠️ from executed notebook → {func: {l1, l2, l3}}

    Most lines follow "<icon> L<n> <category> <func>: <rest>" and are matched
    by the strict regexes below. Some L3 edge-case labels instead read
    "<icon> L<n> <func> <free-text description>: <rest>" (e.g. "L3 edge
    foo empty input: ran without crash") — the strict regex requires the
    function-name token to be immediately followed by ':', which free text
    after it breaks. For those, fall back to a loose substring match against
    the notebook's own primary function name so genuine passes aren't lost
    as "unknown".
    """
    try:
        with open(nb_path) as f:
            nb = json.load(f)
    except Exception:
        return {}

    agg: dict[str, dict] = {}
    for cell in nb["cells"]:
        if cell.get("cell_type") != "code":
            continue
        for output in cell.get("outputs", []):
            text = ""
            ot = output.get("output_type", "")
            if ot == "stream":
                text = "".join(output.get("text", []))
            elif ot in ("error", "display_data", "execute_result"):
                text = "".join(output.get("traceback", [])) or str(output.get("data", ""))

            for line in text.splitlines():
                line_clean = re.sub(r"\x1b\[[0-9;]*m", "", line)  # strip ANSI
                # Bind any marker containing this notebook's full primary
                # function name to that pair before applying the generic
                # token-position regex. L3 labels are intentionally free-form
                # and may omit a category token (for example
                # "L3 <func> duplicate rows"), which the strict regex would
                # otherwise misparse as function "duplicate".
                if primary_fn:
                    lm = _LOOSE_LINE_RE.match(line_clean.strip())
                    primary_token = re.search(
                        rf"(?<![A-Za-z0-9_]){re.escape(primary_fn)}(?![A-Za-z0-9_])",
                        lm.group(3) if lm else "",
                    )
                    if lm and primary_token and f"before_{primary_fn}" not in lm.group(3):
                        layer = f"l{lm.group(2)}"
                        status = {"✅": "pass", "❌": "fail", "⚠️": "skip"}[lm.group(1)]
                        agg.setdefault(primary_fn, {})
                        existing = agg[primary_fn].get(layer)
                        if existing is None or _PRIORITY.get(status, 0) > _PRIORITY.get(existing, 0):
                            agg[primary_fn][layer] = status
                        continue
                matched = False
                for pat, status in [(_PASS_RE, "pass"), (_FAIL_RE, "fail"), (_SKIP_RE, "skip")]:
                    m = pat.search(line_clean)
                    if m:
                        matched = True
                        layer = f"l{m.group(1)}"
                        raw_fn = m.group(2).rstrip(":")
                        if raw_fn.startswith("before_"):
                            break
                        fn = raw_fn
                        fn = re.sub(r"^(?:gen|generated|before)_", "", fn)
                        agg.setdefault(fn, {})
                        existing = agg[fn].get(layer)
                        if existing is None or _PRIORITY.get(status, 0) > _PRIORITY.get(existing, 0):
                            agg[fn][layer] = status
                        break
                if not matched and primary_fn:
                    lm = _LOOSE_LINE_RE.match(line_clean.strip())
                    if lm and f"before_{primary_fn}" not in lm.group(3) and primary_fn in lm.group(3):
                        layer = f"l{lm.group(2)}"
                        status = {"✅": "pass", "❌": "fail", "⚠️": "skip"}[lm.group(1)]
                        agg.setdefault(primary_fn, {})
                        existing = agg[primary_fn].get(layer)
                        if existing is None or _PRIORITY.get(status, 0) > _PRIORITY.get(existing, 0):
                            agg[primary_fn][layer] = status
    return agg


def _snippet_id(condition: str, nb_path: Path, func_name: str) -> str:
    """Derive snippet_id from notebook path + func_name."""
    stem = nb_path.name
    if stem.endswith("_test.ipynb"):
        stem = stem[: -len("_test.ipynb")]

    # Extract sha8 prefix from notebook filename (first 8 hex chars if present)
    sha8_m = re.match(r"([0-9a-f]{8})_", stem)
    sha8 = sha8_m.group(1) if sha8_m else None

    if sha8 and not re.match(r"[0-9a-f]{8}_", func_name):
        return f"{sha8}_{func_name}"
    return func_name


def _make_row(condition, nb_path, fn, res, notes="") -> dict:
    l1 = res.get("l1", "unknown")
    l2 = res.get("l2", "unknown")
    l3 = res.get("l3", "unknown")
    p1 = 1 if l1 == "pass" else 0
    p2 = 1 if l2 == "pass" else (0 if l2 == "fail" else "")
    p3 = 1 if l3 == "pass" else (0 if l3 == "fail" else "")
    all_p = 1 if (l1 == "pass" and l2 in ("pass", "skip", "unknown")
                  and l3 in ("pass", "skip", "unknown")) else 0
    sid = _snippet_id(condition, nb_path, fn)
    return {
        "condition": condition,
        "notebook": nb_path.name,
        "snippet_id": sid,
        "func_name": fn,
        "l1_raw": l1, "l2_raw": l2, "l3_raw": l3,
        "l1_pass": p1, "l2_pass": p2, "l3_pass": p3,
        "all_pass": all_p,
        "excluded": 1 if sid in EXCLUDED_SNIPPET_IDS else 0,
        "notes": notes,
    }


def _process_notebook(args) -> list[dict]:
    condition, nb_path, execute = args
    notes = ""
    installed = []

    # --- execute (with one auto-install retry on ModuleNotFoundError) --------
    if execute:
        for attempt in range(MAX_INSTALL_RETRIES + 1):
            ok, log = _execute_notebook(nb_path)
            if ok:
                break
            pkg = _extract_module(log)
            if pkg and attempt < MAX_INSTALL_RETRIES:
                if _pip_install(pkg):
                    installed.append(pkg)
                    continue
            notes = "nbconvert_failed"
            break
        else:
            ok = True

    if installed:
        notes = f"auto_installed={installed}"

    # --- derive primary snippet_id from notebook filename --------------------
    stem = nb_path.name
    if stem.endswith("_test.ipynb"):
        stem = stem[: -len("_test.ipynb")]
    primary_sid = stem  # e.g. "05afd878_evaluate_coassembly_edges"

    # Report only the PRIMARY pair named by the notebook for every condition.
    # Multi-function wrapper cells must not inflate the 238-pair denominator.
    # derive the func_name that should appear in the primary snippet
    sha8_m = re.match(r"([0-9a-f]{8})_(.+)$", primary_sid)
    primary_fn = sha8_m.group(2) if sha8_m else primary_sid

    # --- parse outputs -------------------------------------------------------
    agg = _parse_outputs(nb_path, primary_fn)

    res = agg.get(primary_fn, {})
    excluded = 1 if primary_sid in EXCLUDED_SNIPPET_IDS else 0
    if not res and not agg:
        # notebook crashed with no output
        return [{
            "condition": condition,
            "notebook": nb_path.name,
            "snippet_id": primary_sid,
            "func_name": primary_fn,
            "l1_raw": "error", "l2_raw": "error", "l3_raw": "error",
            "l1_pass": 0, "l2_pass": 0, "l3_pass": 0,
            "all_pass": 0,
            "excluded": excluded,
            "notes": notes or "no_output_parsed",
        }]
    if not res:
        # notebook ran but produced no output for primary function
        return [{
            "condition": condition,
            "notebook": nb_path.name,
            "snippet_id": primary_sid,
            "func_name": primary_fn,
            "l1_raw": "unknown", "l2_raw": "unknown", "l3_raw": "unknown",
            "l1_pass": 0, "l2_pass": "", "l3_pass": "",
            "all_pass": 0,
            "excluded": excluded,
            "notes": notes or "no_result_for_primary_fn",
        }]
    return [_make_row(condition, nb_path, primary_fn, res, notes)]

# ── main ────────────────────────────────────────────────────────────────────

def run_condition(
    condition: str,
    all_rows: list,
    execute: bool = True,
    only_snippets: set[str] | None = None,
    output_dir: Path | None = None,
):
    nbs = _collect_notebooks(condition, only_snippets)
    total = len(nbs)
    print(f"\n{'='*64}")
    print(f"  {condition.upper()}  ({total} notebooks)")
    print(f"{'='*64}")

    rows: list[dict] = []
    done = 0
    t0 = time.time()

    with ThreadPoolExecutor(max_workers=WORKERS) as exe:
        futures = {
            exe.submit(_process_notebook, (condition, nb, execute)): nb
            for nb in nbs
        }
        for fut in as_completed(futures):
            nb = futures[fut]
            try:
                result_rows = fut.result()
                rows.extend(result_rows)
            except Exception as e:
                sid = nb.stem[: -len("_test")] if nb.stem.endswith("_test") else nb.stem
                rows.append({
                    "condition": condition, "notebook": nb.name,
                    "snippet_id": sid, "func_name": "exception",
                    "l1_raw": "error", "l2_raw": "error", "l3_raw": "error",
                    "l1_pass": 0, "l2_pass": 0, "l3_pass": 0,
                    "all_pass": 0,
                    "excluded": 1 if sid in EXCLUDED_SNIPPET_IDS else 0,
                    "notes": str(e)[:120],
                })
            done += 1
            if done % 20 == 0 or done == total:
                l1ok = sum(1 for r in rows if r["l1_raw"] == "pass")
                elapsed = time.time() - t0
                print(f"  [{done}/{total}] elapsed={elapsed:.0f}s  L1_pass_so_far={l1ok}")

    all_rows.extend(rows)

    # per-condition summary (excluded snippets are still run/scored above but
    # dropped from the aggregate rates — they're flagged unsuitable in the
    # gold-label review, not a reflection of this condition's generated code)
    scored = [r for r in rows if not r["excluded"]]
    n_snippets = len(scored)
    n_excluded = len(rows) - n_snippets
    l1_p = sum(1 for r in scored if r["l1_raw"] == "pass")
    l2_p = sum(1 for r in scored if r["l2_raw"] == "pass")
    l3_p = sum(1 for r in scored if r["l3_raw"] == "pass")
    all_p = sum(1 for r in scored if r["all_pass"] == 1)
    print(f"\n  Snippets={n_snippets} (excluded={n_excluded})  L1={l1_p}  L2={l2_p}  L3={l3_p}  all-pass={all_p}")
    print(f"  Rates: L1={l1_p/n_snippets:.1%}  all-pass={all_p/n_snippets:.1%}" if n_snippets else "")

    # save per-condition CSV
    output_dir = output_dir or ROOT / "shared/results/reproduced"
    output_dir.mkdir(parents=True, exist_ok=True)
    out = output_dir / f"{condition}_test_results_v3.csv"
    with open(out, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(sorted(rows, key=lambda r: r["snippet_id"]))
    print(f"  Saved → {out}")
    return rows


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--parse-only", action="store_true")
    parser.add_argument("--only", default="")
    parser.add_argument(
        "--condition",
        choices=("all", "baseline", "exp1", "exp2", "exp3"),
        default="all",
    )
    parser.add_argument(
        "--workspace-root",
        type=Path,
        help="Isolated workspace containing notebooks/{baseline,exp1,exp2,exp3}.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        help="Directory for per-condition and combined result CSV files.",
    )
    args = parser.parse_args()

    parse_only = args.parse_only
    only_arg = args.only
    only_snippets = (
        {sid for sid in only_arg.split(",") if sid}
        if only_arg else None
    )
    output_dir = (args.output_dir or ROOT / "shared/results/reproduced").resolve()
    if args.workspace_root:
        notebook_root = args.workspace_root.resolve() / "notebooks"
        for condition in NOTEBOOK_ROOTS:
            NOTEBOOK_ROOTS[condition] = notebook_root / condition
            if not NOTEBOOK_ROOTS[condition].exists():
                print(f"ERROR: notebook directory not found: {NOTEBOOK_ROOTS[condition]}")
                sys.exit(1)
    if not parse_only and not Path(JUPYTER).exists():
        print(f"ERROR: jupyter not found at {JUPYTER}")
        sys.exit(1)

    conditions = (
        ["baseline", "exp1", "exp2", "exp3"]
        if args.condition == "all"
        else [args.condition]
    )
    action = "Parsing existing outputs for" if parse_only else "Running"
    print(f"{action} conditions: {', '.join(conditions)}")
    print(f"Workers={WORKERS}, Timeout={TIMEOUT}s per notebook")

    all_rows: list[dict] = []

    for cond in conditions:
        run_condition(
            cond,
            all_rows,
            execute=not parse_only,
            only_snippets=only_snippets,
            output_dir=output_dir,
        )

    # master CSV
    master_out = output_dir / "all_conditions_test_results_v3.csv"
    with open(master_out, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(sorted(all_rows, key=lambda r: (r["condition"], r["snippet_id"])))
    print(f"\nMaster CSV → {master_out}")

    # ── final summary table ──────────────────────────────────────────────────
    print("\n" + "="*64)
    print("  FINAL SUMMARY")
    print("="*64)
    print(f"{'Condition':<12} {'Snippets':>8} {'L1%':>8} {'L2%':>8} {'L3%':>8} {'AllPass%':>9}")
    print("-"*64)
    for cond in conditions:
        rows = [r for r in all_rows if r["condition"] == cond and not r["excluded"]]
        n = len(rows)
        if n == 0:
            print(f"{cond:<12} {'0':>8}")
            continue
        l1p = sum(1 for r in rows if r["l1_raw"] == "pass")
        l2p = sum(1 for r in rows if r["l2_raw"] == "pass")
        l3p = sum(1 for r in rows if r["l3_raw"] == "pass")
        alp = sum(1 for r in rows if r["all_pass"] == 1)
        print(f"{cond:<12} {n:>8} {l1p/n:>8.1%} {l2p/n:>8.1%} {l3p/n:>8.1%} {alp/n:>9.1%}")
    print("="*64)
    print("\nDone.")


if __name__ == "__main__":
    main()
