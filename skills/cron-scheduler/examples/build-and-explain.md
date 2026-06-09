# Worked Examples: Build and Explain Cron

## A. Intent -> expression

### "Every weekday at 9am, Zurich time"
- Field by field: minute `0`, hour `9`, DOM `*`, month `*`, DOW `1-5`.
- Expression: `0 9 * * 1-5`
- Timezone: must be stated. On a host in `Europe/Zurich`, `0 9 * * 1-5` is
  correct. On GitHub Actions (UTC), use `0 8 * * 1-5` in winter / `0 7 * * 1-5`
  in summer (see `references/timezones-and-dst.md`).
- Preview: `python3 scripts/cronlint.py "0 9 * * 1-5" -n 3`

### "Every 15 minutes during business hours on weekdays"
- minute `*/15`, hour `9-17`, DOM `*`, month `*`, DOW `1-5`.
- Expression: `*/15 9-17 * * 1-5`
- Validation output:
  ```
  $ python3 scripts/cronlint.py "*/15 9-17 * * 1-5" -n 4 --from 2026-06-08T08:50
  VALID: */15 9-17 * * 1-5
    minute       = 0,15,30,45
    hour         = 9,10,11,12,13,14,15,16,17
    day-of-month = *
    month        = every
    day-of-week  = 1,2,3,4,5 (0=Sun)

  Next 4 runs (computed from 2026-06-08 08:50:00, local wall clock, no DST modeling):
    2026-06-08 09:00  Mon
    2026-06-08 09:15  Mon
    2026-06-08 09:30  Mon
    2026-06-08 09:45  Mon
  ```

### "First day of every quarter at midnight"
- minute `0`, hour `0`, DOM `1`, month `1,4,7,10`, DOW `*`.
- Expression: `0 0 1 1,4,7,10 *`

### "Last day of every month" (not expressible in classic cron)
- Option 1 (script guard): `0 0 28-31 * * [ "$(date -d tomorrow +\%d)" = 01 ] && /path/job`
- Option 2 (systemd): a timer at `*-*-01 00:00:00` for the job that should run
  *after* month end, or use Quartz `0 0 0 L * ?`.

## B. Expression -> plain English

### `0 2 * * 0`
- minute 0, hour 2, any DOM, any month, DOW 0 (Sunday).
- "At 02:00 every Sunday."

### `30 8,17 * * 1-5`
- minute 30, hours 8 and 17, weekdays.
- "At 08:30 and 17:30, Monday through Friday."

### `0 0 13 * 5`  (the trap)
- minute 0, hour 0, DOM 13, any month, DOW 5 (Friday).
- Naive reading: "midnight on Friday the 13th." WRONG.
- Actual: "midnight on the 13th of every month, OR every Friday at midnight,"
  because both DOM and DOW are restricted -> OR logic.
- `cronlint.py` flags this:
  ```
  $ python3 scripts/cronlint.py "0 0 13 * 5" -n 3 --from 2026-06-08T00:00
  VALID: 0 0 13 * 5
    minute       = 0
    hour         = 0
    day-of-month = 13
    month        = every
    day-of-week  = 5 (0=Sun)
    WARNING: day-of-month AND day-of-week are both restricted.
             Cron fires when EITHER matches (OR logic), not both.

  Next 3 runs (...):
    2026-06-12 00:00  Fri
    2026-06-13 00:00  Sat
    2026-06-19 00:00  Fri
  ```
  Note 2026-06-12 (a Friday, not the 13th) and 2026-06-13 (the 13th, a Saturday)
  both fire — proving the OR behavior.

### To actually get "Friday the 13th"
```
0 0 13 * *   [ "$(date +\%u)" = 5 ] && /path/to/job
```
Keep DOW as `*` in the cron field and test the weekday inside the command.
