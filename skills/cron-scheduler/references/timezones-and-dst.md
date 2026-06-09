# Timezones and DST in Cron

The single most common source of "my job fired at the wrong time" is timezone
and daylight-saving (DST) confusion. Cron expressions carry no timezone of their
own — the **runner** decides which clock they are interpreted against.

## Which clock does each engine use?

| Engine | Default timezone | How to override |
|---|---|---|
| Classic crontab (per-user) | system local TZ of the cron daemon | set `CRON_TZ=Europe/Zurich` at top of crontab, or `TZ=` (impl-dependent) |
| `/etc/cron.d` files | system local TZ | `CRON_TZ=` line in the file |
| systemd timers | system TZ | timezone suffix in `OnCalendar`, e.g. `... 09:00 Europe/Zurich` |
| Kubernetes CronJob | **UTC** | `spec.timeZone: "Europe/Zurich"` (k8s >= 1.27) |
| GitHub Actions | **UTC** (no override) | convert your local time to UTC manually |
| AWS EventBridge | **UTC** (no override) | convert to UTC; account for DST manually |
| Quartz | JVM default TZ | `TimeZone` on the trigger / `zone =` |

**Rule:** never deliver a bare cron expression. Always state "...interpreted in
`<timezone>`" and, for UTC-only engines, show the UTC value plus the local
wall-clock equivalent.

## DST transitions

Two failure modes, both around the spring-forward / fall-back hour:

### Spring forward (clocks jump, e.g. 02:00 -> 03:00)
- The skipped hour does not exist. A job scheduled at `30 2 * * *` (02:30) on the
  transition day **may not run at all** that day, depending on the cron
  implementation.

### Fall back (clocks repeat, e.g. 03:00 -> 02:00)
- The repeated hour happens twice. A job at `30 2 * * *` **may run twice**, or
  once, depending on implementation.

Vixie cron's historical rule: for jobs in the skipped/repeated hour with a fixed
hour+minute, it tries to run them once; jobs with wildcard minute/hour follow
the wall clock and naturally skip/repeat.

## Safe-scheduling rules

1. **Avoid the local 01:00-03:00 window** for once-daily jobs in zones that
   transition there. Schedule at 00:30 or 04:00 instead.
2. **Run business-critical schedules in UTC** and document the local equivalent,
   so DST never shifts them. The tradeoff: the local wall-clock time drifts by an
   hour across DST.
3. **For UTC-only engines (GitHub Actions, EventBridge)** that must hit a local
   wall-clock time year-round, you need TWO expressions (one for standard time,
   one for DST) or external logic — a single UTC cron cannot track DST.
4. **Verify** with the engine's own tooling: `systemd-analyze calendar "<expr>"`
   for systemd; for k8s, reason in UTC unless `timeZone` is set.

## Worked timezone example

User wants "09:00 Europe/Zurich on weekdays" in GitHub Actions (UTC only):
- Zurich is UTC+1 in winter (CET), UTC+2 in summer (CEST).
- Winter: `0 8 * * 1-5`. Summer: `0 7 * * 1-5`.
- A single `0 8 * * 1-5` fires at 09:00 in winter but 10:00 in summer.
- Decision: either accept the 1h summer drift, or maintain two schedules and
  document the switch dates, or move the job to a TZ-aware runner.
