# Data Cleaning Checklist & Validation

A step-by-step checklist to run against any new tabular dataset. Tick each item; record decisions in `templates/cleaning_report.md`.

## 0. Setup

```python
import pandas as pd
import numpy as np

pd.set_option("display.max_columns", None)
raw = pd.read_csv("data/raw.csv")   # keep raw immutable
df = raw.copy()
```

## 1. Profile (before)

- [ ] `df.shape` — rows/cols as expected?
- [ ] `df.head(10)` and `df.sample(10)` — eyeball reality.
- [ ] `df.info()` — dtypes and non-null counts.
- [ ] `df.isna().mean().sort_values(ascending=False)` — null fraction per column.
- [ ] `df.nunique()` — constant columns (1) and ID-like columns (≈ nrows).
- [ ] `df.describe(include="all")` — ranges, top categories, suspicious min/max.
- [ ] For each object column: `df[col].value_counts(dropna=False).head(20)` — disguised missing, casing, synonyms.
- [ ] Memory: `df.memory_usage(deep=True)` — candidates for `category`.

## 2. Structure

- [ ] Normalize column names:
  ```python
  df.columns = (df.columns.str.strip().str.lower()
                  .str.replace(r"[^0-9a-z]+", "_", regex=True)
                  .str.strip("_"))
  ```
- [ ] Drop all-NaN rows/cols: `df = df.dropna(axis=0, how="all").dropna(axis=1, how="all")`.
- [ ] Drop constant columns: `df = df.loc[:, df.nunique(dropna=False) > 1]`.
- [ ] Confirm tidy: one observation/row, one variable/column, one value/cell.

## 3. Dtypes

- [ ] Numeric-looking objects → numbers (strip `$ , %` first).
- [ ] Dates → datetime with explicit `format=`.
- [ ] Booleans from `yes/no`, `Y/N`, `0/1` strings.
- [ ] Low-cardinality strings → `category`.
- [ ] Integers with NaN → nullable `Int64`.
See `dtype-conversion.md`.

## 4. Text & categories

- [ ] `.str.strip()`, normalize case (`.str.lower()` / `.str.title()`).
- [ ] Collapse synonyms via a mapping dict + `.replace()`.
- [ ] Fix obvious typos / encoding mojibake.
- [ ] Map to controlled vocabulary; log unmapped values.

## 5. Missing values

- [ ] Convert disguised missing to NA:
  ```python
  DISGUISED = ["", " ", "NA", "N/A", "na", "null", "none", "-", "--", "?", "unknown", -999]
  df = df.replace(DISGUISED, np.nan)
  ```
- [ ] Decide per-column strategy (see SKILL.md framework).
- [ ] Add `*_was_missing` flags where missingness is informative.

## 6. Duplicates

- [ ] Exact: `df.duplicated().sum()`.
- [ ] Key-based: `df.duplicated(subset=KEY).sum()`.
- [ ] Resolve: `df = df.drop_duplicates(subset=KEY, keep="last")` or aggregate.

## 7. Outliers

- [ ] IQR or z-score flag (see `outliers-and-reshaping.md`).
- [ ] Investigate cause before treating.
- [ ] Cap / transform / remove / keep — document each.

## 8. Reshape

- [ ] `melt` wide→long, `pivot_table` long→wide.
- [ ] Split packed columns with `.str.split(expand=True)` / `.explode()`.

## 9. Validate (after) — assert invariants

```python
assert df.shape[0] > 0, "empty result"
assert df["id"].is_unique, "duplicate ids remain"
assert df["price"].notna().all(), "unexpected null prices"
assert df["price"].between(0, 1e6).all(), "price out of domain"
assert df["category"].isin(ALLOWED).all(), "unknown category"
assert str(df["order_date"].dtype).startswith("datetime"), "date not parsed"
```

Guidelines:
- Validate **counts** (row bounds), **keys** (uniqueness), **nullability** (required cols), **types**, and **domains** (ranges/allowed sets).
- Prefer hard `assert`/raise in pipelines so bad data never flows downstream.
- Re-run the profile from step 1 and diff against the before snapshot.

## 10. Persist

- [ ] Write cleaned data to a new path: `df.to_parquet("data/clean.parquet")`.
- [ ] Save the recipe as one rerunnable function / cell.
- [ ] Fill in `templates/cleaning_report.md`.
