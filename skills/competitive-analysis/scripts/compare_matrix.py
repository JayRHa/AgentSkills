#!/usr/bin/env python3
"""Weighted competitor comparison matrix generator.

Reads competitor scores from a JSON or CSV file and emits a Markdown table
with per-dimension weighted contributions and a ranked weighted total.
Stdlib-only.

INPUT FORMATS
-------------
JSON:
{
  "dimensions": [
    {"name": "Ease of use", "weight": 25},
    {"name": "Price",       "weight": 20}
  ],
  "competitors": [
    {"name": "Us",     "scores": {"Ease of use": 4, "Price": 3}},
    {"name": "RivalX", "scores": {"Ease of use": 5, "Price": 2}}
  ]
}

CSV (first column = dimension name, second = weight, remaining columns = competitors):
  dimension,weight,Us,RivalX
  Ease of use,25,4,5
  Price,20,3,2

Scores are 1-5 (buyer's perspective). Weights should sum to 100 (a warning is
printed otherwise; scores are normalized by total weight regardless).

USAGE
-----
  python3 compare_matrix.py data.json
  python3 compare_matrix.py data.csv
  python3 compare_matrix.py data.json --max-score 10
  python3 compare_matrix.py -            # read JSON from stdin
"""
import argparse
import csv
import json
import sys


def load_json(text):
    data = json.loads(text)
    dims = [(d["name"], float(d["weight"])) for d in data["dimensions"]]
    comps = []
    for c in data["competitors"]:
        comps.append((c["name"], {k: float(v) for k, v in c["scores"].items()}))
    return dims, comps


def load_csv(text):
    reader = csv.reader(text.splitlines())
    rows = [r for r in reader if r and any(cell.strip() for cell in r)]
    header = rows[0]
    comp_names = [h.strip() for h in header[2:]]
    dims = []
    comps = {name: {} for name in comp_names}
    for row in rows[1:]:
        dim = row[0].strip()
        weight = float(row[1])
        dims.append((dim, weight))
        for i, name in enumerate(comp_names):
            comps[name][dim] = float(row[2 + i])
    return dims, [(name, comps[name]) for name in comp_names]


def build_table(dims, comps, max_score):
    total_weight = sum(w for _, w in dims)
    if abs(total_weight - 100.0) > 0.01:
        print(f"WARNING: weights sum to {total_weight:g}, not 100. "
              f"Normalizing by {total_weight:g}.\n", file=sys.stderr)

    names = [n for n, _ in comps]

    # Header
    lines = []
    head = ["Dimension", "Weight"] + names
    lines.append("| " + " | ".join(head) + " |")
    lines.append("|" + "|".join(["---"] * len(head)) + "|")

    # Raw score rows
    for dim, weight in dims:
        cells = [dim, f"{weight:g}"]
        for _, scores in comps:
            cells.append(f"{scores.get(dim, 0):g}")
        lines.append("| " + " | ".join(cells) + " |")

    # Weighted totals
    totals = {}
    for name, scores in comps:
        acc = 0.0
        for dim, weight in dims:
            acc += scores.get(dim, 0) * weight
        # Normalize: weighted average score scaled to 0-100
        totals[name] = (acc / (total_weight * max_score)) * 100 if total_weight else 0

    total_cells = ["**Weighted score (0-100)**", ""]
    for name, _ in comps:
        total_cells.append(f"**{totals[name]:.1f}**")
    lines.append("| " + " | ".join(total_cells) + " |")

    # Ranking
    ranking = sorted(totals.items(), key=lambda kv: kv[1], reverse=True)
    rank_str = "  ".join(f"{i+1}. {n} ({s:.1f})" for i, (n, s) in enumerate(ranking))
    return "\n".join(lines), rank_str


def main():
    p = argparse.ArgumentParser(description="Generate a weighted competitor comparison matrix.")
    p.add_argument("input", help="Path to .json or .csv input file, or '-' for JSON on stdin")
    p.add_argument("--max-score", type=float, default=5.0,
                   help="Maximum per-dimension score (default 5)")
    args = p.parse_args()

    if args.input == "-":
        text = sys.stdin.read()
        dims, comps = load_json(text)
    else:
        with open(args.input, "r", encoding="utf-8") as f:
            text = f.read()
        if args.input.lower().endswith(".csv"):
            dims, comps = load_csv(text)
        else:
            dims, comps = load_json(text)

    table, ranking = build_table(dims, comps, args.max_score)
    print("## Weighted Comparison Matrix\n")
    print(table)
    print("\n**Ranking:** " + ranking)


if __name__ == "__main__":
    main()
