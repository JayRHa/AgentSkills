#!/usr/bin/env python3
"""Lightweight first-pass scanner for hardcoded secrets and dangerous calls.

This is a TRIAGE aid, not a proof of vulnerability — review every hit by hand.
Pure standard library; scans files or directories.

Usage:
    python3 secret_scan.py path/to/file.py
    python3 secret_scan.py src/            # recurse a directory
    python3 secret_scan.py --diff          # scan `git diff` (added lines only)
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

# (label, compiled regex, severity)
PATTERNS = [
    ("AWS access key id", re.compile(r"AKIA[0-9A-Z]{16}"), "Critical"),
    ("Private key block", re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----"), "Critical"),
    ("Generic API key/token assignment", re.compile(r"(?i)(api[_-]?key|secret|token|passwd|password)\s*[:=]\s*['\"][^'\"]{8,}['\"]"), "High"),
    ("Slack token", re.compile(r"xox[baprs]-[0-9A-Za-z-]{10,}"), "High"),
    ("Bearer token literal", re.compile(r"(?i)bearer\s+[A-Za-z0-9._-]{20,}"), "High"),
    ("SQL string-building", re.compile(r"(?i)(select|insert|update|delete)\b.*['\"]\s*\+\s*\w|f['\"](?i)(select|insert|update|delete)\b"), "High"),
    ("Shell injection risk (shell=True)", re.compile(r"shell\s*=\s*True"), "High"),
    ("eval/exec on data", re.compile(r"\b(eval|exec)\s*\("), "Medium"),
    ("Unsafe deserialization", re.compile(r"\b(pickle\.loads|yaml\.load\s*\((?!.*Loader)|marshal\.loads)"), "High"),
    ("Weak hash", re.compile(r"(?i)\b(md5|sha1)\s*\("), "Medium"),
    ("Insecure random for secrets", re.compile(r"(?i)random\.(random|randint|choice)\b"), "Low"),
]

SKIP_DIRS = {".git", "node_modules", "venv", ".venv", "__pycache__", "dist", "build"}
TEXT_SUFFIXES = {".py", ".js", ".ts", ".tsx", ".jsx", ".go", ".rb", ".php", ".java",
                 ".cs", ".sh", ".yml", ".yaml", ".env", ".cfg", ".ini", ".tf", ".sql", ".txt", ".json"}


def scan_text(label_lines, findings):
    for path, lineno, line in label_lines:
        for label, rx, sev in PATTERNS:
            if rx.search(line):
                findings.append((sev, path, lineno, label, line.strip()[:120]))


def iter_file(path: Path):
    try:
        for i, line in enumerate(path.read_text(encoding="utf-8", errors="ignore").splitlines(), 1):
            yield (str(path), i, line)
    except OSError:
        return


def collect_paths(target: Path):
    if target.is_file():
        yield target
        return
    for p in target.rglob("*"):
        if p.is_file() and p.suffix in TEXT_SUFFIXES and not any(d in p.parts for d in SKIP_DIRS):
            yield p


def scan_diff(findings):
    out = subprocess.run(["git", "diff", "--unified=0"], capture_output=True, text=True).stdout
    cur = "<diff>"
    lineno = 0
    for line in out.splitlines():
        if line.startswith("+++ b/"):
            cur = line[6:]
        elif line.startswith("@@"):
            m = re.search(r"\+(\d+)", line)
            lineno = int(m.group(1)) if m else 0
        elif line.startswith("+") and not line.startswith("+++"):
            scan_text([(cur, lineno, line[1:])], findings)
            lineno += 1


SEV_ORDER = {"Critical": 0, "High": 1, "Medium": 2, "Low": 3}


def main() -> int:
    ap = argparse.ArgumentParser(description="Triage scan for secrets and dangerous calls.")
    ap.add_argument("path", nargs="?", default=".", help="file or directory to scan")
    ap.add_argument("--diff", action="store_true", help="scan added lines of `git diff`")
    args = ap.parse_args()

    findings: list[tuple] = []
    if args.diff:
        scan_diff(findings)
    else:
        for fp in collect_paths(Path(args.path)):
            scan_text(list(iter_file(fp)), findings)

    findings.sort(key=lambda f: (SEV_ORDER.get(f[0], 9), f[1], f[2]))
    if not findings:
        print("No obvious secrets or dangerous calls found. (Manual review still required.)")
        return 0

    print(f"{len(findings)} potential issue(s) — TRIAGE ONLY, verify each:\n")
    for sev, path, lineno, label, snippet in findings:
        print(f"[{sev}] {label}\n    {path}:{lineno}\n    {snippet}\n")
    # exit non-zero if anything High+ so it can gate CI
    return 1 if any(f[0] in ("Critical", "High") for f in findings) else 0


if __name__ == "__main__":
    raise SystemExit(main())
