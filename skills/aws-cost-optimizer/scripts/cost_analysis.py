#!/usr/bin/env python3
"""AWS cost-waste analyzer (stdlib only).

Reads a JSON inventory of AWS resources (with utilization/cost metadata),
scores each resource for waste, and prints ranked cost-reduction
recommendations with estimated monthly savings, effort, and risk.

This does NOT call AWS. Feed it an inventory you exported (e.g. from the
AWS CLI, Cost Explorer, or Compute Optimizer) shaped like examples below.

USAGE:
    python3 cost_analysis.py --inventory inventory.json
    python3 cost_analysis.py --inventory inventory.json --format md
    python3 cost_analysis.py --sample > inventory.json   # emit a sample file
    python3 cost_analysis.py --inventory inventory.json --min-savings 5

INVENTORY SCHEMA (list of resource objects):
  {
    "id": "vol-0abc",
    "type": "ebs",                 # ebs|eip|ec2|rds|elb|nat|snapshot
    "monthly_cost": 50.0,           # current $/month
    "attached": false,              # ebs/eip: is it in use?
    "volume_type": "gp2",           # ebs: gp2|gp3|io1|...
    "cpu_p95": 12.0,                # ec2/rds: percent
    "cpu_max": 30.0,                # ec2/rds: percent
    "days_observed": 14,            # metric window
    "state": "running",             # ec2: running|stopped
    "connections": 0,               # rds: avg connections
    "request_count": 0,             # elb: requests over window
    "bytes_processed": 0,           # nat: bytes over window
    "age_days": 400,                # snapshot/stopped age
    "orphaned": true,               # snapshot: source gone
    "tags": {"team": "platform"}
  }
"""
import argparse
import json
import sys

# (effort, risk) per recommendation kind
EFFORT = {
    "delete_unattached_ebs": ("low", "low"),
    "release_eip": ("low", "low"),
    "gp2_to_gp3": ("low", "low"),
    "delete_orphaned_snapshot": ("low", "low"),
    "delete_idle_elb": ("low", "low"),
    "review_idle_nat": ("medium", "medium"),
    "terminate_stopped_ec2": ("medium", "medium"),
    "rightsize_ec2": ("high", "medium"),
    "rightsize_rds": ("high", "medium"),
    "stop_idle_rds": ("medium", "medium"),
}

CPU_P95_THRESHOLD = 40.0
CPU_MAX_THRESHOLD = 60.0
MIN_DAYS = 14
GP2_GP3_SAVINGS = 0.20
RIGHTSIZE_SAVINGS = 0.50  # one size step


def analyze(resources):
    findings = []
    for r in resources:
        rtype = r.get("type")
        cost = float(r.get("monthly_cost", 0) or 0)
        rid = r.get("id", "?")
        tags = r.get("tags", {}) or {}
        owner = tags.get("owner") or tags.get("team") or "UNTAGGED"

        def add(kind, savings, why):
            effort, risk = EFFORT.get(kind, ("medium", "medium"))
            findings.append({
                "id": rid, "type": rtype, "kind": kind,
                "monthly_savings": round(savings, 2),
                "effort": effort, "risk": risk,
                "owner": owner, "why": why,
            })

        if rtype == "ebs":
            if r.get("attached") is False:
                add("delete_unattached_ebs", cost,
                    "Volume is unattached (state=available); pure waste.")
            elif r.get("volume_type") == "gp2":
                add("gp2_to_gp3", cost * GP2_GP3_SAVINGS,
                    "gp2 volume; gp3 is ~20% cheaper with tunable IOPS.")
        elif rtype == "eip":
            if r.get("attached") is False:
                add("release_eip", cost,
                    "Elastic IP not associated to a running instance.")
        elif rtype == "snapshot":
            if r.get("orphaned") or (r.get("age_days", 0) > 365):
                add("delete_orphaned_snapshot", cost,
                    "Snapshot orphaned or older than retention.")
        elif rtype == "elb":
            if r.get("request_count", 0) == 0:
                add("delete_idle_elb", cost,
                    "Load balancer with zero traffic over window.")
        elif rtype == "nat":
            if r.get("bytes_processed", 0) == 0:
                add("review_idle_nat", cost,
                    "NAT gateway processed ~0 bytes; consolidate or use endpoints.")
        elif rtype == "ec2":
            if r.get("state") == "stopped" and r.get("age_days", 0) > 30:
                add("terminate_stopped_ec2", cost,
                    "Stopped >30d but still incurring EBS cost.")
            elif r.get("state") == "running":
                if (r.get("days_observed", 0) >= MIN_DAYS
                        and r.get("cpu_p95", 100) < CPU_P95_THRESHOLD
                        and r.get("cpu_max", 100) < CPU_MAX_THRESHOLD):
                    add("rightsize_ec2", cost * RIGHTSIZE_SAVINGS,
                        "p95 CPU %.0f%%, max %.0f%% over %dd; downsize one step." % (
                            r.get("cpu_p95", 0), r.get("cpu_max", 0),
                            r.get("days_observed", 0)))
        elif rtype == "rds":
            if r.get("connections", 1) == 0 and r.get("days_observed", 0) >= MIN_DAYS:
                add("stop_idle_rds", cost,
                    "No DB connections over window; stop or delete.")
            elif (r.get("days_observed", 0) >= MIN_DAYS
                    and r.get("cpu_p95", 100) < CPU_P95_THRESHOLD):
                add("rightsize_rds", cost * RIGHTSIZE_SAVINGS,
                    "RDS p95 CPU %.0f%%; right-size compute." % r.get("cpu_p95", 0))

    findings.sort(key=lambda f: f["monthly_savings"], reverse=True)
    return findings


def format_table(findings):
    if not findings:
        return "No findings."
    rows = ["%-18s %-12s %-26s %10s  %-6s %-6s %s" % (
        "ID", "TYPE", "ACTION", "$/MO", "EFFORT", "RISK", "OWNER")]
    rows.append("-" * 110)
    for f in findings:
        rows.append("%-18s %-12s %-26s %10.2f  %-6s %-6s %s" % (
            f["id"][:18], f["type"], f["kind"][:26], f["monthly_savings"],
            f["effort"], f["risk"], f["owner"]))
    return "\n".join(rows)


def format_md(findings):
    lines = ["| ID | Type | Action | $/mo | Effort | Risk | Owner | Why |",
             "|---|---|---|---|---|---|---|---|"]
    for f in findings:
        lines.append("| %s | %s | %s | %.2f | %s | %s | %s | %s |" % (
            f["id"], f["type"], f["kind"], f["monthly_savings"],
            f["effort"], f["risk"], f["owner"], f["why"]))
    return "\n".join(lines)


SAMPLE = [
    {"id": "vol-0idle", "type": "ebs", "monthly_cost": 50.0, "attached": False,
     "tags": {"team": "data"}},
    {"id": "vol-0gp2", "type": "ebs", "monthly_cost": 80.0, "attached": True,
     "volume_type": "gp2", "tags": {"team": "web"}},
    {"id": "eipalloc-0x", "type": "eip", "monthly_cost": 3.6, "attached": False,
     "tags": {}},
    {"id": "i-0big", "type": "ec2", "monthly_cost": 600.0, "state": "running",
     "cpu_p95": 12.0, "cpu_max": 28.0, "days_observed": 21,
     "tags": {"team": "payments", "owner": "jane@corp.com"}},
    {"id": "i-0stopped", "type": "ec2", "monthly_cost": 40.0, "state": "stopped",
     "age_days": 120, "tags": {"team": "qa"}},
    {"id": "db-idle", "type": "rds", "monthly_cost": 320.0, "connections": 0,
     "days_observed": 30, "tags": {}},
    {"id": "nat-0z", "type": "nat", "monthly_cost": 32.0, "bytes_processed": 0,
     "tags": {"team": "net"}},
    {"id": "snap-0old", "type": "snapshot", "monthly_cost": 15.0,
     "orphaned": True, "age_days": 500, "tags": {}},
]


def main(argv=None):
    p = argparse.ArgumentParser(description="AWS cost-waste analyzer (stdlib only)")
    p.add_argument("--inventory", help="path to inventory JSON file")
    p.add_argument("--format", choices=["table", "md"], default="table")
    p.add_argument("--min-savings", type=float, default=0.0,
                   help="hide findings below this $/month")
    p.add_argument("--sample", action="store_true",
                   help="print a sample inventory JSON and exit")
    args = p.parse_args(argv)

    if args.sample:
        print(json.dumps(SAMPLE, indent=2))
        return 0

    if not args.inventory:
        p.error("--inventory is required (or use --sample)")

    try:
        with open(args.inventory) as fh:
            resources = json.load(fh)
    except (OSError, ValueError) as e:
        print("Error reading inventory: %s" % e, file=sys.stderr)
        return 1

    if not isinstance(resources, list):
        print("Inventory must be a JSON list of resource objects.", file=sys.stderr)
        return 1

    findings = [f for f in analyze(resources)
                if f["monthly_savings"] >= args.min_savings]
    total = sum(f["monthly_savings"] for f in findings)

    if args.format == "md":
        print(format_md(findings))
    else:
        print(format_table(findings))

    print("\nTotal addressable savings: $%.2f/month  (~$%.2f/year)" % (
        total, total * 12))
    print("Findings: %d" % len(findings))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
