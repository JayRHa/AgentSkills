#!/usr/bin/env python3
"""swot_score.py - Rank SWOT factors and compute strategic posture.

Reads a SWOT defined in JSON, scores each factor by Impact x Confidence,
ranks within each quadrant, and reports the overall strategic posture
implied by where the weight sits (Aggressive / Defensive / Turnaround / Survival).

Usage:
    python3 swot_score.py path/to/swot.json
    python3 swot_score.py --example          # print a sample input and run it
    cat swot.json | python3 swot_score.py -   # read from stdin

Input JSON shape:
{
  "subject": "Northbeam",
  "goal": "Decide FY26 strategy",
  "strengths":     [{"text": "...", "impact": 5, "confidence": 5}, ...],
  "weaknesses":    [{"text": "...", "impact": 5, "confidence": 5}, ...],
  "opportunities": [{"text": "...", "impact": 5, "confidence": 4}, ...],
  "threats":       [{"text": "...", "impact": 5, "confidence": 4}, ...]
}

impact and confidence are integers 1-5. (For O/T, "confidence" = likelihood.)
Pure standard library. No dependencies.
"""
import argparse
import json
import sys

QUADRANTS = ["strengths", "weaknesses", "opportunities", "threats"]
LABELS = {
    "strengths": "STRENGTHS (internal +)",
    "weaknesses": "WEAKNESSES (internal -)",
    "opportunities": "OPPORTUNITIES (external +)",
    "threats": "THREATS (external -)",
}

EXAMPLE = {
    "subject": "Northbeam (B2B SaaS)",
    "goal": "Decide FY26 strategy: enterprise vs. SMB",
    "strengths": [
        {"text": "Fastest time-to-value (2 days)", "impact": 5, "confidence": 5},
        {"text": "NRR 118%", "impact": 5, "confidence": 4},
        {"text": "Patented normalization engine", "impact": 4, "confidence": 4},
    ],
    "weaknesses": [
        {"text": "No SOC 2 / SSO (blocks enterprise)", "impact": 5, "confidence": 5},
        {"text": "Top customer = 22% of ARR", "impact": 4, "confidence": 5},
        {"text": "Thin sales team", "impact": 4, "confidence": 4},
    ],
    "opportunities": [
        {"text": "Incumbent sunsetting SMB tier", "impact": 5, "confidence": 4},
        {"text": "AI-analytics demand surge", "impact": 4, "confidence": 4},
        {"text": "EU compliance-driven demand", "impact": 3, "confidence": 3},
    ],
    "threats": [
        {"text": "$40M-funded entrant cloning UX", "impact": 5, "confidence": 4},
        {"text": "Vendor consolidation to suites", "impact": 4, "confidence": 3},
        {"text": "Macro budget tightening", "impact": 3, "confidence": 4},
    ],
}


def validate_factor(quad, idx, factor):
    if not isinstance(factor, dict):
        raise ValueError(f"{quad}[{idx}] must be an object")
    for key in ("impact", "confidence"):
        val = factor.get(key)
        if not isinstance(val, int) or not (1 <= val <= 5):
            raise ValueError(
                f"{quad}[{idx}].{key} must be an integer 1-5 (got {val!r})"
            )
    if not str(factor.get("text", "")).strip():
        raise ValueError(f"{quad}[{idx}].text is required")


def score_quadrant(factors):
    scored = []
    for f in factors:
        s = f["impact"] * f["confidence"]
        scored.append((s, f["text"], f["impact"], f["confidence"]))
    scored.sort(key=lambda x: x[0], reverse=True)
    return scored


def posture(weights):
    """Pick posture from quadrant total weights."""
    s, w, o, t = (weights[q] for q in QUADRANTS)
    pairs = {
        "Aggressive growth (S-O)": s + o,
        "Defensive / protect core (S-T)": s + t,
        "Turnaround / build to qualify (W-O)": w + o,
        "Survival / de-risk or exit (W-T)": w + t,
    }
    best = max(pairs, key=pairs.get)
    return best, pairs


def run(data):
    out = []
    out.append(f"SWOT SCORE REPORT")
    out.append(f"Subject: {data.get('subject', '(unspecified)')}")
    out.append(f"Goal:    {data.get('goal', '(unspecified)')}")
    out.append("=" * 60)

    weights = {}
    for quad in QUADRANTS:
        factors = data.get(quad, [])
        for i, f in enumerate(factors):
            validate_factor(quad, i, f)
        scored = score_quadrant(factors)
        weights[quad] = sum(row[0] for row in scored)
        out.append("")
        out.append(f"{LABELS[quad]}  | total weight: {weights[quad]}")
        if not scored:
            out.append("  (no factors)")
        for rank, (sc, text, imp, conf) in enumerate(scored, 1):
            out.append(f"  {rank}. [{sc:>2}] (I{imp} x C{conf})  {text}")

    best, pairs = posture(weights)
    out.append("")
    out.append("=" * 60)
    out.append("STRATEGIC POSTURE (by paired quadrant weight)")
    for name, val in sorted(pairs.items(), key=lambda x: x[1], reverse=True):
        marker = "  <-- recommended" if name == best else ""
        out.append(f"  {val:>4}  {name}{marker}")
    out.append("")
    out.append(f"=> Recommended posture: {best}")
    out.append("   Next: run the TOWS matrix on the top-ranked factors above")
    out.append("   to generate concrete strategies, then turn them into actions.")
    return "\n".join(out)


def main(argv=None):
    p = argparse.ArgumentParser(description="Rank SWOT factors and infer posture.")
    p.add_argument("path", nargs="?", help="Path to SWOT JSON, or '-' for stdin")
    p.add_argument("--example", action="store_true",
                   help="Run on a built-in example input")
    args = p.parse_args(argv)

    if args.example:
        print("# Example input:")
        print(json.dumps(EXAMPLE, indent=2))
        print("\n# Output:")
        print(run(EXAMPLE))
        return 0

    if not args.path:
        p.error("provide a JSON path, '-' for stdin, or --example")

    try:
        if args.path == "-":
            data = json.load(sys.stdin)
        else:
            with open(args.path, "r", encoding="utf-8") as fh:
                data = json.load(fh)
    except (OSError, json.JSONDecodeError) as e:
        print(f"error: could not read JSON: {e}", file=sys.stderr)
        return 1

    try:
        print(run(data))
    except ValueError as e:
        print(f"error: invalid SWOT input: {e}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
