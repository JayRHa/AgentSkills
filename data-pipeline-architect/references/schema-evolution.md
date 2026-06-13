# Schema Evolution

Schemas change. The goal is to absorb safe changes automatically and surface breaking ones loudly — without corrupting downstream consumers.

## Change taxonomy

| Change | Safe? | Default handling |
|---|---|---|
| Add nullable/optional column | Safe (additive) | Auto-add in raw/bronze |
| Add column with default | Safe | Auto-add; backfill default |
| Widen type (int→bigint, etc.) | Usually safe | Allow; validate |
| Drop column | Breaking | Quarantine/alert; never silent |
| Rename column | Breaking | Treat as drop+add; map explicitly |
| Narrow/incompatible type change | Breaking | Fail/quarantine; require migration |
| Change column semantics (same name) | Breaking & sneaky | Contract test must catch |

## Policy per layer

- **Bronze / raw:** **additive auto-evolution.** New columns appear automatically; never block ingestion on a new optional field. Keep everything; missing fields are null for old rows.
- **Silver:** **explicit, validated schema.** Map raw → typed columns deliberately. Breaking upstream changes fail tests here, not in dashboards.
- **Gold / marts:** **strict contract.** These power BI/ML. Changes go through review + versioning. Never auto-evolve.

## File/table formats and what they support

| Format | Add col | Drop col | Rename | Type promote | Notes |
|---|---|---|---|---|---|
| CSV | manual | manual | no | no | Avoid beyond landing |
| JSON | yes | yes | n/a | n/a | Flexible but untyped |
| Avro | yes (w/ default) | yes | aliases | yes | Schema registry friendly |
| Parquet | yes | yes | no | limited | Columnar, common in lakes |
| Delta / Iceberg / Hudi | yes | yes | yes | yes | Full evolution + time travel |

For evolving sources, prefer Avro (with a **schema registry** and compatibility mode) on the wire and Delta/Iceberg at rest.

## Schema registry compatibility modes (Avro/Protobuf)

- **BACKWARD** (default): new schema can read old data — safe to add optional fields / remove fields with defaults. Consumers upgrade first.
- **FORWARD:** old schema can read new data. Producers upgrade first.
- **FULL:** both. **NONE:** no checks (avoid).

Choose BACKWARD for most analytics consumers.

## Detecting and handling drift

1. **Diff incoming schema vs expected** at ingest. Compute added/removed/type-changed columns.
2. **Additive →** evolve target, log the change, continue.
3. **Breaking →** route the batch to a `quarantine` zone, alert, and **do not** promote. Replay after the contract is fixed.
4. **Track schema versions** in a `meta.schema_history` table (column set + hash + first_seen).

```sql
CREATE TABLE IF NOT EXISTS meta.schema_history (
  dataset      TEXT,
  schema_hash  TEXT,
  columns      JSON,
  first_seen   TIMESTAMPTZ DEFAULT now(),
  PRIMARY KEY (dataset, schema_hash)
);
```

## Data contracts

A data contract is a versioned, testable agreement between producer and consumer: column names, types, nullability, semantics, and SLAs. Enforce it with automated tests in CI and at the silver boundary. Breaking the contract should fail the producer's pipeline, not the consumer's dashboard.
