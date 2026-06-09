#!/usr/bin/env python3
"""Generate Prometheus multi-window multi-burn-rate SLO alert rules.

Produces recording rules for the SLI error ratio across the standard windows
plus paired-window burn-rate alerting rules (Google SRE method). Output is a
Prominetheus rule-group YAML written to stdout, ready to drop into a rules file.

No third-party dependencies (stdlib only); YAML is emitted as plain text so the
script runs anywhere Python 3.8+ is available.

Usage:
    python3 gen_slo_alerts.py \
        --service checkout \
        --job checkout-api \
        --slo 99.9 \
        --metric http_server_requests_total \
        --error-selector 'status=~"5.."' \
        --runbook https://runbooks.example.com/checkout

    # latency SLO (good = fast requests, using a histogram bucket):
    python3 gen_slo_alerts.py --service checkout --job checkout-api --slo 99.0 \
        --latency --metric http_server_request_duration_seconds --threshold 0.3

Exit codes: 0 ok, 2 on bad arguments.
"""
import argparse
import sys

# (severity, long_window, short_window, burn_rate)
BURN_TIERS = [
    ("page", "1h", "5m", 14.4),
    ("page", "6h", "30m", 6.0),
    ("ticket", "1d", "1h", 3.0),
    ("ticket", "3d", "6h", 1.0),
]

RECORD_WINDOWS = ["5m", "30m", "1h", "6h", "1d", "3d"]


def record_name(service, window):
    return f"job:slo_errors:ratio_rate{window}_{service}"


def availability_expr(metric, job, error_selector, window):
    base = f'job="{job}"'
    err = f'{base},{error_selector}'
    return (
        f'sum(rate({metric}{{{err}}}[{window}]))\n'
        f'          / sum(rate({metric}{{{base}}}[{window}]))'
    )


def latency_expr(metric, job, threshold, window):
    # good = requests at or under threshold (le bucket); bad ratio = 1 - good ratio
    base = f'job="{job}"'
    return (
        f'1 - (\n'
        f'            sum(rate({metric}_bucket{{{base},le="{threshold}"}}[{window}]))\n'
        f'            / sum(rate({metric}_count{{{base}}}[{window}]))\n'
        f'          )'
    )


def build_recording_rules(args):
    lines = []
    for w in RECORD_WINDOWS:
        if args.latency:
            expr = latency_expr(args.metric, args.job, args.threshold, w)
        else:
            expr = availability_expr(args.metric, args.job, args.error_selector, w)
        lines.append(f"      - record: {record_name(args.service, w)}")
        lines.append(f"        expr: |")
        lines.append(f"          {expr}")
    return lines


def build_alert_rules(args):
    budget = 1.0 - (args.slo / 100.0)
    lines = []
    for severity, long_w, short_w, burn in BURN_TIERS:
        threshold = round(burn * budget, 8)
        long_rec = record_name(args.service, long_w)
        short_rec = record_name(args.service, short_w)
        alert_name = f"{args.service}_SLO_burn_{severity}_{long_w}"
        kind = "latency" if args.latency else "availability"
        lines.append(f"      - alert: {alert_name}")
        lines.append(f"        expr: |")
        lines.append(f"          {long_rec} > {threshold}")
        lines.append(f"          and {short_rec} > {threshold}")
        lines.append(f"        for: 2m")
        lines.append(f"        labels:")
        lines.append(f"          severity: {severity}")
        lines.append(f"          service: {args.service}")
        lines.append(f"          slo: \"{args.slo}\"")
        lines.append(f"        annotations:")
        lines.append(
            f"          summary: \"{args.service} {kind} SLO burning at {burn}x "
            f"({long_w}/{short_w} windows)\""
        )
        lines.append(
            f"          description: \"Error budget for the {args.slo}% SLO is "
            f"burning fast enough to exhaust the window. Investigate now.\""
        )
        lines.append(f"          runbook_url: \"{args.runbook}\"")
    return lines


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--service", required=True, help="SLO/service short name, e.g. checkout")
    p.add_argument("--job", required=True, help="Prometheus job label value")
    p.add_argument("--slo", type=float, required=True, help="SLO target percent, e.g. 99.9")
    p.add_argument("--metric", required=True, help="base metric name")
    p.add_argument("--error-selector", default='status=~"5.."',
                   help='label selector identifying bad events (availability mode)')
    p.add_argument("--latency", action="store_true",
                   help="latency SLO mode (uses _bucket/_count of a histogram)")
    p.add_argument("--threshold", default="0.3",
                   help='latency le-bucket threshold in seconds (latency mode)')
    p.add_argument("--runbook", default="https://runbooks.example.com/REPLACE",
                   help="runbook URL added to alert annotations")
    args = p.parse_args(argv)

    if not (0 < args.slo < 100):
        p.error("--slo must be between 0 and 100 (exclusive)")

    out = []
    out.append("groups:")
    out.append(f"  - name: slo_recording_{args.service}")
    out.append("    interval: 30s")
    out.append("    rules:")
    out.extend(build_recording_rules(args))
    out.append(f"  - name: slo_alerts_{args.service}")
    out.append("    rules:")
    out.extend(build_alert_rules(args))
    print("\n".join(out))
    return 0


if __name__ == "__main__":
    sys.exit(main())
