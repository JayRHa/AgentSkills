#!/usr/bin/env python3
"""proof_check.py - Fast first-pass scanner for common mechanical writing issues.

This is a heuristic pre-screen, NOT a grammar checker. It surfaces likely
problems (doubled words, wordy phrases, redundancies, filler, comma splices,
mixed spelling variants, straight/curly quote mixing) so a human or model can
review them. It never rewrites text; it only reports.

Usage:
    python3 proof_check.py FILE [FILE ...]
    python3 proof_check.py -            # read from stdin
    echo "some text" | python3 proof_check.py -
    python3 proof_check.py essay.txt --variant uk

Options:
    --variant {us,uk}   Preferred English variant for spelling-consistency hints.
    --quiet             Only print findings, suppress the per-file header.

Exit code is 0 always (it is a linter-style advisory tool).
"""
import argparse
import re
import sys

# Wordy phrase -> concise suggestion
WORDY = {
    r"\bin order to\b": "to",
    r"\bdue to the fact that\b": "because",
    r"\bin the event that\b": "if",
    r"\bat this point in time\b": "now",
    r"\ba large number of\b": "many",
    r"\bthe majority of\b": "most",
    r"\bhas the ability to\b": "can",
    r"\bis able to\b": "can",
    r"\bmake a decision\b": "decide",
    r"\bin spite of the fact that\b": "although",
    r"\bwith regard to\b": "about",
    r"\bfor the purpose of\b": "to",
    r"\bon a daily basis\b": "daily",
    r"\bin close proximity to\b": "near",
    r"\beach and every\b": "each",
}

# Redundant pairs (pleonasms)
REDUNDANT = [
    r"\bfree gift\b", r"\badded bonus\b", r"\bnew innovation\b",
    r"\bunexpected surprise\b", r"\bexact same\b", r"\bfinal outcome\b",
    r"\brevert back\b", r"\breturn back\b", r"\brepeat again\b",
    r"\bmerge together\b", r"\bcombine together\b", r"\bend result\b",
    r"\bpast history\b", r"\bATM machine\b", r"\bPIN number\b",
    r"\b12 noon\b", r"\b12 midnight\b", r"\babsolutely essential\b",
    r"\bbasic fundamentals\b", r"\bclose proximity\b",
]

# Filler words (advisory only - context decides)
FILLER = [r"\bvery\b", r"\breally\b", r"\bbasically\b", r"\bactually\b",
          r"\bliterally\b", r"\bquite\b", r"\bjust\b", r"\bsimply\b"]

# Commonly confused homophones to eyeball
CONFUSABLES = [r"\bits\b", r"\bit's\b", r"\byour\b", r"\byou're\b",
               r"\btheir\b", r"\bthere\b", r"\bthey're\b",
               r"\bthen\b", r"\bthan\b", r"\baffect\b", r"\beffect\b"]

US_WORDS = ["color", "favor", "honor", "organize", "analyze", "center",
            "theater", "defense", "toward", "gray", "traveling", "canceled"]
UK_WORDS = ["colour", "favour", "honour", "organise", "analyse", "centre",
            "theatre", "defence", "towards", "grey", "travelling", "cancelled"]

COORD = "and|but|or|so|yet|for|nor"


def find_lines(text):
    return text.splitlines()


def scan(text, variant):
    findings = []  # (line_no, category, message)
    lines = find_lines(text)

    for i, line in enumerate(lines, 1):
        low = line.lower()

        # Doubled words: "the the", "is is"
        for m in re.finditer(r"\b(\w+)\s+\1\b", line, flags=re.IGNORECASE):
            findings.append((i, "doubled-word", f"repeated word '{m.group(1)}'"))

        # Multiple spaces
        if re.search(r"\S  +\S", line):
            findings.append((i, "spacing", "multiple consecutive spaces"))

        # Space before punctuation
        if re.search(r"\s[,.;:!?]", line):
            findings.append((i, "spacing", "space before punctuation"))

        # Missing space after sentence punctuation (not decimals/URLs)
        if re.search(r"[a-z]{2}[.!?][A-Z]", line):
            findings.append((i, "spacing", "possible missing space after sentence punctuation"))

        # Wordy phrases
        for pat, sug in WORDY.items():
            if re.search(pat, low):
                phrase = re.search(pat, low).group(0)
                findings.append((i, "wordy", f"'{phrase}' -> '{sug}'"))

        # Redundancies
        for pat in REDUNDANT:
            if re.search(pat, low):
                findings.append((i, "redundant", f"redundant: '{re.search(pat, low).group(0)}'"))

        # Filler
        for pat in FILLER:
            if re.search(pat, low):
                findings.append((i, "filler", f"possible filler: '{re.search(pat, low).group(0).strip()}'"))

        # Comma splice heuristic: ", <pronoun/article> ... " joining two clauses
        # crude: comma followed by a likely independent-clause starter
        if re.search(r",\s+(i|we|you|he|she|they|it|this|that|there)\s+\w+", low) \
                and not re.search(r",\s+(?:" + COORD + r")\b", low):
            findings.append((i, "comma-splice?", "comma may join two independent clauses; check"))

        # Straight vs curly quote mixing within a line
        if ('"' in line and ('“' in line or '”' in line)):
            findings.append((i, "quotes", "mixed straight and curly double quotes"))

    # Spelling-variant consistency across whole doc
    full_low = text.lower()
    us_hits = [w for w in US_WORDS if re.search(r"\b" + w + r"\b", full_low)]
    uk_hits = [w for w in UK_WORDS if re.search(r"\b" + w + r"\b", full_low)]
    if us_hits and uk_hits:
        findings.append((0, "variant-mix",
                         f"mixed US ({', '.join(us_hits)}) and UK ({', '.join(uk_hits)}) spellings"))
    elif variant == "uk" and us_hits:
        findings.append((0, "variant", f"US spellings in UK doc: {', '.join(us_hits)}"))
    elif variant == "us" and uk_hits:
        findings.append((0, "variant", f"UK spellings in US doc: {', '.join(uk_hits)}"))

    return findings


def read_source(path):
    if path == "-":
        return sys.stdin.read()
    with open(path, "r", encoding="utf-8") as fh:
        return fh.read()


def main(argv=None):
    p = argparse.ArgumentParser(description="Heuristic first-pass proofreading scanner.")
    p.add_argument("files", nargs="+", help="file paths, or - for stdin")
    p.add_argument("--variant", choices=["us", "uk"], default="us",
                   help="preferred English variant (default: us)")
    p.add_argument("--quiet", action="store_true", help="suppress per-file headers")
    args = p.parse_args(argv)

    total = 0
    for path in args.files:
        try:
            text = read_source(path)
        except OSError as e:
            print(f"error: cannot read {path}: {e}", file=sys.stderr)
            continue

        findings = scan(text, args.variant)
        total += len(findings)

        if not args.quiet:
            label = "<stdin>" if path == "-" else path
            print(f"=== {label}: {len(findings)} finding(s) ===")

        for line_no, cat, msg in sorted(findings, key=lambda x: (x[0], x[1])):
            loc = f"line {line_no}" if line_no else "document"
            print(f"  [{cat}] {loc}: {msg}")

        if not findings and not args.quiet:
            print("  no obvious mechanical issues found (review manually anyway)")

    if not args.quiet:
        print(f"\nTotal findings: {total}  (advisory - human/model review required)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
