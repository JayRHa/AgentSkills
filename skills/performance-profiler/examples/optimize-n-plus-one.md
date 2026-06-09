# Worked Example: From 1.9s to 60ms (N+1 + missing index)

A `/dashboard` endpoint that lists 50 recent orders is slow. We follow the full
loop: measure -> profile -> diagnose -> fix -> verify.

## 1. Goal & metric

> Cut `/dashboard` p95 latency from ~1.9s to under 200ms with the same output.

Primary metric: server-side request latency (median + p95). Correctness: the
rendered order list must be byte-identical.

## 2 & 3. Reproduce + baseline

Seed a representative DB (50k users, 200k orders) and hit the endpoint 30 times:

```
baseline (A):
  median : 1.880 s
  p95    : 2.050 s
```

Log the result. Now find *why*.

## 4. Profile

Attach a sampling profiler and, crucially, log the SQL for one request:

```bash
py-spy record -o flame.svg --pid <gunicorn-worker-pid>
```

The flamegraph shows ~80% of time inside the DB driver's `execute`, called from
a loop in `render_orders`. SQL logging confirms the smoking gun:

```
SELECT * FROM orders ORDER BY created_at DESC LIMIT 50;     -- 1 query
SELECT * FROM users WHERE id = 1013;                        -- repeated...
SELECT * FROM users WHERE id = 4471;                        -- ...50 times
...                                                          -- N+1!
```

Two problems: (a) a classic **N+1** — one user lookup per order; (b) each user
lookup is a `Seq Scan` because `users.id` lookups go through an unindexed path
on a 50k-row table (verified with `EXPLAIN ANALYZE`).

## 5. Fix (one change at a time)

### Fix A — collapse N+1 into a single batched query

```python
# BEFORE: 1 + 50 queries
orders = db.query("SELECT * FROM orders ORDER BY created_at DESC LIMIT 50")
for o in orders:
    o.user = db.query_one("SELECT * FROM users WHERE id = ?", o.user_id)

# AFTER: 2 queries total
orders = db.query("SELECT * FROM orders ORDER BY created_at DESC LIMIT 50")
user_ids = {o.user_id for o in orders}
users = db.query("SELECT * FROM users WHERE id IN ?", tuple(user_ids))
by_id = {u.id: u for u in users}
for o in orders:
    o.user = by_id[o.user_id]
```

Re-measure: **1.880s -> 240ms**. Huge, but still over target.

### Fix B — add the index the profiler implicated

```sql
CREATE INDEX CONCURRENTLY idx_users_id ON users (id);  -- if PK wasn't indexed
-- and the real win here: index the orders sort
CREATE INDEX idx_orders_created_at ON orders (created_at DESC);
```

`EXPLAIN ANALYZE` now shows an `Index Scan` instead of `Seq Scan` for the
orders ordering.

## 6. Verify

Re-run the exact baseline benchmark (and confirm identical output):

```bash
python scripts/bench.py --compare \
  --cmd   "curl -s localhost:8000/dashboard" \
  --cmd-b "curl -s localhost:8000/dashboard" \
  -n 30 --warmup 5
```

```
comparison (median):
  A median = 1.880 s
  B median = 60.2 ms
  speedup  = 31.23x  (-96.8% change)  -> B is FASTER
```

- p95 dropped from 2.05s to 88ms — under the 200ms target.
- Output diff: empty (correctness preserved).

## 7. Guard against regression

Add a test that fails if the endpoint issues more than 2 queries:

```python
def test_dashboard_query_count(query_counter):
    client.get("/dashboard")
    assert query_counter.count <= 2, "N+1 regression on /dashboard"
```

## Takeaways

- The biggest win came from **doing less I/O** (N+1 -> batch), not from CPU
  micro-tuning — exactly what the CPU-vs-I/O decision rule predicted.
- We changed one thing at a time, so each win was attributable.
- A cheap regression test locks in the gain forever.
