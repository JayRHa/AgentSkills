# Data Types, Constraints, Indexing & Naming

## Naming conventions

- Tables: singular or plural consistently (`customer` or `customers`) — pick one. snake_case.
- Primary key: `<table>_id` or `id`.
- Foreign key column: `<referenced_table>_id`.
- Constraints/indexes: `pk_<t>`, `fk_<t>_<ref>`, `uq_<t>_<cols>`, `ck_<t>_<rule>`, `ix_<t>_<cols>`.

## Cross-engine type mapping

| Need | PostgreSQL | MySQL (8+) | SQLite | SQL Server |
|------|-----------|------------|--------|-----------|
| Auto surrogate PK | `BIGINT GENERATED ALWAYS AS IDENTITY` | `BIGINT AUTO_INCREMENT` | `INTEGER PRIMARY KEY` (rowid) | `BIGINT IDENTITY(1,1)` |
| UUID | `UUID` | `CHAR(36)` / `BINARY(16)` | `TEXT` | `UNIQUEIDENTIFIER` |
| Short text | `TEXT` / `VARCHAR(n)` | `VARCHAR(n)` | `TEXT` | `NVARCHAR(n)` |
| Long text | `TEXT` | `TEXT`/`LONGTEXT` | `TEXT` | `NVARCHAR(MAX)` |
| Integer | `INTEGER`/`BIGINT` | `INT`/`BIGINT` | `INTEGER` | `INT`/`BIGINT` |
| Money / exact decimal | `NUMERIC(p,s)` | `DECIMAL(p,s)` | `NUMERIC` | `DECIMAL(p,s)` |
| Boolean | `BOOLEAN` | `BOOLEAN` (TINYINT(1)) | `INTEGER` (0/1) | `BIT` |
| Date | `DATE` | `DATE` | `TEXT` (ISO-8601) | `DATE` |
| Instant (UTC) | `TIMESTAMPTZ` | `TIMESTAMP`/`DATETIME` | `TEXT`/`INTEGER` | `DATETIME2` / `DATETIMEOFFSET` |
| Enum-like | `TEXT` + CHECK or native `ENUM type` | `ENUM(...)` | `TEXT` + CHECK | `NVARCHAR` + CHECK |
| JSON | `JSONB` | `JSON` | `TEXT` (JSON1) | `NVARCHAR(MAX)` (JSON) |
| Binary | `BYTEA` | `BLOB` | `BLOB` | `VARBINARY(MAX)` |

Rules of thumb:
- Money: **always** exact `NUMERIC`/`DECIMAL`, never `FLOAT`/`REAL`/`DOUBLE`.
- Store instants in UTC; prefer time-zone-aware types.
- Size `VARCHAR` to a real limit; don't reflexively use 255.
- Prefer native `BOOLEAN`/`UUID`/`JSONB` where the engine supports them.

## Constraint types

- `NOT NULL` — default; relax only for genuinely optional facts.
- `PRIMARY KEY` — one per table, immutable, minimal.
- `UNIQUE` — natural keys, even when a surrogate is PK.
- `FOREIGN KEY ... REFERENCES ... ON DELETE <a> ON UPDATE <a>` — always declare actions explicitly.
- `CHECK` — domain rules (`quantity > 0`, status whitelist, `end_date >= start_date`).
- `DEFAULT` — sensible defaults (`now()`, `'pending'`, `0`).

### Referential action guide

| Action | Use when |
|--------|----------|
| `RESTRICT` / `NO ACTION` | Parent must not be deleted while children exist (orders -> customer). Safe default. |
| `CASCADE` | Children are owned parts of the parent (order_item -> order). |
| `SET NULL` | Relationship is optional; orphaning is acceptable (employee.manager_id). FK column must be nullable. |

## Indexing strategy

1. Index **every foreign key column** (most engines do not do this automatically).
2. Add indexes matching real `WHERE`, `JOIN`, and `ORDER BY` columns.
3. Composite index column order: **equality predicates first, then range/sort columns**; most selective leading where ties.
4. A composite index on `(a, b)` also serves queries filtering on `a` alone — no separate single-column index on `a` needed.
5. Use partial/filtered indexes for hot subsets (`WHERE status = 'active'`) where supported.
6. Covering indexes (`INCLUDE` columns) avoid table lookups for read-hot queries.
7. Don't over-index: every index slows writes and costs storage. Drop unused indexes.

## Denormalization patterns (apply last)

| Pattern | What | Keep consistent via |
|---------|------|--------------------|
| Cached aggregate | `order.total_amount` | Trigger or application on item change |
| Duplicated lookup | `order.customer_country` copied | Trigger; or accept snapshot semantics |
| Materialized view | Precomputed report | Scheduled/`REFRESH` (engine-specific) |
| Pre-joined read table | Reporting/denorm table | ETL / CDC pipeline |

Always document: source of truth, sync mechanism, and tolerated staleness.
