#!/usr/bin/env python3
"""changelog_tool.py - Validate and manipulate a Keep a Changelog CHANGELOG.md.

Stdlib only. Two subcommands:

  validate FILE
      Check structure: top-level heading, presence of [Unreleased],
      canonical group names, dates on released versions, newest-first order.
      Exits 0 if valid, 1 if problems are found (printed to stdout).

  release FILE VERSION DATE
      Convert the current [Unreleased] section into a dated release header
      '## [VERSION] - DATE' and insert a fresh empty '## [Unreleased]' above it.
      The rewritten changelog is printed to stdout (redirect to overwrite).

Examples:
  python3 changelog_tool.py validate CHANGELOG.md
  python3 changelog_tool.py release CHANGELOG.md 1.3.0 2026-06-08 > CHANGELOG.new.md
"""
import argparse
import re
import sys

SECTIONS = ["Added", "Changed", "Deprecated", "Removed", "Fixed", "Security"]
VER_RE = re.compile(
    r'^## \[('
    r'\d+\.\d+\.\d+(?:-[0-9A-Za-z.-]+)?(?:\+[0-9A-Za-z.-]+)?'
    r'|Unreleased)\]'
    r'(?: - (\d{4}-\d{2}-\d{2}))?\s*$'
)


def parse(text):
    """Return list of {version, date, line, sections:[(name,line)]}."""
    lines = text.splitlines()
    versions, cur = [], None
    for i, line in enumerate(lines, 1):
        m = VER_RE.match(line)
        if m:
            cur = {"version": m.group(1), "date": m.group(2),
                   "line": i, "sections": []}
            versions.append(cur)
        elif line.startswith("### ") and cur is not None:
            cur["sections"].append((line[4:].strip(), i))
    return versions


def _semver_key(version):
    core = version.split("-")[0].split("+")[0]
    return tuple(int(x) for x in core.split("."))


def cmd_validate(text):
    errs = []
    head = text.splitlines()[:5]
    if not any(l.strip() == "# Changelog" for l in head):
        errs.append("Missing top-level '# Changelog' heading near top of file.")

    versions = parse(text)
    if not versions:
        errs.append("No version sections found (expected '## [x.y.z] - DATE').")
    else:
        if versions[0]["version"] != "Unreleased":
            errs.append(
                "First section should usually be '## [Unreleased]' "
                f"(found '[{versions[0]['version']}]' at line {versions[0]['line']})."
            )
        for v in versions:
            if v["version"] != "Unreleased" and not v["date"]:
                errs.append(
                    f"Line {v['line']}: released version [{v['version']}] "
                    "missing ' - YYYY-MM-DD' date."
                )
            for name, ln in v["sections"]:
                if name not in SECTIONS:
                    errs.append(
                        f"Line {ln}: invalid section '### {name}'. "
                        f"Use one of: {', '.join(SECTIONS)}."
                    )
        released = [v for v in versions if v["version"] != "Unreleased"]
        for a, b in zip(released, released[1:]):
            if _semver_key(a["version"]) < _semver_key(b["version"]):
                errs.append(
                    f"Version order: [{a['version']}] precedes higher "
                    f"[{b['version']}] (versions must be newest first)."
                )

    if errs:
        print("INVALID:")
        for e in errs:
            print("  - " + e)
        return 1
    print(f"VALID: {len(versions)} version section(s), newest first.")
    return 0


def cmd_release(text, version, date):
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", date):
        print(f"ERROR: date must be YYYY-MM-DD, got '{date}'.", file=sys.stderr)
        return 1
    versions = parse(text)
    unrel = next((v for v in versions if v["version"] == "Unreleased"), None)
    if not unrel:
        print("ERROR: no [Unreleased] section to release.", file=sys.stderr)
        return 1
    lines = text.splitlines()
    out = []
    for i, line in enumerate(lines, 1):
        if i == unrel["line"]:
            out.append("## [Unreleased]")
            out.append("")
            out.append(f"## [{version}] - {date}")
        else:
            out.append(line)
    print("\n".join(out))
    return 0


def main():
    p = argparse.ArgumentParser(
        description="Validate/manipulate a Keep a Changelog CHANGELOG.md")
    sub = p.add_subparsers(dest="cmd", required=True)

    pv = sub.add_parser("validate", help="Check structure & ordering")
    pv.add_argument("file")

    pr = sub.add_parser(
        "release",
        help="Cut [Unreleased] into a dated release; prints result to stdout")
    pr.add_argument("file")
    pr.add_argument("version")
    pr.add_argument("date")

    args = p.parse_args()
    with open(args.file, encoding="utf-8") as f:
        text = f.read()

    if args.cmd == "validate":
        sys.exit(cmd_validate(text))
    if args.cmd == "release":
        sys.exit(cmd_release(text, args.version, args.date))


if __name__ == "__main__":
    main()
