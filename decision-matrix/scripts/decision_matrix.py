#!/usr/bin/env python3
"""Weighted decision matrix calculator.

Computes weighted scores and a ranking for a set of options evaluated against
weighted criteria. Supports benefit and cost (lower-is-better) criteria, a
formatted table, and simple sensitivity analysis.

INPUT (JSON), e.g. input.json:
{
  "title": "Pick a PM tool",
  "scale_max": 5,
  "criteria": [
    {"name": "Affordability", "weight": 3},
    {"name": "Ease of use",   "weight": 5},
    {"name": "Integrations",  "weight": 4},
    {"name": "Price", "weight": 4, "direction": "cost"}
  ],
  "options": {
    "Tool A": {"Affordability": 5, "Ease of use": 3, "Integrations": 3, "Price": 12},
    "Tool B": {"Affordability": 3, "Ease of use": 5, "Integrations": 4, "Price": 25}
  }
}

For a criterion with "direction": "cost", provide RAW values (e.g. dollars); the
script min-max inverts them onto the scale so cheapest -> best. Benefit criteria
may use either raw values (auto-normalized) or already-on-scale scores; if all
values for a criterion are within [1, scale_max] they are treated as scores,
otherwise they are min-max normalized.

USAGE:
    python3 decision_matrix.py input.json
    python3 decision_matrix.py input.csv --csv
    python3 decision_matrix.py input.json --sensitivity
    python3 decision_matrix.py input.json --json   # machine-readable output

CSV FORMAT (first column = criterion name, optional 'weight' and 'direction'
columns, remaining columns = options):
    criterion,weight,direction,Tool A,Tool B
    Affordability,3,benefit,5,3
    Price,4,cost,12,25

Pure standard library. No dependencies.
"""
import argparse
import csv
import json
import sys


def load_json(path):
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def load_csv(path):
    with open(path, newline="", encoding="utf-8") as fh:
        rows = list(csv.reader(fh))
    if not rows:
        raise ValueError("Empty CSV")
    header = [h.strip() for h in rows[0]]
    lower = [h.lower() for h in header]
    w_idx = lower.index("weight") if "weight" in lower else None
    d_idx = lower.index("direction") if "direction" in lower else None
    reserved = {0}
    if w_idx is not None:
        reserved.add(w_idx)
    if d_idx is not None:
        reserved.add(d_idx)
    opt_cols = [i for i in range(len(header)) if i not in reserved]
    opt_names = [header[i] for i in opt_cols]

    criteria = []
    options = {name: {} for name in opt_names}
    for row in rows[1:]:
        if not row or not row[0].strip():
            continue
        cname = row[0].strip()
        weight = float(row[w_idx]) if w_idx is not None else 1.0
        direction = row[d_idx].strip().lower() if d_idx is not None else "benefit"
        criteria.append({"name": cname, "weight": weight, "direction": direction})
        for i, name in zip(opt_cols, opt_names):
            options[name][cname] = float(row[i])
    return {"title": "Decision Matrix", "scale_max": 5,
            "criteria": criteria, "options": options}


def normalize_column(values, direction, scale_max):
    """Map a criterion's values onto [1, scale_max].

    If benefit-direction values already sit within [1, scale_max], treat them as
    raw scores. Otherwise min-max normalize. Cost values are always inverted.
    """
    vmin, vmax = min(values), max(values)
    looks_like_scores = (direction == "benefit"
                         and vmin >= 1 and vmax <= scale_max)
    if looks_like_scores:
        return list(values)
    if vmax == vmin:
        return [scale_max for _ in values]  # no discrimination
    out = []
    for v in values:
        frac = (v - vmin) / (vmax - vmin)
        if direction == "cost":
            frac = 1.0 - frac
        out.append(frac * (scale_max - 1) + 1)
    return out


def compute(model):
    scale_max = model.get("scale_max", 5)
    criteria = model["criteria"]
    options = model["options"]
    opt_names = list(options.keys())

    total_weight = sum(c["weight"] for c in criteria)
    if total_weight == 0:
        raise ValueError("Criteria weights sum to zero.")

    # Build normalized score per criterion across options.
    norm_scores = {}  # crit -> {opt: score}
    for c in criteria:
        name = c["name"]
        direction = c.get("direction", "benefit").lower()
        raw = [float(options[o][name]) for o in opt_names]
        normed = normalize_column(raw, direction, scale_max)
        norm_scores[name] = dict(zip(opt_names, normed))

    results = []
    max_possible = total_weight * scale_max
    for o in opt_names:
        weighted = sum(c["weight"] * norm_scores[c["name"]][o] for c in criteria)
        index = 100.0 * weighted / max_possible
        results.append({"option": o, "weighted": weighted, "index": index})
    results.sort(key=lambda r: r["weighted"], reverse=True)
    return results, norm_scores, total_weight


def fmt_table(model, results, norm_scores):
    criteria = model["criteria"]
    opt_order = [r["option"] for r in results]
    headers = ["Criterion", "Wt"] + opt_order
    rows = []
    for c in criteria:
        name = c["name"]
        tag = " (cost)" if c.get("direction", "benefit").lower() == "cost" else ""
        row = [name + tag, f"{c['weight']:g}"]
        for o in opt_order:
            row.append(f"{norm_scores[name][o]:.2f}")
        rows.append(row)
    idx_row = ["INDEX (0-100)", ""] + [f"{r['index']:.1f}" for r in results]
    rows.append(idx_row)

    widths = [max(len(headers[i]), *(len(r[i]) for r in rows))
              for i in range(len(headers))]
    def line(cells):
        return "  ".join(c.ljust(widths[i]) for i, c in enumerate(cells))
    out = [line(headers), "  ".join("-" * w for w in widths)]
    for r in rows[:-1]:
        out.append(line(r))
    out.append("  ".join("-" * w for w in widths))
    out.append(line(rows[-1]))
    return "\n".join(out)


def sensitivity(model, base_results):
    """Bump each criterion weight by +/-25% and report whether the winner flips."""
    base_winner = base_results[0]["option"]
    lines = ["\nSensitivity (winner stability vs. +/-25% on each weight):"]
    flips = 0
    for c in model["criteria"]:
        flipped = []
        for factor in (1.25, 0.75):
            trial = json.loads(json.dumps(model))
            for tc in trial["criteria"]:
                if tc["name"] == c["name"]:
                    tc["weight"] = max(0.0001, tc["weight"] * factor)
            res, _, _ = compute(trial)
            if res[0]["option"] != base_winner:
                flipped.append(f"{'+25%' if factor > 1 else '-25%'} -> {res[0]['option']}")
        if flipped:
            flips += 1
            lines.append(f"  [FLIP] {c['name']}: {', '.join(flipped)}")
        else:
            lines.append(f"  [ok]   {c['name']}: winner stays {base_winner}")
    margin = base_results[0]["index"] - base_results[1]["index"] if len(base_results) > 1 else 100
    verdict = "ROBUST" if flips == 0 and margin > 5 else "FRAGILE / near-tie"
    lines.append(f"  Top-2 margin: {margin:.1f} index points -> {verdict}")
    return "\n".join(lines)


def main(argv=None):
    ap = argparse.ArgumentParser(description="Weighted decision matrix calculator.")
    ap.add_argument("input", help="Path to JSON (or CSV with --csv) input file.")
    ap.add_argument("--csv", action="store_true", help="Treat input as CSV.")
    ap.add_argument("--sensitivity", action="store_true",
                    help="Run +/-25% weight sensitivity analysis.")
    ap.add_argument("--json", dest="as_json", action="store_true",
                    help="Emit machine-readable JSON results.")
    args = ap.parse_args(argv)

    try:
        model = load_csv(args.input) if args.csv else load_json(args.input)
        results, norm_scores, _ = compute(model)
    except (OSError, ValueError, KeyError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    if args.as_json:
        print(json.dumps({"title": model.get("title", ""), "ranking": results},
                         indent=2))
        return 0

    title = model.get("title", "Decision Matrix")
    print(f"== {title} ==\n")
    print(fmt_table(model, results, norm_scores))
    winner = results[0]
    print(f"\nRecommended: {winner['option']}  (index {winner['index']:.1f}/100)")
    if len(results) > 1:
        margin = winner["index"] - results[1]["index"]
        note = "  <-- NEAR TIE, inspect closely" if margin <= 5 else ""
        print(f"Margin over runner-up ({results[1]['option']}): "
              f"{margin:.1f} pts{note}")
    if args.sensitivity:
        print(sensitivity(model, results))
    return 0


if __name__ == "__main__":
    sys.exit(main())
