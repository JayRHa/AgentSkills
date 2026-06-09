#!/usr/bin/env python3
"""Validate a GitHub Actions workflow file for common reliability and security issues.

Checks performed (heuristic, no external deps):
  - top-level `permissions:` is declared
  - top-level `concurrency:` is declared
  - every job sets `timeout-minutes`
  - third-party actions (`uses:`) are pinned to a commit SHA (warn on floating tags)
  - no secret is echoed in a `run:` step
  - `actions/checkout` appears before build/test run steps
  - matrix test jobs consider `fail-fast: false`

Usage:
    python3 validate_workflow.py .github/workflows/ci.yml [more.yml ...]
    python3 validate_workflow.py --strict ci.yml   # exit non-zero on warnings too

Exit codes: 0 = clean (or warnings only without --strict), 1 = errors found,
            2 = bad invocation / unreadable file.
"""
import argparse
import re
import sys

SHA_RE = re.compile(r"@[0-9a-fA-F]{40}\b")
FLOATING_RE = re.compile(r"@(v?\d+(\.\d+)*|main|master|latest|HEAD)\b")
FIRST_PARTY_RE = re.compile(r"uses:\s*(actions|github|docker|aws-actions|azure|google-github-actions)/")
ECHO_SECRET_RE = re.compile(r"(echo|printf|cat|print)\b.*\$\{\{\s*secrets\.", re.IGNORECASE)


def indent_of(line):
    return len(line) - len(line.lstrip(" "))


def analyze(path):
    errors, warnings = [], []
    try:
        with open(path, "r", encoding="utf-8") as fh:
            lines = fh.readlines()
    except OSError as exc:
        return [f"cannot read {path}: {exc}"], []

    text = "".join(lines)

    # Top-level keys are at indent 0.
    top_level = [l.split(":", 1)[0].strip() for l in lines
                 if l.strip() and indent_of(l) == 0 and ":" in l]

    if "permissions" not in top_level:
        errors.append("missing top-level `permissions:` (declare least privilege, e.g. `contents: read`)")
    if "concurrency" not in top_level:
        warnings.append("missing top-level `concurrency:` (recommended to cancel superseded runs)")

    # Per-line checks.
    saw_checkout = False
    saw_build_run_before_checkout = False
    for i, line in enumerate(lines, start=1):
        stripped = line.strip()

        if "actions/checkout@" in stripped:
            saw_checkout = True

        if stripped.startswith("- run:") or stripped == "run: |" or stripped.startswith("run:"):
            body = stripped
            if not saw_checkout and re.search(r"(npm|yarn|pnpm|pip|go |mvn|gradle|make|cargo|dotnet) ", body):
                saw_build_run_before_checkout = True
            if ECHO_SECRET_RE.search(body):
                errors.append(f"line {i}: secret appears to be echoed/printed in a run step")

        if ECHO_SECRET_RE.search(line):
            # also catch multi-token run blocks
            errors.append(f"line {i}: secret appears to be echoed/printed")

        m = re.search(r"uses:\s*([^\s#]+)", stripped)
        if m:
            ref = m.group(1)
            local = ref.startswith("./") or ref.startswith(".\\")
            if not local and "@" in ref:
                if not SHA_RE.search(ref):
                    if FIRST_PARTY_RE.search(stripped):
                        warnings.append(f"line {i}: `{ref}` uses a floating tag; SHA pin is safest (first-party tag tolerated)")
                    else:
                        errors.append(f"line {i}: third-party action `{ref}` is not pinned to a commit SHA")

    # Dedupe echoed-secret double hits.
    errors = list(dict.fromkeys(errors))

    if saw_build_run_before_checkout:
        warnings.append("a build/test `run:` step appears before any `actions/checkout` — repo may not be checked out")

    # Job-level timeout check (heuristic: count `jobs:` block job ids vs timeout-minutes).
    if "jobs:" in text:
        job_ids = re.findall(r"^  ([A-Za-z0-9_-]+):\s*$", text, re.MULTILINE)
        timeouts = len(re.findall(r"timeout-minutes:", text))
        if job_ids and timeouts < len(job_ids):
            warnings.append(f"{len(job_ids)} job(s) detected but only {timeouts} `timeout-minutes:` — set one per job")

    if "matrix:" in text and "fail-fast:" not in text:
        warnings.append("matrix detected without `fail-fast:` — set `fail-fast: false` for test matrices")

    return errors, warnings


def main(argv=None):
    parser = argparse.ArgumentParser(description="Validate GitHub Actions workflow files.")
    parser.add_argument("files", nargs="+", help="workflow YAML file(s)")
    parser.add_argument("--strict", action="store_true", help="treat warnings as failures")
    args = parser.parse_args(argv)

    total_err = total_warn = 0
    for path in args.files:
        errors, warnings = analyze(path)
        print(f"\n=== {path} ===")
        if not errors and not warnings:
            print("  OK — no issues found")
        for e in errors:
            print(f"  ERROR: {e}")
        for w in warnings:
            print(f"  WARN:  {w}")
        total_err += len(errors)
        total_warn += len(warnings)

    print(f"\nSummary: {total_err} error(s), {total_warn} warning(s)")
    if total_err or (args.strict and total_warn):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
