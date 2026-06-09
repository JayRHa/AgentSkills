#!/usr/bin/env python3
"""Scan files or a directory tree for likely hardcoded secrets.

Stdlib-only heuristic scanner for quick local checks and CI gating. It is NOT a
replacement for gitleaks/trufflehog history scanning, but catches the common
cases in the working tree before they are committed.

Usage:
    python scan_secrets.py [PATH ...] [--ext .py,.js,.env] [--quiet]
    python scan_secrets.py .                # scan current dir tree
    python scan_secrets.py app.py config.yml

Exit code 0 = clean, 1 = findings (suitable for pre-commit / CI gates).
Matches are redacted: only the first and last 4 chars are shown.
"""
import argparse
import os
import re
import sys

# (name, compiled regex). Patterns favor precision to limit false positives.
PATTERNS = [
    ("AWS Access Key ID", re.compile(r"\b(?:AKIA|ASIA)[0-9A-Z]{16}\b")),
    ("AWS Secret Access Key", re.compile(r"(?i)aws.{0,20}?(?:secret|key).{0,3}['\"]([0-9a-zA-Z/+]{40})['\"]")),
    ("GitHub Token", re.compile(r"\bgh[pousr]_[0-9A-Za-z]{36,}\b")),
    ("Slack Token", re.compile(r"\bxox[baprs]-[0-9A-Za-z-]{10,}\b")),
    ("Stripe Live Key", re.compile(r"\b(?:sk|rk)_live_[0-9a-zA-Z]{16,}\b")),
    ("Google API Key", re.compile(r"\bAIza[0-9A-Za-z_-]{35}\b")),
    ("OpenAI Key", re.compile(r"\bsk-[A-Za-z0-9]{20,}\b")),
    ("Private Key Block", re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH |DSA |PGP )?PRIVATE KEY-----")),
    ("JWT", re.compile(r"\beyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\b")),
    ("Generic Assigned Secret", re.compile(
        r"(?i)(?:password|passwd|pwd|secret|api[_-]?key|token|access[_-]?key)"
        r"\s*[:=]\s*['\"]([^'\"]{8,})['\"]")),
    ("Slack Webhook", re.compile(r"https://hooks\.slack\.com/services/[A-Za-z0-9/]+")),
    ("Connection String w/ Password", re.compile(r"(?i)(?:postgres|mysql|mongodb|redis|amqp)://[^:\s]+:[^@\s]+@")),
]

SKIP_DIRS = {".git", "node_modules", ".venv", "venv", "__pycache__", "dist", "build", ".terraform"}
DEFAULT_BINARY_HINT = b"\x00"

# crude placeholder/sample detector to cut noise
PLACEHOLDER = re.compile(r"(?i)(your[_-]?|example|placeholder|changeme|dummy|xxxx+|<.*>|\.\.\.|test123|password123|s3cr3t)")


def redact(value):
    value = value.strip()
    if len(value) <= 8:
        return "*" * len(value)
    return f"{value[:4]}...{value[-4:]} (len={len(value)})"


def iter_files(paths, exts):
    for p in paths:
        if os.path.isfile(p):
            yield p
            continue
        for root, dirs, files in os.walk(p):
            dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
            for f in files:
                if exts and not any(f.endswith(e) for e in exts):
                    # always include .env-style files regardless of ext filter
                    if not f.startswith(".env") and "credential" not in f.lower():
                        continue
                yield os.path.join(root, f)


def scan_file(path):
    findings = []
    try:
        with open(path, "rb") as fh:
            raw = fh.read(2_000_000)  # cap at 2MB
        if DEFAULT_BINARY_HINT in raw:
            return findings  # skip binaries
        text = raw.decode("utf-8", errors="replace")
    except (OSError, ValueError):
        return findings
    for lineno, line in enumerate(text.splitlines(), 1):
        if len(line) > 4000:
            continue
        for name, rx in PATTERNS:
            m = rx.search(line)
            if not m:
                continue
            captured = m.group(1) if m.groups() else m.group(0)
            if PLACEHOLDER.search(captured):
                continue
            findings.append((path, lineno, name, redact(captured)))
    return findings


def main(argv=None):
    parser = argparse.ArgumentParser(description="Heuristic hardcoded-secret scanner (stdlib only).")
    parser.add_argument("paths", nargs="*", default=["."], help="Files or directories to scan (default: .)")
    parser.add_argument("--ext", default="", help="Comma-separated extension allowlist, e.g. .py,.js,.yml")
    parser.add_argument("--quiet", action="store_true", help="Only print findings, suppress the clean message")
    args = parser.parse_args(argv)

    paths = args.paths or ["."]
    exts = [e if e.startswith(".") else "." + e for e in args.ext.split(",") if e] if args.ext else []

    all_findings = []
    for fpath in iter_files(paths, exts):
        all_findings.extend(scan_file(fpath))

    if not all_findings:
        if not args.quiet:
            print("OK: no likely secrets found.")
        return 0

    print(f"FOUND {len(all_findings)} potential secret(s):\n")
    for path, lineno, name, red in all_findings:
        print(f"  {path}:{lineno}  [{name}]  {red}")
    print("\nReview each finding. Rotate any real exposed secret BEFORE removing it.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
