#!/usr/bin/env python3
"""Generate candidate chunkings from a text or Markdown file for inspection.

Stdlib only. Produces chunks with a self-context title prefix and reports
token-ish statistics so you can eyeball whether your chunk size/overlap are sane
before wiring up an embedding pipeline.

Usage:
    python chunk_text.py INPUT.md --strategy recursive --size 400 --overlap 60
    python chunk_text.py INPUT.md --strategy markdown
    python chunk_text.py INPUT.md --strategy fixed --size 300 --overlap 0 --json

Strategies:
    fixed      Fixed-size word windows with overlap (baseline).
    recursive  Split on paragraphs, then sentences, packing up to --size.
    markdown   Header-aware: one chunk per section, heading kept as prefix.

Size/overlap are measured in approximate tokens (~0.75 words/token assumed:
we count words and treat 1 word ~= 1.3 tokens).
"""
import argparse
import json
import re
import sys

WORDS_PER_TOKEN = 0.75  # ~1.3 tokens per word


def approx_tokens(text):
    words = len(text.split())
    return int(round(words / WORDS_PER_TOKEN))


def split_sentences(text):
    # Lightweight sentence splitter; good enough for inspection.
    parts = re.split(r"(?<=[.!?])\s+", text.strip())
    return [p for p in parts if p]


def fixed_chunks(text, size_tokens, overlap_tokens):
    words = text.split()
    size_w = max(1, int(size_tokens * WORDS_PER_TOKEN))
    overlap_w = max(0, int(overlap_tokens * WORDS_PER_TOKEN))
    step = max(1, size_w - overlap_w)
    chunks = []
    i = 0
    while i < len(words):
        chunk = " ".join(words[i:i + size_w])
        chunks.append(chunk)
        if i + size_w >= len(words):
            break
        i += step
    return chunks


def recursive_chunks(text, size_tokens, overlap_tokens):
    paragraphs = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
    units = []
    for p in paragraphs:
        if approx_tokens(p) <= size_tokens:
            units.append(p)
        else:
            units.extend(split_sentences(p))
    chunks = []
    current = []
    current_tokens = 0
    for u in units:
        ut = approx_tokens(u)
        if current and current_tokens + ut > size_tokens:
            chunks.append(" ".join(current))
            # carry overlap: keep tail units until overlap budget met
            carried = []
            carried_tokens = 0
            for prev in reversed(current):
                pt = approx_tokens(prev)
                if carried_tokens + pt > overlap_tokens:
                    break
                carried.insert(0, prev)
                carried_tokens += pt
            current = carried
            current_tokens = carried_tokens
        current.append(u)
        current_tokens += ut
    if current:
        chunks.append(" ".join(current))
    return chunks


def markdown_chunks(text, size_tokens):
    lines = text.splitlines()
    sections = []
    heading_stack = []
    buf = []

    def flush():
        if buf and any(l.strip() for l in buf):
            prefix = " > ".join(heading_stack)
            body = "\n".join(buf).strip()
            sections.append((prefix, body))

    for line in lines:
        m = re.match(r"^(#{1,6})\s+(.*)$", line)
        if m:
            flush()
            buf = []
            level = len(m.group(1))
            title = m.group(2).strip()
            heading_stack = heading_stack[: level - 1]
            while len(heading_stack) < level - 1:
                heading_stack.append("")
            heading_stack.append(title)
        else:
            buf.append(line)
    flush()

    chunks = []
    for prefix, body in sections:
        header = prefix.replace(" > ", " ").strip()
        full = (header + "\n" + body).strip() if header else body
        if approx_tokens(full) <= size_tokens or not header:
            chunks.append(full)
        else:
            for sub in recursive_chunks(body, size_tokens, int(size_tokens * 0.1)):
                chunks.append((header + "\n" + sub).strip())
    return chunks


def main(argv=None):
    ap = argparse.ArgumentParser(description="Generate candidate chunkings for inspection.")
    ap.add_argument("input", help="Path to a .txt or .md file")
    ap.add_argument("--strategy", choices=["fixed", "recursive", "markdown"], default="recursive")
    ap.add_argument("--size", type=int, default=400, help="Target chunk size in approx tokens")
    ap.add_argument("--overlap", type=int, default=60, help="Overlap in approx tokens (fixed/recursive)")
    ap.add_argument("--json", action="store_true", help="Emit chunks as JSON")
    args = ap.parse_args(argv)

    try:
        with open(args.input, "r", encoding="utf-8") as f:
            text = f.read()
    except OSError as e:
        print(f"error: cannot read {args.input}: {e}", file=sys.stderr)
        return 1

    if args.strategy == "fixed":
        chunks = fixed_chunks(text, args.size, args.overlap)
    elif args.strategy == "recursive":
        chunks = recursive_chunks(text, args.size, args.overlap)
    else:
        chunks = markdown_chunks(text, args.size)

    chunks = [c for c in chunks if c.strip()]
    if args.json:
        out = [{"index": i, "approx_tokens": approx_tokens(c), "text": c} for i, c in enumerate(chunks)]
        print(json.dumps(out, indent=2, ensure_ascii=False))
        return 0

    sizes = [approx_tokens(c) for c in chunks] or [0]
    print(f"strategy={args.strategy} size={args.size} overlap={args.overlap}")
    print(f"chunks={len(chunks)} tokens: min={min(sizes)} max={max(sizes)} "
          f"mean={sum(sizes) // len(sizes)}")
    print("-" * 60)
    for i, c in enumerate(chunks):
        preview = c.replace("\n", " ")
        if len(preview) > 200:
            preview = preview[:200] + " ..."
        print(f"[{i}] (~{approx_tokens(c)} tok) {preview}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
