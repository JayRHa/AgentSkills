#!/usr/bin/env python3
"""Validate Mermaid diagram source for common errors.

Performs fast static checks (no dependencies) and, if the Mermaid CLI
(`mmdc`) is installed, attempts a real render to catch deep syntax errors.

Usage:
    python3 validate_mermaid.py FILE [FILE ...]
    python3 validate_mermaid.py diagram.mmd
    cat diagram.mmd | python3 validate_mermaid.py -      # read stdin
    python3 validate_mermaid.py --no-render diagram.mmd  # skip mmdc render

Exit code 0 if all files pass static checks, 1 otherwise.
The file may be a raw .mmd file or Markdown containing ```mermaid fences;
fenced blocks are extracted and each is checked independently.
"""
import argparse
import re
import shutil
import subprocess
import sys
import tempfile
import os

KNOWN_HEADERS = (
    "flowchart", "graph", "sequenceDiagram", "erDiagram", "classDiagram",
    "stateDiagram-v2", "stateDiagram", "gantt", "journey", "gitGraph",
    "pie", "quadrantChart", "mindmap", "timeline", "C4Context",
    "C4Container", "C4Component", "C4Dynamic", "architecture-beta",
    "requirementDiagram", "sankey-beta", "xychart-beta", "block-beta",
)

FLOW_RESERVED = {"end", "subgraph", "class", "click", "style", "linkStyle"}


class Issue:
    def __init__(self, level, line, msg):
        self.level = level  # "error" or "warn"
        self.line = line
        self.msg = msg

    def __str__(self):
        loc = f"L{self.line}: " if self.line else ""
        return f"  [{self.level.upper()}] {loc}{self.msg}"


def extract_blocks(text):
    """Return list of (label, code). Markdown fences become separate blocks."""
    fence = re.compile(r"```mermaid\s*\n(.*?)```", re.DOTALL | re.IGNORECASE)
    matches = fence.findall(text)
    if matches:
        return [(f"mermaid block #{i + 1}", m) for i, m in enumerate(matches)]
    return [("diagram", text)]


def code_lines(code):
    """Lines with comments and blanks stripped, keeping original numbers."""
    out = []
    for i, raw in enumerate(code.splitlines(), 1):
        line = raw
        if "%%" in line and not line.strip().startswith("%%{"):
            line = line.split("%%", 1)[0]
        out.append((i, line))
    return out


def header_of(lines):
    for num, line in lines:
        s = line.strip()
        if not s or s.startswith("%%"):
            continue
        return num, s
    return None, None


def check_balanced(code):
    """Check bracket/paren/quote balance across the whole block."""
    issues = []
    pairs = {")": "(", "]": "[", "}": "{"}
    opens = set(pairs.values())
    in_str = False
    stack = []
    line_no = 1
    for ch in code:
        if ch == "\n":
            line_no += 1
            continue
        if ch == '"':
            in_str = not in_str
            continue
        if in_str:
            continue
        if ch in opens:
            stack.append((ch, line_no))
        elif ch in pairs:
            if not stack or stack[-1][0] != pairs[ch]:
                issues.append(Issue("error", line_no,
                                    f"unbalanced '{ch}' (no matching '{pairs[ch]}')"))
            else:
                stack.pop()
    for ch, ln in stack:
        issues.append(Issue("error", ln, f"unclosed '{ch}'"))
    if in_str:
        issues.append(Issue("error", None, 'unclosed double-quote (")'))
    return issues


def check_flowchart(lines):
    issues = []
    node_def = re.compile(r"(?:^|[\s&])([A-Za-z0-9_]+)\s*[\[({]")
    for num, line in lines:
        for m in node_def.finditer(line):
            nid = m.group(1)
            if nid in FLOW_RESERVED:
                issues.append(Issue(
                    "error", num,
                    f"'{nid}' is a reserved word used as a node id; "
                    f"rename (e.g. capitalize) or quote it"))
        if "->>" in line or "-->>" in line:
            issues.append(Issue(
                "warn", num,
                "sequence-style arrow ('->>') in a flowchart; "
                "use '-->' instead"))
    return issues


def check_sequence(lines):
    issues = []
    for num, line in lines:
        s = line.strip()
        if not s or s.startswith("sequenceDiagram"):
            continue
        if re.search(r"-->(?!>)", s) and "->>" not in s and "-->>" not in s:
            if ":" not in s:
                issues.append(Issue(
                    "warn", num,
                    "flowchart-style '-->' without a ': message' in a "
                    "sequence diagram; sequence messages need a colon"))
    return issues


def static_check(label, code):
    issues = []
    lines = code_lines(code)
    hnum, header = header_of(lines)
    if header is None:
        issues.append(Issue("error", None, "empty diagram (no content)"))
        return issues
    first_word = re.split(r"[\s]", header)[0]
    matched = header.startswith(KNOWN_HEADERS) or first_word in KNOWN_HEADERS
    if not matched:
        issues.append(Issue(
            "error", hnum,
            f"first line '{header[:40]}' is not a recognized Mermaid "
            f"header keyword"))
    issues += check_balanced(code)
    if header.startswith(("flowchart", "graph")):
        issues += check_flowchart(lines)
    elif header.startswith("sequenceDiagram"):
        issues += check_sequence(lines)
    elif header.startswith("stateDiagram") and not header.startswith("stateDiagram-v2"):
        issues.append(Issue(
            "warn", hnum,
            "use 'stateDiagram-v2' instead of 'stateDiagram' for better "
            "layout and features"))
    return issues


def render_check(code):
    """Try a real render with mmdc. Returns (ok, message) or (None, reason)."""
    mmdc = shutil.which("mmdc")
    if not mmdc:
        return None, "mmdc not installed (skipping real render)"
    with tempfile.TemporaryDirectory() as d:
        src = os.path.join(d, "in.mmd")
        out = os.path.join(d, "out.svg")
        with open(src, "w") as f:
            f.write(code)
        try:
            r = subprocess.run([mmdc, "-i", src, "-o", out],
                               capture_output=True, text=True, timeout=60)
        except subprocess.TimeoutExpired:
            return False, "mmdc render timed out"
        if r.returncode == 0 and os.path.exists(out):
            return True, "mmdc render OK"
        return False, (r.stderr or r.stdout or "mmdc failed").strip()


def main():
    ap = argparse.ArgumentParser(description="Validate Mermaid diagrams.")
    ap.add_argument("files", nargs="+", help="file(s) or '-' for stdin")
    ap.add_argument("--no-render", action="store_true",
                    help="skip the mmdc render check")
    args = ap.parse_args()

    total_errors = 0
    for path in args.files:
        if path == "-":
            text = sys.stdin.read()
            display = "<stdin>"
        else:
            try:
                with open(path) as f:
                    text = f.read()
            except OSError as e:
                print(f"{path}: cannot read ({e})")
                total_errors += 1
                continue
            display = path
        blocks = extract_blocks(text)
        for label, code in blocks:
            issues = static_check(label, code)
            errors = [i for i in issues if i.level == "error"]
            warns = [i for i in issues if i.level == "warn"]
            status = "FAIL" if errors else ("WARN" if warns else "PASS")
            print(f"{display} [{label}]: {status}")
            for i in issues:
                print(i)
            if not errors and not args.no_render:
                ok, msg = render_check(code)
                if ok is True:
                    print(f"  [INFO] {msg}")
                elif ok is False:
                    print(f"  [ERROR] {msg}")
                    errors.append(True)
                else:
                    print(f"  [INFO] {msg}")
            total_errors += len(errors)

    if total_errors:
        print(f"\n{total_errors} error(s) found.")
        return 1
    print("\nAll checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
