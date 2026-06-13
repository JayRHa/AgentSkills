# Schema Design: <PROJECT / DOMAIN NAME>

- **Target engine:** <PostgreSQL | MySQL | SQLite | SQL Server> <version>
- **Normalization target:** 3NF (note any documented exceptions)
- **Expected scale / read-write profile:** <rows, RPS, read-heavy/write-heavy>

## 1. Entities

| Entity | Description | Notable attributes |
|--------|-------------|--------------------|
| <entity> | <what it represents> | <key facts> |

## 2. Relationships

| From | To | Cardinality | Implementation | ON DELETE |
|------|----|-------------|----------------|-----------|
| <a> | <b> | 1:N / M:N / 1:1 | FK on b / junction table / shared PK | RESTRICT/CASCADE/SET NULL |

## 3. Keys

| Table | Primary key | Type | Natural key (UNIQUE) |
|-------|-------------|------|----------------------|
| <table> | <pk col> | surrogate identity / UUID / composite | <unique business key> |

## 4. DDL (dependency order: parents first)

```sql
-- lookup / parent tables
CREATE TABLE ... ;

-- junction (M:N) tables
CREATE TABLE ... ;

-- child / transactional tables
CREATE TABLE ... ;

-- indexes (all FKs + query predicates)
CREATE INDEX ... ;
```

## 5. Constraints summary

| Table.column | Constraint | Rule |
|--------------|-----------|------|
| <t.col> | NOT NULL / CHECK / DEFAULT / UNIQUE | <rule> |

## 6. Indexing plan

| Index | Table(cols) | Serves query |
|-------|-------------|--------------|
| <ix_name> | <table>(<cols>) | <WHERE/JOIN/ORDER BY pattern> |

## 7. Denormalization decisions (if any)

| Field | Reason | Source of truth | Sync mechanism | Tolerated staleness |
|-------|--------|-----------------|----------------|--------------------|
| <table.col> | <slow query X> | <canonical source> | <trigger/app/MV/ETL> | <none/seconds/...> |

## 8. Open questions / assumptions

- <assumption or thing to confirm with stakeholders>
