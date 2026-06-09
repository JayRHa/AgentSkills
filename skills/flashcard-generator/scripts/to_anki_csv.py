#!/usr/bin/env python3
"""Convert simple flashcard text into an Anki-importable CSV.

Input formats (auto-detected per line):
  Basic:  Question ? | Answer            (pipe-separated)
  Basic:  Q: ...  /  A: ...              (two-line pairs)
  Cloze:  any line containing {{c1::...}} markers

Output: a UTF-8 CSV. Import into Anki with "Fields separated by: Comma".
Cloze rows are tagged so you can map them to the Cloze note type.

Usage:
    python3 to_anki_csv.py cards.txt -o deck.csv
    python3 to_anki_csv.py cards.txt          # writes cards.csv
"""
from __future__ import annotations

import argparse
import csv
import re
import sys
from pathlib import Path

CLOZE = re.compile(r"\{\{c\d+::.+?\}\}")


def parse(text: str):
    rows = []  # (type, field1, field2)
    lines = [ln.rstrip() for ln in text.splitlines()]
    i = 0
    pending_q = None
    for raw in lines:
        line = raw.strip()
        if not line:
            continue
        if CLOZE.search(line):
            rows.append(("cloze", line, ""))
            continue
        if "|" in line:
            q, _, a = line.partition("|")
            rows.append(("basic", q.strip(), a.strip()))
            continue
        m = re.match(r"^Q[:.]\s*(.+)$", line, re.I)
        if m:
            pending_q = m.group(1).strip()
            continue
        m = re.match(r"^A[:.]\s*(.+)$", line, re.I)
        if m and pending_q is not None:
            rows.append(("basic", pending_q, m.group(1).strip()))
            pending_q = None
            continue
    return rows


def main() -> int:
    ap = argparse.ArgumentParser(description="Flashcard text -> Anki CSV.")
    ap.add_argument("input", help="text file of cards")
    ap.add_argument("-o", "--output", help="output CSV path")
    args = ap.parse_args()

    src = Path(args.input)
    if not src.is_file():
        print(f"error: {src} not found", file=sys.stderr)
        return 1
    rows = parse(src.read_text(encoding="utf-8"))
    if not rows:
        print("No cards parsed. Use 'Q: .. / A: ..', 'Question | Answer', or {{c1::cloze}} lines.", file=sys.stderr)
        return 1

    out = Path(args.output) if args.output else src.with_suffix(".csv")
    with out.open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        for typ, f1, f2 in rows:
            if typ == "cloze":
                w.writerow([f1, "", "cloze"])
            else:
                w.writerow([f1, f2, "basic"])
    n_cloze = sum(1 for r in rows if r[0] == "cloze")
    print(f"Wrote {len(rows)} cards ({n_cloze} cloze, {len(rows)-n_cloze} basic) -> {out}")
    print("Import into Anki: File > Import, comma-separated. Column 3 = note type tag.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
