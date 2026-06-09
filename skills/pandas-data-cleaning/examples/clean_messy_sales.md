# Worked Example: Cleaning a Messy Sales Export

A realistic raw→clean walkthrough. The raw file `sales_raw.csv` came from a
spreadsheet export and has every classic problem.

## Raw input (`sales_raw.csv`)

```
Order ID , Customer Name, Order Date, Country ,  Amount , Qty,Status
1001, Acme  , 2023-01-05, USA ,$1,200.00, 3,Shipped
1002, beta llc, 05/02/2023, U.S.A., "$980.50", 2 , shipped
1003, Acme, 2023-01-05, United States, N/A, 1, SHIPPED
1003, Acme, 2023-01-05, United States, N/A, 1, SHIPPED
1004, Gamma, 2023-13-40, usa, $45,000.00 , 1, cancelled
1005, Delta, , unknown, $-5.00, 99999, shipped
```

Problems: messy headers (spaces, casing), whitespace in values, mixed date
formats + an impossible date, currency strings with commas, disguised missing
(`N/A`, `unknown`, empty), country synonyms, inconsistent status casing, an
exact duplicate row (1003), a negative amount (error), and an outlier qty.

## Step 1 — Profile

```bash
python scripts/profile_data.py sales_raw.csv
```
Flags: `[numeric-str] 'amount'`, `[disguised] 'amount'/'country'`, duplicate rows = 1.

## Step 2 — Structure (column names + drop dup)

```python
import pandas as pd, numpy as np
df = pd.read_csv("sales_raw.csv", skipinitialspace=True)
df.columns = (df.columns.str.strip().str.lower()
                .str.replace(r"[^0-9a-z]+", "_", regex=True).str.strip("_"))
# -> order_id, customer_name, order_date, country, amount, qty, status
df = df.drop_duplicates()                      # removes the repeated 1003
```

## Step 3 — Disguised missing → NaN

```python
df = df.replace(["", "N/A", "unknown"], np.nan)
for c in ["customer_name", "country", "status"]:
    df[c] = df[c].str.strip()
```

## Step 4 — Types

```python
df["amount"] = (df["amount"].str.replace(r"[$,]", "", regex=True)
                  .pipe(pd.to_numeric, errors="coerce"))
df["qty"] = pd.to_numeric(df["qty"], errors="coerce").astype("Int64")
df["order_date"] = pd.to_datetime(df["order_date"], errors="coerce")  # 2023-13-40 -> NaT
```

## Step 5 — Standardize categories

```python
country_map = {"usa": "United States", "u.s.a.": "United States",
               "united states": "United States"}
df["country"] = df["country"].str.lower().map(country_map).fillna(df["country"])
df["status"] = df["status"].str.lower().str.capitalize()  # Shipped / Cancelled
```

## Step 6 — Fix errors & outliers

```python
# negative amount is a data error -> treat as missing then drop or impute
df.loc[df["amount"] < 0, "amount"] = np.nan
# qty=99999 is an entry error; cap with IQR fence
q1, q3 = df["qty"].quantile([0.25, 0.75]); iqr = q3 - q1
df["qty"] = df["qty"].clip(upper=int(q3 + 1.5 * iqr))
```

## Step 7 — Impute remaining missing (documented choices)

```python
# amount is right-skewed -> median; flag that it was missing
df["amount_was_missing"] = df["amount"].isna()
df["amount"] = df["amount"].fillna(df["amount"].median())
df["country"] = df["country"].fillna("Unknown")
```

## Step 8 — Validate

```python
assert df["amount"].notna().all()
assert (df["amount"] >= 0).all()
assert df["status"].isin(["Shipped", "Cancelled"]).all()
assert str(df["order_date"].dtype).startswith("datetime")
```

## Cleaned output (conceptual)

| order_id | customer_name | order_date | country | amount | qty | status | amount_was_missing |
|---|---|---|---|---|---|---|---|
| 1001 | Acme | 2023-01-05 | United States | 1200.00 | 3 | Shipped | False |
| 1002 | beta llc | 2023-05-02 | United States | 980.50 | 2 | Shipped | False |
| 1003 | Acme | 2023-01-05 | United States | 1090.25 | 1 | Shipped | True |
| 1004 | Gamma | NaT | United States | 1090.25 | 1 | Cancelled | True |
| 1005 | Delta | NaT | Unknown | 1090.25 | 4 | Shipped | True |

Result: consistent names, parsed dates (bad date → NaT), numeric amount/qty,
standardized country/status, duplicate removed, error fixed, outlier capped,
missing imputed with an audit flag.

## Or run the bundled pipeline

```bash
python scripts/clean_pipeline.py sales_raw.csv -o sales_clean.parquet \
  --dates order_date --dropdup-subset order_id \
  --impute amount:median country:mode --cap-outliers qty
```
