# Complexity Cheat Sheet & Optimization Patterns

## Big-O of common operations

| Data structure | Lookup | Insert | Delete | Notes |
|---|---|---|---|---|
| Array / list (index) | O(1) | O(1) end | O(n) middle | Append amortized O(1) |
| Dynamic array (search) | O(n) | — | — | Linear scan for value |
| Hash map / set | O(1) avg | O(1) avg | O(1) avg | O(n) worst (collisions) |
| Balanced tree / sorted map | O(log n) | O(log n) | O(log n) | Ordered iteration |
| Heap (priority queue) | O(1) peek | O(log n) | O(log n) pop | Top-k, scheduling |
| Linked list | O(n) | O(1) at node | O(1) at node | No random access |

## Common algorithm costs

| Pattern | Complexity | Faster alternative |
|---|---|---|
| Nested loop over same data | O(n²) | Hash set / single sort: O(n) / O(n log n) |
| Repeated `list.contains()` / `x in list` | O(n) each → O(n·m) | Build a `set` once: O(1) membership |
| Sort inside a loop | O(n² log n) | Sort once outside: O(n log n) |
| String concat in a loop (`s += ...`) | O(n²) | Collect to list, `"".join()` / builder: O(n) |
| Recompute pure function repeatedly | O(calls·cost) | Memoize / cache: O(unique) |
| Query inside a loop (N+1) | O(n) round-trips | Batch / JOIN / `IN (...)`: O(1) round-trips |
| Linear search of sorted data | O(n) | Binary search: O(log n) |
| Building intermediate full lists | extra O(n) memory | Generators / streaming: O(1) memory |

## Canonical "swap this for that" patterns

### 1. Membership / dedup — list → set
```python
# SLOW O(n*m): a list membership test for each item
result = [x for x in items if x in allowed_list]
# FAST O(n): hash-set membership
allowed = set(allowed_list)
result = [x for x in items if x in allowed]
```

### 2. Join two collections — nested loop → dict index
```python
# SLOW O(n*m)
for order in orders:
    for user in users:
        if user.id == order.user_id: ...
# FAST O(n+m)
users_by_id = {u.id: u for u in users}
for order in orders:
    user = users_by_id[order.user_id]
```

### 3. N+1 query — query-in-loop → batch fetch
```python
# SLOW: 1 + N queries
for post in posts:
    post.author = db.query("SELECT * FROM users WHERE id=?", post.author_id)
# FAST: 2 queries total
ids = {p.author_id for p in posts}
authors = {u.id: u for u in db.query("SELECT * FROM users WHERE id IN ?", ids)}
for post in posts:
    post.author = authors[post.author_id]
```
ORM equivalents: Django `select_related`/`prefetch_related`, SQLAlchemy
`joinedload`/`selectinload`, Rails `includes`.

### 4. Repeated pure computation — memoize
```python
from functools import lru_cache
@lru_cache(maxsize=None)
def expensive(n): ...
```

### 5. Hoist invariants out of loops
```python
# SLOW: recompute / re-fetch every iteration
for row in rows:
    cfg = load_config()        # invariant!
    process(row, cfg)
# FAST
cfg = load_config()
for row in rows:
    process(row, cfg)
```

### 6. Stream instead of buffer
```python
# SLOW: load whole file into memory
data = open('huge.csv').read().splitlines()
# FAST: iterate lazily, O(1) memory
for line in open('huge.csv'):
    ...
```

### 7. Batch I/O round-trips
```python
# SLOW: one network/disk call per item
for item in items:
    api.send(item)
# FAST: one call
api.send_bulk(items)        # or chunk into batches of e.g. 500
```

## Database index quick rules
- Index columns used in `WHERE`, `JOIN`, and `ORDER BY`.
- Composite index column order = equality columns first, then range/sort.
- A covering index (includes selected columns) avoids table lookups.
- Indexes speed reads but slow writes — don't over-index.
- Verify the index is actually used via `EXPLAIN` (planner may ignore it).

## When NOT to optimize
- The code isn't on a hot path (profiler says <~5% of total cost).
- It runs rarely and is already fast enough for the user.
- The win is dwarfed by a larger downstream bottleneck (Amdahl's law).
- The optimization meaningfully hurts readability for a gain nobody perceives.
