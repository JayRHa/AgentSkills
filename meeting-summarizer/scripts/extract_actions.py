#!/usr/bin/env python3
"""
extract_actions.py — heuristic first-pass extractor for meeting notes.

Scans a plain-text meeting transcript or notes file and surfaces lines that
look like ACTION ITEMS, DECISIONS, or OPEN QUESTIONS using cue-word matching.
It also attempts to guess an owner from a leading "Name:" speaker label.

This is a DRAFT AID to speed up writing a polished summary -- it is not a
replacement for reading the full input. Lines it flags should be verified.

Usage:
    python3 extract_actions.py MEETING.txt
    python3 extract_actions.py MEETING.txt --json
    cat notes.txt | python3 extract_actions.py -

Exit codes:
    0  success
    1  file not found / unreadable

Stdlib only. No third-party dependencies.
"""
import argparse
import json
import re
import sys

ACTION_CUES = [
    r"\bi'?ll\b", r"\bwe'?ll\b", r"\bcan you\b", r"\bcould you\b",
    r"\bplease\b", r"\bfollow up\b", r"\bnext step\b", r"\baction item\b",
    r"\btake care of\b", r"\bhandle\b", r"\bsend\b", r"\bprepare\b",
    r"\bowns?\b", r"\bassign\b", r"\bto-?do\b", r"\bby (eod|tomorrow|monday|tuesday|wednesday|thursday|friday|next)\b",
]
DECISION_CUES = [
    r"\bdecided?\b", r"\bdecision\b", r"\bagreed?\b", r"\bapproved?\b",
    r"\bwe'?ll go with\b", r"\blet'?s do\b", r"\bfinal\b", r"\bsign(ed)? off\b",
    r"\bchosen\b", r"\brejected?\b", r"\bgo with\b",
]
QUESTION_CUES = [
    r"\bopen question\b", r"\bblocked?\b", r"\bblocker\b", r"\bunresolved\b",
    r"\bnot sure\b", r"\bwe should look into\b", r"\btbd\b", r"\bparking lot\b",
    r"\brisk\b", r"\bdepends on\b",
]

SPEAKER_RE = re.compile(r"^\s*(?:\[[^\]]+\]\s*)?([A-Z][\w.'-]+)\s*:\s*(.*)$")
DATE_RE = re.compile(
    r"\b(eod|tomorrow|today|next week|next sprint|"
    r"mon(day)?|tue(s|sday)?|wed(nesday)?|thu(rs|rsday)?|fri(day)?|sat(urday)?|sun(day)?|"
    r"\d{4}-\d{2}-\d{2}|\d{1,2}/\d{1,2})\b",
    re.IGNORECASE,
)


def compile_cues(cues):
    return [re.compile(c, re.IGNORECASE) for c in cues]


ACTION_RE = compile_cues(ACTION_CUES)
DECISION_RE = compile_cues(DECISION_CUES)
QUESTION_RE = compile_cues(QUESTION_CUES)


def any_match(patterns, text):
    return any(p.search(text) for p in patterns)


def classify(text):
    """Return a category for the line, or None to skip.
    Decision takes precedence over action; action over question."""
    if any_match(DECISION_RE, text):
        return "decision"
    if any_match(ACTION_RE, text):
        return "action"
    if any_match(QUESTION_RE, text):
        return "question"
    return None


def parse_line(raw):
    """Split a line into (speaker, body). Speaker may be None."""
    m = SPEAKER_RE.match(raw)
    if m:
        return m.group(1), m.group(2).strip()
    return None, raw.strip()


def guess_due(text):
    m = DATE_RE.search(text)
    return m.group(0) if m else None


def extract(lines):
    results = {"decision": [], "action": [], "question": []}
    for raw in lines:
        if not raw.strip():
            continue
        speaker, body = parse_line(raw)
        if not body:
            continue
        cat = classify(body)
        if cat is None:
            continue
        item = {"text": body}
        if cat == "action":
            # "I'll/we'll" implies the speaker is the owner
            owner = speaker if re.search(r"\b(i'?ll|i will|i'?m going to)\b", body, re.IGNORECASE) else None
            item["owner"] = owner or "UNASSIGNED"
            item["due"] = guess_due(body) or "-"
        elif speaker:
            item["said_by"] = speaker
        results[cat].append(item)
    return results


def print_human(results):
    def section(title, items):
        print(f"\n=== {title} ({len(items)}) ===")
        if not items:
            print("  (none detected)")
            return
        for it in items:
            if "owner" in it:
                print(f"  - [{it['owner']} | due: {it['due']}] {it['text']}")
            elif "said_by" in it:
                print(f"  - ({it['said_by']}) {it['text']}")
            else:
                print(f"  - {it['text']}")

    section("DECISIONS", results["decision"])
    section("ACTION ITEMS", results["action"])
    section("OPEN QUESTIONS / RISKS", results["question"])
    print("\nNote: heuristic output -- verify against the full transcript before finalizing.")


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Heuristic first-pass extractor for meeting notes."
    )
    parser.add_argument("file", help="Path to notes/transcript file, or '-' for stdin.")
    parser.add_argument("--json", action="store_true", help="Emit JSON instead of text.")
    args = parser.parse_args(argv)

    try:
        if args.file == "-":
            lines = sys.stdin.read().splitlines()
        else:
            with open(args.file, "r", encoding="utf-8") as fh:
                lines = fh.read().splitlines()
    except (OSError, UnicodeDecodeError) as exc:
        print(f"error: could not read {args.file!r}: {exc}", file=sys.stderr)
        return 1

    results = extract(lines)
    if args.json:
        print(json.dumps(results, indent=2, ensure_ascii=False))
    else:
        print_human(results)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
