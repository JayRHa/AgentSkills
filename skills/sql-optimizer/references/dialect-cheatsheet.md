# Dialect Cheat Sheet

Commands to collect plans, statistics, and metadata per engine.

## PostgreSQL
```sql
-- Plan with actuals + I/O
EXPLAIN (ANALYZE, BUFFERS, VERBOSE, FORMAT TEXT) <query>;
EXPLAIN (ANALYZE, FORMAT JSON) <query>;   -- feed to scripts/explain_analyzer.py

-- Table size & row estimate
SELECT reltuples::bigint AS est_rows, pg_size_pretty(pg_total_relation_size('orders'));
SELECT count(*) FROM orders;              -- true count

-- Existing indexes
SELECT indexname, indexdef FROM pg_indexes WHERE tablename = 'orders';

-- Refresh statistics
ANALYZE orders;            -- VACUUM ANALYZE orders; to also reclaim/freeze

-- Column stats / skew
SELECT attname, n_distinct, most_common_vals FROM pg_stats WHERE tablename='orders';

-- Unused indexes
SELECT relname, indexrelname, idx_scan FROM pg_stat_user_indexes WHERE idx_scan = 0;

-- Memory knob for sorts/hashes (session)
SET work_mem = '64MB';
```

## MySQL / MariaDB
```sql
EXPLAIN ANALYZE <query>;            -- MySQL 8.0.18+, actual timings
EXPLAIN FORMAT=JSON <query>;        -- detailed estimates

SHOW INDEX FROM orders;
SHOW TABLE STATUS LIKE 'orders';    -- Rows is approximate
SELECT COUNT(*) FROM orders;

ANALYZE TABLE orders;               -- refresh index statistics

-- Optimizer trace (deep dive)
SET optimizer_trace='enabled=on';
<query>;
SELECT * FROM information_schema.optimizer_trace;
```

## SQL Server
```sql
SET STATISTICS IO, TIME ON;         -- logical reads + CPU/elapsed
-- enable "Include Actual Execution Plan" in SSMS / Ctrl+M

EXEC sp_helpindex 'dbo.Orders';
SELECT * FROM sys.dm_db_index_usage_stats WHERE object_id = OBJECT_ID('dbo.Orders');

UPDATE STATISTICS dbo.Orders WITH FULLSCAN;

-- Missing index DMV hints (validate, don't blindly apply)
SELECT * FROM sys.dm_db_missing_index_details;
```

## Oracle
```sql
EXPLAIN PLAN FOR <query>;
SELECT * FROM TABLE(DBMS_XPLAN.DISPLAY);
-- after executing for real, with bind values:
SELECT * FROM TABLE(DBMS_XPLAN.DISPLAY_CURSOR(FORMAT=>'ALLSTATS LAST'));

SELECT index_name, column_name FROM user_ind_columns WHERE table_name = 'ORDERS';
EXEC DBMS_STATS.GATHER_TABLE_STATS(USER, 'ORDERS');
SELECT num_rows FROM user_tables WHERE table_name = 'ORDERS';
```

## SQLite
```sql
EXPLAIN QUERY PLAN <query>;
ANALYZE;                            -- refresh sqlite_stat1
.indexes orders                     -- (CLI dot command)
SELECT count(*) FROM orders;
```

## Safety for write queries
To plan/test UPDATE/DELETE without changing data (PostgreSQL example):
```sql
BEGIN;
EXPLAIN (ANALYZE, BUFFERS) UPDATE orders SET status='x' WHERE ...;
ROLLBACK;
```
Or rewrite the WHERE into a `SELECT count(*)` / `SELECT ...` of the same shape to inspect the scan.
