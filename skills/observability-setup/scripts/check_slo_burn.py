#!/usr/bin/env python3
"""Compute the current error budget and burn rate for an SLO.

Given the SLO target and observed good/bad event counts (or an error ratio),
this prints the error budget, how much of it is consumed, the current burn
rate, and which standard burn-rate alert tiers would currently fire. Useful
for validating SLO definitions and sanity-checking alert thresholds without a
live Prometheus.

No third-party dependencies (stdlib only).

Usage:
    # from raw counts over the SLO window:
    python3 check_slo_burn.py --slo 99.9 --good 29950000 --bad 50000

    # from an observed instantaneous error ratio:
    python3 check_slo_burn.py --slo 99.9 --error-ratio 0.0144

    # specify the window to translate burn rate into time-to-exhaust:
    python3 check_slo_burn.py --slo 99.9 --error-ratio 0.0144 --window-days 30

Exit codes: 0 ok, 2 on bad arguments.
"""
import argparse
import sys

# (severity, long_window, short_window, burn_rate) -- mirrors gen_slo_alerts.py
BURN_TIERS = [
    ("page", "1h/5m", 14.4),
    ("page", "6h/30m", 6.0),
    ("ticket", "1d/1h", 3.0),
    ("ticket", "3d/6h", 1.0),
]


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--slo", type=float, required=True, help="SLO target percent, e.g. 99.9")
    p.add_argument("--good", type=float, help="count of good events in window")
    p.add_argument("--bad", type=float, help="count of bad events in window")
    p.add_argument("--error-ratio", type=float,
                   help="observed error ratio (0..1); alternative to --good/--bad")
    p.add_argument("--window-days", type=float, default=30.0,
                   help="SLO window length in days (default 30)")
    args = p.parse_args(argv)

    if not (0 < args.slo < 100):
        p.error("--slo must be between 0 and 100 (exclusive)")

    budget = 1.0 - (args.slo / 100.0)  # allowed bad fraction

    if args.error_ratio is not None:
        error_ratio = args.error_ratio
        total = None
        consumed = None
    elif args.good is not None and args.bad is not None:
        total = args.good + args.bad
        if total <= 0:
            p.error("good + bad must be > 0")
        error_ratio = args.bad / total
        budget_events = budget * total
        consumed = (args.bad / budget_events) if budget_events > 0 else float("inf")
    else:
        p.error("provide either --error-ratio OR both --good and --bad")

    burn_rate = error_ratio / budget if budget > 0 else float("inf")

    print("SLO burn report")
    print("=" * 40)
    print(f"SLO target           : {args.slo}%")
    print(f"Error budget (bad)   : {budget*100:.4f}% of valid events")
    print(f"Observed error ratio : {error_ratio*100:.4f}%")
    print(f"Burn rate            : {burn_rate:.2f}x")

    if burn_rate > 0 and burn_rate != float("inf"):
        hours_to_exhaust = (args.window_days * 24.0) / burn_rate
        print(f"Time to exhaust full budget at this rate: {hours_to_exhaust:.1f}h")
    if consumed is not None:
        print(f"Budget consumed so far: {consumed*100:.2f}% "
              f"(remaining {max(0.0, (1-consumed))*100:.2f}%)")

    print("\nAlert tiers that would FIRE now:")
    any_fire = False
    for severity, windows, tier_burn in BURN_TIERS:
        fires = burn_rate >= tier_burn
        mark = "FIRE" if fires else "ok  "
        if fires:
            any_fire = True
        print(f"  [{mark}] {severity:6s} {windows:8s} threshold burn {tier_burn}x")
    if not any_fire:
        print("  (none — within normal operating range)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
