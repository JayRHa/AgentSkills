#!/usr/bin/env python3
"""timeline_builder.py - Build a clean incident timeline and compute key metrics.

Reads a simple pipe-delimited events file and produces:
  1. A sorted, normalized timeline table (Markdown).
  2. Incident metrics: time-to-detect (TTD), time-to-mitigate (TTM),
     time-to-resolve (TTR), and total duration.

Input format (one event per line; '#' and blank lines ignored):

    <ISO8601 timestamp> | <actor/system> | <tag> | <description>

The <tag> is optional but powers metric detection. Recognized tags
(case-insensitive): start, detect, ack, mitigate, resolve. A line with no
tag column is treated as a plain event (use 3 fields: ts | actor | desc).

Timestamps may include a trailing 'Z' or an offset like '+02:00'; all are
normalized to UTC for sorting and metrics.

Usage:
    python3 timeline_builder.py events.txt
    python3 timeline_builder.py events.txt --md         # Markdown timeline only
    python3 timeline_builder.py events.txt --metrics     # metrics only
    cat events.txt | python3 timeline_builder.py -        # read from stdin

Example events.txt:
    2026-06-08T14:02:00Z | deploy-bot | start    | Deploy v812 shipped to checkout-service
    2026-06-08T14:10:00Z | datadog    | detect   | Alert: API 5xx rate > 5%
    2026-06-08T14:12:00Z | priya      | ack      | On-call acknowledged page
    2026-06-08T14:24:00Z | priya      | mitigate | Rolled back to v811
    2026-06-08T14:53:00Z | priya      | resolve  | Error rate back to baseline, incident closed

Standard library only. Exit code 0 on success, 1 on input error.
"""
import argparse
import sys
from datetime import datetime, timezone

TAGS = {"start", "detect", "ack", "mitigate", "resolve"}


def parse_ts(raw):
    """Parse an ISO-8601 timestamp into a UTC-aware datetime."""
    s = raw.strip()
    if s.endswith("Z"):
        s = s[:-1] + "+00:00"
    try:
        dt = datetime.fromisoformat(s)
    except ValueError as exc:
        raise ValueError(f"bad timestamp {raw!r}: {exc}") from exc
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def parse_events(lines):
    """Parse raw lines into a list of event dicts, sorted by time."""
    events = []
    for n, line in enumerate(lines, 1):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = [p.strip() for p in line.split("|")]
        if len(parts) == 4:
            ts, actor, tag, desc = parts
            tag = tag.lower()
        elif len(parts) == 3:
            ts, actor, desc = parts
            tag = ""
        else:
            raise ValueError(
                f"line {n}: expected 3 or 4 '|'-separated fields, got {len(parts)}: {line!r}"
            )
        events.append({
            "ts": parse_ts(ts),
            "actor": actor,
            "tag": tag if tag in TAGS else "",
            "desc": desc,
        })
    events.sort(key=lambda e: e["ts"])
    return events


def fmt(dt):
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")


def render_markdown(events):
    out = ["| Time (UTC) | Actor/System | Event |", "|---|---|---|"]
    for e in events:
        marker = f"**[{e['tag']}]** " if e["tag"] else ""
        out.append(f"| {fmt(e['ts'])} | {e['actor']} | {marker}{e['desc']} |")
    return "\n".join(out)


def human_delta(seconds):
    if seconds is None:
        return "n/a"
    m, s = divmod(int(seconds), 60)
    h, m = divmod(m, 60)
    if h:
        return f"{h}h {m}m {s}s"
    if m:
        return f"{m}m {s}s"
    return f"{s}s"


def first(events, tag):
    for e in events:
        if e["tag"] == tag:
            return e["ts"]
    return None


def compute_metrics(events):
    start = first(events, "start") or (events[0]["ts"] if events else None)
    detect = first(events, "detect")
    mitigate = first(events, "mitigate")
    resolve = first(events, "resolve") or (events[-1]["ts"] if events else None)

    def delta(a, b):
        if a is None or b is None:
            return None
        return (b - a).total_seconds()

    return {
        "Incident start": fmt(start) if start else "n/a",
        "Detected": fmt(detect) if detect else "n/a",
        "Mitigated": fmt(mitigate) if mitigate else "n/a",
        "Resolved": fmt(resolve) if resolve else "n/a",
        "Time to detect (TTD)": human_delta(delta(start, detect)),
        "Time to mitigate (TTM)": human_delta(delta(start, mitigate)),
        "Time to resolve (TTR)": human_delta(delta(start, resolve)),
        "Total duration": human_delta(delta(start, resolve)),
    }


def render_metrics(metrics):
    width = max(len(k) for k in metrics)
    lines = ["Incident metrics", "=" * 16]
    for k, v in metrics.items():
        lines.append(f"{k.ljust(width)} : {v}")
    return "\n".join(lines)


def main(argv=None):
    ap = argparse.ArgumentParser(description="Build incident timeline and metrics.")
    ap.add_argument("events", help="path to events file, or '-' for stdin")
    ap.add_argument("--md", action="store_true", help="output Markdown timeline only")
    ap.add_argument("--metrics", action="store_true", help="output metrics only")
    args = ap.parse_args(argv)

    try:
        if args.events == "-":
            lines = sys.stdin.read().splitlines()
        else:
            with open(args.events, encoding="utf-8") as fh:
                lines = fh.read().splitlines()
        events = parse_events(lines)
    except (OSError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    if not events:
        print("error: no events parsed", file=sys.stderr)
        return 1

    show_md = args.md or not args.metrics
    show_metrics = args.metrics or not args.md

    blocks = []
    if show_md:
        blocks.append("## Timeline\n\n" + render_markdown(events))
    if show_metrics:
        blocks.append(render_metrics(compute_metrics(events)))
    print("\n\n".join(blocks))
    return 0


if __name__ == "__main__":
    sys.exit(main())
