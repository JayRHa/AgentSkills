# README Quality Checklist

Run through this before finalizing. The bundled `scripts/lint_readme.py`
automates the mechanical checks (marked [auto]).

## Structure
- [ ] Exactly one H1 (`#`) — the project title. [auto]
- [ ] Tagline present on the first screen, under ~12 words.
- [ ] Heading levels don't skip (no H2 → H4 jump). [auto]
- [ ] Sections appear in a logical, conventional order.
- [ ] Table of Contents present iff the README is long (6+ H2). [auto: warns]
- [ ] A License section exists. [auto]

## Above the fold
- [ ] A reader learns WHAT this is within the first 3 lines.
- [ ] Badges resolve and are relevant (4-7, not spam).
- [ ] Hero image/demo has alt text, if present. [auto]

## Accuracy (the most important category)
- [ ] Install commands are real and copy-pasteable.
- [ ] Version numbers/URLs are real, not invented.
- [ ] Usage examples actually run as written.
- [ ] Relative links point to files that exist. [auto]
- [ ] No placeholder leftovers: TODO, FIXME, lorem, `<your-...>`. [auto]

## Quick Start
- [ ] Gets the reader to a working result in the shortest happy path.
- [ ] Every code block has a language hint. [auto: warns]

## Usage & Reference
- [ ] Common tasks shown with real code, simple → advanced.
- [ ] Options/flags/env vars presented as tables, not prose.
- [ ] Defaults and accepted values documented.

## Closing
- [ ] Contributing: links CONTRIBUTING.md or has an inline blurb.
- [ ] License line names the license and links LICENSE.
- [ ] Acknowledgments credit major inspirations/deps (if any).

## Tone & polish
- [ ] Imperative, concise; no marketing fluff.
- [ ] Consistent capitalization in headings.
- [ ] Consistent badge style across the row.
- [ ] Spell-checked.
