# Outliers & Tidy Reshaping Reference

## Part A — Outlier Detection & Treatment

### IQR method (robust, default for skewed data)

```python
def iqr_bounds(s: pd.Series, k: float = 1.5):
    q1, q3 = s.quantile(0.25), s.quantile(0.75)
    iqr = q3 - q1
    return q1 - k * iqr, q3 + k * iqr

lo, hi = iqr_bounds(df["amount"])
outliers = df[(df["amount"] < lo) | (df["amount"] > hi)]
```

### Z-score method (for roughly normal data)

```python
z = (df["amount"] - df["amount"].mean()) / df["amount"].std()
outliers = df[z.abs() > 3]
```
Note: mean/std are themselves pulled by outliers; on skewed data prefer IQR or a modified z-score using the median and MAD.

### Treatment options

| Treatment | When | How |
|---|---|---|
| Keep | Legitimate, meaningful extreme | do nothing; note it |
| Cap / winsorize | Real but distorts model | `df["amount"].clip(lo, hi)` |
| Transform | Right-skewed positive data | `np.log1p(df["amount"])` |
| Remove | Confirmed data error | `df = df[df["amount"].between(lo, hi)]` |
| Fix | Known unit/typo error | recompute / correct value |

Winsorize at percentiles:
```python
lo_p, hi_p = df["amount"].quantile([0.01, 0.99])
df["amount"] = df["amount"].clip(lo_p, hi_p)
```

**Always investigate the cause before removing.** Outliers are often the signal, not the noise (fraud, failures, top customers).

## Part B — Tidy Data & Reshaping

### The three rules of tidy data
1. Each variable is a column.
2. Each observation is a row.
3. Each type of observational unit is a table.

### Wide → long with `melt`

Columns that are really values of one variable (e.g., `jan`, `feb`, `mar`):
```python
long = df.melt(
    id_vars=["store", "product"],
    value_vars=["jan", "feb", "mar"],
    var_name="month",
    value_name="sales",
)
```

### Long → wide with `pivot` / `pivot_table`

```python
wide = long.pivot(index="store", columns="month", values="sales")
# When index/column pairs repeat, aggregate explicitly:
wide = long.pivot_table(index="store", columns="month",
                        values="sales", aggfunc="sum", fill_value=0)
```
`pivot` raises on duplicate index/column pairs; `pivot_table` resolves them via `aggfunc`.

### Split packed columns

```python
# "red;blue;green" in one cell -> separate columns
df[["c1", "c2", "c3"]] = df["colors"].str.split(";", expand=True)

# Or one row per value (long form):
df = df.assign(color=df["colors"].str.split(";")).explode("color")

# Split a combined "city, state":
df[["city", "state"]] = df["location"].str.split(",", n=1, expand=True)
df["state"] = df["state"].str.strip()
```

### Stack / unstack (MultiIndex)

```python
df.stack()     # columns -> innermost index level (wide->long)
df.unstack()   # index level -> columns (long->wide)
```

### Reshape checklist
- [ ] After reshape, re-confirm the three tidy rules.
- [ ] Check no values were dropped (`pivot` silently drops on collisions if misused).
- [ ] Reset index if downstream code expects flat columns: `wide.reset_index()`.
