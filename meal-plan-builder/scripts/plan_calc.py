#!/usr/bin/env python3
"""plan_calc.py - Total macros/calories for a weekly meal plan and flag off-target days.

Reads a JSON plan file and prints per-day and weekly totals for calories, protein,
carbs, and fat. Flags any day whose calories fall outside +/-tolerance of the target
and whose protein falls below the protein floor.

Calories are derived from macros (protein 4, carb 4, fat 9 kcal/g) so the numbers stay
internally consistent; if a meal omits a macro it is treated as 0.

USAGE:
    python3 plan_calc.py plan.json
    python3 plan_calc.py plan.json --tolerance 0.05

PLAN JSON SHAPE:
{
  "targets": {"calories": 1750, "protein": 122, "carbs": 185, "fat": 58},
  "days": {
    "Monday": [
      {"name": "Oats & berries", "protein": 20, "carbs": 55, "fat": 12},
      {"name": "Chicken bowl",   "protein": 45, "carbs": 60, "fat": 18}
    ],
    "Tuesday": [ ... ]
  }
}

The per-meal numbers are PER SERVING as eaten by this person that day.
Exit code is 1 if any day is out of tolerance, else 0.
"""
import argparse
import json
import sys

KCAL = {"protein": 4, "carbs": 4, "fat": 9}


def meal_kcal(meal):
    return sum(KCAL[m] * float(meal.get(m, 0) or 0) for m in KCAL)


def sum_macros(meals):
    totals = {"protein": 0.0, "carbs": 0.0, "fat": 0.0, "calories": 0.0}
    for meal in meals:
        for m in KCAL:
            totals[m] += float(meal.get(m, 0) or 0)
        totals["calories"] += meal_kcal(meal)
    return totals


def fmt(t):
    return (f"{t['calories']:6.0f} kcal | "
            f"P {t['protein']:5.0f}g  C {t['carbs']:5.0f}g  F {t['fat']:5.0f}g")


def main():
    p = argparse.ArgumentParser(description="Total a weekly meal plan and flag off-target days.")
    p.add_argument("plan", help="Path to plan JSON file")
    p.add_argument("--tolerance", type=float, default=0.05,
                   help="Allowed fractional deviation from calorie target (default 0.05 = 5%%)")
    args = p.parse_args()

    try:
        with open(args.plan, encoding="utf-8") as fh:
            plan = json.load(fh)
    except FileNotFoundError:
        print(f"error: file not found: {args.plan}", file=sys.stderr)
        return 2
    except json.JSONDecodeError as e:
        print(f"error: invalid JSON: {e}", file=sys.stderr)
        return 2

    targets = plan.get("targets", {})
    cal_target = float(targets.get("calories", 0) or 0)
    prot_floor = float(targets.get("protein", 0) or 0)
    days = plan.get("days", {})
    if not days:
        print("error: plan has no 'days'", file=sys.stderr)
        return 2

    week = {"protein": 0.0, "carbs": 0.0, "fat": 0.0, "calories": 0.0}
    any_off = False
    n_days = 0

    print("Daily totals")
    print("-" * 64)
    for day, meals in days.items():
        n_days += 1
        t = sum_macros(meals)
        for k in week:
            week[k] += t[k]
        flags = []
        if cal_target:
            lo, hi = cal_target * (1 - args.tolerance), cal_target * (1 + args.tolerance)
            if t["calories"] < lo:
                flags.append(f"LOW kcal (<{lo:.0f})")
            elif t["calories"] > hi:
                flags.append(f"HIGH kcal (>{hi:.0f})")
        if prot_floor and t["protein"] < prot_floor:
            flags.append(f"protein below floor ({prot_floor:.0f}g)")
        if flags:
            any_off = True
        flag_str = "  <-- " + "; ".join(flags) if flags else ""
        print(f"{day:<10} {fmt(t)}{flag_str}")

    print("-" * 64)
    print(f"{'WEEK':<10} {fmt(week)}")
    if n_days:
        avg = {k: week[k] / n_days for k in week}
        print(f"{'AVG/day':<10} {fmt(avg)}")

    if cal_target:
        print(f"\nTarget/day: {cal_target:.0f} kcal | protein floor {prot_floor:.0f}g | "
              f"tolerance +/-{args.tolerance*100:.0f}%")

    return 1 if any_off else 0


if __name__ == "__main__":
    sys.exit(main())
