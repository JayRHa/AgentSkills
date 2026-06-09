# Orchestration & Layering

## Medallion architecture

```
source ──ingest──▶ BRONZE (raw, immutable, append-only, minimally typed,
                          partitioned by load date)
        ──clean──▶ SILVER (deduped, conformed, typed, business keys,
                          validated against contract)
        ──model──▶ GOLD   (marts/aggregates for BI, ML, reverse-ETL)
```

- Bronze is the replay log — never mutate it.
- Silver is where dedup, MERGE, and quality gates live.
- Gold is consumer-facing and contract-stable.

## Orchestrator selection

| Tool | Model | Pick when |
|---|---|---|
| **Airflow** | Task DAGs (Python) | Mature ops, broad integrations, time-based batch, large teams |
| **Dagster** | Software-defined assets, data-aware | You think in datasets/lineage, want built-in data quality + types |
| **Prefect** | Pythonic flows, dynamic | Highly dynamic/parametric Python workflows, lighter setup |
| **dbt** | SQL transforms + DAG | In-warehouse ELT transforms, tests, docs (pair with the above) |
| **Step Functions / managed** | Cloud-native | Serverless, AWS-centric, low ops |

Common stack: an orchestrator (Airflow/Dagster/Prefect) triggers ingestion **and** runs `dbt build` for transforms + tests.

## DAG design rules

- One task = one idempotent unit of work; pass parameters (run date / partition), not state.
- Make dependencies explicit; let the orchestrator parallelize independent branches.
- Sensors/triggers over polling loops where supported (event-driven beats busy-wait).
- Keep tasks small enough to retry cheaply; large monoliths waste reruns.

## Retries, timeouts, SLAs

```python
# Airflow example defaults
default_args = {
    "retries": 3,
    "retry_delay": timedelta(minutes=5),
    "retry_exponential_backoff": True,
    "max_retry_delay": timedelta(minutes=30),
    "execution_timeout": timedelta(hours=1),
    "sla": timedelta(hours=2),
    "on_failure_callback": alert_oncall,
}
```

- **Retries only after idempotency.** Otherwise retries multiply corruption.
- **Exponential backoff** for transient source/API errors; cap it.
- **Timeouts** prevent a hung task from blocking the schedule.
- **SLA + freshness checks** detect "ran successfully but data is stale".

## Backfills

- Parameterize every task by `run_date` / partition.
- Backfill = run the same DAG over a historical range; idempotency guarantees no dupes.
- Throttle concurrency on backfills to avoid hammering sources and the warehouse.
- Document the exact backfill command in the design doc.

## Scheduling & dependencies

- Prefer **data-aware** triggering (run when upstream asset updates) over fixed cron when the tool supports it (Dagster assets, Airflow datasets) — avoids race conditions where a downstream job runs before fresh data lands.
- For cross-DAG dependencies, use explicit triggers/sensors, not coincidental timing.

## Observability

Emit per run: rows in/out, duration, freshness lag, check pass/fail, error class. Centralize logs (structured JSON), expose lineage (dbt docs, OpenLineage/Marquez), and alert on failure + SLA miss + freshness breach.
