#!/usr/bin/env python3
"""email_lint.py - Heuristic linter for draft emails.

Checks a draft for common problems this skill cares about:
  - missing or weak subject line
  - missing call to action (CTA)
  - missing deadline when a CTA exists
  - excessive length / wall-of-text paragraphs
  - hedging / filler phrases
  - passive-aggressive phrases
  - over-apologizing
  - vague closers ("let me know")

This is heuristic, not a grammar checker. Treat warnings as prompts to review,
not hard rules.

Usage:
    python3 email_lint.py draft.txt
    python3 email_lint.py draft.txt --max-words 150
    cat draft.txt | python3 email_lint.py -

Draft format (optional): a line starting with 'Subject:' is treated as the
subject line. Everything else is the body. If no Subject: line is present,
the whole input is treated as the body and a subject warning is emitted.

Exit code: 0 if no errors (warnings allowed), 1 if any ERROR-level issues found.
"""
import argparse
import re
import sys

WEAK_SUBJECTS = {
    "", "hi", "hello", "hey", "question", "quick question", "update",
    "meeting", "touching base", "following up", "follow up", "fyi",
    "important", "urgent", "re:", "check in", "checking in",
}

HEDGES = [
    r"\bi was wondering if\b", r"\bjust wanted to\b", r"\bjust checking\b",
    r"\bif possible\b.*\bif possible\b", r"\bmaybe\b", r"\bpossibly\b",
    r"\bsort of\b", r"\bkind of\b", r"\bi think maybe\b",
    r"\bhope this (email|message) finds you well\b",
]

PASSIVE_AGGRESSIVE = [
    r"\bper my last email\b", r"\bas (i|previously) (stated|mentioned) (before|again)\b",
    r"\bas already (stated|mentioned)\b", r"\bgentle reminder\b.*\bagain\b",
    r"\bnot sure if you saw\b",
]

VAGUE_CLOSERS = [
    r"\blet me know your thoughts\b", r"\blet me know\b\.?\s*$",
    r"\bthoughts\?\s*$", r"\bcircle back\b",
]

CTA_SIGNALS = [
    r"\bcould you\b", r"\bcan you\b", r"\bplease\b", r"\bwould you\b",
    r"\bcan we\b", r"\blet's\b", r"\bapprove\b", r"\bconfirm\b",
    r"\breview\b", r"\bsend\b", r"\bsign\b", r"\brsvp\b", r"\breply\b",
    r"\bschedule\b", r"\bbook\b",
]

DEADLINE_SIGNALS = [
    r"\bby (mon|tue|wed|thu|fri|sat|sun)", r"\bby (january|february|march|april|may|june|july|august|september|october|november|december)",
    r"\bby <date>", r"\bby (the )?\d{1,2}(st|nd|rd|th)?\b",
    r"\bby (today|tomorrow|eod|end of day|end of week|noon)\b",
    r"\bbefore (mon|tue|wed|thu|fri|sat|sun|noon|\d)", r"\b\d{1,2}:\d{2}\b",
    r"\bby <day", r"\bdeadline\b", r"\bdue\b",
]

APOLOGY = r"\b(sorry|apolog(y|ize|ise)|my apologies)\b"


class Finding:
    def __init__(self, level, msg):
        self.level = level  # 'ERROR' or 'WARN'
        self.msg = msg


def any_match(patterns, text):
    return any(re.search(p, text) for p in patterns)


def count_matches(pattern, text):
    return len(re.findall(pattern, text))


def split_subject_body(raw):
    subject = None
    body_lines = []
    for line in raw.splitlines():
        m = re.match(r"\s*subject\s*:\s*(.*)$", line, re.IGNORECASE)
        if m and subject is None:
            subject = m.group(1).strip()
        else:
            body_lines.append(line)
    return subject, "\n".join(body_lines)


def lint(raw, max_words):
    findings = []
    subject, body = split_subject_body(raw)
    low_body = body.lower()

    # Subject checks
    if subject is None:
        findings.append(Finding("WARN", "No 'Subject:' line found. Add a specific subject line."))
    else:
        norm = subject.strip().lower().rstrip("!?.")
        if norm in WEAK_SUBJECTS or len(norm) < 4:
            findings.append(Finding("ERROR", f"Weak/vague subject line: {subject!r}. Front-load a keyword and add a deadline if relevant."))
        if len(subject) > 60:
            findings.append(Finding("WARN", f"Subject is {len(subject)} chars; may truncate on mobile (aim <= 60)."))

    # Word count
    words = re.findall(r"\b\w+\b", body)
    wc = len(words)
    if wc > max_words:
        findings.append(Finding("WARN", f"Body is {wc} words (target <= {max_words}). Consider trimming or a call/doc."))
    if wc == 0:
        findings.append(Finding("ERROR", "Empty body."))
        return findings, subject, wc

    # Wall of text: any paragraph over 90 words
    for i, para in enumerate(re.split(r"\n\s*\n", body.strip()), 1):
        pwc = len(re.findall(r"\b\w+\b", para))
        if pwc > 90:
            findings.append(Finding("WARN", f"Paragraph {i} is {pwc} words. Break it up with white space or bullets."))

    # CTA presence
    has_cta = any_match(CTA_SIGNALS, low_body)
    if not has_cta:
        findings.append(Finding("ERROR", "No clear call to action detected. State a specific ask (action + owner)."))
    else:
        if not any_match(DEADLINE_SIGNALS, low_body):
            findings.append(Finding("WARN", "CTA found but no deadline/timeframe detected. Add 'by <day, time>'."))

    # Vague closers
    if any_match(VAGUE_CLOSERS, low_body):
        findings.append(Finding("WARN", "Vague closer (e.g., 'let me know'). Replace with a specific ask and deadline."))

    # Hedging
    hedge_hits = [p for p in HEDGES if re.search(p, low_body)]
    if hedge_hits:
        findings.append(Finding("WARN", f"Hedging/filler detected ({len(hedge_hits)} pattern(s)). Trim qualifiers; keep one softener max per ask."))

    # Passive-aggressive
    if any_match(PASSIVE_AGGRESSIVE, low_body):
        findings.append(Finding("WARN", "Possible passive-aggressive phrasing (e.g., 'per my last email'). Rephrase neutrally."))

    # Over-apologizing
    apologies = count_matches(APOLOGY, low_body)
    if apologies >= 3:
        findings.append(Finding("WARN", f"Apologizes {apologies} times. Own it once, then focus on the fix."))

    return findings, subject, wc


def main():
    ap = argparse.ArgumentParser(description="Heuristic linter for draft emails.")
    ap.add_argument("path", help="Path to draft file, or '-' to read stdin.")
    ap.add_argument("--max-words", type=int, default=150, help="Target max body word count (default 150).")
    args = ap.parse_args()

    if args.path == "-":
        raw = sys.stdin.read()
    else:
        try:
            with open(args.path, "r", encoding="utf-8") as fh:
                raw = fh.read()
        except OSError as e:
            print(f"Could not read {args.path}: {e}", file=sys.stderr)
            return 2

    findings, subject, wc = lint(raw, args.max_words)

    errors = [f for f in findings if f.level == "ERROR"]
    warns = [f for f in findings if f.level == "WARN"]

    print(f"Email lint report  (body words: {wc}, subject: {subject!r})")
    print("-" * 60)
    if not findings:
        print("OK - no issues found. Still do a human read-aloud pass.")
    else:
        for f in errors:
            print(f"  ERROR  {f.msg}")
        for f in warns:
            print(f"  WARN   {f.msg}")
    print("-" * 60)
    print(f"{len(errors)} error(s), {len(warns)} warning(s).")

    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
