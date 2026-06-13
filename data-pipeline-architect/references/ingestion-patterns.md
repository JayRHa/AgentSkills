# Ingestion Patterns

Map every source to exactly one extraction strategy.

## 1. Full snapshot
Extract the entire dataset each run. Replace the target atomically.

- **Use when:** small tables (< ~1M rows), no reliable change column, dimension/reference data.
- **Idempotent because:** full replace is naturally idempotent (swap, don't append).
- **Cost:** O(table size) every run. Doesn't scale.

## 2. Incremental by high-watermark
Extract only rows changed since the last run, tracked by a monotonic column.

**Watermark column candidates (in order of preference):**
1. Append-only monotonic id / sequence (best — no clock skew).
2. `updated_at` maintained reliably by the source.
3. CDC log offset / LSN (see CDC below).

**The lookback rule.** Never query strictly `> last_watermark`. Use an overlap window to catch late writes and same-timestamp rows, then dedup:

```sql
-- Extract with a lookback (e.g., 2 hours / a few thousand ids)
SELECT * FROM source.orders
WHERE updated_at > :last_watermark - INTERVAL '2 hours';
```

After loading, advance the watermark to `MAX(updated_at)` of the extracted batch, stored in a state table:

```sql
CREATE TABLE IF NOT EXISTS meta.pipeline_state (
  pipeline    TEXT PRIMARY KEY,
  watermark   TIMESTAMPTZ NOT NULL,
  updated_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

Store state in a queryable table, never in code or a local file.

## 3. Change Data Capture (CDC)
Read the database's transaction log to stream inserts/updates/deletes.

- **Tools:** Debezium (Kafka), native logical replication, Fivetran/Airbyte connectors.
- **Use when:** you need deletes captured, near-real-time, or the source has no reliable `updated_at`.
- **Handling deletes:** CDC emits delete events — apply soft deletes (`_deleted = true`) in silver so history is preserved; hard-delete only if required by policy/GDPR.
- **Idempotency:** key on (primary key, log offset/op sequence); apply latest op per key.

## Late-arriving and out-of-order data

Late data is the norm, not the exception. Defenses:

1. **Lookback window** on extraction (above).
2. **Dedup on read** keeping the latest version per business key:

```sql
WITH ranked AS (
  SELECT *,
         ROW_NUMBER() OVER (
           PARTITION BY order_id
           ORDER BY updated_at DESC, _loaded_at DESC
         ) AS rn
  FROM bronze.orders
)
SELECT * EXCEPT(rn) FROM ranked WHERE rn = 1;
```

3. **Reprocess affected partitions** when late events land in old windows (event-time partitioning makes this targeted).
4. **Watermark + allowed lateness** in streaming: hold windows open for a bounded grace period.

## Metadata to stamp on every row

Add these technical columns at ingestion for lineage, dedup, and debugging:

- `_loaded_at` — when this row was ingested.
- `_source` — system/connector name.
- `_batch_id` / `_run_id` — the run that produced it.
- `_op` (for CDC) — insert/update/delete.

## Partitioning

- **Raw/bronze:** partition by **load date** (`_loaded_at::date`) → cheap replay and append.
- **Silver/gold:** partition by **event/business date** → query pruning for consumers.
- Keep partitions reasonably sized (target ~hundreds of MB to ~1 GB per file/partition); avoid the small-files problem with compaction.
