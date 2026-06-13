#!/usr/bin/env python3
"""Scaffold a new Architecture Decision Record (ADR).

Scans an ADR directory, computes the next zero-padded sequence number, slugifies the
title, and writes a new ADR file pre-filled from the canonical template.

Usage:
    python3 new_adr.py "Use PostgreSQL for the orders service"
    python3 new_adr.py "Adopt gRPC for internal RPC" --dir docs/adr --deciders "Platform team"
    python3 new_adr.py "Deprecate the legacy gateway" --status Proposed --print

The script depends only on the Python standard library.
"""
import argparse
import datetime as _dt
import pathlib
import re
import sys

VALID_STATUSES = {"Proposed", "Accepted", "Rejected", "Deprecated"}

TEMPLATE = """# ADR-{num}: {title}

- **Status:** {status}
- **Date:** {date}
- **Deciders:** {deciders}
- **Technical Story:** <optional link to ticket, RFC, or design doc>

## Context

<Describe the problem and the forces at play: business drivers, technical constraints,
non-functional requirements, deadlines, existing systems, team capabilities. State the
problem before the solution. Separate facts from assumptions.>

**Facts:**
- <objective, verifiable fact>

**Assumptions:**
- <assumption that, if wrong, would change the decision>

## Decision Drivers

- <driver 1>
- <driver 2>
- <driver 3>

## Considered Options

1. **<Option A>** - <one-line summary>
2. **<Option B>** - <one-line summary>
3. **<Option C / Do nothing>** - <one-line summary>

### Option A: <name>

<How it works.>

- Good: <pro tied to a driver>
- Bad: <con tied to a driver>

### Option B: <name>

<How it works.>

- Good: <pro>
- Bad: <con>

## Options Matrix

| Driver | Option A | Option B | Option C |
|--------|:--------:|:--------:|:--------:|
| <driver 1> | ++ | o | - |
| <driver 2> | + | ++ | - |
| <driver 3> | o | - | ++ |

## Decision Outcome

**Chosen option: <Option X>.**

<Why this option wins, tied to the drivers and matrix; why the others were rejected.>

## Consequences

**Positive:**
- <good thing that follows>

**Negative:**
- <cost / risk we accept - mandatory>

**Neutral / Follow-ups:**
- <new work, things to revisit, metrics to watch>

## Links

- Supersedes: none
- Superseded by: none
- Related: <ADR-NNNN, design doc>
"""


def slugify(text):
    """Convert a title into a lowercase, hyphen-separated slug."""
    text = text.lower()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return text.strip("-")


def next_number(adr_dir):
    """Return the next sequential ADR number by scanning existing NNNN-*.md files."""
    highest = 0
    if adr_dir.is_dir():
        for path in adr_dir.glob("*.md"):
            match = re.match(r"(\d+)", path.name)
            if match:
                highest = max(highest, int(match.group(1)))
    return highest + 1


def build_parser():
    parser = argparse.ArgumentParser(
        description="Scaffold a new Architecture Decision Record."
    )
    parser.add_argument("title", help="Short imperative ADR title.")
    parser.add_argument(
        "--dir", default="docs/adr", help="ADR directory (default: docs/adr)."
    )
    parser.add_argument(
        "--status",
        default="Proposed",
        choices=sorted(VALID_STATUSES),
        help="Initial status (default: Proposed).",
    )
    parser.add_argument(
        "--deciders",
        default="<names / roles>",
        help="Who made or approved the decision.",
    )
    parser.add_argument(
        "--date",
        default=_dt.date.today().isoformat(),
        help="ISO date (default: today).",
    )
    parser.add_argument(
        "--print",
        dest="print_only",
        action="store_true",
        help="Print to stdout instead of writing a file.",
    )
    return parser


def main(argv=None):
    args = build_parser().parse_args(argv)
    adr_dir = pathlib.Path(args.dir)
    num = f"{next_number(adr_dir):04d}"
    slug = slugify(args.title)

    content = TEMPLATE.format(
        num=num,
        title=args.title,
        status=args.status,
        date=args.date,
        deciders=args.deciders,
    )

    if args.print_only:
        sys.stdout.write(content)
        return 0

    adr_dir.mkdir(parents=True, exist_ok=True)
    out_path = adr_dir / f"{num}-{slug}.md"
    if out_path.exists():
        sys.stderr.write(f"Refusing to overwrite existing file: {out_path}\n")
        return 1
    out_path.write_text(content, encoding="utf-8")
    sys.stdout.write(f"Created {out_path}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
