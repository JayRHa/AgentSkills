#!/usr/bin/env python3
"""Generate a sorted risk register from a STRIDE threat list.

Reads a list of threats from a YAML or JSON file and prints a Markdown risk
register sorted by risk score (descending), plus summary statistics by STRIDE
category and risk bucket. Pure standard library (a tiny YAML subset parser is
included so PyYAML is not required).

Input schema (per threat):
  id:          str   (e.g. "T-01")
  title:       str
  stride:      str   one of S,T,R,I,D,E (or full word)
  element:     str   DFD element id/name the threat targets
  likelihood:  int   1-5
  impact:      int   1-5
  mitigation:  str
  status:      str   Proposed | Planned | Implemented   (optional)

Usage:
  python3 threat_report.py threats.yaml
  python3 threat_report.py threats.json --format md > risk-register.md
  cat threats.yaml | python3 threat_report.py -

Example threats.yaml:
  - id: T-01
    title: Forged webhook calls (no signature verification)
    stride: S
    element: DF1
    likelihood: 4
    impact: 4
    mitigation: Verify HMAC signature + timestamp anti-replay
    status: Implemented
"""
import argparse
import json
import sys

STRIDE_NAMES = {
    "S": "Spoofing", "T": "Tampering", "R": "Repudiation",
    "I": "Information disclosure", "D": "Denial of service",
    "E": "Elevation of privilege",
}
FULL_TO_LETTER = {v.lower(): k for k, v in STRIDE_NAMES.items()}


def bucket(score):
    if score >= 20:
        return "Critical"
    if score >= 12:
        return "High"
    if score >= 6:
        return "Medium"
    return "Low"


def normalize_stride(value):
    if value is None:
        return "?"
    v = str(value).strip()
    if v.upper() in STRIDE_NAMES:
        return v.upper()
    return FULL_TO_LETTER.get(v.lower(), v[:1].upper())


def _coerce(raw):
    """Turn a scalar string into int/float/bool/str."""
    s = raw.strip()
    if (s.startswith('"') and s.endswith('"')) or (s.startswith("'") and s.endswith("'")):
        return s[1:-1]
    for caster in (int, float):
        try:
            return caster(s)
        except ValueError:
            pass
    low = s.lower()
    if low in ("true", "false"):
        return low == "true"
    if low in ("null", "~", "none", ""):
        return None
    return s


def parse_minimal_yaml(text):
    """Parse a YAML subset: a list of mappings (key: value), the shape this
    tool documents. Items begin with '- '. Falls back cleanly on JSON."""
    items = []
    current = None
    for line_no, raw in enumerate(text.splitlines(), 1):
        line = raw.split(" #")[0].rstrip()
        if not line.strip() or line.strip().startswith("#"):
            continue
        stripped = line.lstrip()
        if stripped.startswith("- "):
            if current is not None:
                items.append(current)
            current = {}
            stripped = stripped[2:]
        elif stripped == "-":
            if current is not None:
                items.append(current)
            current = {}
            continue
        if ":" not in stripped:
            raise ValueError(f"line {line_no}: expected 'key: value', got {raw!r}")
        key, _, value = stripped.partition(":")
        if current is None:
            current = {}
        current[key.strip()] = _coerce(value)
    if current is not None:
        items.append(current)
    return items


def load(path):
    text = sys.stdin.read() if path == "-" else open(path, encoding="utf-8").read()
    stripped = text.lstrip()
    if stripped.startswith("[") or stripped.startswith("{"):
        data = json.loads(text)
    else:
        data = parse_minimal_yaml(text)
    if isinstance(data, dict):
        data = data.get("threats", [data])
    if not isinstance(data, list):
        raise ValueError("input must be a list of threats")
    return data


def enrich(threats):
    out = []
    for t in threats:
        likelihood = int(t.get("likelihood", 0) or 0)
        impact = int(t.get("impact", 0) or 0)
        score = likelihood * impact
        out.append({
            "id": t.get("id", "?"),
            "title": t.get("title", ""),
            "stride": normalize_stride(t.get("stride")),
            "element": t.get("element", ""),
            "likelihood": likelihood,
            "impact": impact,
            "score": score,
            "bucket": bucket(score),
            "mitigation": t.get("mitigation", ""),
            "status": t.get("status", "Proposed"),
        })
    out.sort(key=lambda r: r["score"], reverse=True)
    return out


def render_md(rows):
    lines = ["# Risk Register", ""]
    lines.append("| ID | Risk | Score | STRIDE | Element | Threat | Mitigation | Status |")
    lines.append("|---|---|:-:|---|---|---|---|---|")
    for r in rows:
        lines.append(
            f"| {r['id']} | {r['bucket']} | {r['score']} "
            f"({r['likelihood']}x{r['impact']}) | {r['stride']} {STRIDE_NAMES.get(r['stride'],'')} "
            f"| {r['element']} | {r['title']} | {r['mitigation']} | {r['status']} |"
        )
    lines += ["", "## Summary", ""]
    by_bucket = {}
    by_stride = {}
    for r in rows:
        by_bucket[r["bucket"]] = by_bucket.get(r["bucket"], 0) + 1
        by_stride[r["stride"]] = by_stride.get(r["stride"], 0) + 1
    lines.append(f"Total threats: {len(rows)}")
    lines.append("")
    lines.append("By risk bucket:")
    for b in ("Critical", "High", "Medium", "Low"):
        if by_bucket.get(b):
            lines.append(f"- {b}: {by_bucket[b]}")
    lines.append("")
    lines.append("By STRIDE category:")
    for k in "STRIDE":
        if by_stride.get(k):
            lines.append(f"- {k} {STRIDE_NAMES[k]}: {by_stride[k]}")
    unmitigated = [r for r in rows if r["status"] != "Implemented" and r["bucket"] in ("Critical", "High")]
    if unmitigated:
        lines += ["", "## Action required (High/Critical, not Implemented)", ""]
        for r in unmitigated:
            lines.append(f"- {r['id']} [{r['bucket']}] {r['title']} -> {r['status']}")
    return "\n".join(lines)


def render_json(rows):
    return json.dumps(rows, indent=2)


def main(argv=None):
    ap = argparse.ArgumentParser(description="Sorted STRIDE risk register generator.")
    ap.add_argument("input", help="Path to YAML/JSON threat list, or '-' for stdin.")
    ap.add_argument("--format", choices=["md", "json"], default="md",
                    help="Output format (default: md).")
    args = ap.parse_args(argv)
    try:
        rows = enrich(load(args.input))
    except (ValueError, json.JSONDecodeError, OSError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    print(render_md(rows) if args.format == "md" else render_json(rows))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
