# Indexing Guide

## When an index helps
An index pays off when the query reads a **small fraction** of the table (selective predicate),
or when it lets the engine avoid a sort, or serve a query entirely from the index (covering).
For predicates matching a large share of rows (e.g. `status <> 'archived'` on mostly-active data),
a full scan can be the *correct* plan — adding an index will not help and just slows writes.

Rough selectivity guide for a non-covering B-tree index to be chosen:
- < ~5% of rows matched: index almost always wins.
- 5-15%: depends on row width, clustering, and visibility/heap fetches.
- > ~20%: scan usually wins.

## Index types (B-tree unless noted)
| Type | Good for | Engines |
|---|---|---|
| B-tree | equality, range, sort, prefix LIKE | all |
| Hash | equality only | PG (limited), MySQL MEMORY |
| GIN/GiST | full text, arrays, JSONB, geometry | PostgreSQL |
| BRIN | huge, naturally-ordered tables (time series) | PostgreSQL |
| Composite | multi-column filters/sorts | all |
| Covering (INCLUDE) | index-only scans | PG, SQL Server, others |
| Partial / filtered | indexing a subset (`WHERE active`) | PG (partial), SQL Server (filtered) |
| Functional / expression | `lower(email)`, computed values | PG, others |
| Full-text | text search | all (varies) |

## Composite index column ordering — the core rule
Order columns: **Equality → Range → Sort/Order → Include(covering).** ("E-R-S".)

For a query:
```sql
SELECT id, total FROM orders
WHERE customer_id = ? AND created_at >= ?
ORDER BY created_at DESC;
```
Best index:
```sql
CREATE INDEX ix_orders_cust_created ON orders (customer_id, created_at DESC) INCLUDE (id, total);
--                                       ^equality      ^range+sort           ^covering payload
```
- `customer_id` first (equality) narrows to one customer.
- `created_at` second serves both the range filter and the ORDER BY (no separate sort).
- `INCLUDE (id, total)` makes it covering → index-only scan, no heap/table lookups.

### Leading-column rule
A composite index `(a, b, c)` can satisfy predicates on `a`, `a,b`, or `a,b,c` — but **not** a
query filtering only on `b` or `c`. The leftmost prefix must be used.

## Covering indexes
If a query's SELECT and WHERE columns all live in one index, the engine never touches the table
("index-only scan" / `Using index`). Add non-key columns via `INCLUDE (...)` (PG/SQL Server) or as
trailing key columns. This removes Key Lookups — often the single biggest win.

## Partial / filtered indexes
Index only the rows you query:
```sql
CREATE INDEX ix_orders_open ON orders (created_at) WHERE status = 'open';  -- PostgreSQL
```
Smaller, faster, cheaper to maintain when most queries target the same subset.

## Expression / functional indexes
If you must filter on a transformed column, index the expression so the predicate stays sargable:
```sql
CREATE INDEX ix_users_lower_email ON users (lower(email));
-- then query WHERE lower(email) = lower(?)
```

## Costs to weigh before recommending
- **Writes:** each index adds work to every INSERT/UPDATE/DELETE touching its columns.
- **Storage:** wide covering indexes can rival the table size.
- **Maintenance:** more indexes = longer VACUUM/rebuild/stats time.
- **Redundancy:** `(a)` is redundant if `(a, b)` exists. Drop the prefix-only index.

Find unused/redundant indexes — see `references/dialect-cheatsheet.md` for the per-engine catalog queries.
