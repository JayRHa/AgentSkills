# Query Rewrite Patterns

Rewrites are free (no schema change). Try them before adding indexes. The unifying theme is
**make predicates sargable** (the optimizer can use an index range) and **do less work**.

## 1. Don't wrap indexed columns in functions
```sql
-- BAD: function on column defeats the index
WHERE YEAR(created_at) = 2024
-- GOOD: range on the raw column (sargable)
WHERE created_at >= '2024-01-01' AND created_at < '2025-01-01'
```

```sql
-- BAD
WHERE UPPER(email) = 'A@B.COM'
-- GOOD: expression index on lower(email) + match it, or store normalized
WHERE email = 'a@b.com'   -- with a functional index lower(email) if case-insensitive
```

## 2. Avoid implicit type casts
A `varchar` column compared to a number, or `int` column to a string, forces a cast that disables
the index. Match types exactly and bind parameters with the column's type.

## 3. Leading wildcard LIKE
```sql
-- BAD: cannot use a B-tree index
WHERE name LIKE '%smith'
-- GOOD: prefix search is sargable
WHERE name LIKE 'smith%'
-- For contains-search, use full-text / trigram (pg_trgm GIN) index instead.
```

## 4. OR across columns → UNION ALL
```sql
-- BAD: OR on different columns often blocks index use
SELECT * FROM t WHERE a = 1 OR b = 2;
-- GOOD: each branch uses its own index
SELECT * FROM t WHERE a = 1
UNION ALL
SELECT * FROM t WHERE b = 2 AND a <> 1;  -- de-dup overlap as needed
```

## 5. IN-list vs OR (same column)
```sql
-- Fine and index-friendly:
WHERE status IN ('open','pending');
```

## 6. Correlated subquery → JOIN / window
```sql
-- BAD: runs the subquery per outer row
SELECT o.*, (SELECT COUNT(*) FROM items i WHERE i.order_id = o.id) AS n
FROM orders o;
-- GOOD: single aggregate join
SELECT o.*, COALESCE(c.n, 0) AS n
FROM orders o
LEFT JOIN (SELECT order_id, COUNT(*) n FROM items GROUP BY order_id) c
  ON c.order_id = o.id;
```

## 7. NOT IN with nullable column → NOT EXISTS / LEFT JOIN
```sql
-- BAD: NULL semantics + poor plans
WHERE id NOT IN (SELECT customer_id FROM blocked);
-- GOOD:
WHERE NOT EXISTS (SELECT 1 FROM blocked b WHERE b.customer_id = t.id);
```

## 8. Pagination: keyset over OFFSET
```sql
-- BAD: OFFSET 100000 scans and discards 100000 rows
SELECT * FROM events ORDER BY id LIMIT 20 OFFSET 100000;
-- GOOD: seek/keyset pagination
SELECT * FROM events WHERE id > :last_id ORDER BY id LIMIT 20;
```

## 9. Narrow the SELECT list
`SELECT *` blocks index-only scans and ships unused bytes. Select only needed columns so a covering
index can serve the query.

## 10. Push filters down / eliminate early
Filter before joining/aggregating. Apply `WHERE` on the largest table first; only join the rows
that survive. Use derived tables/CTEs that prefilter (note: some engines materialize CTEs).

## 11. Kill the N+1
ORM loops that issue one query per parent row are the most common app-level slowdown.
```
# BAD (N+1): 1 + N queries
for o in orders: o.items   # lazy load per order
# GOOD: eager load / single join
orders = Order.objects.prefetch_related('items')   # or a JOIN
```

## 12. EXISTS vs COUNT for existence checks
```sql
-- BAD: counts everything just to test > 0
IF (SELECT COUNT(*) FROM t WHERE ...) > 0
-- GOOD: stops at first match
IF EXISTS (SELECT 1 FROM t WHERE ...)
```

## 13. DISTINCT masking a bad join
`SELECT DISTINCT` to remove duplicates often hides a fan-out join. Fix the join (use EXISTS or
aggregate) instead of paying for a dedup sort over a bloated result.

Always re-run the analyze form after a rewrite to confirm the plan actually changed.
