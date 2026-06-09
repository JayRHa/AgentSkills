#!/usr/bin/env python3
"""Critical Path Method (CPM) calculator.

Reads a JSON task list and computes, for each task, the earliest/latest
start and finish, total slack (float), and flags the critical path.
Also prints the overall project duration and the critical chain.

Input JSON format (a list of tasks):
[
  {"id": "A", "name": "Design",  "duration": 3, "predecessors": []},
  {"id": "B", "name": "Build",   "duration": 2, "predecessors": []},
  {"id": "C", "name": "Integrate","duration": 2, "predecessors": ["A", "B"]},
  {"id": "D", "name": "Launch",  "duration": 4, "predecessors": ["C"]}
]

Duration may be in any consistent unit (days or hours). Only Finish-to-Start
dependencies are modeled (the common case); add lead/lag manually if needed.

Usage:
  python3 critical_path.py tasks.json
  python3 critical_path.py tasks.json --json     # machine-readable output
  cat tasks.json | python3 critical_path.py -     # read from stdin
"""
import argparse
import json
import sys


def load_tasks(source):
    raw = sys.stdin.read() if source == "-" else open(source, encoding="utf-8").read()
    data = json.loads(raw)
    if not isinstance(data, list):
        raise ValueError("Top-level JSON must be a list of task objects.")
    tasks = {}
    for t in data:
        tid = t["id"]
        if tid in tasks:
            raise ValueError(f"Duplicate task id: {tid}")
        tasks[tid] = {
            "id": tid,
            "name": t.get("name", tid),
            "duration": float(t["duration"]),
            "predecessors": list(t.get("predecessors", [])),
        }
    for t in tasks.values():
        for p in t["predecessors"]:
            if p not in tasks:
                raise ValueError(f"Task {t['id']} references unknown predecessor {p}")
    return tasks


def topological_order(tasks):
    """Kahn's algorithm; raises on cycles."""
    indeg = {tid: 0 for tid in tasks}
    succ = {tid: [] for tid in tasks}
    for t in tasks.values():
        for p in t["predecessors"]:
            indeg[t["id"]] += 1
            succ[p].append(t["id"])
    queue = sorted([tid for tid, d in indeg.items() if d == 0])
    order = []
    while queue:
        n = queue.pop(0)
        order.append(n)
        for s in succ[n]:
            indeg[s] -= 1
            if indeg[s] == 0:
                queue.append(s)
        queue.sort()
    if len(order) != len(tasks):
        cyc = [tid for tid, d in indeg.items() if d > 0]
        raise ValueError(f"Dependency cycle detected involving: {sorted(cyc)}")
    return order, succ


def compute_cpm(tasks):
    order, succ = topological_order(tasks)
    es, ef, ls, lf = {}, {}, {}, {}

    # Forward pass
    for tid in order:
        preds = tasks[tid]["predecessors"]
        es[tid] = max((ef[p] for p in preds), default=0.0)
        ef[tid] = es[tid] + tasks[tid]["duration"]
    project_duration = max(ef.values()) if ef else 0.0

    # Backward pass
    for tid in reversed(order):
        succs = succ[tid]
        lf[tid] = min((ls[s] for s in succs), default=project_duration)
        ls[tid] = lf[tid] - tasks[tid]["duration"]

    results = {}
    for tid in tasks:
        slack = round(ls[tid] - es[tid], 6)
        results[tid] = {
            "id": tid,
            "name": tasks[tid]["name"],
            "duration": tasks[tid]["duration"],
            "ES": es[tid], "EF": ef[tid], "LS": ls[tid], "LF": lf[tid],
            "slack": slack,
            "critical": abs(slack) < 1e-9,
        }
    return results, project_duration, order


def critical_chain(results, order):
    return [tid for tid in order if results[tid]["critical"]]


def fmt(n):
    return str(int(n)) if float(n).is_integer() else f"{n:.2f}"


def print_table(results, project_duration, order):
    headers = ["ID", "Task", "Dur", "ES", "EF", "LS", "LF", "Slack", "Critical"]
    rows = []
    for tid in order:
        r = results[tid]
        rows.append([
            r["id"], r["name"][:28], fmt(r["duration"]),
            fmt(r["ES"]), fmt(r["EF"]), fmt(r["LS"]), fmt(r["LF"]),
            fmt(r["slack"]), "YES" if r["critical"] else "",
        ])
    widths = [max(len(h), *(len(row[i]) for row in rows)) if rows else len(h)
              for i, h in enumerate(headers)]
    line = "  ".join(h.ljust(widths[i]) for i, h in enumerate(headers))
    print(line)
    print("  ".join("-" * widths[i] for i in range(len(headers))))
    for row in rows:
        print("  ".join(c.ljust(widths[i]) for i, c in enumerate(row)))
    chain = critical_chain(results, order)
    print()
    print(f"Project duration: {fmt(project_duration)}")
    print(f"Critical path:    {' -> '.join(chain)}")


def main():
    ap = argparse.ArgumentParser(description="Critical Path Method calculator.")
    ap.add_argument("source", help="Path to tasks JSON file, or '-' for stdin.")
    ap.add_argument("--json", action="store_true", help="Emit JSON instead of a table.")
    args = ap.parse_args()

    try:
        tasks = load_tasks(args.source)
        results, project_duration, order = compute_cpm(tasks)
    except (ValueError, KeyError, json.JSONDecodeError) as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    if args.json:
        print(json.dumps({
            "project_duration": project_duration,
            "critical_path": critical_chain(results, order),
            "tasks": [results[tid] for tid in order],
        }, indent=2))
    else:
        print_table(results, project_duration, order)
    return 0


if __name__ == "__main__":
    sys.exit(main())
