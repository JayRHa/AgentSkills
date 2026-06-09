#!/usr/bin/env python3
"""okr_lint.py - Lint OKRs for common weaknesses.

Reads a simple OKR file (or stdin) and flags key results that look like tasks,
lack a number, lack a baseline/target, or look like vanity metrics. Pure stdlib.

INPUT FORMAT (plain text):
    O: <objective text>
    KR: <key result text>
    KR: <key result text>
    O: <next objective>
    KR: ...

Lines starting with 'O:' are objectives; 'KR:' are key results. Blank lines and
other lines are ignored. Indentation/whitespace is tolerated.

USAGE:
    python3 okr_lint.py path/to/okrs.txt
    cat okrs.txt | python3 okr_lint.py
    python3 okr_lint.py --demo        # run on a built-in sample

EXIT CODE: 0 if no errors (warnings allowed), 1 if any ERROR-level issue found.
"""
import argparse
import re
import sys

# Verbs that signal an output/task rather than a measurable outcome.
TASK_VERBS = {
    "launch", "ship", "build", "create", "write", "implement", "add",
    "develop", "design", "hire", "migrate", "set", "setup", "deploy",
    "release", "deliver", "complete", "finish", "run", "hold", "do",
    "organize", "plan", "draft", "refactor", "rebuild", "introduce",
}

# Metrics that are frequently vanity unless tied to value.
VANITY_TERMS = {
    "page views", "pageviews", "impressions", "signups", "sign-ups",
    "downloads", "followers", "likes", "clicks", "lines of code",
    "registrations", "hits", "traffic",
}

NUMBER_RE = re.compile(r"\d")
# baseline/target phrasing: 'from X to Y', 'X% to Y%', 'X -> Y', etc.
BASELINE_RE = re.compile(r"\bfrom\b.*\bto\b|->|→|\b\d+%?\s*to\s*\d+%?", re.I)
DEADLINE_RE = re.compile(
    r"\bby\b|\bQ[1-4]\b|end of|eoq|eoy|\bjan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec",
    re.I,
)

DEMO = """
O: Improve onboarding
KR: Launch new onboarding flow
KR: Get 1,000,000 page views
KR: Increase day-1 activation from 38% to 58% by Q3
O: Grow the business and improve quality and hire
KR: Increase revenue
KR: Reduce P1 incidents from 6 to 2 per quarter by end of Q4
""".strip()


def first_word(text):
    m = re.match(r"\s*([A-Za-z']+)", text)
    return m.group(1).lower() if m else ""


def lint_objective(text):
    issues = []
    if NUMBER_RE.search(text):
        issues.append(("WARN", "Objective contains a number - numbers belong in key results."))
    if re.search(r"\band\b", text, re.I):
        issues.append(("WARN", "Objective stitches goals with 'and' - consider splitting."))
    if len(text.split()) > 12:
        issues.append(("WARN", "Objective is long (>12 words) - make it memorable."))
    return issues


def lint_kr(text):
    issues = []
    low = text.lower()
    if first_word(text) in TASK_VERBS:
        issues.append(("ERROR", "Looks like a task/output (starts with a doing-verb). Measure the outcome instead."))
    if not NUMBER_RE.search(text):
        issues.append(("ERROR", "No number found - a key result must be measurable."))
    if not BASELINE_RE.search(text):
        issues.append(("WARN", "No baseline->target ('from X to Y') detected - add a baseline so it can be graded."))
    if not DEADLINE_RE.search(text):
        issues.append(("WARN", "No deadline detected - add a date within the period."))
    for term in VANITY_TERMS:
        if term in low:
            issues.append(("WARN", f"'{term}' is often a vanity metric - tie it to value or pair with an outcome KR."))
            break
    return issues


def parse(lines):
    """Yield (kind, text) where kind is 'O' or 'KR'."""
    for raw in lines:
        line = raw.strip()
        if not line:
            continue
        if line[:2].upper() == "O:":
            yield "O", line[2:].strip()
        elif line[:3].upper() == "KR:":
            yield "KR", line[3:].strip()


def run(lines):
    error_count = 0
    warn_count = 0
    kr_count = 0
    obj_count = 0
    for kind, text in parse(lines):
        if kind == "O":
            obj_count += 1
            print(f"\nOBJECTIVE: {text}")
            issues = lint_objective(text)
        else:
            kr_count += 1
            print(f"  KR: {text}")
            issues = lint_kr(text)
        for level, msg in issues:
            print(f"    [{level}] {msg}")
            if level == "ERROR":
                error_count += 1
            else:
                warn_count += 1
        if not issues:
            print("    [OK]")
    print(
        f"\nSummary: {obj_count} objective(s), {kr_count} key result(s), "
        f"{error_count} error(s), {warn_count} warning(s)."
    )
    if kr_count and (kr_count < 2 or kr_count > 5 * max(obj_count, 1)):
        print("Note: aim for 2-5 key results per objective.")
    return 1 if error_count else 0


def main(argv=None):
    p = argparse.ArgumentParser(description="Lint OKRs for common weaknesses.")
    p.add_argument("file", nargs="?", help="OKR file (O:/KR: format). Reads stdin if omitted.")
    p.add_argument("--demo", action="store_true", help="Run on a built-in sample.")
    args = p.parse_args(argv)

    if args.demo:
        return run(DEMO.splitlines())
    if args.file:
        with open(args.file, "r", encoding="utf-8") as fh:
            return run(fh.readlines())
    if sys.stdin.isatty():
        p.error("no input: pass a file, pipe stdin, or use --demo")
    return run(sys.stdin.readlines())


if __name__ == "__main__":
    raise SystemExit(main())
