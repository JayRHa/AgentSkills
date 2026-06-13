# Cron Scheduling Pitfalls

## 1. The day-of-month / day-of-week OR-logic trap

When BOTH the day-of-month (field 3) and day-of-week (field 5) are restricted
(neither is `*`), classic Vixie cron runs the job when **EITHER** field matches.

```
0 0 13 * 5
```
This does NOT mean "Friday the 13th." It means "every 13th of the month, OR every
Friday" — typically 4-5 runs a week.

- Friday the 13th in one expression is impossible in classic cron. Use a guard:
  ```
  0 0 13 * *  [ "$(date +\%u)" = 5 ] && /path/to/job
  ```
- If you want "every Friday in months that have a 13th" — that's still the script
  guard approach.
- Rule of thumb: keep one of DOM/DOW as `*` unless you deliberately want OR.

## 2. Step vs fixed minute

| Expression | Fires |
|---|---|
| `5 * * * *` | once per hour at :05 (24x/day) |
| `*/5 * * * *` | every 5 minutes (288x/day) |
| `0 */2 * * *` | every 2 hours on the hour |
| `0 2 * * *` | once a day at 02:00 |

Swapping `5` and `*/5` is a frequent and costly bug (e.g. a billing job running
288x instead of 24x).

## 3. Uneven steps

`*/N` restarts each field at its low bound. `0 */7 * * *` fires at hours
0,7,14,21 — the gap from 21 to next-day 0 is only 3 hours, not 7. Steps are only
evenly spaced when `N` divides the field's range (e.g. `*/15` of 60, `*/2` of 24,
`*/6` of 24). For even spacing across the day, pick a divisor of 24 for hours and
of 60 for minutes.

## 4. Overlapping (concurrent) runs

Cron starts a new instance on schedule regardless of whether the previous one
finished. A 7-minute job on `*/5 * * * *` will pile up and can exhaust resources
or corrupt shared state.

Mitigations:
- `flock`: `*/5 * * * * /usr/bin/flock -n /tmp/myjob.lock /path/to/job`
  (`-n` = fail immediately if locked; omit for queueing).
- systemd: timer-triggered services are single-instance per unit by default.
- Kubernetes: `spec.concurrencyPolicy: Forbid` (skip) or `Replace` (kill old).

## 5. Missed runs after downtime

Plain cron does not catch up runs that were due while the machine was off or the
daemon stopped. If catch-up matters (backups, billing):
- Use `anacron` (designed for non-24/7 machines).
- Use systemd timers with `Persistent=true`.
- Add an idempotent catch-up check at the start of the job.

## 6. Environment differences

Cron runs with a minimal environment: short `PATH`, no shell profile, possibly a
different `HOME`/`SHELL`. "Works in my terminal, fails in cron" is almost always
this. Fixes:
- Use absolute paths to binaries and files.
- Set `PATH=` and any needed vars at the top of the crontab.
- Redirect output for debugging: `command >> /var/log/myjob.log 2>&1`.
- Cron emails stdout/stderr to the user by default; silence with redirection if
  intentional, but don't hide real errors.

## 7. Seconds resolution

Classic cron's finest granularity is 1 minute. For sub-minute scheduling use a
systemd timer with `OnUnitActiveSec=`, a sleep loop, or a dedicated scheduler.
Don't try to fake it with overlapping minute jobs.

## 8. The 6th field surprise

In `/etc/crontab` and `/etc/cron.d/*`, there is a **user** field between the
day-of-week and the command. Copying a per-user `crontab -e` line (no user field)
into `/etc/cron.d` shifts everything and silently breaks the schedule.
