# Data Cleaning Report

> Fill this in alongside your cleaning script so every decision is auditable.
> One report per dataset version.

## Metadata
- **Dataset:** <name>
- **Raw source path:** <path / URL>
- **Clean output path:** <path>
- **Author:** <name>
- **Date:** <YYYY-MM-DD>
- **pandas version:** <x.y.z>

## Before → After Snapshot
| Metric | Before | After |
|---|---|---|
| Rows | | |
| Columns | | |
| Total nulls | | |
| Duplicate rows | | 0 |
| Memory (MB) | | |

## Structural changes
- Column renames applied: <yes/no — note convention>
- Columns dropped (and why): <e.g. `notes` 78% null; `region_code` constant>
- Rows dropped (and why): <e.g. 3 rows missing primary key>

## Dtype conversions
| Column | From | To | Notes |
|---|---|---|---|
| | object | float64 | stripped `$`, `,` |
| | object | datetime64 | format `%Y-%m-%d` |
| | object | category | low cardinality |
| | float64 | Int64 | nullable integer |

## Disguised-missing tokens normalized
- Tokens treated as missing: <e.g. "NA", "unknown", -999, "">

## Missing-value handling (per column)
| Column | % missing | Strategy | Rationale | Added flag? |
|---|---|---|---|---|
| | | median | skewed numeric | yes |
| | | mode | categorical | no |
| | | drop rows | required key | n/a |

## Text / category standardization
- Synonym mappings applied: <e.g. country: USA/U.S.A. → United States>
- Case/whitespace normalization: <describe>
- Unmapped values logged: <yes/no — where>

## Duplicate handling
- Key columns: <e.g. order_id>
- Keep policy: <first / last / aggregate>
- Duplicates removed: <count>

## Outlier handling
| Column | Method | Threshold | Action | Count affected |
|---|---|---|---|---|
| | IQR | k=1.5 | winsorize | |
| | z-score | >3 | remove (errors) | |

## Reshaping
- Operation: <melt / pivot / split / none>
- Description: <wide months → long month/sales>

## Validation assertions (must all pass)
- [ ] Row count within expected range
- [ ] Key column(s) unique
- [ ] No nulls in required columns: <list>
- [ ] Dtypes correct
- [ ] Value domains respected: <ranges / allowed sets>

## Open questions / known limitations
- <e.g. 5% of dates unparseable → set NaT; investigate upstream export>
