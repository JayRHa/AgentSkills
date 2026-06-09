#!/usr/bin/env python3
"""Configurable end-to-end pandas cleaning pipeline.

Applies, in order: column-name normalization, disguised-missing -> NaN,
numeric/date coercion (auto-detected or specified), duplicate removal,
per-column missing-value imputation, and optional IQR outlier capping.
Prints a before/after summary so every change is auditable. Writes the
cleaned data to an output file (csv/parquet).

Usage:
    python clean_pipeline.py raw.csv -o clean.parquet
    python clean_pipeline.py raw.csv -o clean.csv \
        --dates order_date,dob --dropdup-subset id \
        --impute price:median qty:median country:mode \
        --cap-outliers amount

Strategies for --impute COL:STRATEGY  ->  median | mean | mode | zero | drop
Requires: pandas, numpy.
"""
import argparse
import sys

DISGUISED = ["", " ", "NA", "N/A", "na", "n/a", "null", "NULL", "none",
             "None", "-", "--", "?", "unknown", "Unknown", "missing"]


def normalize_columns(df):
    df = df.copy()
    df.columns = (
        df.columns.astype(str).str.strip().str.lower()
        .str.replace(r"[^0-9a-z]+", "_", regex=True).str.strip("_")
    )
    return df


def to_na(df):
    import numpy as np
    return df.replace(DISGUISED, np.nan)


def coerce_numeric_auto(df, skip):
    import pandas as pd
    df = df.copy()
    for col in df.columns:
        if col in skip or df[col].dtype != object:
            continue
        cleaned = (df[col].astype("string").str.strip()
                   .str.replace(r"[$,€£%\s]", "", regex=True))
        parsed = pd.to_numeric(cleaned, errors="coerce")
        nonnull = df[col].notna()
        if nonnull.sum() and parsed[nonnull].notna().mean() > 0.9:
            df[col] = parsed
    return df


def coerce_dates(df, cols):
    import pandas as pd
    df = df.copy()
    for col in cols:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")
    return df


def impute(df, specs):
    df = df.copy()
    for col, strat in specs.items():
        if col not in df.columns:
            print(f"  warn: impute target {col!r} not found", file=sys.stderr)
            continue
        if strat == "drop":
            df = df[df[col].notna()]
        elif strat == "median":
            df[col] = df[col].fillna(df[col].median())
        elif strat == "mean":
            df[col] = df[col].fillna(df[col].mean())
        elif strat == "mode":
            m = df[col].mode(dropna=True)
            if len(m):
                df[col] = df[col].fillna(m.iloc[0])
        elif strat == "zero":
            df[col] = df[col].fillna(0)
        else:
            raise SystemExit(f"unknown impute strategy: {strat}")
    return df


def cap_outliers(df, cols, k=1.5):
    df = df.copy()
    for col in cols:
        if col not in df.columns:
            continue
        q1, q3 = df[col].quantile(0.25), df[col].quantile(0.75)
        iqr = q3 - q1
        lo, hi = q1 - k * iqr, q3 + k * iqr
        before = ((df[col] < lo) | (df[col] > hi)).sum()
        df[col] = df[col].clip(lo, hi)
        print(f"  capped {int(before)} outliers in {col!r} to [{lo:.3g}, {hi:.3g}]")
    return df


def parse_kv(items):
    out = {}
    for it in items or []:
        if ":" not in it:
            raise SystemExit(f"expected COL:STRATEGY, got {it!r}")
        k, v = it.split(":", 1)
        out[k] = v
    return out


def snapshot(df):
    return {"rows": len(df), "cols": df.shape[1],
            "nulls": int(df.isna().sum().sum())}


def main(argv=None) -> int:
    import pandas as pd
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("input", help="raw csv/tsv/excel/parquet")
    ap.add_argument("-o", "--output", required=True, help="clean output (.csv/.parquet)")
    ap.add_argument("--dates", default="", help="comma-separated date columns")
    ap.add_argument("--no-auto-numeric", action="store_true",
                    help="skip auto numeric coercion of object columns")
    ap.add_argument("--dropdup-subset", default="",
                    help="comma-separated key columns for de-dup (default: full row)")
    ap.add_argument("--dropdup-keep", default="first", choices=["first", "last"])
    ap.add_argument("--impute", nargs="*", help="COL:STRATEGY pairs")
    ap.add_argument("--cap-outliers", default="", help="comma-separated numeric cols")
    args = ap.parse_args(argv)

    if args.input.endswith((".xlsx", ".xls")):
        df = pd.read_excel(args.input)
    elif args.input.endswith(".parquet"):
        df = pd.read_parquet(args.input)
    elif args.input.endswith(".tsv"):
        df = pd.read_csv(args.input, sep="\t")
    else:
        df = pd.read_csv(args.input)

    before = snapshot(df)
    dates = [c for c in args.dates.split(",") if c]

    df = normalize_columns(df)
    df = to_na(df)
    if not args.no_auto_numeric:
        df = coerce_numeric_auto(df, skip=set(dates))
    df = coerce_dates(df, dates)

    subset = [c for c in args.dropdup_subset.split(",") if c] or None
    dup_before = int(df.duplicated(subset=subset).sum())
    df = df.drop_duplicates(subset=subset, keep=args.dropdup_keep)
    print(f"  removed {dup_before} duplicate rows")

    df = impute(df, parse_kv(args.impute))
    df = cap_outliers(df, [c for c in args.cap_outliers.split(",") if c])

    after = snapshot(df)
    print("\n=== SUMMARY ===")
    print(f"  rows:  {before['rows']} -> {after['rows']}")
    print(f"  cols:  {before['cols']} -> {after['cols']}")
    print(f"  nulls: {before['nulls']} -> {after['nulls']}")

    if args.output.endswith(".parquet"):
        df.to_parquet(args.output, index=False)
    else:
        df.to_csv(args.output, index=False)
    print(f"\n  wrote {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
