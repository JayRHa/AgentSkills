#!/usr/bin/env python3
"""Profile a tabular dataset to guide cleaning decisions.

Reports shape, dtypes, per-column null %, unique counts, sample values, and
flags common problems: constant columns, ID-like columns, numeric-looking
object columns, high-cardinality text, and likely disguised-missing tokens.

Usage:
    python profile_data.py data/raw.csv
    python profile_data.py data/raw.xlsx --sheet 0
    python profile_data.py data/raw.parquet --max-cols 50

Requires: pandas (stdlib + pandas only).
"""
import argparse
import sys

DISGUISED = {"", " ", "na", "n/a", "null", "none", "-", "--", "?",
             "unknown", "nan", "missing", "-999", "999"}


def load(path: str, sheet):
    import pandas as pd
    if path.endswith((".xlsx", ".xls")):
        return pd.read_excel(path, sheet_name=sheet if sheet is not None else 0)
    if path.endswith(".parquet"):
        return pd.read_parquet(path)
    if path.endswith((".tsv",)):
        return pd.read_csv(path, sep="\t")
    return pd.read_csv(path)


def looks_numeric(series) -> bool:
    import pandas as pd
    if series.dtype != object:
        return False
    sample = series.dropna().astype(str).str.strip()
    sample = sample.str.replace(r"[$,€£%\s]", "", regex=True)
    if sample.empty:
        return False
    parsed = pd.to_numeric(sample, errors="coerce")
    return parsed.notna().mean() > 0.8


def profile(df) -> None:
    n = len(df)
    print(f"\n=== SHAPE ===\n{n} rows x {df.shape[1]} columns")

    print("\n=== PER-COLUMN SUMMARY ===")
    header = f"{'column':<24}{'dtype':<12}{'null%':>7}{'unique':>9}  sample"
    print(header)
    print("-" * len(header))
    for col in df.columns:
        s = df[col]
        null_pct = s.isna().mean() * 100
        nuniq = s.nunique(dropna=True)
        sample_vals = s.dropna().unique()[:3]
        sample = ", ".join(str(v)[:18] for v in sample_vals)
        print(f"{str(col)[:23]:<24}{str(s.dtype):<12}{null_pct:>6.1f}%{nuniq:>9}  {sample}")

    print("\n=== FLAGGED ISSUES ===")
    issues = []
    for col in df.columns:
        s = df[col]
        nuniq = s.nunique(dropna=False)
        null_pct = s.isna().mean() * 100
        if nuniq <= 1:
            issues.append(f"[constant]   {col!r} has <=1 distinct value -> consider dropping")
        if n and nuniq >= 0.95 * n and s.dtype == object:
            issues.append(f"[id-like]    {col!r} nearly unique -> likely an identifier")
        if null_pct > 50:
            issues.append(f"[mostly-na]  {col!r} is {null_pct:.0f}% missing -> drop or special-case")
        if looks_numeric(s):
            issues.append(f"[numeric-str]{col!r} is object but looks numeric -> to_numeric")
        if s.dtype == object:
            low = s.dropna().astype(str).str.strip().str.lower()
            hits = sorted(set(low) & DISGUISED)
            if hits:
                issues.append(f"[disguised]  {col!r} contains likely missing tokens: {hits}")
            if n and s.nunique(dropna=True) > 0.5 * n and s.nunique(dropna=True) > 50:
                issues.append(f"[high-card]  {col!r} high-cardinality text -> standardize/parse")

    if issues:
        for i in issues:
            print(" - " + i)
    else:
        print(" (no automatic flags)")

    print("\n=== DUPLICATES ===")
    print(f" exact duplicate rows: {int(df.duplicated().sum())}")

    print("\nNext: see references/cleaning-checklist.md for the ordered workflow.")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("path", help="CSV/TSV/Excel/Parquet file to profile")
    ap.add_argument("--sheet", default=None, help="Excel sheet name or index")
    ap.add_argument("--max-cols", type=int, default=200,
                    help="abort profiling if more columns than this")
    args = ap.parse_args(argv)

    try:
        df = load(args.path, args.sheet)
    except Exception as exc:  # noqa: BLE001
        print(f"ERROR loading {args.path}: {exc}", file=sys.stderr)
        return 1

    if df.shape[1] > args.max_cols:
        print(f"ERROR: {df.shape[1]} columns exceeds --max-cols={args.max_cols}",
              file=sys.stderr)
        return 1

    profile(df)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
