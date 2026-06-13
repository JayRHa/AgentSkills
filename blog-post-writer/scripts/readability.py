#!/usr/bin/env python3
"""Readability and filler metrics for a blog post draft.

Gives objective, fast signals during the editing pass: reading ease,
grade level, sentence-length distribution, passive-voice and filler-word
counts, and an estimated read time. Pure standard library.

Usage:
    python3 readability.py draft.md
    python3 readability.py draft.md --top 15
    cat draft.md | python3 readability.py -

Markdown fences, headings, and link syntax are stripped before analysis
so code blocks don't skew the prose metrics.
"""
import argparse
import re
import sys
from collections import Counter

FILLER = [
    "very", "really", "just", "basically", "actually", "simply",
    "literally", "quite", "rather", "somewhat", "in order to",
    "the fact that", "needless to say", "at the end of the day",
    "it is important to note", "in today's", "ever-evolving",
]
PASSIVE_RE = re.compile(
    r"\b(am|is|are|was|were|be|been|being)\b\s+\w+(ed|en)\b", re.IGNORECASE
)
VOWEL_GROUPS = re.compile(r"[aeiouy]+", re.IGNORECASE)


def strip_markdown(text):
    text = re.sub(r"```.*?```", " ", text, flags=re.DOTALL)  # fenced code
    text = re.sub(r"`[^`]*`", " ", text)                      # inline code
    text = re.sub(r"^\s{0,3}#{1,6}\s.*$", " ", text, flags=re.MULTILINE)  # headings
    text = re.sub(r"!?\[([^\]]*)\]\([^)]*\)", r"\1", text)    # links/images
    text = re.sub(r"[*_>#|`-]", " ", text)                     # stray md chars
    return text


def count_syllables(word):
    word = word.lower().strip(".,;:!?\"'()")
    if not word:
        return 0
    groups = VOWEL_GROUPS.findall(word)
    syl = len(groups)
    if word.endswith("e") and syl > 1:
        syl -= 1
    return max(syl, 1)


def split_sentences(text):
    parts = re.split(r"(?<=[.!?])\s+", text.strip())
    return [p for p in parts if p.strip()]


def analyze(text):
    prose = strip_markdown(text)
    sentences = split_sentences(prose)
    words = re.findall(r"[A-Za-z']+", prose)
    n_words = len(words)
    n_sent = max(len(sentences), 1)
    syllables = sum(count_syllables(w) for w in words)

    asl = n_words / n_sent                      # avg sentence length
    asw = syllables / max(n_words, 1)           # avg syllables/word
    flesch = 206.835 - 1.015 * asl - 84.6 * asw
    grade = 0.39 * asl + 11.8 * asw - 15.59

    lengths = [len(re.findall(r"[A-Za-z']+", s)) for s in sentences]
    long_sentences = [s for s, ln in zip(sentences, lengths) if ln > 30]

    lower = prose.lower()
    filler_hits = Counter()
    for f in FILLER:
        c = len(re.findall(r"\b" + re.escape(f) + r"\b", lower))
        if c:
            filler_hits[f] = c

    passive = PASSIVE_RE.findall(prose)
    return {
        "words": n_words,
        "sentences": n_sent,
        "avg_sentence_len": asl,
        "flesch": flesch,
        "grade": grade,
        "read_min": n_words / 220.0,
        "long_sentences": long_sentences,
        "filler": filler_hits,
        "passive": len(passive),
    }


def ease_label(score):
    if score >= 70:
        return "easy (conversational)"
    if score >= 60:
        return "plain English (good for most posts)"
    if score >= 50:
        return "fairly difficult"
    return "difficult — consider shorter sentences/words"


def main():
    ap = argparse.ArgumentParser(description="Readability metrics for a blog draft.")
    ap.add_argument("path", help="Markdown file, or - for stdin")
    ap.add_argument("--top", type=int, default=10, help="max long sentences to show")
    args = ap.parse_args()

    if args.path == "-":
        text = sys.stdin.read()
    else:
        with open(args.path, encoding="utf-8") as fh:
            text = fh.read()

    r = analyze(text)
    print("Blog Readability Report")
    print("=" * 32)
    print(f"Words:              {r['words']}")
    print(f"Sentences:          {r['sentences']}")
    print(f"Avg sentence len:   {r['avg_sentence_len']:.1f} words")
    print(f"Read time:          ~{r['read_min']:.1f} min @220 wpm")
    print(f"Flesch ease:        {r['flesch']:.0f}  ({ease_label(r['flesch'])})")
    print(f"Grade level:        {r['grade']:.1f}")
    print(f"Passive (approx):   {r['passive']}")

    if r["filler"]:
        print("\nFiller words to consider cutting:")
        for word, count in r["filler"].most_common():
            print(f"  {count:>3}x  {word}")
    else:
        print("\nFiller words: none detected. Nice.")

    if r["long_sentences"]:
        print(f"\nLong sentences (>30 words) — split these ({len(r['long_sentences'])} total):")
        for s in r["long_sentences"][: args.top]:
            snippet = s.strip().replace("\n", " ")
            if len(snippet) > 90:
                snippet = snippet[:87] + "..."
            print(f"  - {snippet}")
    else:
        print("\nNo overly long sentences. Good rhythm.")

    print("\nTargets: Flesch 60-70, avg sentence < 20 words, minimal filler/passive.")


if __name__ == "__main__":
    main()
