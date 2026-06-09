#!/usr/bin/env python3
"""cronlint.py - validate, explain, and preview classic 5-field cron expressions.

Stdlib-only. Parses a standard Vixie/POSIX 5-field cron expression (or a macro
like @daily), prints a plain-language breakdown, flags the day-of-month /
day-of-week OR-logic trap, and lists the next N fire times.

Usage:
    python3 cronlint.py "<expression>" [-n N] [--from ISO_DATETIME]

Examples:
    python3 cronlint.py "*/15 9-17 * * 1-5"
    python3 cronlint.py "@daily" -n 3
    python3 cronlint.py "0 0 13 * 5" -n 5 --from 2026-06-08T00:00

Field order: minute hour day-of-month month day-of-week
Day-of-week: 0-7 where 0 and 7 are Sunday; names sun-sat accepted.
Month names jan-dec accepted.

Note: next-run computation uses the local wall clock of whatever machine runs
this script and does NOT model DST transitions. Treat the previews as guidance,
not a substitute for the target scheduler's timezone semantics.
"""
import argparse
import datetime
import sys

DOW_NAMES = {"sun": 0, "mon": 1, "tue": 2, "wed": 3, "thu": 4, "fri": 5, "sat": 6}
MON_NAMES = {"jan": 1, "feb": 2, "mar": 3, "apr": 4, "may": 5, "jun": 6,
             "jul": 7, "aug": 8, "sep": 9, "oct": 10, "nov": 11, "dec": 12}
MACROS = {
    "@yearly": "0 0 1 1 *", "@annually": "0 0 1 1 *",
    "@monthly": "0 0 1 * *", "@weekly": "0 0 * * 0",
    "@daily": "0 0 * * *", "@midnight": "0 0 * * *",
    "@hourly": "0 * * * *",
}


def resolve(token, names):
    token = token.strip().lower()
    if names and token in names:
        return names[token]
    return int(token)


def parse_field(field, lo, hi, names=None):
    values = set()
    for part in field.split(","):
        step = 1
        if "/" in part:
            part, step_s = part.split("/", 1)
            step = int(step_s)
            if step <= 0:
                raise ValueError("step must be positive")
        if part == "*":
            start, end = lo, hi
        elif "-" in part and not part.lstrip("-").isdigit():
            a, b = part.split("-", 1)
            start, end = resolve(a, names), resolve(b, names)
        elif "-" in part:
            a, b = part.split("-", 1)
            start, end = resolve(a, names), resolve(b, names)
        else:
            start = end = resolve(part, names)
        if start > end:
            raise ValueError(f"range start {start} > end {end}")
        for v in range(start, end + 1, step):
            if not (lo <= v <= hi):
                raise ValueError(f"value {v} out of range {lo}-{hi}")
            values.add(v)
    return values


def parse(expr):
    expr = expr.strip()
    if expr in MACROS:
        expr = MACROS[expr]
    fields = expr.split()
    if len(fields) != 5:
        raise ValueError(f"expected 5 fields, got {len(fields)}: {expr!r}")
    dow = parse_field(fields[4], 0, 7, DOW_NAMES)
    if 7 in dow:
        dow.discard(7)
        dow.add(0)
    return {
        "minute": parse_field(fields[0], 0, 59),
        "hour": parse_field(fields[1], 0, 23),
        "dom": parse_field(fields[2], 1, 31),
        "month": parse_field(fields[3], 1, 12, MON_NAMES),
        "dow": dow,
        "_dom_star": fields[2] == "*",
        "_dow_star": fields[4] == "*",
    }


def matches(p, dt):
    if dt.minute not in p["minute"]:
        return False
    if dt.hour not in p["hour"]:
        return False
    if dt.month not in p["month"]:
        return False
    dom_ok = dt.day in p["dom"]
    # Python weekday(): Mon=0..Sun=6; cron: Sun=0..Sat=6
    dow_ok = ((dt.weekday() + 1) % 7) in p["dow"]
    if p["_dom_star"] and p["_dow_star"]:
        return True
    if p["_dom_star"]:
        return dow_ok
    if p["_dow_star"]:
        return dom_ok
    # Both restricted -> Vixie cron OR semantics
    return dom_ok or dow_ok


def next_runs(p, start, n):
    out = []
    dt = start.replace(second=0, microsecond=0) + datetime.timedelta(minutes=1)
    limit = 525600 * 4  # ~4 years of minutes
    while len(out) < n and limit > 0:
        if matches(p, dt):
            out.append(dt)
        dt += datetime.timedelta(minutes=1)
        limit -= 1
    return out


def _fmt(values, full_len):
    s = sorted(values)
    if len(s) == full_len:
        return "every"
    return ",".join(str(v) for v in s)


def explain(p):
    lines = [
        f"  minute       = {_fmt(p['minute'], 60)}",
        f"  hour         = {_fmt(p['hour'], 24)}",
        f"  day-of-month = {'*' if p['_dom_star'] else _fmt(p['dom'], 31)}",
        f"  month        = {_fmt(p['month'], 12)}",
        f"  day-of-week  = {'*' if p['_dow_star'] else _fmt(p['dow'], 7)} (0=Sun)",
    ]
    out = "\n".join(lines)
    if not p["_dom_star"] and not p["_dow_star"]:
        out += ("\n  WARNING: day-of-month AND day-of-week are both restricted.\n"
                "           Cron fires when EITHER matches (OR logic), not both.")
    return out


def main():
    ap = argparse.ArgumentParser(
        description="Validate, explain, and preview classic 5-field cron expressions.")
    ap.add_argument("expr", help="cron expression or macro, e.g. '*/15 9-17 * * 1-5' or '@daily'")
    ap.add_argument("-n", "--next", type=int, default=5, help="number of upcoming runs to show")
    ap.add_argument("--from", dest="frm", help="ISO datetime to compute from (default: now)")
    args = ap.parse_args()

    try:
        p = parse(args.expr)
    except Exception as e:
        print(f"INVALID: {e}", file=sys.stderr)
        sys.exit(1)

    print(f"VALID: {args.expr}")
    print(explain(p))

    start = datetime.datetime.fromisoformat(args.frm) if args.frm else datetime.datetime.now()
    base = start.replace(second=0, microsecond=0)
    print(f"\nNext {args.next} runs (computed from {base}, local wall clock, no DST modeling):")
    runs = next_runs(p, start, args.next)
    if not runs:
        print("  (no matching runs found within ~4 years)")
    for r in runs:
        print("  " + r.strftime("%Y-%m-%d %H:%M  %a"))


if __name__ == "__main__":
    main()
