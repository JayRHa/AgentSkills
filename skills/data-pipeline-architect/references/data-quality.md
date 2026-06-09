# Data Quality

Quality checks are part of the pipeline DAG. A failed critical check **blocks promotion** to the next layer or quarantines the batch. Warnings-only checks let bad data through — avoid them for anything load-bearing.

## Where to place gates

```
ingest ─▶ [QC: schema match, row count > 0, freshness] ─▶ bronze
bronze ─▶ [QC: pk uniqueness, not-null keys, dedup ok] ─▶ silver
silver ─▶ [QC: referential integrity, accepted values, metric reconciliation] ─▶ gold
gold   ─▶ [QC: freshness SLA, volume anomaly, BI contract] ─▶ consumers
```

## Check taxonomy

| Category | Examples | Severity default |
|---|---|---|
| **Schema** | expected columns present, types match contract | block |
| **Completeness** | not-null on keys, required fields | block |
| **Uniqueness** | PK / business key unique, no dupes | block |
| **Validity** | accepted values, ranges, regex, enums | block |
| **Referential** | every FK exists in parent | block |
| **Freshness** | max(_loaded_at) within SLA | block/alert |
| **Volume** | row count within expected band (anomaly) | alert |
| **Distribution** | mean/null-rate within tolerance | alert |
| **Reconciliation** | sum(gold) == sum(source) for a control total | block |

## dbt tests (declarative)

```yaml
models:
  - name: silver_orders
    columns:
      - name: order_id
        tests: [unique, not_null]
      - name: status
        tests:
          - accepted_values: {values: ['placed','shipped','cancelled']}
      - name: customer_id
        tests:
          - relationships: {to: ref('silver_customers'), field: customer_id}
    tests:
      - dbt_utils.recency: {datepart: hour, field: _loaded_at, interval: 6}
```

Use `dbt build` (not `dbt run`) so models and tests run together; a failing test stops dependents.

## Great Expectations (programmatic, for non-SQL stages)

```python
validator.expect_column_values_to_not_be_null("order_id")
validator.expect_column_values_to_be_unique("order_id")
validator.expect_column_values_to_be_in_set("status", ["placed","shipped","cancelled"])
validator.expect_table_row_count_to_be_between(min_value=1, max_value=10_000_000)
```

## Freshness check (SQL)

```sql
SELECT CASE
  WHEN max(_loaded_at) < now() - INTERVAL '6 hours'
  THEN error('STALE: orders not refreshed within SLA')
END
FROM bronze.orders;
```

## Volume anomaly (simple band)

```sql
-- Compare today's count to trailing 7-day average; alert if off by > 40%
WITH d AS (SELECT count(*) c FROM silver.orders WHERE order_date = current_date),
     h AS (SELECT avg(c) avg_c FROM (
        SELECT count(*) c FROM silver.orders
        WHERE order_date BETWEEN current_date-7 AND current_date-1
        GROUP BY order_date))
SELECT d.c, h.avg_c FROM d, h
WHERE abs(d.c - h.avg_c) > 0.4 * h.avg_c;
```

## Quarantine pattern

Rows failing validity but not schema → route to `quarantine.<table>` with a `_reason`, alert, and continue with the clean subset. Reprocess quarantine after fixes. This keeps one bad row from failing an entire batch while ensuring nothing bad is silently promoted.

## Principles

- Make critical checks **blocking**; reserve alerts for anomalies you can't auto-decide.
- Test the **keys and contracts** first — they cause the worst downstream damage.
- Add a **reconciliation control total** end-to-end; it catches silent row loss.
- Version checks with the models; review changes to severity.
