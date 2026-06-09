# Worked Example: From 4.2s to 11ms

**Engine:** PostgreSQL 15. **Complaint:** "The customer order history page times out."

## 1. The query
```sql
SELECT o.id, o.total, o.created_at
FROM orders o
WHERE o.customer_id = 80421
  AND o.created_at >= '2024-01-01'
ORDER BY o.created_at DESC
LIMIT 20;
```
`orders` has ~48 million rows. Existing index: `orders_pkey (id)` only.

## 2. Capture the real plan
```sql
EXPLAIN (ANALYZE, BUFFERS) <query>;
```
```
Limit  (actual time=4180.2..4180.3 rows=20 loops=1)
  ->  Sort  (actual time=4180.2..4180.2 rows=20 loops=1)
        Sort Key: created_at DESC
        Sort Method: top-N heapsort  Memory: 28kB
        ->  Seq Scan on orders o  (actual time=0.3..4120.7 rows=1163 loops=1)
              Filter: (customer_id = 80421 AND created_at >= '2024-01-01')
              Rows Removed by Filter: 47998837
              Buffers: shared read=812004
 Planning Time: 0.2 ms
 Execution Time: 4180.5 ms
```

## 3. Find the dominant cost
The `Seq Scan` took ~4.12s and **removed 47,998,837 rows** to find 1,163. Classic missing-index
symptom: a highly selective filter (1,163 of 48M ≈ 0.0024%) is being served by a full scan.
High `Buffers: read` confirms it is I/O bound.

## 4. Classify + design the index
Bucket: *full scan on large table with selective filter.* Apply the E-R-S ordering rule from
`references/indexing-guide.md`:
- `customer_id` — equality predicate → first.
- `created_at` — range filter **and** the ORDER BY column → second, descending to match the sort.
- SELECT needs `id, total` → add as INCLUDE to make it covering (index-only scan, skip the heap).

```sql
CREATE INDEX CONCURRENTLY ix_orders_cust_created
  ON orders (customer_id, created_at DESC)
  INCLUDE (id, total);
```
(`CONCURRENTLY` avoids locking writes on the live 48M-row table.)

## 5. Verify
```
Limit  (actual time=0.05..0.09 rows=20 loops=1)
  ->  Index Only Scan using ix_orders_cust_created on orders o
        (actual time=0.04..0.07 rows=20 loops=1)
        Index Cond: (customer_id = 80421 AND created_at >= '2024-01-01')
        Heap Fetches: 0
        Buffers: shared hit=6
 Execution Time: 0.11 ms
```
Result: Seq Scan → **Index Only Scan**, no sort node (the index is already in `created_at DESC`
order so `LIMIT 20` just reads the first 20), `Heap Fetches: 0` (covering), buffers 812,004 → 6.
Execution time **4180ms → 0.11ms**.

## 6. Trade-offs noted
- New index adds ~1.6GB storage and a small write cost on each order insert. Justified: this query
  runs on every page load for every customer.
- No query rewrite was needed — the predicate was already sargable; only the index was missing.

See `templates/optimization-report.md` for how this is handed off.
