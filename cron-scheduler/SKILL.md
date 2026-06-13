---
name: cron-scheduler
description: Builds, validates, explains, and previews cron expressions across Vixie/POSIX cron, systemd timers, and cloud schedulers, with explicit handling of timezones, DST, the day-of-month/day-of-week OR-logic trap, and overlap/missed-run pitfalls. Use this skill when the user asks to "write a cron job", "what does this cron expression mean", "schedule something every X", "explain `*/15 9-17 * * 1-5`", debug a cron that fires at the wrong time, convert a human schedule to cron, or reason about cron timezones, DST, and overlapping runs.
license: MIT
---

# Cron Scheduler

## Overview

Translate human scheduling intent into correct cron expressions, explain existing expressions in plain language, preview the next fire times, and avoid the subtle traps (DOM/DOW OR-logic, timezone/DST drift, overlapping long-running jobs, missed runs on downtime). Covers classic Vixie/POSIX cron, plus the dialects used by systemd timers, Quartz, AWS EventBridge, Kubernetes CronJobs, and GitHub Actions.

**Keywords:** cron, crontab, cron expression, schedule, scheduler, scheduled job, `*/5`, `0 9 * * 1-5`, timezone, TZ, DST, daylight saving, day-of-week, day-of-month, systemd timer, OnCalendar, Quartz, EventBridge rate/cron, Kubernetes CronJob, GitHub Actions schedule, every N minutes, weekday, next run, overlap, concurrencyPolicy, flock.

## Workflow

1. **Identify the target system.** Cron dialects differ. Ask or infer: classic crontab (5 fields), systemd `OnCalendar`, Quartz/Spring (6-7 fields with seconds + `?`), AWS EventBridge (6 fields, year, requires `?`), Kubernetes CronJob (5 fields, UTC by default), or GitHub Actions (5 fields, UTC only). See `references/cron-syntax.md` for the field tables per dialect.
2. **Pin down the timezone.** Determine where the schedule should fire in wall-clock terms and which TZ the runner uses. Most engines run in UTC or the daemon's local TZ — not the user's. Decide and state explicitly. See `references/timezones-and-dst.md`.
3. **Build the expression** field by field using `references/cron-syntax.md`. Prefer ranges and steps (`9-17`, `*/15`) over enumerations when they read clearly.
4. **Check the OR-logic trap.** If BOTH day-of-month and day-of-week are restricted (neither is `*`), Vixie cron fires when EITHER matches, not both. This is the #1 silent bug. See the worked example in `examples/build-and-explain.md`.
5. **Validate and preview.** Run `scripts/cronlint.py "<expr>" -n 5` to confirm it parses, see a plain-language breakdown, and list the next fire times. Always preview before delivering.
6. **Audit operational pitfalls:** DST gaps/doubles, jobs slower than their interval (overlap), missed runs after downtime, and the difference between "every 5 minutes" and "every hour at minute 5." See `references/scheduling-pitfalls.md`.
7. **Deliver** the expression, a one-line plain-English explanation, the assumed timezone, and the next 3-5 fire times.

## Cron field reference (classic 5-field)

```
┌───────────── minute        (0-59)
│ ┌─────────── hour          (0-23)
│ │ ┌───────── day of month  (1-31)
│ │ │ ┌─────── month         (1-12 or jan-dec)
│ │ │ │ ┌───── day of week   (0-7, 0 and 7 = Sunday, or sun-sat)
│ │ │ │ │
* * * * *  command
```

Operators: `*` (all), `,` (list), `-` (range), `/` (step). Macros: `@yearly` `@monthly` `@weekly` `@daily` `@hourly` `@reboot`.

## Decision framework: translating intent

| Human request | Expression | Notes |
|---|---|---|
| Every 5 minutes | `*/5 * * * *` | Not the same as "at minute 5" |
| At minute 5 of every hour | `5 * * * *` | |
| Every hour on the hour | `0 * * * *` | |
| Every weekday at 9am | `0 9 * * 1-5` | DOW only — safe |
| 1st of every month, midnight | `0 0 1 * *` | DOM only — safe |
| Every 15 min, business hours, weekdays | `*/15 9-17 * * 1-5` | |
| Every Sunday 2am | `0 2 * * 0` | |
| Twice daily (0am/12pm) | `0 0,12 * * *` | |
| Every quarter (1st of Jan/Apr/Jul/Oct) | `0 0 1 1,4,7,10 *` | |
| Last day of month | not expressible in classic cron | use `0 0 28-31 * *` + a guard, or systemd `*-*-01 00:00:00` minus a day, or Quartz `L` |

## Best Practices

- **Always state the timezone** alongside any cron expression you deliver. "0 9 * * 1-5 (Europe/Zurich)" is complete; "0 9 * * 1-5" is ambiguous.
- **Prefer `*/N` only for divisors of the field range** so spacing is even (`*/15` of 60 is even; `*/13` wraps unevenly each hour).
- **Avoid restricting both DOM and DOW** unless you genuinely want OR semantics. If you need "Friday the 13th", that's a single expression; "every Friday AND the 13th" needs a script guard.
- **Make long jobs overlap-safe** with `flock` (e.g. `flock -n /tmp/job.lock command`) or `concurrencyPolicy: Forbid` on Kubernetes CronJobs. A 7-minute job on `*/5` will stack up.
- **Pin schedules off the DST boundary.** Avoid 02:00-03:00 local time for daily jobs in TZs that spring forward at 2am; that hour can be skipped or doubled.
- **Validate before shipping.** Run `scripts/cronlint.py` and confirm the next runs match intent.
- **Comment crontab entries** with the intent and TZ, since the expression alone is hard to read months later.

## Common Pitfalls

- **DOM/DOW OR-logic:** `0 0 13 * 5` runs every 13th OR every Friday, not Friday the 13th. Covered in `references/scheduling-pitfalls.md`.
- **`*/5` vs `5`:** `5 * * * *` fires once an hour at :05; `*/5 * * * *` fires twelve times an hour. Easy to swap.
- **UTC assumptions:** Kubernetes CronJobs and GitHub Actions run in UTC; "0 9" is 9am UTC, possibly the middle of the night locally.
- **Sunday is both 0 and 7;** some parsers reject `7`, some reject `0`. Use names (`sun`) when supported for clarity.
- **systemd `OnCalendar` is NOT cron syntax** — it is `DOW YYYY-MM-DD HH:MM:SS`. Don't paste a crontab line into a `.timer`. See `references/cron-syntax.md`.
- **Quartz/EventBridge require `?`** in one of the day fields and use 6+ fields; a 5-field expression is invalid there.
- **Missed runs:** plain cron does not catch up after the machine was off. Use `anacron`, systemd `Persistent=true`, or a catch-up flag for backups.
- **Overlapping runs:** without locking, slow jobs run concurrently and corrupt state or exhaust resources.

## Bundled files

- `scripts/cronlint.py` — stdlib-only validator/explainer that parses a 5-field cron (or macro), prints a plain-language breakdown, flags the DOM/DOW OR trap, and lists the next N fire times. Usage: `python3 scripts/cronlint.py "*/15 9-17 * * 1-5" -n 5 [--from 2026-06-08T08:00]`.
- `references/cron-syntax.md` — field tables and operator/macro reference across classic cron, systemd, Quartz, EventBridge, Kubernetes, and GitHub Actions.
- `references/timezones-and-dst.md` — how each engine resolves timezone, DST spring-forward/fall-back behavior, and safe-scheduling rules.
- `references/scheduling-pitfalls.md` — deep dive on OR-logic, overlap/locking, missed runs, and step-vs-fixed confusion.
- `examples/build-and-explain.md` — worked examples: intent → expression and expression → explanation, including the Friday-the-13th trap.
