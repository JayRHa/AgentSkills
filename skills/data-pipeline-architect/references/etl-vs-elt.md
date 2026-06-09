# ETL vs ELT, Batch vs Streaming

## ETL vs ELT

| Dimension | ETL (transform before load) | ELT (transform after load) |
|---|---|---|
| Where transforms run | External engine (Spark, Python, in-flight) | In the warehouse/lake (SQL, dbt) |
| Raw data retained | Often not | Yes — raw is landed and kept |
| Replay / reprocess | Hard (must re-extract) | Easy (re-run SQL over raw) |
| Best destination | Legacy DBs, constrained targets | Columnar MPP warehouses, lakehouse |
| PII handling | Can mask before landing (compliance win) | Must mask in-warehouse or pre-land |
| Skill set | Python/Spark engineers | SQL analysts + analytics engineers |
| Cost model | Compute on ETL cluster | Compute in warehouse (pay per query) |

**Default: ELT.** Land raw (immutable, partitioned by load date), then transform with version-controlled SQL. Choose ETL when the target can't transform cheaply, or compliance requires masking/dropping PII before it lands, or you need in-flight stream transforms.

A common hybrid: lightweight ETL for PII redaction + schema typing at ingest, then ELT for business logic.

## Batch vs Streaming

Pick based on **freshness SLA** and **cost tolerance**, not novelty.

| Need | Pattern |
|---|---|
| Daily/hourly reporting | Batch (scheduled DAG) |
| Minutes-fresh dashboards | Micro-batch (5–15 min) |
| Sub-second / event-driven | Streaming (Kafka/Kinesis + Flink/Spark Streaming) |
| Operational replication | CDC stream (Debezium, native logical replication) |

Streaming costs more in engineering and ops. **Start with batch/micro-batch**; move to streaming only when the SLA truly demands it. Micro-batch satisfies most "real-time" requests.

## Lakehouse table formats

When landing to object storage, prefer an open table format over bare files:

- **Delta Lake** — ACID, MERGE, time travel; strong on Databricks/Spark.
- **Apache Iceberg** — engine-agnostic, hidden partitioning, schema evolution, broad warehouse support.
- **Apache Hudi** — upsert/CDC-optimized, incremental pulls.

All three give ACID + schema evolution + time travel, which directly enable idempotent MERGE and safe backfills. Avoid raw CSV/JSON for anything beyond a landing zone.

## Quick selection rules

1. Destination is a modern warehouse/lake → ELT.
2. Freshness > a few minutes acceptable → batch or micro-batch.
3. Must mask PII before storage → add an ETL redaction step at ingest.
4. Need replay/backfill cheaply → keep immutable raw, never transform-in-place.
