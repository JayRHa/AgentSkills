#!/usr/bin/env python3
"""jd_lint.py - Lint a job description for bias, inflation, and missing sections.

Flags coded/gendered language, requirement inflation, jargon, accessibility
risks, and checks that key sections are present. Stdlib only.

Usage:
    python3 jd_lint.py path/to/jd.md
    cat jd.md | python3 jd_lint.py -
    python3 jd_lint.py jd.md --json

Exit code is 0 if no high-severity issues, 1 otherwise.
"""
import argparse
import json
import re
import sys

# (pattern, severity, message) - patterns are case-insensitive word/phrase matches
CODED_TERMS = [
    (r"\brock\s?star(s)?\b", "warn", "'rockstar' is coded jargon; use 'skilled/experienced'."),
    (r"\bninja(s)?\b", "warn", "'ninja' is coded jargon; use 'expert/specialist'."),
    (r"\bguru(s)?\b", "warn", "'guru' is coded jargon; use 'expert'."),
    (r"\bwizard(s)?\b", "warn", "'wizard' is coded jargon; use 'expert'."),
    (r"\bhe/she\b|\bhis/her\b|\b(s)?he\b", "warn", "Use gender-neutral 'they/you' instead of he/she."),
    (r"\bmanpower\b|\bman-?hours?\b", "warn", "Gendered; use 'workforce/staffing/work hours'."),
    (r"\bchairman\b|\bforeman\b|\bsalesman\b", "warn", "Gendered title; use neutral form."),
    (r"\baggressive\b|\bdominant\b", "warn", "Male-coded; consider 'proactive/driven'."),
    (r"\byoung\b|\benergetic\b|\bdigital native\b", "warn", "Age bias / proxy; describe skills instead."),
    (r"\brecent graduate(s)?\b", "warn", "Potential age bias; say 'early-career' or state skills."),
]

INFLATION_TERMS = [
    (r"\b(\d{2,})\s*\+?\s*years?\b", "warn", "High years-of-experience requirement; prefer capability statements."),
    (r"\bbachelor'?s?\b|\bdegree required\b|\bmaster'?s?\b", "info", "Is a degree truly required? Consider 'or equivalent experience'."),
    (r"\bexpert in\b.*\b(and|,)\b.*\b(and|,)\b", "info", "Possible requirement stacking; split must-have vs nice-to-have."),
]

ACCESSIBILITY_TERMS = [
    (r"\bable-?bodied\b", "warn", "Ableist; remove unless bona fide."),
    (r"\bmust be able to (lift|stand|walk|carry)\b", "info", "Include physical requirements only if genuinely essential."),
    (r"\bvalid driver'?s? licen[cs]e\b", "info", "Only require if driving is essential to the role."),
]

JARGON_TERMS = [
    (r"\bfast-?paced\b", "info", "'fast-paced' is filler; describe the actual pace/work."),
    (r"\bwork hard,? play hard\b", "warn", "Cliche that can signal poor work-life balance."),
    (r"\bwe are a family\b", "warn", "'we are a family' can read as a boundary red flag."),
    (r"\bsynergy\b|\bsynergize\b", "info", "Buzzword; say what you mean."),
]

REQUIRED_SECTIONS = {
    "responsibilities": r"(what you'?ll do|responsibilit|key duties|the role)",
    "requirements": r"(what you'?ll bring|requirement|qualification|you have|must.?have)",
    "compensation": r"(salary|compensation|pay range|\$|€|£|benefit)",
    "eeo": r"(equal[- ]opportunity|diversity|inclusi|do not discriminate)",
}

ALL_TERM_GROUPS = [
    ("bias", CODED_TERMS),
    ("inflation", INFLATION_TERMS),
    ("accessibility", ACCESSIBILITY_TERMS),
    ("jargon", JARGON_TERMS),
]


def lint(text):
    issues = []
    lines = text.splitlines()
    for i, line in enumerate(lines, start=1):
        for group, terms in ALL_TERM_GROUPS:
            for pattern, sev, msg in terms:
                if re.search(pattern, line, flags=re.IGNORECASE):
                    issues.append({
                        "line": i,
                        "category": group,
                        "severity": sev,
                        "message": msg,
                        "text": line.strip()[:120],
                    })
    lower = text.lower()
    for name, pattern in REQUIRED_SECTIONS.items():
        if not re.search(pattern, lower):
            issues.append({
                "line": 0,
                "category": "missing-section",
                "severity": "warn",
                "message": f"Missing or unclear '{name}' section.",
                "text": "",
            })
    return issues


def format_text(issues):
    if not issues:
        return "No issues found. JD looks clean."
    order = {"warn": 0, "info": 1}
    issues = sorted(issues, key=lambda x: (order.get(x["severity"], 2), x["line"]))
    out = []
    for it in issues:
        loc = f"L{it['line']}" if it["line"] else "--"
        out.append(f"[{it['severity'].upper():4}] {loc:>4} ({it['category']}) {it['message']}")
        if it["text"]:
            out.append(f"            > {it['text']}")
    warns = sum(1 for it in issues if it["severity"] == "warn")
    infos = sum(1 for it in issues if it["severity"] == "info")
    out.append("")
    out.append(f"Summary: {warns} warning(s), {infos} info note(s).")
    return "\n".join(out)


def main(argv=None):
    p = argparse.ArgumentParser(description="Lint a job description for bias and quality issues.")
    p.add_argument("path", help="Path to JD markdown/text file, or '-' for stdin.")
    p.add_argument("--json", action="store_true", help="Output JSON instead of text.")
    args = p.parse_args(argv)

    if args.path == "-":
        text = sys.stdin.read()
    else:
        try:
            with open(args.path, "r", encoding="utf-8") as fh:
                text = fh.read()
        except OSError as e:
            print(f"error: cannot read {args.path}: {e}", file=sys.stderr)
            return 2

    issues = lint(text)
    if args.json:
        print(json.dumps(issues, indent=2))
    else:
        print(format_text(issues))

    has_warn = any(it["severity"] == "warn" for it in issues)
    return 1 if has_warn else 0


if __name__ == "__main__":
    sys.exit(main())
