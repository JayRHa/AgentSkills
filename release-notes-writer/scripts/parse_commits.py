#!/usr/bin/env python3
"""Parse a git commit range (or piped git log) into categorized release-note groups.

Groups commits by Conventional Commit type, flags breaking changes ("!" or a
"BREAKING CHANGE:" trailer), drops noise types, and emits either Markdown
(ready to refine) or JSON (for further processing).

The output is a STARTING POINT, not final copy. Always rewrite entries into
user-facing language per references/style-guide.md before publishing.

Usage:
    # From a git range (runs `git log` for you):
    python scripts/parse_commits.py --range v2.3.0..HEAD
    python scripts/parse_commits.py --range v2.3.0..HEAD --format json

    # From piped input (no git needed):
    git log v2.3.0..HEAD --pretty=format:'%H%x09%s%x09%b%x1e' | \
        python scripts/parse_commits.py --stdin

    # Keep normally-omitted noise (chore/ci/etc.):
    python scripts/parse_commits.py --range v2.3.0..HEAD --keep-noise

Pure standard library. Python 3.8+.
"""
import argparse
import json
import re
import subprocess
import sys

# Conventional-commit type -> release-note category.
TYPE_TO_CATEGORY = {
    "feat": "Features",
    "fix": "Bug Fixes",
    "perf": "Improvements",
    "security": "Security",
    "deprecate": "Deprecations",
}
# Types omitted from user-facing notes unless --keep-noise.
NOISE_TYPES = {"chore", "ci", "build", "style", "test", "refactor", "docs"}

CATEGORY_ORDER = [
    "Breaking Changes",
    "Security",
    "Features",
    "Improvements",
    "Bug Fixes",
    "Deprecations",
    "Other",
]

RECORD_SEP = "\x1e"
FIELD_SEP = "\t"

# type(scope)!: subject
HEADER_RE = re.compile(
    r"^(?P<type>\w+)(?:\((?P<scope>[^)]*)\))?(?P<bang>!)?:\s*(?P<subject>.+)$"
)
PR_RE = re.compile(r"\(#(\d+)\)|#(\d+)")
BREAKING_TRAILER_RE = re.compile(r"BREAKING[ -]CHANGE:\s*(.+)", re.IGNORECASE | re.DOTALL)


def git_log(rng):
    fmt = f"%H{FIELD_SEP}%s{FIELD_SEP}%b{RECORD_SEP}"
    try:
        out = subprocess.check_output(
            ["git", "log", rng, f"--pretty=format:{fmt}"],
            stderr=subprocess.STDOUT,
            text=True,
        )
    except FileNotFoundError:
        sys.exit("error: git not found on PATH")
    except subprocess.CalledProcessError as exc:
        sys.exit(f"error: git log failed:\n{exc.output}")
    return out


def parse_records(raw):
    for chunk in raw.split(RECORD_SEP):
        chunk = chunk.strip("\n")
        if not chunk:
            continue
        parts = chunk.split(FIELD_SEP)
        sha = parts[0] if len(parts) > 0 else ""
        subject = parts[1] if len(parts) > 1 else ""
        body = parts[2] if len(parts) > 2 else ""
        yield sha.strip(), subject.strip(), body.strip()


def extract_refs(text):
    refs = []
    for m in PR_RE.finditer(text):
        refs.append(m.group(1) or m.group(2))
    # de-dupe, preserve order
    seen = set()
    return [r for r in refs if not (r in seen or seen.add(r))]


def classify(subject, body, keep_noise):
    m = HEADER_RE.match(subject)
    breaking_note = None
    bt = BREAKING_TRAILER_RE.search(body)
    if bt:
        breaking_note = bt.group(1).strip()

    if not m:
        return ("Other", subject, breaking_note, bool(breaking_note))

    ctype = m.group("type").lower()
    bang = bool(m.group("bang"))
    subj = m.group("subject").strip()
    scope = m.group("scope")
    is_breaking = bang or bool(breaking_note)

    if is_breaking:
        category = "Breaking Changes"
    elif ctype in TYPE_TO_CATEGORY:
        category = TYPE_TO_CATEGORY[ctype]
    elif ctype in NOISE_TYPES:
        category = None if not keep_noise else "Other"
    else:
        category = "Other"

    if scope:
        subj = f"**{scope}:** {subj}"
    return (category, subj, breaking_note, is_breaking)


def build_groups(records, keep_noise):
    groups = {c: [] for c in CATEGORY_ORDER}
    for sha, subject, body in records:
        category, text, breaking_note, is_breaking = classify(subject, body, keep_noise)
        if category is None:
            continue
        refs = extract_refs(subject + " " + body)
        groups[category].append(
            {
                "sha": sha[:7],
                "text": text,
                "refs": refs,
                "breaking_note": breaking_note,
            }
        )
    return {c: items for c, items in groups.items() if items}


def suggest_bump(groups):
    if "Breaking Changes" in groups:
        return "major"
    if "Features" in groups:
        return "minor"
    if groups:
        return "patch"
    return "none"


def render_markdown(groups):
    lines = []
    bump = suggest_bump(groups)
    lines.append(f"<!-- suggested semver bump: {bump} -->")
    lines.append("<!-- DRAFT: rewrite each line into user-facing language before publishing -->\n")
    for category in CATEGORY_ORDER:
        items = groups.get(category)
        if not items:
            continue
        lines.append(f"### {category}\n")
        for it in items:
            ref = ""
            if it["refs"]:
                ref = " (" + ", ".join(f"#{r}" for r in it["refs"]) + ")"
            lines.append(f"- {it['text']}{ref}")
            if it["breaking_note"]:
                note = it["breaking_note"].replace("\n", " ").strip()
                lines.append(f"  - Migration: {note}")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    src = p.add_mutually_exclusive_group(required=True)
    src.add_argument("--range", help="git range, e.g. v2.3.0..HEAD")
    src.add_argument("--stdin", action="store_true", help="read git log from stdin (see usage)")
    p.add_argument("--format", choices=["markdown", "json"], default="markdown")
    p.add_argument("--keep-noise", action="store_true", help="keep chore/ci/etc. under 'Other'")
    args = p.parse_args(argv)

    raw = sys.stdin.read() if args.stdin else git_log(args.range)
    records = list(parse_records(raw))
    groups = build_groups(records, args.keep_noise)

    if args.format == "json":
        print(json.dumps({"suggested_bump": suggest_bump(groups), "groups": groups}, indent=2))
    else:
        print(render_markdown(groups))


if __name__ == "__main__":
    main()
