# Pipeline Design: <pipeline-name>

> Fill every section. Empty sections are design gaps. Lint with `scripts/pipeline_lint.py`.

## 1. Requirements
- **Purpose / consumers:** <BI / ML / reverse-ETL / ...>
- **Freshness SLA:** <real-time | 15 min | hourly | daily>
- **Volume:** <rows/day, GB/day, peak>
- **Data sensitivity / PII:** <yes/no; handling>
- **Owners / on-call:** <team, contact>

## 2. Sources
| Source | Type | Extraction strategy | Watermark col | Volume | Notes |
|---|---|---|---|---|---|
| | db/api/file/stream | full / incremental / cdc | | | |

## 3. Load pattern
- **ETL or ELT:** <ELT default> — rationale:
- **Batch / micro-batch / streaming:** 
- **Destination:** <warehouse/lake + format>
- **Raw landing:** partitioned by <load date>; immutable: yes

## 4. Idempotency (REQUIRED)
- **Business key(s):** 
- **Pattern:** <MERGE | delete-insert by partition | staging swap>
- **Dedup / recency tiebreaker:** 
- **Re-run safety statement:** running range [A,B] twice yields identical output because ...

## 5. Incremental extraction & watermarks
- **Watermark storage:** meta.pipeline_state table
- **Lookback window:** 
- **Late-arriving handling:** 

## 6. Schema evolution policy
- **Bronze:** additive auto-evolve
- **Silver/Gold:** explicit contract; breaking change → <quarantine | fail | alert>
- **Format / registry:** 

## 7. Transformation layers
- **Bronze →** 
- **Silver →** 
- **Gold →** 
- **Transform tool:** <dbt / Spark / SQL>

## 8. Orchestration
- **Tool:** <Airflow / Dagster / Prefect / dbt>
- **Schedule / trigger:** 
- **Retries:** <count + backoff>
- **Timeout / SLA:** 
- **Alerting:** 

## 9. Data quality gates (REQUIRED)
| Stage | Checks | Severity (block/alert) |
|---|---|---|
| post-ingest | schema, row_count>0, freshness | |
| post-silver | pk unique, not-null keys, accepted values, referential | |
| post-gold | freshness SLA, volume anomaly, reconciliation | |

## 10. Backfill & recovery
- **Parameterized by:** <run_date / partition>
- **Backfill command:** 
- **Concurrency limit during backfill:** 

## 11. Observability & cost
- **Metrics emitted:** rows in/out, duration, freshness lag, check results
- **Lineage:** 
- **Partitioning / pruning for cost:** 
- **Estimated cost:** 

## 12. Open risks / decisions
- 
