#!/usr/bin/env python3
"""pacing.py — Sanity-check presentation pacing.

Given a talk length and a slide count (or a slide-outline file), this computes
the time budget per slide and flags decks that are over- or under-packed.

Usage:
    # From explicit numbers:
    python3 pacing.py --minutes 10 --slides 12

    # Count content slides from a markdown outline (lines starting with '### Slide' or '#### Slide'):
    python3 pacing.py --minutes 20 --file outline.md

    # Tune the comfortable seconds-per-slide range (default 60-120):
    python3 pacing.py --minutes 30 --slides 40 --min-sps 45 --max-sps 150

Exit code is 0 if pacing is comfortable, 1 if it's flagged (too fast/too slow).
Uses only the Python standard library.
"""
import argparse
import re
import sys

SLIDE_HEADING = re.compile(r"^#{2,6}\s+slide\b", re.IGNORECASE)


def count_slides_in_file(path):
    """Count slide headings of the form '### Slide ...' / '#### Slide ...'."""
    count = 0
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            if SLIDE_HEADING.match(line.strip()):
                count += 1
    return count


def assess(minutes, slides, min_sps, max_sps):
    if slides <= 0:
        raise ValueError("slide count must be greater than 0")
    total_seconds = minutes * 60
    sps = total_seconds / slides
    if sps < min_sps:
        verdict = "TOO FAST"
        advice = (
            "Too many slides for the time. Cut slides, merge ideas, or move "
            "detail to speaker notes/an appendix. Aim for fewer, stronger slides."
        )
        ok = False
    elif sps > max_sps:
        verdict = "TOO SLOW"
        advice = (
            "Too few slides for the time — you risk lingering. Either add a "
            "demo/proof beat, break dense slides into a build, or tighten the talk."
        )
        ok = False
    else:
        verdict = "COMFORTABLE"
        advice = "Pacing is in a healthy range. Rehearse aloud to confirm."
        ok = True
    return sps, verdict, advice, ok


def main(argv=None):
    p = argparse.ArgumentParser(description="Check presentation pacing.")
    p.add_argument("--minutes", type=float, required=True, help="Talk length in minutes.")
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("--slides", type=int, help="Number of content slides.")
    g.add_argument("--file", help="Outline markdown file; counts '### Slide' headings.")
    p.add_argument("--min-sps", type=float, default=60.0,
                   help="Min comfortable seconds per slide (default 60).")
    p.add_argument("--max-sps", type=float, default=120.0,
                   help="Max comfortable seconds per slide (default 120).")
    args = p.parse_args(argv)

    if args.file:
        try:
            slides = count_slides_in_file(args.file)
        except OSError as exc:
            print(f"error: could not read {args.file}: {exc}", file=sys.stderr)
            return 2
        if slides == 0:
            print("error: no slide headings ('### Slide ...') found in file.",
                  file=sys.stderr)
            return 2
    else:
        slides = args.slides

    try:
        sps, verdict, advice, ok = assess(args.minutes, slides, args.min_sps, args.max_sps)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    print(f"Talk length : {args.minutes:g} min ({args.minutes * 60:g} sec)")
    print(f"Slides      : {slides}")
    print(f"Per slide   : {sps:.0f} sec  (comfortable range {args.min_sps:g}-{args.max_sps:g})")
    print(f"Verdict     : {verdict}")
    print(f"Advice      : {advice}")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
