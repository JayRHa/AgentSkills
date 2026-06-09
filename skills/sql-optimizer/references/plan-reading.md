# Reading Execution Plans

Goal: find the single node that dominates total time, then explain *why* it is expensive.

## How to read, by engine

### PostgreSQL
Use `EXPLAIN (ANALYZE, BUFFERS, VERBOSE) <query>`. Read **inner-most / most-indented first**.
Each node shows:
```
Node  (cost=START..TOTAL rows=EST width=BYTES) (actual time=FIRST..LAST rows=ACT loops=N)
```
- **Total node time = `actual time (last)` * `loops`.** A node showing `0.05ms` but `loops=50000`
  is the real hot spot (2.5s).
- Compare `rows=EST` (planner estimate) vs `rows=ACT` (reality). A >10x gap = bad estimate.
- `Buffers: shared hit=... read=...` — `read` means it went to disk/OS cache. High `read` = I/O bound.
- Look for `Sort Method: external merge Disk: 24000kB` → sort spilled to disk (raise work_mem or index).

### MySQL / MariaDB
`EXPLAIN ANALYZE` (8.0.18+) gives actual timing. Older: `EXPLAIN FORMAT=JSON`. Key columns of
classic `EXPLAIN`:
- `type`: from best to worst — `const` > `eq_ref` > `ref` > `range` > `index` > `ALL`.
  `ALL` = full table scan. `index` = full index scan (often still bad).
- `key`: which index was actually chosen (`NULL` = none).
- `rows`: estimated rows examined per the optimizer.
- `Extra`: watch for `Using filesort`, `Using temporary`, `Using where` (good: `Using index` = covering).

### SQL Server
Turn on `SET STATISTICS IO, TIME ON` and capture the **Actual** execution plan. Watch for:
- `Table Scan` / `Clustered Index Scan` on large tables with selective filters → missing index.
- `Key Lookup (Clustered)` repeated many times → add INCLUDE columns to make the index covering.
- Thick arrows = many rows flowing; the estimated-vs-actual row counts on each operator.
- A green "Missing Index" hint — treat as a suggestion, validate before applying.

### Oracle
```sql
EXPLAIN PLAN FOR <query>;
SELECT * FROM TABLE(DBMS_XPLAN.DISPLAY);
-- after running for real:
SELECT * FROM TABLE(DBMS_XPLAN.DISPLAY_CURSOR(FORMAT=>'ALLSTATS LAST'));
```
Compare `E-Rows` (estimated) with `A-Rows` (actual). `TABLE ACCESS FULL` on a big table with a
selective predicate signals a missing/unused index. `Buffers` column = logical reads.

### SQLite
`EXPLAIN QUERY PLAN <query>;` Output like `SCAN TABLE t` (full scan) vs
`SEARCH TABLE t USING INDEX ix (col=?)` (index used). `USE TEMP B-TREE FOR ORDER BY` = sort not
served by an index.

## Diagnosis Table

| Symptom in plan | Likely cause | First fix |
|---|---|---|
| Seq/Full/Table Scan on large table + selective WHERE | no usable index | add index on filter column(s) |
| Index exists but `key=NULL` / scan chosen | non-sargable predicate, type mismatch, low selectivity | rewrite predicate; or scan is correct |
| `rows=EST` >> or << `rows=ACT` | stale statistics or skewed data | `ANALYZE` / `UPDATE STATISTICS`; consider extended stats |
| Sort spills to disk (`external merge`, `Using filesort`) | ORDER BY/GROUP BY not indexed; small work_mem | composite index covering sort; raise work_mem |
| Nested loop with high `loops` | N+1, or join with no index on inner side | index inner join column; batch; or hash join |
| `Key Lookup` / `Bookmark Lookup` repeated | non-covering index | add INCLUDE/extra columns |
| Hash join builds huge hash | join produces/consumes too many rows | filter earlier; reduce intermediate set |
| `Using temporary` (MySQL) | GROUP BY/DISTINCT/UNION needs temp table | index to support grouping; rewrite |
| Many rows returned then discarded | over-fetching | add LIMIT, narrow predicate, paginate |

## What "good" looks like
- Index Seek/`ref`/`SEARCH ... USING INDEX` instead of a scan on the big table.
- `rows=EST` within ~2-3x of `rows=ACT`.
- No disk spill on sorts/hashes for the working set.
- Total actual time dropped meaningfully and the dominant node changed or shrank.
