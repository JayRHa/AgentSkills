# Cron Syntax Reference (by dialect)

## Classic Vixie / POSIX cron (crontab)

Five space-separated fields, then the command.

```
* * * * * command
│ │ │ │ │
│ │ │ │ └── day of week   0-7   (0 and 7 = Sunday; sun-sat names ok)
│ │ │ └──── month         1-12  (jan-dec names ok)
│ │ └────── day of month  1-31
│ └──────── hour          0-23
└────────── minute        0-59
```

### Operators

| Operator | Meaning | Example | Expands to |
|---|---|---|---|
| `*` | every value | `* * * * *` | every minute |
| `,` | list | `0 0,12 * * *` | 00:00 and 12:00 |
| `-` | range | `0 9-17 * * *` | hourly 09:00-17:00 |
| `/` | step | `*/15 * * * *` | every 15 min |
| range+step | `0-30/10 * * * *` | 0,10,20,30 |

### Macros (nicknames)

| Macro | Equivalent |
|---|---|
| `@yearly` / `@annually` | `0 0 1 1 *` |
| `@monthly` | `0 0 1 * *` |
| `@weekly` | `0 0 * * 0` |
| `@daily` / `@midnight` | `0 0 * * *` |
| `@hourly` | `0 * * * *` |
| `@reboot` | once at daemon startup |

### Special notes
- Sunday is both `0` and `7`. Some implementations only accept one form; use names (`sun`) where supported.
- If BOTH day-of-month and day-of-week are restricted, the job runs when EITHER matches (OR). See `scheduling-pitfalls.md`.
- `crontab -e` edits per-user tables; `/etc/crontab` and `/etc/cron.d/*` files add a **user** field as a 6th field before the command.

## systemd timers (`OnCalendar=`)

NOT cron syntax. Format: `DayOfWeek Year-Month-Day Hour:Minute:Second`.

```
OnCalendar=Mon..Fri 09:00
OnCalendar=*-*-01 00:00:00         # 1st of every month
OnCalendar=*-*-* 00/15:00          # not valid; use minute step below
OnCalendar=*-*-* *:0/15            # every 15 minutes
OnCalendar=daily                   # shorthand
```

Key directives in the `.timer` unit:
- `Persistent=true` — run missed jobs after downtime (like anacron).
- `RandomizedDelaySec=` — jitter to avoid thundering herd.
- Timezone follows the system timezone unless overridden. Inspect with `systemd-analyze calendar "<expr>"`.

## Quartz / Spring `@Scheduled(cron=...)`

Six or seven fields: `second minute hour day-of-month month day-of-week [year]`.

- Day-of-week is `1-7` with `1=Sunday` (or `SUN-SAT`), or `MON-FRI` names.
- Exactly one of day-of-month / day-of-week must be `?` (no-specific-value).
- Special chars: `L` (last), `W` (weekday nearest), `#` (nth weekday, e.g. `FRI#3`).
- Example: `0 0 9 ? * MON-FRI` = 09:00 weekdays. `0 0 0 L * ?` = last day of month.

## AWS EventBridge / CloudWatch `cron(...)`

Six fields, UTC only: `cron(minute hour day-of-month month day-of-week year)`.

- One of day-of-month / day-of-week must be `?`.
- Day-of-week `1-7` (1=Sunday) or `SUN-SAT`; supports `L`, `#`.
- `rate(...)` alternative: `rate(5 minutes)`, `rate(1 hour)`, `rate(1 day)`.
- Example: `cron(0/15 9-17 ? * MON-FRI *)`.

## Kubernetes CronJob

Standard 5-field cron. Runs in **UTC** by default; set `spec.timeZone: "Europe/Zurich"` (k8s 1.27+) to use a named zone. Control overlap with `spec.concurrencyPolicy: Allow|Forbid|Replace` and lateness with `spec.startingDeadlineSeconds`.

## GitHub Actions `on.schedule`

Standard 5-field cron, **UTC only**, no timezone option. Minimum effective interval is ~5 minutes and runs may be delayed under load. Example: `cron: '0 9 * * 1-5'` = 09:00 UTC weekdays.

## Quick conversion crib

| Intent | classic | systemd OnCalendar | Quartz |
|---|---|---|---|
| every 15 min | `*/15 * * * *` | `*-*-* *:0/15` | `0 0/15 * ? * *` |
| weekdays 9am | `0 9 * * 1-5` | `Mon..Fri 09:00` | `0 0 9 ? * MON-FRI` |
| 1st of month | `0 0 1 * *` | `*-*-01 00:00:00` | `0 0 0 1 * ?` |
| last day of month | (guard needed) | `*-*-* 00:00:00` + check | `0 0 0 L * ?` |
