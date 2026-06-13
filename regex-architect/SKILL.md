---
name: regex-architect
description: Designs, explains, hardens, and tests regular expressions for parsing and validation tasks (emails, URLs, dates, IPs, log lines, CSV fields, identifiers, etc.) while actively defending against catastrophic backtracking (ReDoS). Use this skill when the user asks to "write a regex", "build/fix a regular expression", "match/extract/validate X with regex", "explain this regex", "why is my regex slow/hanging", check for "ReDoS"/"catastrophic backtracking", or convert a pattern between flavors (PCRE, Python re, JavaScript, Java, Go RE2, .NET). Covers capturing/named groups, anchors, lookarounds, Unicode, and flavor portability.
license: MIT
---

# Regex Architect

## Overview
Build correct, readable, and *safe* regular expressions, then prove they work.
Keywords: regex, regular expression, pattern matching, ReDoS, catastrophic
backtracking, validation, extraction, capture group, named group, lookahead,
lookbehind, anchor, Unicode, PCRE, RE2, flavor portability.

This skill exists because regex is easy to write and hard to write *well*. Naive
patterns silently accept bad input, reject good input, or hang a server when fed
an adversarial string. The job is not just "produce a pattern" — it is to produce
a pattern that is anchored correctly, scoped to the right flavor, free of
exponential backtracking, and accompanied by a test plan.

Use this skill whenever a task involves matching, extracting, replacing, splitting,
or validating text with a pattern — or explaining/debugging an existing one.

## Core Principles
1. **Clarify before constructing.** Know the flavor, the input source, whether you
   are validating (whole string) or searching (substring), and what counts as
   valid. Ambiguity here produces wrong regexes.
2. **Anchor on purpose.** Validation almost always needs `^...$` (or `\A...\z`).
   Search/extract usually must NOT be anchored. Mismatched anchoring is the #1
   correctness bug.
3. **Prefer explicit character classes over `.`** `.` is greedy, matches almost
   anything, and is a backtracking magnet. Use `[^"]`, `[^\n]`, `\d`, etc.
4. **Make quantified subpatterns mutually exclusive.** Overlapping alternations or
   nested quantifiers (`(a+)+`, `(a|a)*`, `(.*)*`) cause catastrophic backtracking.
5. **Readability is a feature.** Use named groups, verbose/extended mode, and
   comments for anything non-trivial. A regex nobody can edit is a liability.
6. **Validate with structured logic when regex is the wrong tool.** Do not regex
   HTML, nested brackets, or full email RFC 5322. Say so and offer a parser.

## Workflow
1. **Gather requirements** (see `references/clarifying-questions.md`):
   - Target flavor / language runtime.
   - Validation vs. search vs. replace vs. split.
   - Exact set of valid and invalid examples (ask for at least 2 of each).
   - Multiline? Unicode? Case sensitivity? Performance constraints / untrusted input?
2. **Choose a strategy.** Pick character classes, anchoring, and grouping. Consult
   `references/patterns-cookbook.md` for vetted building blocks rather than
   inventing from scratch.
3. **Draft the pattern** in the requested flavor. Use named capture groups and,
   for non-trivial patterns, provide a verbose/commented version too.
4. **Audit for ReDoS** using the checklist in `references/redos-guide.md`. Rewrite
   nested/overlapping quantifiers; prefer atomic groups, possessive quantifiers,
   or bounded `{0,n}` quantifiers. If the runtime is RE2/Go/Rust, note it is
   already linear-time and lookarounds/backrefs are unsupported.
5. **Explain it.** Provide a token-by-token breakdown so the user can maintain it.
6. **Test it.** Run `scripts/regex_test.py` with positive and negative cases. It
   also runs a lightweight ReDoS timing probe. Report pass/fail per case.
7. **Note portability.** If the user may switch flavors, flag flavor-specific
   constructs (lookbehind, named-group syntax, `\d` Unicode semantics, inline
   flags) per `references/flavor-portability.md`.

## Quick Decision Framework
- **"Is this string entirely valid?"** → anchor with `^$` (or `\A\z`); use `re.fullmatch`
  in Python.
- **"Find all occurrences."** → no anchors; use global/`findall`; mind overlapping matches.
- **"Untrusted/large input?"** → prioritize linear-time design; consider RE2-family
  engine; cap input length before matching.
- **"Nested or recursive structure (HTML, JSON, code)?"** → do NOT use regex; use a parser.
- **"Just needs a yes/no on a simple format?"** → small anchored class-based pattern.

## Worked Example (short)
Validate a US ZIP (5 digits, optional `-####`), JavaScript:
```js
/^\d{5}(?:-\d{4})?$/
```
- `^` / `$` anchor the whole string.
- `\d{5}` exactly five digits.
- `(?:-\d{4})?` optional non-capturing group: hyphen + four digits.

Why it is ReDoS-safe: fixed-count quantifiers, no nested/overlapping repetition.
See `examples/worked-example.md` for a full email-validation walkthrough including
a naive-vs-safe comparison and test output.

## Best Practices
- Always provide both the raw pattern and a one-line explanation of anchoring intent.
- Use non-capturing groups `(?:...)` unless you need the capture; name the ones you keep.
- For validation, return whole-string semantics explicitly (`fullmatch`, `\A...\z`,
  or `^...$` with the right flags).
- Escape user-provided literals; never interpolate raw user input into a pattern.
- Cap input length and/or set engine timeouts when matching untrusted data.
- Offer a verbose/`x`-mode version for any pattern longer than ~40 chars.
- Prefer `[0-9]` over `\d` when you must exclude non-ASCII digits (`\d` matches
  Unicode digits in many flavors).

## Common Pitfalls
- **Unanchored validation** — `/\d{5}/` matches inside `abc12345xyz`. Anchor it.
- **Greedy `.*` across delimiters** — `<.*>` over `<a><b>` grabs everything; use
  `<[^>]*>` or lazy `<.*?>` with care.
- **Nested quantifiers** — `(\d+)+`, `(a*)*`, `(.*,)*` → catastrophic backtracking.
- **Unescaped dot/metachars in literals** — `3.14` matches `3x14`; escape to `3\.14`.
- **`^`/`$` with multiline** — they match line boundaries under `m`; use `\A`/`\z`
  (or `\Z`) for true string ends.
- **Backreferences/lookbehind in RE2/Go/Rust** — unsupported; redesign.
- **Trying to regex HTML/recursive grammars** — wrong tool; use a parser.
- **`\b` word-boundary surprises** — depends on `\w` definition and Unicode mode.

## Bundled Files
- `references/patterns-cookbook.md` — vetted, safe patterns for common formats with
  notes and traps.
- `references/redos-guide.md` — how catastrophic backtracking happens and how to fix it.
- `references/flavor-portability.md` — cross-flavor syntax differences and a mapping table.
- `references/clarifying-questions.md` — the question set to ask before writing a pattern.
- `scripts/regex_test.py` — runnable Python tester for positive/negative cases plus a
  ReDoS timing probe.
- `examples/worked-example.md` — end-to-end email-validation example with test output.
