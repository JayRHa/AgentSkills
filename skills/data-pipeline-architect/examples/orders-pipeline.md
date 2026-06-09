# Worked Example: Orders Pipeline (Postgres → Warehouse)

**Scenario:** Replicate an operational `orders` table from Postgres into a warehouse for daily revenue dashboards. ~2M new/updated rows/day, hourly freshness, no special PII beyond customer_id.

## 1. Requirements
- Consumers: Finance BI (daily revenue), churn ML feature store.
- Freshness SLA: 1 hour.
- Volume: ~2M changed rows/day, ~3 GB/day.
- PII: customer_id (pseudonymous) — no extra masking needed.

## 2. Load pattern
- **ELT** into a columnar warehouse; land raw first.
- **Micro-batch** every 30 min (well within 1h SLA, cheaper than streaming).
- Raw landed as Parquet/Delta partitioned by `_loaded_at::date`.

## 3. Ingestion strategy
- **Incremental by `updated_at`** (source maintains it reliably) with a **2-hour lookback**.
- Watermark stored in `meta.pipeline_state`.

```sql
SELECT *, now() AS _loaded_at, 'pg_orders' AS _source, :run_id AS _batch_id
FROM public.orders
WHERE updated_at > :last_watermark - INTERVAL '2 hours';
```

After a committed load: `watermark := MAX(updated_at)` of the batch.

## 4. Layers

**Bronze** — append raw extracts, partitioned by load date, additive schema evolution.

**Silver** — dedup to one row per `order_id` (latest), MERGE (idempotent):

```sql
MERGE INTO silver.orders t
USING (
  SELECT * FROM (
    SELECT *, ROW_NUMBER() OVER (PARTITION BY order_id
             ORDER BY updated_at DESC, _loaded_at DESC) rn
    FROM bronze.orders WHERE _loaded_at >= :batch_start
  ) WHERE rn = 1
) s
ON t.order_id = s.order_id
WHEN MATCHED AND s.updated_at > t.updated_at THEN UPDATE SET *
WHEN NOT MATCHED THEN INSERT *;
```

**Gold** — `daily_revenue`, rebuilt per day via delete-insert (idempotent backfill):

```sql
BEGIN;
DELETE FROM gold.daily_revenue WHERE order_date = :run_date;
INSERT INTO gold.daily_revenue
SELECT order_date, sum(amount) revenue, count(*) orders
FROM silver.orders
WHERE order_date = :run_date AND status != 'cancelled'
GROUP BY order_date;
COMMIT;
```

## 5. Schema evolution
- Bronze auto-adds new optional columns.
- Silver/Gold are contract-tested; a dropped/renamed column fails dbt tests → batch quarantined, on-call alerted.

## 6. Orchestration (Airflow + dbt)
- DAG every 30 min: `extract_orders` → `load_bronze` → `dbt build` (silver, gold, tests).
- `retries=3`, exponential backoff, `execution_timeout=1h`, `sla=1h`, failure callback pages on-call.

## 7. Data quality gates
- Post-ingest: schema matches, `row_count >= 0`, freshness (`max(_loaded_at) within 1h`).
- Post-silver: `order_id` unique + not_null; `status` in accepted set; `customer_id` relationships test.
- Post-gold: reconciliation — `sum(gold.revenue)` for the day equals `sum(silver.amount)` of non-cancelled orders.

## 8. Backfill
Re-run for any date range; delete-insert on gold and MERGE on silver make it duplicate-free:

```bash
airflow dags backfill orders_pipeline -s 2026-01-01 -e 2026-01-31 --max-active-runs 2
```

## 9. Why this is safe
- Raw is immutable → can replay any window from bronze without re-hitting Postgres.
- Every write is idempotent (MERGE / delete-insert) → retries and backfills can't duplicate.
- Lookback + dedup → late updates within the same second are not lost.
- Quality gates block promotion → Finance never sees half-loaded days.
