#!/usr/bin/env python3
"""Analyze a PostgreSQL EXPLAIN plan in JSON format and flag likely problems.

Usage:
    # Capture the plan as JSON:
    #   EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON) <your query>;
    # Save it to a file, then:
    python3 explain_analyzer.py plan.json
    psql -At -c "EXPLAIN (ANALYZE, FORMAT JSON) SELECT ..." | python3 explain_analyzer.py -

Flags:
    --top N        Show the N most expensive nodes (default 5).
    --skew N       Row estimate/actual ratio to flag as mis-estimate (default 10).

Detects: sequential scans on large tables, estimate-vs-actual row skew, disk-spilling
sorts/hashes, and high-loop nested nodes. Pure standard library; no dependencies.
"""
import argparse
import json
import sys


def load_plan(path):
    raw = sys.stdin.read() if path == "-" else open(path, "r", encoding="utf-8").read()
    data = json.loads(raw)
    # EXPLAIN FORMAT JSON returns a list with one object holding "Plan".
    if isinstance(data, list):
        data = data[0]
    if "Plan" not in data:
        sys.exit("error: input does not look like a PostgreSQL EXPLAIN JSON plan (no 'Plan' key)")
    return data["Plan"]


def walk(node, depth=0):
    """Yield (node, depth) for every node depth-first."""
    yield node, depth
    for child in node.get("Plans", []) or []:
        yield from walk(child, depth + 1)


def node_self_time(node):
    """Approximate time spent in this node (excl. children) * loops, in ms."""
    total = node.get("Actual Total Time")
    loops = node.get("Actual Loops", 1) or 1
    if total is None:
        return None
    incl = total * loops
    child_incl = 0.0
    for c in node.get("Plans", []) or []:
        ct = c.get("Actual Total Time")
        cl = c.get("Actual Loops", 1) or 1
        if ct is not None:
            child_incl += ct * cl
    return max(incl - child_incl, 0.0)


def label(node):
    name = node.get("Node Type", "?")
    rel = node.get("Relation Name")
    idx = node.get("Index Name")
    parts = [name]
    if rel:
        parts.append("on " + rel)
    if idx:
        parts.append("using " + idx)
    return " ".join(parts)


def analyze(plan, top, skew):
    findings = []
    nodes = list(walk(plan))

    for node, _ in nodes:
        nt = node.get("Node Type", "")
        est = node.get("Plan Rows")
        act = node.get("Actual Rows")
        loops = node.get("Actual Loops", 1) or 1

        # Sequential scan returning many rows
        if nt == "Seq Scan":
            rows = (act if act is not None else est) or 0
            if rows >= 10000:
                findings.append(
                    f"SEQ SCAN: {label(node)} read ~{rows:,} rows. "
                    f"If the filter is selective, add an index on the filtered column(s)."
                )

        # Row estimate skew
        if est is not None and act is not None and est > 0 and act > 0:
            ratio = max(est / act, act / est)
            if ratio >= skew:
                findings.append(
                    f"ROW SKEW: {label(node)} estimated {est:,} vs actual {act:,} "
                    f"({ratio:.0f}x off). Run ANALYZE; consider extended statistics."
                )

        # Disk-spilling sort
        if node.get("Sort Method", "").startswith("external"):
            disk = node.get("Sort Space Used", "?")
            findings.append(
                f"DISK SORT: {label(node)} spilled to disk ({disk}kB). "
                f"Add an index to serve ORDER BY, or raise work_mem."
            )

        # Hash batches > 1 means hash spilled to disk
        if nt == "Hash" and (node.get("Hash Batches", 1) or 1) > 1:
            findings.append(
                f"HASH SPILL: {label(node)} used {node.get('Hash Batches')} batches "
                f"(spilled to disk). Reduce input size or raise work_mem."
            )

        # High-loop nested node (possible N+1 / missing inner index)
        if loops >= 1000 and node.get("Actual Total Time") is not None:
            findings.append(
                f"HIGH LOOPS: {label(node)} executed {loops:,} times "
                f"({node.get('Actual Total Time')}ms each). Check join index / N+1."
            )

    # Hottest nodes by self time
    timed = [(node_self_time(n), n) for n, _ in nodes]
    timed = [(t, n) for t, n in timed if t is not None]
    timed.sort(key=lambda x: x[0], reverse=True)

    return findings, timed[:top]


def main():
    ap = argparse.ArgumentParser(description="Flag problems in a PostgreSQL EXPLAIN JSON plan.")
    ap.add_argument("plan", help="path to JSON plan file, or '-' for stdin")
    ap.add_argument("--top", type=int, default=5, help="show N hottest nodes (default 5)")
    ap.add_argument("--skew", type=float, default=10.0, help="row est/act ratio to flag (default 10)")
    args = ap.parse_args()

    plan = load_plan(args.plan)
    findings, hottest = analyze(plan, args.top, args.skew)

    print("=" * 60)
    print("HOTTEST NODES (self time, includes loops)")
    print("=" * 60)
    if not hottest:
        print("  (no actual-time data; run EXPLAIN ANALYZE, not plain EXPLAIN)")
    for t, n in hottest:
        print(f"  {t:10.2f} ms  {label(n)}")

    print()
    print("=" * 60)
    print(f"FINDINGS ({len(findings)})")
    print("=" * 60)
    if not findings:
        print("  No common problems detected. Review the hottest node manually.")
    for i, f in enumerate(findings, 1):
        print(f"  {i}. {f}")

    # Non-zero exit if we found something actionable (handy in CI).
    sys.exit(1 if findings else 0)


if __name__ == "__main__":
    main()
