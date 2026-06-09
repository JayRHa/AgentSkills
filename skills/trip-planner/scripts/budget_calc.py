#!/usr/bin/env python3
"""Trip budget calculator and reconciler.

Breaks a total trip budget into category allocations, estimates on-the-ground
spend from regional day-rates, and reconciles planned costs against the budget.
Pure standard library.

Usage examples:
  # Allocate a total budget into categories for a mid-range trip
  python3 budget_calc.py allocate --total 3000 --tier mid --currency USD

  # Estimate on-the-ground cost from a regional day rate
  python3 budget_calc.py estimate --days 5 --travelers 2 --daily 150 \
      --lodging 130 --flights 1400 --buffer 0.12

  # Reconcile planned line items against a total budget
  python3 budget_calc.py reconcile --total 3000 \
      --item flights=1400 --item lodging=650 --item food=400 \
      --item activities=250 --item transit=90
"""
import argparse
import sys

# Category split heuristics by tier (see references/budgeting.md)
SPLITS = {
    "budget": {"transport": 0.35, "lodging": 0.25, "food": 0.18,
               "activities": 0.10, "local_transit": 0.04, "buffer": 0.08},
    "mid":    {"transport": 0.30, "lodging": 0.30, "food": 0.18,
               "activities": 0.10, "local_transit": 0.04, "buffer": 0.08},
    "comfort": {"transport": 0.25, "lodging": 0.35, "food": 0.18,
                "activities": 0.12, "local_transit": 0.03, "buffer": 0.07},
}


def fmt(amount, currency):
    return f"{currency} {amount:,.0f}"


def cmd_allocate(args):
    tier = args.tier
    if tier not in SPLITS:
        sys.exit(f"Unknown tier '{tier}'. Choose from: {', '.join(SPLITS)}")
    split = SPLITS[tier]
    print(f"Budget allocation ({tier} tier) for total {fmt(args.total, args.currency)}")
    print("-" * 48)
    for cat, pct in split.items():
        amount = args.total * pct
        label = cat.replace("_", " ").title()
        print(f"  {label:<16} {pct*100:>4.0f}%   {fmt(amount, args.currency):>14}")
    print("-" * 48)
    print(f"  {'Total':<16} {'100%':>5}   {fmt(args.total, args.currency):>14}")


def cmd_estimate(args):
    on_ground = args.days * args.travelers * args.daily
    lodging = args.days * args.lodging  # per-night room cost (not per person)
    subtotal = on_ground + lodging + args.flights
    buffer = subtotal * args.buffer
    total = subtotal + buffer
    c = args.currency
    print("Trip cost estimate")
    print("-" * 48)
    print(f"  On-the-ground  {args.days}d x {args.travelers}p x {fmt(args.daily, c)}"
          f"  = {fmt(on_ground, c)}")
    print(f"  Lodging        {args.days} nights x {fmt(args.lodging, c)}/night"
          f"   = {fmt(lodging, c)}")
    print(f"  Flights                                = {fmt(args.flights, c)}")
    print(f"  Subtotal                               = {fmt(subtotal, c)}")
    print(f"  Buffer ({args.buffer*100:.0f}%)                          = {fmt(buffer, c)}")
    print("-" * 48)
    print(f"  TOTAL                                  = {fmt(total, c)}")
    per_person = total / args.travelers if args.travelers else total
    print(f"  Per traveler                           = {fmt(per_person, c)}")


def parse_items(items):
    parsed = {}
    for raw in items:
        if "=" not in raw:
            sys.exit(f"Bad item '{raw}'. Use name=amount, e.g. food=400")
        name, _, val = raw.partition("=")
        try:
            parsed[name.strip()] = float(val)
        except ValueError:
            sys.exit(f"Bad amount in item '{raw}'")
    return parsed


def cmd_reconcile(args):
    items = parse_items(args.item)
    c = args.currency
    planned = sum(items.values())
    print(f"Reconciliation against budget {fmt(args.total, c)}")
    print("-" * 48)
    for name, val in items.items():
        print(f"  {name:<16} {fmt(val, c):>14}")
    print("-" * 48)
    print(f"  {'Planned total':<16} {fmt(planned, c):>14}")
    diff = args.total - planned
    if diff >= 0:
        print(f"  {'Remaining':<16} {fmt(diff, c):>14}  (within budget)")
        suggested_buffer = args.total * 0.10
        if diff < suggested_buffer:
            print(f"  Note: remaining is below a ~10% buffer "
                  f"({fmt(suggested_buffer, c)}). Consider trimming.")
    else:
        over = -diff
        print(f"  {'OVER by':<16} {fmt(over, c):>14}")
        print("  Trade-down ladder: 1) lodging tier  2) paid attractions")
        print("                     3) dining tier   4) local transport")
        print("                     5) trip length")


def build_parser():
    p = argparse.ArgumentParser(description="Trip budget calculator and reconciler")
    sub = p.add_subparsers(dest="command", required=True)

    a = sub.add_parser("allocate", help="Split a total budget into categories")
    a.add_argument("--total", type=float, required=True)
    a.add_argument("--tier", default="mid", choices=list(SPLITS))
    a.add_argument("--currency", default="USD")
    a.set_defaults(func=cmd_allocate)

    e = sub.add_parser("estimate", help="Estimate total cost from day rates")
    e.add_argument("--days", type=int, required=True)
    e.add_argument("--travelers", type=int, default=1)
    e.add_argument("--daily", type=float, required=True,
                   help="On-the-ground spend per person per day")
    e.add_argument("--lodging", type=float, default=0.0,
                   help="Lodging cost per night (room, not per person)")
    e.add_argument("--flights", type=float, default=0.0,
                   help="Total flights/intercity transport cost")
    e.add_argument("--buffer", type=float, default=0.12,
                   help="Buffer fraction (default 0.12)")
    e.add_argument("--currency", default="USD")
    e.set_defaults(func=cmd_estimate)

    r = sub.add_parser("reconcile", help="Reconcile line items vs total budget")
    r.add_argument("--total", type=float, required=True)
    r.add_argument("--item", action="append", default=[],
                   help="Repeatable: name=amount, e.g. --item food=400")
    r.add_argument("--currency", default="USD")
    r.set_defaults(func=cmd_reconcile)

    return p


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()
