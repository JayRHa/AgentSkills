# Idempotency & Safe Re-runs

**Definition:** running a step N times produces the same target state as running it once. This is the single most important property of a reliable pipeline — it makes retries, backfills, and recovery safe.

## Anti-pattern

```sql
-- NEVER do this on a retryable task: re-running duplicates rows
INSERT INTO target.orders SELECT * FROM staging.orders;
```

## Pattern 1: MERGE / upsert on a stable key (preferred)

Requires a stable business/natural key and a recency tiebreaker.

```sql
MERGE INTO silver.orders AS t
USING (
  SELECT * FROM (
    SELECT *, ROW_NUMBER() OVER (
      PARTITION BY order_id ORDER BY updated_at DESC, _loaded_at DESC) rn
    FROM bronze.orders
    WHERE _loaded_at >= :batch_start
  ) WHERE rn = 1
) AS s
ON t.order_id = s.order_id
WHEN MATCHED AND s.updated_at > t.updated_at THEN UPDATE SET *
WHEN NOT MATCHED THEN INSERT *;
```

Re-running re-applies the same latest version → no duplicates, no drift.

## Pattern 2: Delete-insert by partition

When you reload whole partitions (e.g., a day). Idempotent because you delete the partition before reinserting it.

```sql
BEGIN;
DELETE FROM gold.daily_sales WHERE sales_date = :run_date;
INSERT INTO gold.daily_sales
SELECT ... FROM silver.orders WHERE order_date = :run_date;
COMMIT;
```

Match the delete predicate exactly to the insert's grain. Wrap in a transaction so a failure rolls back cleanly.

## Pattern 3: Staging + atomic swap

For full snapshots. Build the new table fully, then swap names atomically so consumers never see a partial state.

```sql
CREATE OR REPLACE TABLE staging.dim_customer_new AS SELECT ...;
-- atomic rename / partition swap
ALTER TABLE prod.dim_customer SWAP WITH staging.dim_customer_new;  -- Snowflake
-- BigQuery: CREATE OR REPLACE TABLE prod.dim_customer AS SELECT ...;
```

## Pattern 4: Deterministic keys / dedup on read

Generate a deterministic surrogate key (hash of business columns) so re-ingested rows collide instead of duplicating:

```sql
SELECT md5(order_id || '|' || line_no) AS _pk, * FROM bronze.order_lines;
```

Combined with dedup-on-read (`ROW_NUMBER`), this tolerates at-least-once delivery.

## Idempotency checklist

- [ ] Each task has a stable key OR a partition it fully owns.
- [ ] No blind `INSERT` into a target on a retryable path.
- [ ] Delete predicate exactly matches insert grain (delete-insert).
- [ ] Transactions wrap multi-statement target writes.
- [ ] Dedup keeps a deterministic "latest" (recency + tiebreaker).
- [ ] Backfilling date range [A,B] twice yields identical output.
- [ ] Watermark advances only after a successful, committed load.

## At-least-once vs exactly-once

Most ingestion is **at-least-once** (sources/queues re-deliver). You achieve effective exactly-once *semantics* downstream by making writes idempotent (dedup + MERGE), not by trusting the transport. Design for duplicates; eliminate them with keys.
