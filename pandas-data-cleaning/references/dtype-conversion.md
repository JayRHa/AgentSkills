# Dtype Conversion Reference

Getting dtypes right is the highest-leverage cleaning step: it unlocks correct math, sorting, grouping, and memory savings, and surfaces hidden bad values.

## Numeric from messy strings

Strip currency/grouping/percent symbols, then coerce.

```python
def to_number(s: pd.Series) -> pd.Series:
    cleaned = (s.astype("string")
                .str.strip()
                .str.replace(r"[$,€£\s]", "", regex=True))
    is_pct = cleaned.str.endswith("%", na=False)
    cleaned = cleaned.str.rstrip("%")
    out = pd.to_numeric(cleaned, errors="coerce")   # unparseable -> NaN
    out = out.where(~is_pct, out / 100)
    return out
```

Always inspect new NaNs after coercion — they pinpoint values that failed to parse:
```python
bad = df.loc[to_number(df["price"]).isna() & df["price"].notna(), "price"]
```

## Dates

Use an **explicit format** whenever you know it; ambiguous formats silently misparse.

```python
df["order_date"] = pd.to_datetime(df["order_date"], format="%Y-%m-%d", errors="coerce")
# Day-first European dates:
df["dob"] = pd.to_datetime(df["dob"], dayfirst=True, errors="coerce")
# Unix epoch seconds:
df["ts"] = pd.to_datetime(df["ts"], unit="s")
```
Extract parts: `df["order_date"].dt.year`, `.dt.month`, `.dt.dayofweek`, `.dt.normalize()`.

## Booleans

```python
BOOL_MAP = {"yes": True, "y": True, "true": True, "1": True, 1: True,
            "no": False, "n": False, "false": False, "0": False, 0: False}
df["active"] = (df["active"].astype("string").str.strip().str.lower()
                   .map(BOOL_MAP).astype("boolean"))   # nullable boolean
```

## Categoricals

Convert low-cardinality strings to `category` for memory + speed. Use ordered categories where order matters.

```python
df["size"] = pd.Categorical(df["size"], categories=["S", "M", "L", "XL"], ordered=True)
df["country"] = df["country"].astype("category")
```
Rule of thumb: convert when `nunique / len < ~0.5`.

## Nullable dtypes (pandas >= 1.0)

The classic gotcha: an integer column with one NaN becomes `float64` (`1.0`, `2.0`). Use nullable dtypes to keep integer/boolean/string semantics alongside missing values.

```python
df["qty"]   = df["qty"].astype("Int64")      # capital I — nullable integer
df["flag"]  = df["flag"].astype("boolean")   # nullable boolean
df["name"]  = df["name"].astype("string")    # dedicated string dtype
```

| Want | Old dtype | Nullable dtype |
|---|---|---|
| Integer + NaN | float64 | `Int64` |
| Boolean + NaN | object | `boolean` |
| Text | object | `string` |

## Downcasting for memory

```python
df[ints]   = df[ints].apply(pd.to_numeric, downcast="integer")
df[floats] = df[floats].apply(pd.to_numeric, downcast="float")
```

## Quick conversion order

1. Normalize disguised missing to NaN.
2. Strip symbols / whitespace from strings.
3. `to_numeric` / `to_datetime` with `errors="coerce"`.
4. Inspect new NaNs (parse failures).
5. Cast to `category` / nullable `Int64` / `boolean` / `string`.
6. Downcast numerics for memory.
