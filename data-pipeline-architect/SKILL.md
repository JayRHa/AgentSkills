---
name: data-pipeline-architect
description: Designs robust ETL/ELT data pipelines covering ingestion, idempotency, schema evolution, orchestration, and data quality validation. Use this skill when the user asks to design, build, or review a data pipeline, ingest data from APIs/databases/files into a warehouse or lake, set up batch or streaming ETL/ELT, choose an orchestrator (Airflow, Dagster, Prefect, dbt), make a pipeline idempotent or backfill-safe, handle late-arriving or duplicate data, manage schema drift/evolution, add data quality or freshness checks, or model incremental/CDC loads.
license: MIT
---

# Data Pipeline Architect

## Overview

This skill helps you design and review production-grade data pipelines. It covers the full lifecycle: ingestion, transformation, idempotency and backfills, schema evolution, orchestration, and data quality. It is opinionated toward modern ELT (load raw, transform in-warehouse) but supports classic ETL where it fits.

Keywords: ETL, ELT, data pipeline, ingestion, idempotency, backfill, schema evolution, schema drift, CDC, incremental load, watermark, orchestration, Airflow, Dagster, Prefect, dbt, data quality, freshness, dedup, late-arriving data, partitioning, medallion, bronze silver gold.

Use this skill to produce a concrete pipeline design (a design doc), to review an existing pipeline against best practices, or to generate skeleton DAGs/models and data-quality checks.

## Decision: ETL vs ELT

Default to **ELT** when the destination is a modern columnar warehouse/lake (Snowflake, BigQuery, Redshift, Databricks, DuckDB). Land raw data first, transform with SQL/dbt. Use **ETL** when: the destination can't transform cheaply, you must mask/drop PII before it lands (compliance), or you transform in-flight for a stream. See `references/etl-vs-elt.md`.

## Workflow

Follow these steps in order. Produce the design document in `templates/pipeline-design.md` as you go.

1. **Clarify requirements.** Capture: sources, destination, SLA/freshness (real-time, hourly, daily), volume (rows/day, GB/day), data sensitivity (PII?), and consumers (BI, ML, reverse-ETL). Don't design before you know freshness and volume — they drive batch-vs-stream and incremental-vs-full.

2. **Choose load pattern.** Decide ETL vs ELT (above) and batch vs streaming. Map each source to an extraction strategy: full snapshot, incremental by watermark, or CDC. See `references/ingestion-patterns.md`.

3. **Design for idempotency.** Every load step must be safe to re-run and produce the same result. Use the techniques in `references/idempotency.md`: deterministic partition keys, MERGE/upsert on a stable business key, delete-insert by partition, or staging-then-atomic-swap. Never blind `INSERT` into a target on retry.

4. **Plan incremental extraction + watermarks.** Pick a high-watermark column (`updated_at`, monotonic id, or LSN/CDC offset). Store the watermark in a state table, not in code. Re-read with overlap (lookback window) to catch late updates, then dedup. See `references/ingestion-patterns.md`.

5. **Handle schema evolution.** Decide a policy per layer: additive-only in raw (auto-add columns), explicit contracts in curated layers. Choose a file format that supports evolution (Parquet/Avro/Delta/Iceberg). Define what happens on a breaking change (quarantine, alert, fail). See `references/schema-evolution.md`.

6. **Model the transformation layers.** Use the medallion pattern: bronze (raw, append-only, typed minimally) → silver (cleaned, deduped, conformed) → gold (business marts). Keep transformations declarative and version-controlled (dbt models). See `references/orchestration.md`.

7. **Choose orchestration.** Map dependencies as a DAG. Pick a tool by fit (Airflow for ops maturity, Dagster for asset/data-aware, Prefect for Pythonic dynamism, dbt for SQL transforms). Define schedules, retries with backoff, timeouts, SLAs, and alerting. See `references/orchestration.md`.

8. **Add data quality gates.** Place checks at boundaries: post-ingestion (row counts, schema), post-transform (uniqueness, not-null, referential, accepted values), and freshness. Fail loud or quarantine — never silently pass bad data downstream. See `references/data-quality.md`.

9. **Plan backfills & reprocessing.** Pipelines must support re-running an arbitrary date range without duplicates. Parameterize by partition/date; lean on idempotency from step 3. Document the backfill command.

10. **Observability & cost.** Emit metrics (rows in/out, duration, freshness lag, failure rate), structured logs, and lineage. Right-size partitions and prune scans to control warehouse cost.

11. **Validate the design.** Run `scripts/pipeline_lint.py` against the design doc / config to catch missing idempotency keys, absent quality checks, no retry policy, and no schema-evolution policy.

## Quick Heuristics

- **Land raw, immutable, partitioned by ingestion date.** Raw is your replay log; never mutate it.
- **One business key, everywhere.** Idempotency, dedup, and MERGE all hinge on a stable natural/surrogate key.
- **Watermark with a lookback.** Always re-scan a small overlap window and dedup, or you will lose late-arriving rows.
- **Partition by event/date, not by load time, for query pruning** — but partition raw by load date for replay.
- **Quality checks are part of the DAG, not a cron afterthought.** A failed check should block promotion to the next layer.
- **Make every task retry-safe before adding retries.** Retries amplify non-idempotent bugs.

## Best Practices

- Separate extract (E) from load (L) so you can replay loads from cached raw extracts.
- Use staging tables + atomic swap/MERGE; never partially-write a target table.
- Store pipeline state (watermarks, run metadata) in a queryable table, not in files or memory.
- Treat schema as a contract between producer and consumer; version it and test it.
- Tag/partition data with a `_loaded_at`, `_source`, and `_batch_id` for lineage and debugging.
- Encode SLAs and freshness as monitored checks, not tribal knowledge.
- Keep secrets out of code; use a secret manager and least-privilege source credentials.

## Common Pitfalls

- **Blind appends on retry** → duplicates. Fix with upsert/MERGE or delete-insert by partition.
- **Watermark = exactly last max(updated_at)** → silently drops rows updated within the same second or arriving late. Use a lookback window.
- **Auto-evolving schema into gold tables** → breaks BI dashboards. Auto-evolve only in raw/bronze.
- **Full reloads "because it's simpler"** at scale → cost and SLA blowups. Move to incremental once volume grows.
- **Quality checks that warn but don't block** → bad data reaches consumers. Gate promotion on checks.
- **No backfill story** → an upstream outage means manual, error-prone recovery. Parameterize by date from day one.
- **Coupling extraction and transformation** → can't replay or reprocess without re-hitting the source API/DB.

## Bundled Resources

- `references/etl-vs-elt.md` — decision matrix, batch vs streaming, when each wins.
- `references/ingestion-patterns.md` — full/incremental/CDC, watermarks, late-arriving data, dedup SQL.
- `references/idempotency.md` — MERGE, delete-insert, staging swap patterns with SQL.
- `references/schema-evolution.md` — formats, policies per layer, breaking-change handling.
- `references/orchestration.md` — tool comparison, DAG/retry/SLA patterns, medallion layering.
- `references/data-quality.md` — check taxonomy, where to place gates, dbt/Great Expectations examples.
- `templates/pipeline-design.md` — fill-in design document.
- `examples/orders-pipeline.md` — worked end-to-end example (Postgres → warehouse).
- `scripts/pipeline_lint.py` — lints a pipeline design config (YAML/JSON) for required safeguards.
