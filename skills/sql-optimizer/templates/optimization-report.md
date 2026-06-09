# SQL Optimization Report

**Date:** <YYYY-MM-DD>
**Engine / version:** <e.g. PostgreSQL 15.4>
**Query / endpoint:** <name or location of the query>
**Reported by / symptom:** <"order history page times out", etc.>

## 1. Query
```sql
<the exact query, with realistic parameter values>
```

## 2. Environment
- Affected table(s) and row counts: <orders ~48M, items ~120M>
- Existing indexes: <list>
- Run frequency / criticality: <e.g. every page load; p95 SLA 200ms>

## 3. Before (evidence)
Plan command used: `<EXPLAIN (ANALYZE, BUFFERS) ...>`
```
<paste the dominant part of the plan>
```
- Dominant cost node: <Seq Scan on orders — 4.12s, removed 48M rows>
- Total execution time: <4180 ms>
- Estimate vs actual skew: <none / 50x on node X>
- I/O: <buffers read 812,004>

## 4. Root cause
<One or two sentences. e.g. "Highly selective filter (0.002% of rows) served by a full table scan
because no supporting index exists.">

## 5. Change applied
Change type: [ ] statistics  [ ] rewrite  [ ] index  [ ] schema  [ ] config
```sql
<the exact DDL / rewritten query>
```
Rationale: <why this column order / why covering / why this rewrite>

## 6. After (evidence)
```
<paste the new plan's dominant part>
```
- New plan: <Index Only Scan, no sort, Heap Fetches 0>
- Total execution time: <0.11 ms>
- Improvement: <~38,000x>

## 7. Trade-offs & follow-ups
- Write/storage cost: <+1.6GB index, minor insert overhead — justified by run frequency>
- Risk: <built with CONCURRENTLY; no downtime>
- Redundant/now-unused indexes to drop: <none / ix_old_single_col>
- Monitoring: <watch pg_stat_user_indexes.idx_scan to confirm usage>
