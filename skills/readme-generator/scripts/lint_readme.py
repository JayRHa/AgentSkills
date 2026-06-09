#!/usr/bin/env python3
"""Lint a README.md for common quality problems.

Checks (mechanical subset of references/quality-checklist.md):
  - Exactly one H1.
  - No skipped heading levels (e.g. H2 -> H4).
  - A License section exists.
  - No placeholder leftovers (TODO, FIXME, lorem ipsum, <your-...>, OWNER/REPO).
  - Relative links / images point to files that exist on disk.
  - Images have non-empty alt text.
  - Fenced code blocks have a language hint (warning).
  - Table of Contents present when the doc is long (warning).

Exit code 0 if no errors (warnings allowed), 1 if any errors, 2 on bad input.

Usage:
    python3 lint_readme.py README.md
    python3 lint_readme.py path/to/README.md --strict   # warnings fail too

Pure standard library.
"""
import argparse
import os
import re
import sys

PLACEHOLDERS = [
    r"\bTODO\b",
    r"\bFIXME\b",
    r"lorem ipsum",
    r"<your-[^>]*>",
    r"<PLACEHOLDER>",
    r"\bOWNER/REPO\b",
    r"<PROJECT NAME>",
]


def strip_code_blocks(text):
    """Return text with fenced code block bodies blanked (keep line count)."""
    out, in_block = [], False
    for line in text.splitlines():
        if line.lstrip().startswith("```"):
            in_block = not in_block
            out.append("")
            continue
        out.append("" if in_block else line)
    return "\n".join(out)


def lint(path, strict=False):
    errors, warnings = [], []
    base = os.path.dirname(os.path.abspath(path))
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        raw = f.read()
    prose = strip_code_blocks(raw)

    # Headings
    headings = re.findall(r"^(#{1,6})\s+(.+)$", prose, re.MULTILINE)
    levels = [len(h) for h, _ in headings]
    h1s = [t for h, t in headings if len(h) == 1]
    if len(h1s) == 0:
        errors.append("No H1 title found (need exactly one `#` heading).")
    elif len(h1s) > 1:
        errors.append(f"Multiple H1 headings found ({len(h1s)}): {h1s}.")

    prev = 0
    for lvl in levels:
        if prev and lvl > prev + 1:
            warnings.append(
                f"Heading level jumps from H{prev} to H{lvl} (skips a level)."
            )
        prev = lvl

    titles = [t.strip().lower() for _, t in headings]
    if not any("license" in t for t in titles):
        errors.append("No License section found.")

    # Placeholders (search prose, not code samples)
    for pat in PLACEHOLDERS:
        for m in re.finditer(pat, prose, re.IGNORECASE):
            line = prose[: m.start()].count("\n") + 1
            errors.append(f"Placeholder leftover {m.group(0)!r} at line {line}.")

    # Links & images
    for m in re.finditer(r"(!?)\[([^\]]*)\]\(([^)]+)\)", raw):
        is_img, alt, target = m.group(1) == "!", m.group(2), m.group(3).strip()
        target = target.split()[0]  # drop optional "title"
        if is_img and not alt.strip():
            warnings.append(f"Image with empty alt text: ({target}).")
        if target.startswith(("http://", "https://", "#", "mailto:")):
            continue
        local = target.split("#", 1)[0]
        if local and not os.path.exists(os.path.join(base, local)):
            errors.append(f"Broken relative link/image: {target}")

    # Code fence language hints
    fences = re.findall(r"^```(.*)$", raw, re.MULTILINE)
    openers = fences[::2]  # every other fence is an opener
    if any(tag.strip() == "" for tag in openers):
        warnings.append("Some fenced code blocks have no language hint.")

    # TOC for long docs
    h2count = sum(1 for lvl in levels if lvl == 2)
    has_toc = any("table of contents" in t or t == "contents" for t in titles)
    if h2count >= 6 and not has_toc:
        warnings.append(
            f"Long README ({h2count} H2 sections) but no Table of Contents."
        )

    return errors, warnings


def main(argv=None):
    ap = argparse.ArgumentParser(description="Lint a README.md.")
    ap.add_argument("readme", help="path to README.md")
    ap.add_argument(
        "--strict", action="store_true", help="treat warnings as errors"
    )
    args = ap.parse_args(argv)

    if not os.path.isfile(args.readme):
        print(f"error: file not found: {args.readme}", file=sys.stderr)
        return 2

    errors, warnings = lint(args.readme, args.strict)

    for w in warnings:
        print(f"WARN  {w}")
    for e in errors:
        print(f"ERROR {e}")

    if not errors and not warnings:
        print("OK    No issues found.")

    fail = bool(errors) or (args.strict and bool(warnings))
    if fail:
        n = len(errors) + (len(warnings) if args.strict else 0)
        print(f"\n{n} issue(s) must be fixed.")
        return 1
    print(f"\nPassed ({len(warnings)} warning(s)).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
