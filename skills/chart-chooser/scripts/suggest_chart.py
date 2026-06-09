#!/usr/bin/env python3
"""Suggest a chart type and encodings from a data profile and question intent.

Pure standard library. Works in two modes:

1. CSV mode  — profile a CSV and (optionally) suggest a chart for chosen columns.
     python3 suggest_chart.py --csv data.csv --profile
     python3 suggest_chart.py --csv data.csv --intent trend --x date --y revenue

2. Manual mode — describe columns directly, no file needed.
     python3 suggest_chart.py --intent comparison \
         --col region:categorical:8 --col sales:quantitative

Intents: comparison, trend, distribution, relationship, part-to-whole,
         ranking, geospatial, flow

Column spec for --col:  name:type[:cardinality]
  type in {categorical, ordinal, quantitative, temporal, geographic}

The tool prints a recommended chart, runner-up, encoding hints, and honesty notes.
It is heuristic guidance, not a substitute for judgment.
"""
import argparse
import csv
import sys
from datetime import datetime

VALID_TYPES = {"categorical", "ordinal", "quantitative", "temporal", "geographic"}
VALID_INTENTS = {
    "comparison", "trend", "distribution", "relationship",
    "part-to-whole", "ranking", "geospatial", "flow",
}

DATE_FORMATS = ("%Y-%m-%d", "%Y/%m/%d", "%m/%d/%Y", "%d.%m.%Y", "%Y-%m", "%Y")


class Column:
    def __init__(self, name, ctype, cardinality=None):
        self.name = name
        self.ctype = ctype
        self.cardinality = cardinality

    def __repr__(self):
        c = "" if self.cardinality is None else f", n={self.cardinality}"
        return f"{self.name} ({self.ctype}{c})"


def _looks_temporal(values):
    hits = 0
    for v in values:
        v = (v or "").strip()
        if not v:
            continue
        for fmt in DATE_FORMATS:
            try:
                datetime.strptime(v, fmt)
                hits += 1
                break
            except ValueError:
                continue
    nonblank = sum(1 for v in values if (v or "").strip())
    return nonblank > 0 and hits / nonblank > 0.8


def _looks_numeric(values):
    nonblank = [v for v in values if (v or "").strip()]
    if not nonblank:
        return False
    ok = 0
    for v in nonblank:
        try:
            float(v.replace(",", ""))
            ok += 1
        except ValueError:
            pass
    return ok / len(nonblank) > 0.9


def profile_csv(path, sample=2000):
    with open(path, newline="", encoding="utf-8") as fh:
        reader = csv.reader(fh)
        try:
            header = next(reader)
        except StopIteration:
            print("Empty CSV.", file=sys.stderr)
            sys.exit(1)
        cols = {h: [] for h in header}
        for i, row in enumerate(reader):
            if i >= sample:
                break
            for h, val in zip(header, row):
                cols[h].append(val)
    columns = []
    for h in header:
        vals = cols[h]
        distinct = len(set(v.strip() for v in vals if v.strip()))
        if _looks_temporal(vals):
            ctype = "temporal"
        elif _looks_numeric(vals):
            ctype = "quantitative"
        else:
            ctype = "categorical"
        columns.append(Column(h, ctype, distinct))
    return columns


def parse_col_spec(spec):
    parts = spec.split(":")
    if len(parts) < 2:
        raise argparse.ArgumentTypeError(
            f"--col must be name:type[:cardinality], got '{spec}'")
    name, ctype = parts[0], parts[1].lower()
    if ctype not in VALID_TYPES:
        raise argparse.ArgumentTypeError(
            f"type must be one of {sorted(VALID_TYPES)}, got '{ctype}'")
    card = int(parts[2]) if len(parts) > 2 and parts[2] else None
    return Column(name, ctype, card)


def recommend(intent, x=None, y=None, columns=None):
    """Return (primary, runner_up, encoding_hints, notes)."""
    notes = []
    enc = []

    def card_of(col):
        return col.cardinality if col and col.cardinality is not None else None

    if intent == "trend":
        primary, runner = "Line chart", "Area chart (if volume matters)"
        enc = ["x = time (left to right)", "y = quantitative value",
               "color = series (direct-label; limit to ~5)"]
        notes.append("Baseline may be non-zero if change is the message — label it.")
        if x and x.ctype != "temporal":
            notes.append(f"Warning: x ('{x.name}') is {x.ctype}, not temporal. "
                         "Use bars for a categorical x.")
    elif intent == "comparison":
        c = card_of(x)
        if c is not None and c > 12:
            primary = "Horizontal bar chart (sorted)"
            runner = "Lollipop chart"
        else:
            primary = "Bar chart"
            runner = "Lollipop / dot plot"
        enc = ["axis = category", "length = quantitative value",
               "sort bars by value"]
        notes.append("Start the value axis at zero — bar length encodes magnitude.")
    elif intent == "distribution":
        has_group = columns and any(c.ctype == "categorical" for c in columns)
        if has_group:
            primary, runner = "Box plot (or violin) by group", "Strip/jitter plot"
        else:
            primary, runner = "Histogram", "Density plot"
        enc = ["x = quantitative variable (binned for histogram)", "y = count/density"]
        notes.append("Choose bin width deliberately; show sample size n.")
    elif intent == "relationship":
        primary, runner = "Scatter plot", "Hexbin / 2D density (if overplotted)"
        enc = ["x = quantitative", "y = quantitative",
               "color = category (optional)", "size = 3rd quantitative (use sparingly)"]
        notes.append("Add a trend line only if a real relationship exists and is labeled.")
        notes.append("Correlation is not causation — do not imply it.")
    elif intent == "part-to-whole":
        c = card_of(x)
        if c is not None and c <= 4:
            primary = "Pie/donut (acceptable) or single stacked bar"
            runner = "Sorted bar chart"
        else:
            primary = "Sorted horizontal bar chart"
            runner = "Treemap (if hierarchical)"
        enc = ["part = category", "value = share of total"]
        notes.append("Parts must sum to a meaningful total; else it is a comparison.")
    elif intent == "ranking":
        primary, runner = "Sorted horizontal bar chart", "Lollipop / ordered dot plot"
        enc = ["axis = category (sorted by value)", "length = value"]
        notes.append("Start value axis at zero; sort descending.")
    elif intent == "geospatial":
        primary, runner = "Choropleth (normalized rate)", "Symbol/bubble map"
        enc = ["region/point = location", "color/size = normalized value"]
        notes.append("Map rates per-capita/per-area, not raw counts.")
    elif intent == "flow":
        primary, runner = "Sankey diagram", "Funnel chart (for stage drop-off)"
        enc = ["nodes = stages/entities", "link width = flow magnitude"]
    else:
        primary, runner = "(unknown intent)", ""

    return primary, runner, enc, notes


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--csv", help="Path to a CSV file to profile.")
    p.add_argument("--profile", action="store_true",
                   help="Print the inferred column profile and exit.")
    p.add_argument("--intent", choices=sorted(VALID_INTENTS),
                   help="The analytical question intent.")
    p.add_argument("--x", help="Name of the x/category column.")
    p.add_argument("--y", help="Name of the y/value column.")
    p.add_argument("--col", action="append", type=parse_col_spec, default=[],
                   help="Manual column spec name:type[:cardinality]. Repeatable.")
    args = p.parse_args(argv)

    columns = list(args.col)
    if args.csv:
        columns = profile_csv(args.csv)

    if args.profile or (args.csv and not args.intent):
        print("Column profile:")
        for c in columns:
            print(f"  - {c}")
        if not args.intent:
            return 0

    if not args.intent:
        p.error("--intent is required (unless only profiling).")

    by_name = {c.name: c for c in columns}
    x = by_name.get(args.x) if args.x else None
    y = by_name.get(args.y) if args.y else None

    primary, runner, enc, notes = recommend(args.intent, x=x, y=y, columns=columns)

    print(f"\nIntent: {args.intent}")
    if columns:
        print("Columns: " + ", ".join(repr(c) for c in columns))
    print(f"\n  Recommended : {primary}")
    if runner:
        print(f"  Runner-up   : {runner}")
    if enc:
        print("  Encodings   :")
        for e in enc:
            print(f"    - {e}")
    if notes:
        print("  Notes       :")
        for n in notes:
            print(f"    - {n}")
    print("\nThen run the clarity-and-honesty checklist before publishing.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
