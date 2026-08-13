"""
Experiment 1 (AST-guided) — v2 test notebook generation and execution.

For each of the 238 snippets:
  1. Read generated_py/{snippet_id}.py  (function body only)
  2. Find baseline test notebook (by funcname -> notebook index)
  3. Extract baseline notebook structure
  4. Assemble new gen cell: keep other gen functions, replace only this snippet's function
  5. Write test_notebooks_v2/{snippet_id}_test.ipynb
  6. Execute with nbconvert
  7. Parse results and write test_results_v2.csv
"""

import json
import re
import sys
import textwrap
import subprocess
import csv
import shutil
from pathlib import Path

# ── Paths ─────────────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parents[2]
GENERATED_PY_DIR = BASE_DIR / "exp1/results/generated_py"
OUTPUT_NB_DIR = BASE_DIR / "exp1/tests"
RESULTS_CSV = BASE_DIR / "exp1/results/test_results_reproduced.csv"
GENERATED_OUTPUTS_DIR = BASE_DIR / "baseline/tests"
PYTHON = sys.executable
JUPYTER = shutil.which("jupyter") or "jupyter"

OUTPUT_NB_DIR.mkdir(parents=True, exist_ok=True)

# ── Step 1: Build funcname → notebook index ───────────────────────────────────

def build_notebook_index():
    """Return dict: funcname -> list of (nb_path, raw_funcdef_name, num_gen_funcs, has_test_cells)"""
    nbs = list(GENERATED_OUTPUTS_DIR.rglob("*_test.ipynb"))
    nbs = [p for p in nbs if "legacy" not in str(p) and "edgecase" not in str(p)]

    func_to_nbs = {}
    for nb_path in nbs:
        try:
            nb = json.load(open(nb_path))
            full_text = "\n".join("".join(c["source"]) for c in nb["cells"])
            funcs = re.findall(r"def (gen_\w+|generated_\w+)\s*\(", full_text)
            for raw in funcs:
                if raw.startswith("gen_"):
                    funcname = raw[4:]
                else:
                    funcname = raw[10:]  # generated_
                # Check if this notebook has standard test cells for this funcname
                has_test = bool(re.search(
                    rf"[✅❌⚠️]\s+L\d\s+\w+\s+{re.escape(raw)}\b|"
                    rf"gen_{re.escape(funcname)}\s*\(",
                    full_text
                ))
                # More specific: check for standard L1 smoke markers
                has_standard_test = bool(re.search(
                    rf"L1 smoke {re.escape(raw)}|=== Tests: {re.escape(funcname)} ===",
                    full_text
                ))
                if funcname not in func_to_nbs:
                    func_to_nbs[funcname] = []
                func_to_nbs[funcname].append((nb_path, raw, len(funcs), has_standard_test))
        except Exception as e:
            print(f"  WARN: could not parse {nb_path}: {e}", file=sys.stderr)
    return func_to_nbs


def pick_best_notebook(candidates):
    """
    When multiple notebooks match, prefer:
    1. Notebooks with standard test cells for this funcname (=== Tests: funcname ===)
    2. gen_ prefix over generated_
    3. More gen functions (shared notebook)
    """
    if len(candidates) == 1:
        return candidates[0]
    # Prefer candidates with standard test cells
    standard_cands = [c for c in candidates if c[3]]
    if standard_cands:
        candidates = standard_cands
    # Prefer gen_ over generated_
    gen_cands = [c for c in candidates if c[1].startswith("gen_")]
    if gen_cands:
        candidates = gen_cands
    # Among those, prefer more gen functions
    candidates = sorted(candidates, key=lambda c: c[2], reverse=True)
    return candidates[0]


# ── Step 2: Extract gen cell and split per function ──────────────────────────

def find_gen_cell_index(nb, funcname):
    """Find the cell index containing def gen_{funcname} or def generated_{funcname}."""
    patterns = [f"def gen_{funcname}", f"def generated_{funcname}"]
    for i, cell in enumerate(nb["cells"]):
        src = "".join(cell["source"])
        if any(p in src for p in patterns):
            return i
    return None


def split_gen_cell_into_blocks(src):
    """
    Split the source of a gen cell into per-function blocks.
    Returns list of (raw_funcdef_name, block_text) tuples.
    block_text includes the def line and all subsequent indented lines.
    """
    # Find all def gen_... or def generated_... positions
    pattern = re.compile(r"^(def (?:gen_|generated_)\w+\s*\()", re.MULTILINE)
    lines = src.split("\n")

    # Find line indices where gen functions start
    func_starts = []
    for i, line in enumerate(lines):
        m = re.match(r"^def (gen_\w+|generated_\w+)\s*\(", line)
        if m:
            func_starts.append((i, m.group(1)))

    if not func_starts:
        return []

    blocks = []
    for idx, (start_line, raw_name) in enumerate(func_starts):
        end_line = func_starts[idx + 1][0] if idx + 1 < len(func_starts) else len(lines)
        block = "\n".join(lines[start_line:end_line]).rstrip()
        blocks.append((raw_name, block))

    return blocks


def extract_header_lines(src, func_starts_line_idx):
    """Extract lines before the first def gen_/generated_ function (imports, comments)."""
    lines = src.split("\n")
    header = []
    for line in lines[:func_starts_line_idx]:
        header.append(line)
    return "\n".join(header).strip()


def parse_baseline_function(block_src):
    """
    Parse a baseline gen function block.
    Returns:
        signature_line: the def line (e.g. 'def gen_foo(a, b=None):')
        default_arg_lines: lines that set up default args (e.g. 'if b is None: b = ...')
        body_lines: the main body (excluding default arg setup)
        return_line: the return statement (if any)
    """
    lines = block_src.split("\n")
    if not lines:
        return None, [], [], None

    # Collect multi-line signature
    sig_lines = []
    i = 0
    paren_depth = 0
    while i < len(lines):
        line = lines[i]
        sig_lines.append(line)
        paren_depth += line.count("(") - line.count(")")
        i += 1
        if paren_depth <= 0 and sig_lines:
            # Check if we have the closing colon
            if ":" in "".join(sig_lines):
                break

    signature_line = "\n".join(sig_lines)

    # Rest is the body
    body_lines = lines[i:]

    # Find default arg setup lines (if X is None: X = ...)
    # These are typically at the start of the body
    default_arg_lines = []
    main_body_start = 0
    j = 0
    while j < len(body_lines):
        stripped = body_lines[j].strip()
        # Check for default arg patterns
        is_default = (
            re.match(r"if \w+ is None", stripped) or
            stripped.startswith("if not ") and "is None" not in stripped and j == 0 and False
        )
        if is_default:
            # Collect the if block (simple single-liner or multi-line)
            default_arg_lines.append(body_lines[j])
            j += 1
            # Collect indented continuation
            while j < len(body_lines) and (body_lines[j].startswith("        ") or body_lines[j].strip() == ""):
                default_arg_lines.append(body_lines[j])
                j += 1
        else:
            break
    main_body_start = j

    main_body = body_lines[main_body_start:]

    # Find return line (last non-empty line)
    return_line = None
    for line in reversed(main_body):
        stripped = line.strip()
        if stripped.startswith("return "):
            return_line = stripped
            break

    return signature_line, default_arg_lines, main_body, return_line


# ── Step 3: Assemble new gen cell ────────────────────────────────────────────

IMPORT_DROP_PATTERNS = [
    re.compile(r"^import polars(\s|$)"),
    re.compile(r"^import pandas(\s|$)"),
    re.compile(r"^from polars import \*"),
    re.compile(r"^from pandas import \*"),
    re.compile(r"^from polars import (?!\*)\w"),  # from polars import specific -> drop
    re.compile(r"^from pandas import (?!\*)\w"),
    re.compile(r"^import polars as"),
    re.compile(r"^import pandas as"),
]


def should_drop_import(line):
    stripped = line.strip()
    return any(p.match(stripped) for p in IMPORT_DROP_PATTERNS)


def assemble_new_gen_function(signature_line, default_arg_lines, generated_body_raw, baseline_return_line, raw_name):
    """
    Assemble the new gen function source code.
    """
    # Normalize generated body indentation
    body = textwrap.dedent(generated_body_raw).strip()

    # Split body into lines
    body_lines = body.split("\n")

    # Separate module-level imports from the actual body
    module_imports = []
    actual_body_lines = []
    for line in body_lines:
        stripped = line.strip()
        if stripped.startswith("import ") or stripped.startswith("from "):
            if not should_drop_import(stripped):
                module_imports.append(stripped)
            # else skip polars/pandas imports
        else:
            actual_body_lines.append(line)

    # Check if generated body has a return statement
    has_return = any(l.strip().startswith("return ") for l in actual_body_lines)

    # Build function source
    parts = []

    # Module-level imports (before the def)
    if module_imports:
        parts.extend(module_imports)
        parts.append("")

    # Function definition
    parts.append(signature_line)

    # Default arg setup lines from baseline
    for line in default_arg_lines:
        parts.append(line)

    # Actual body (indented 4 spaces)
    # Remove leading/trailing blank lines from actual body
    while actual_body_lines and not actual_body_lines[0].strip():
        actual_body_lines.pop(0)
    while actual_body_lines and not actual_body_lines[-1].strip():
        actual_body_lines.pop()

    for line in actual_body_lines:
        if line.strip():
            parts.append("    " + line)
        else:
            parts.append("")

    # Add baseline return line if generated code has no return
    if not has_return and baseline_return_line:
        parts.append("    " + baseline_return_line)

    return "\n".join(parts)


def build_new_gen_cell(baseline_gen_src, funcname, generated_body_raw):
    """
    Replace only the specific funcname's function in the baseline gen cell.
    Keep all other gen functions as-is.
    Returns new cell source string.
    """
    # Split into header + function blocks
    lines = baseline_gen_src.split("\n")

    # Find the header (comment lines before first gen_ def)
    func_pattern = re.compile(r"^def (gen_\w+|generated_\w+)\s*\(")
    first_func_line = None
    for i, line in enumerate(lines):
        if func_pattern.match(line):
            first_func_line = i
            break

    header = "\n".join(lines[:first_func_line]).rstrip() if first_func_line else ""

    # Split remaining into function blocks
    blocks = split_gen_cell_into_blocks(baseline_gen_src)

    # Find the block for this funcname
    new_blocks = []
    for raw_name, block_src in blocks:
        if raw_name.startswith("gen_"):
            block_funcname = raw_name[4:]
        else:
            block_funcname = raw_name[10:]

        if block_funcname == funcname:
            # This is the function we need to replace
            sig_line, default_arg_lines, main_body, return_line = parse_baseline_function(block_src)
            new_func_src = assemble_new_gen_function(
                sig_line, default_arg_lines, generated_body_raw, return_line, raw_name
            )
            new_blocks.append(new_func_src)
        else:
            new_blocks.append(block_src)

    # Reassemble: new header + new blocks
    new_header = "# ── Generated wrappers (experiment-generated Polars) ─────────────────────────"
    parts = [new_header, ""]
    for block in new_blocks:
        parts.append(block)
        parts.append("")

    return "\n".join(parts).rstrip()


# ── Step 4: Write notebook ────────────────────────────────────────────────────

def make_cell(cell_type, source):
    """Create a notebook cell dict."""
    if cell_type == "code":
        return {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": source if isinstance(source, list) else [source],
        }
    else:
        return {
            "cell_type": "markdown",
            "metadata": {},
            "source": source if isinstance(source, list) else [source],
        }


def clear_cell(cell):
    """Clear outputs and execution_count from a cell."""
    cell = dict(cell)
    if cell.get("cell_type") == "code":
        cell["outputs"] = []
        cell["execution_count"] = None
    return cell


def assemble_notebook(baseline_nb, gen_cell_idx, new_gen_cell_src):
    """
    Create new notebook from baseline, replacing cell at gen_cell_idx with new gen cell.
    """
    import copy
    nb = copy.deepcopy(baseline_nb)

    # Replace the gen cell
    old_cell = nb["cells"][gen_cell_idx]
    new_cell = dict(old_cell)
    new_cell["source"] = new_gen_cell_src
    new_cell["outputs"] = []
    new_cell["execution_count"] = None
    nb["cells"][gen_cell_idx] = new_cell

    # Clear all cells
    nb["cells"] = [clear_cell(c) for c in nb["cells"]]

    return nb


# ── Step 5: Execute notebook ──────────────────────────────────────────────────

def execute_notebook(nb_path, timeout=120):
    """Execute notebook in-place. Returns (success, stderr_text)."""
    cmd = [
        JUPYTER, "nbconvert",
        "--to", "notebook",
        "--execute",
        "--inplace",
        f"--ExecutePreprocessor.timeout={timeout}",
        "--ExecutePreprocessor.kernel_name=python3",
        str(nb_path),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout + 30)
    return result.returncode == 0, result.stderr


# ── Step 6: Parse results ─────────────────────────────────────────────────────

PASS_PAT = re.compile(r"✅ L(\d)\s+\S+\s+(\S+):")
FAIL_PAT = re.compile(r"❌ L(\d)\s+\S+\s+(\S+):")
SKIP_PAT = re.compile(r"⚠️\s*L(\d)\s+\S+\s+(\S+):")


def parse_results_from_notebook(nb_path, funcname):
    """
    Parse L1/L2/L3 pass/fail/skip from executed notebook outputs.
    Returns dict with l1_pass, l2_pass, l3_pass, l1_raw, l2_raw, l3_raw.
    """
    try:
        nb = json.load(open(nb_path))
    except Exception:
        return None

    # Collect all output text
    all_output = []
    for cell in nb["cells"]:
        for out in cell.get("outputs", []):
            text = out.get("text", out.get("data", {}).get("text/plain", ""))
            if isinstance(text, list):
                text = "".join(text)
            all_output.append(text)

    full_output = "\n".join(all_output)

    # Find results for this funcname (strip gen_/generated_ prefix when matching)
    layer_results = {}  # layer -> list of statuses

    for line in full_output.split("\n"):
        for pat, status in [(PASS_PAT, "pass"), (FAIL_PAT, "fail"), (SKIP_PAT, "skip")]:
            m = pat.search(line)
            if m:
                layer = int(m.group(1))
                raw_fn = m.group(2)
                # Normalize funcname from output
                fn = raw_fn
                if fn.startswith("gen_"):
                    fn = fn[4:]
                elif fn.startswith("generated_"):
                    fn = fn[10:]

                if fn == funcname:
                    if layer not in layer_results:
                        layer_results[layer] = []
                    layer_results[layer].append(status)

    def aggregate(statuses):
        if not statuses:
            return "", "unknown"
        # Priority: fail > skip > pass
        if "fail" in statuses:
            return 0, "fail"
        if "skip" in statuses:
            return "", "skip"
        return 1, "pass"

    results = {}
    for layer in [1, 2, 3]:
        statuses = layer_results.get(layer, [])
        val, raw = aggregate(statuses)
        results[f"l{layer}_pass"] = val
        results[f"l{layer}_raw"] = raw

    return results


# ── Main ──────────────────────────────────────────────────────────────────────

def get_funcname(snippet_id):
    """Extract function name from snippet_id."""
    if re.match(r"^[0-9a-f]{8}_", snippet_id):
        return re.sub(r"^[0-9a-f]{8}_", "", snippet_id)
    return snippet_id


def main():
    print("Building notebook index...")
    func_to_nbs = build_notebook_index()
    print(f"Index built: {len(func_to_nbs)} unique functions across {128} notebooks")

    # Get all snippet IDs
    snippet_ids = sorted(p.stem for p in GENERATED_PY_DIR.glob("*.py"))
    print(f"Total snippets: {len(snippet_ids)}")

    results = []

    for i, snippet_id in enumerate(snippet_ids):
        funcname = get_funcname(snippet_id)
        nb_out_path = OUTPUT_NB_DIR / f"{snippet_id}_test.ipynb"

        row = {
            "snippet_id": snippet_id,
            "func_name": funcname,
            "l1_pass": "",
            "l2_pass": "",
            "l3_pass": "",
            "l1_raw": "unknown",
            "l2_raw": "unknown",
            "l3_raw": "unknown",
            "notebook": "",
            "notes": "",
        }

        # ── Step 1: Read generated body ────────────────────────────────────────
        py_file = GENERATED_PY_DIR / f"{snippet_id}.py"
        generated_body = py_file.read_text()

        # ── Step 2: Find baseline notebook ────────────────────────────────────
        candidates = func_to_nbs.get(funcname)
        if not candidates:
            row["notes"] = "no_test_notebook"
            results.append(row)
            if (i + 1) % 20 == 0:
                print(f"[{i+1}/{len(snippet_ids)}] {snippet_id}: no_test_notebook")
            continue

        nb_path, raw_name, num_funcs, _has_std = pick_best_notebook(candidates)
        row["notebook"] = nb_path.name

        try:
            # ── Step 3: Load baseline notebook ────────────────────────────────
            baseline_nb = json.load(open(nb_path))

            # Find the gen cell
            gen_cell_idx = find_gen_cell_index(baseline_nb, funcname)
            if gen_cell_idx is None:
                row["notes"] = "no_gen_cell_found"
                row["l1_raw"] = "error"
                results.append(row)
                continue

            baseline_gen_src = "".join(baseline_nb["cells"][gen_cell_idx]["source"])

            # ── Step 4: Build new gen cell ─────────────────────────────────────
            new_gen_src = build_new_gen_cell(baseline_gen_src, funcname, generated_body)

            # ── Step 5: Write notebook ─────────────────────────────────────────
            new_nb = assemble_notebook(baseline_nb, gen_cell_idx, new_gen_src)

            with open(nb_out_path, "w") as f:
                json.dump(new_nb, f, indent=1)

            # ── Step 6: Execute notebook ───────────────────────────────────────
            success, stderr = execute_notebook(nb_out_path)

            if not success:
                row["notes"] = "exec_error"
                row["l1_raw"] = "error"
                row["l2_raw"] = "error"
                row["l3_raw"] = "error"
                results.append(row)
                if (i + 1) % 20 == 0:
                    print(f"[{i+1}/{len(snippet_ids)}] {snippet_id}: exec_error")
                continue

            # ── Parse results ──────────────────────────────────────────────────
            parsed = parse_results_from_notebook(nb_out_path, funcname)
            if parsed:
                row.update(parsed)

        except subprocess.TimeoutExpired:
            row["notes"] = "exec_timeout"
            row["l1_raw"] = "error"
        except Exception as e:
            row["notes"] = f"error: {type(e).__name__}: {str(e)[:80]}"
            row["l1_raw"] = "error"

        results.append(row)

        if (i + 1) % 20 == 0:
            l1 = row["l1_raw"]
            l2 = row["l2_raw"]
            l3 = row["l3_raw"]
            print(f"[{i+1}/{len(snippet_ids)}] {snippet_id}: L1={l1} L2={l2} L3={l3}")

    # ── Write CSV ──────────────────────────────────────────────────────────────
    fieldnames = ["snippet_id", "func_name", "l1_pass", "l2_pass", "l3_pass",
                  "l1_raw", "l2_raw", "l3_raw", "notebook", "notes"]
    with open(RESULTS_CSV, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    # ── Summary ────────────────────────────────────────────────────────────────
    l1_pass = sum(1 for r in results if r["l1_pass"] == 1)
    l1_fail = sum(1 for r in results if r["l1_raw"] == "fail")
    l2_pass = sum(1 for r in results if r["l2_pass"] == 1)
    l2_fail = sum(1 for r in results if r["l2_raw"] == "fail")
    l3_pass = sum(1 for r in results if r["l3_pass"] == 1)
    l3_fail = sum(1 for r in results if r["l3_raw"] == "fail")
    errors = sum(1 for r in results if "error" in r["notes"])

    print("\n" + "="*60)
    print("FINAL RESULTS")
    print("="*60)
    print(f"Total snippets: {len(results)}")
    print(f"L1: pass={l1_pass}, fail={l1_fail}, other={len(results)-l1_pass-l1_fail}")
    print(f"L2: pass={l2_pass}, fail={l2_fail}, other={len(results)-l2_pass-l2_fail}")
    print(f"L3: pass={l3_pass}, fail={l3_fail}, other={len(results)-l3_pass-l3_fail}")
    print(f"Execution errors: {errors}")
    print(f"\nResults written to: {RESULTS_CSV}")


if __name__ == "__main__":
    main()
