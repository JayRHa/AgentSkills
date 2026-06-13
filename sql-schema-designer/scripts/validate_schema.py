#!/usr/bin/env python3
"""Lint a SQL schema (CREATE TABLE DDL) for common design omissions.

This is a heuristic, regex-based checker -- it does NOT fully parse SQL. It flags
likely problems so a human can review them. Intended for PostgreSQL/MySQL/SQLite/
SQL Server style DDL.

Checks per table:
  * missing PRIMARY KEY
  * foreign key columns that have no matching CREATE INDEX (slow joins/cascades)
  * money-ish columns (price/amount/cost/total/balance) declared FLOAT/REAL/DOUBLE
  * timestamp columns without time-zone awareness (best-effort)

Usage:
  python3 validate_schema.py schema.sql
  cat schema.sql | python3 validate_schema.py -
  python3 validate_schema.py schema.sql --strict   # exit 1 if any findings

Exit codes: 0 = no findings (or non-strict), 1 = findings with --strict, 2 = usage error.
"""
import argparse
import re
import sys

MONEY_RE = re.compile(r"\b(price|amount|cost|total|balance|salary|fee|payment)\w*\b", re.I)
FLOAT_RE = re.compile(r"\b(float|real|double)\b", re.I)
INDEXED_RE = re.compile(r"create\s+(?:unique\s+)?index[^;]*?on\s+\"?([\w.]+)\"?\s*\(([^)]*)\)", re.I)
TABLE_RE = re.compile(r"create\s+table\s+(?:if\s+not\s+exists\s+)?\"?([\w.]+)\"?\s*\((.*?)\);",
                      re.I | re.S)
FK_INLINE_RE = re.compile(r"\"?(\w+)\"?[^,]*\breferences\b", re.I)
FK_OUT_RE = re.compile(r"foreign\s+key\s*\(([^)]*)\)", re.I)


def strip_comments(sql: str) -> str:
    sql = re.sub(r"--[^\n]*", "", sql)
    sql = re.sub(r"/\*.*?\*/", "", sql, flags=re.S)
    return sql


def split_columns(body: str):
    """Split a CREATE TABLE body on top-level commas (ignoring parens)."""
    parts, depth, cur = [], 0, []
    for ch in body:
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
        if ch == "," and depth == 0:
            parts.append("".join(cur))
            cur = []
        else:
            cur.append(ch)
    if cur:
        parts.append("".join(cur))
    return [p.strip() for p in parts if p.strip()]


def indexed_columns(sql: str):
    idx = {}
    for m in INDEXED_RE.finditer(sql):
        table = m.group(1).split(".")[-1].lower()
        cols = [c.strip().strip('"').split()[0].lower() for c in m.group(2).split(",") if c.strip()]
        if cols:
            idx.setdefault(table, set()).add(cols[0])  # leading column of the index
    return idx


def analyze(sql: str):
    findings = []
    clean = strip_comments(sql)
    idx = indexed_columns(clean)

    for tmatch in TABLE_RE.finditer(clean):
        raw_name = tmatch.group(1)
        table = raw_name.split(".")[-1].lower()
        body = tmatch.group(2)
        cols = split_columns(body)

        if not re.search(r"primary\s+key", body, re.I):
            findings.append((table, "ERROR", "no PRIMARY KEY defined"))

        fk_cols = set()
        for c in cols:
            low = c.lower()
            if low.startswith(("primary key", "unique", "check", "constraint", "foreign key")):
                fkm = FK_OUT_RE.search(c)
                if fkm:
                    for fc in fkm.group(1).split(","):
                        fk_cols.add(fc.strip().strip('"').lower())
                continue
            if re.search(r"\breferences\b", low):
                m = FK_INLINE_RE.match(c.strip())
                if m:
                    fk_cols.add(m.group(1).lower())
            # money as float
            colname = c.split()[0].strip('"') if c.split() else ""
            if MONEY_RE.search(colname) and FLOAT_RE.search(low):
                findings.append((table, "WARN",
                                 f"money-like column '{colname}' uses FLOAT/REAL/DOUBLE — use NUMERIC/DECIMAL"))
            # naive timestamp
            if re.search(r"\b(timestamp|datetime)\b", low) and not re.search(
                    r"with time zone|timestamptz|datetimeoffset|tz", low):
                findings.append((table, "INFO",
                                 f"column '{colname}' is a timestamp without explicit time zone"))

        for fk in fk_cols:
            if fk not in idx.get(table, set()):
                findings.append((table, "WARN",
                                 f"foreign key column '{fk}' has no leading index — add CREATE INDEX"))
    return findings


def main():
    ap = argparse.ArgumentParser(description="Lint SQL CREATE TABLE DDL for design omissions.")
    ap.add_argument("file", help="path to .sql file, or '-' for stdin")
    ap.add_argument("--strict", action="store_true", help="exit 1 if any findings")
    args = ap.parse_args()

    try:
        sql = sys.stdin.read() if args.file == "-" else open(args.file, encoding="utf-8").read()
    except OSError as e:
        print(f"error: cannot read {args.file}: {e}", file=sys.stderr)
        return 2

    findings = analyze(sql)
    if not findings:
        print("OK: no schema design issues detected.")
        return 0

    rank = {"ERROR": 0, "WARN": 1, "INFO": 2}
    for table, level, msg in sorted(findings, key=lambda f: (rank[f[1]], f[0])):
        print(f"[{level}] {table}: {msg}")
    print(f"\n{len(findings)} finding(s).")
    return 1 if args.strict else 0


if __name__ == "__main__":
    sys.exit(main())
