#!/usr/bin/env python3
"""Readability and writing-smell analyzer for technical docs.

Analyzes a Markdown or plain-text file and reports:
  - Flesch Reading Ease and Flesch-Kincaid grade level
  - Average sentence length and long-sentence offenders (> threshold words)
  - Likely passive-voice sentences
  - Weasel / filler words to reconsider

Pure standard library. Heuristic, not perfect — use as a guide, not a gate.

Usage:
    python3 readability.py FILE [--max-sentence-words N] [--show N]

Examples:
    python3 readability.py README.md
    python3 readability.py docs/guide.md --max-sentence-words 22 --show 10

Exit status is 0 always (informational tool).
"""
import argparse
import re
import sys

WEASEL_WORDS = [
    "simply", "just", "easily", "obviously", "clearly", "of course",
    "basically", "actually", "really", "very", "quite", "robust",
    "seamless", "seamlessly", "several", "various", "a number of",
    "needless to say", "in order to", "utilize", "leverage", "facilitate",
]

PASSIVE_RE = re.compile(
    r"\b(am|is|are|was|were|be|been|being|get|got|gets)\b\s+"
    r"(\w+ed|written|done|made|built|set|sent|run|given|taken|seen|known|"
    r"shown|held|kept|found|chosen|drawn|begun)\b",
    re.IGNORECASE,
)


def strip_markdown(text):
    """Remove code blocks, inline code, links markup, headings markers."""
    text = re.sub(r"```.*?```", " ", text, flags=re.DOTALL)
    text = re.sub(r"`[^`]*`", " ", text)
    text = re.sub(r"!?\[([^\]]*)\]\([^)]*\)", r"\1", text)  # links/images
    text = re.sub(r"^\s{0,3}#{1,6}\s*", "", text, flags=re.MULTILINE)  # headings
    text = re.sub(r"^\s*[-*+]\s+", "", text, flags=re.MULTILINE)  # bullets
    text = re.sub(r"[*_>#|]", " ", text)  # leftover markup
    return text


def split_sentences(text):
    text = re.sub(r"\s+", " ", text).strip()
    parts = re.split(r"(?<=[.!?])\s+(?=[A-Z0-9])", text)
    return [s.strip() for s in parts if s.strip()]


def count_syllables(word):
    word = word.lower()
    word = re.sub(r"[^a-z]", "", word)
    if not word:
        return 0
    groups = re.findall(r"[aeiouy]+", word)
    count = len(groups)
    if word.endswith("e") and count > 1:
        count -= 1
    return max(count, 1)


def words_of(sentence):
    return re.findall(r"[A-Za-z']+", sentence)


def analyze(raw, max_sentence_words, show):
    clean = strip_markdown(raw)
    sentences = split_sentences(clean)
    if not sentences:
        print("No prose sentences found (file may be all code/markup).")
        return

    all_words = []
    syllables = 0
    for s in sentences:
        ws = words_of(s)
        all_words.extend(ws)
        syllables += sum(count_syllables(w) for w in ws)

    n_words = len(all_words)
    n_sent = len(sentences)
    if n_words == 0:
        print("No words found.")
        return

    asl = n_words / n_sent           # avg sentence length
    asw = syllables / n_words        # avg syllables per word
    flesch = 206.835 - 1.015 * asl - 84.6 * asw
    fk_grade = 0.39 * asl + 11.8 * asw - 15.59

    print("=" * 60)
    print("READABILITY")
    print("=" * 60)
    print(f"Sentences:                {n_sent}")
    print(f"Words:                    {n_words}")
    print(f"Avg sentence length:      {asl:.1f} words")
    print(f"Flesch Reading Ease:      {flesch:.0f}  "
          f"({reading_ease_label(flesch)})")
    print(f"Flesch-Kincaid grade:     {fk_grade:.1f}")
    print("  (Aim for grade 8-12 for general technical docs.)")

    long_sents = [(len(words_of(s)), s) for s in sentences
                  if len(words_of(s)) > max_sentence_words]
    long_sents.sort(reverse=True)
    print()
    print("-" * 60)
    print(f"LONG SENTENCES (> {max_sentence_words} words): {len(long_sents)}")
    print("-" * 60)
    for wc, s in long_sents[:show]:
        print(f"  [{wc}w] {trim(s)}")

    passive = [s for s in sentences if PASSIVE_RE.search(s)]
    print()
    print("-" * 60)
    print(f"LIKELY PASSIVE VOICE: {len(passive)}")
    print("-" * 60)
    for s in passive[:show]:
        print(f"  {trim(s)}")

    low = clean.lower()
    print()
    print("-" * 60)
    print("WEASEL / FILLER WORDS")
    print("-" * 60)
    found_any = False
    for w in WEASEL_WORDS:
        c = len(re.findall(r"\b" + re.escape(w) + r"\b", low))
        if c:
            found_any = True
            print(f"  {c:>3}x  {w}")
    if not found_any:
        print("  none found - nice.")
    print()


def reading_ease_label(score):
    if score >= 70:
        return "easy"
    if score >= 50:
        return "medium"
    if score >= 30:
        return "difficult"
    return "very difficult"


def trim(s, n=90):
    return s if len(s) <= n else s[: n - 1] + "…"


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("file", help="Path to .md or .txt file")
    p.add_argument("--max-sentence-words", type=int, default=25,
                   help="Flag sentences longer than this (default 25)")
    p.add_argument("--show", type=int, default=8,
                   help="Max examples to show per category (default 8)")
    args = p.parse_args(argv)

    try:
        with open(args.file, "r", encoding="utf-8") as f:
            raw = f.read()
    except OSError as e:
        print(f"error: cannot read {args.file}: {e}", file=sys.stderr)
        return 2

    analyze(raw, args.max_sentence_words, args.show)
    return 0


if __name__ == "__main__":
    sys.exit(main())
