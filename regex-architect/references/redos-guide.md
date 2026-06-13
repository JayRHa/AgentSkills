# ReDoS & Catastrophic Backtracking Guide

## What it is
Backtracking regex engines (PCRE, Python `re`, JavaScript, Java, .NET, Ruby) try
every possible way to match before giving up. Certain patterns create an
**exponential** number of paths on a non-matching input, so a 30-character string
can hang the engine for seconds, minutes, or effectively forever. An attacker who
controls the input can use this to DoS your service (ReDoS).

RE2 (Go's `regexp`, Rust's `regex`, RE2 library) uses an automaton and runs in
linear time — it is immune, but does NOT support backreferences or lookarounds.

## The three danger signatures
1. **Nested quantifiers**: a quantifier applied to a group that already repeats.
   - `(a+)+`, `(a*)*`, `(\d+)*`, `([a-z]+)*`
2. **Overlapping alternation under a quantifier**: alternatives that can match the
   same text.
   - `(a|a)*`, `(a|ab)*`, `(\w|\d)*` (\d is a subset of \w)
3. **Adjacent unbounded quantifiers over overlapping classes**:
   - `.*.*`, `\s*\s*`, `[0-9]*[0-9]*`

All three explode when the input *almost* matches but fails at the very end
(e.g., a long run of `a`s followed by `!` against `^(a+)+$`).

## How to spot it fast
- Look for `)+`, `)*`, `){...,}` immediately after a group that itself contains
  `+`, `*`, or `{n,}`.
- Look for alternations `(x|y)` inside a `*`/`+` where `x` and `y` can both match
  the same first character.
- Look for two consecutive greedy open-ended quantifiers.

## Fixes (in order of preference)
1. **Eliminate the nesting.** Rewrite to a single quantifier.
   - `(a+)+`  →  `a+`
   - `(ab+)+` →  `(?:ab+)+` only if outer repetition is truly needed AND inner is
     not also unbounded over the same chars; usually flatten the intent.
2. **Make alternatives mutually exclusive / use the unrolled-loop idiom.**
   - Quoted string: replace `".*?"` or `"(\\.|[^"])*"` with
     `"[^"\\]*(?:\\.[^"\\]*)*"`. The negated class `[^"\\]*` cannot overlap with
     `\\.`, so there is exactly one way to match — linear.
3. **Use atomic groups / possessive quantifiers** (PCRE, Java, .NET, PCRE2; NOT
   stock JS or Python <3.11).
   - `(?>\d+)`, `\d++`, `[a-z]*+` prevent the engine from backtracking into that
     subexpression.
   - Python 3.11+ supports possessive quantifiers and atomic groups.
4. **Bound the quantifiers.** If a field has a max length, use `{1,64}` instead of
   `+`. Exponential blowup needs unbounded repetition; bounding caps the work.
5. **Anchor.** A leading `^` lets the engine fail fast instead of retrying at every
   start position.
6. **Switch engines.** For untrusted input, prefer RE2 (Go/Rust) or a regex engine
   with a timeout (.NET `Regex` with `matchTimeout`, Java with a watchdog).
7. **Pre-validate length.** Reject inputs longer than a sane cap before matching.

## Before / after examples
| Vulnerable | Safe rewrite | Why |
|---|---|---|
| `^(a+)+$` | `^a+$` | Removes nesting. |
| `^(\d+)*$` | `^\d*$` | Removes nesting. |
| `^(\w+\s?)*$` | `^\w+(?:\s\w+)*\s?$` | Mutually exclusive segments. |
| `"(\\.|[^"])*"` | `"[^"\\]*(?:\\.[^"\\]*)*"` | Unrolled loop; classes disjoint. |
| `^(.*,)*$` | `^[^,\n]*(?:,[^,\n]*)*$` | Negated class, disjoint alternation. |
| `(a|ab)+` | `a(?:b)?(?:a(?:b)?)*` or redesign | Removes overlap (often a parser is better). |
| `^([a-zA-Z]+)*$` | `^[a-zA-Z]*$` | Removes nesting. |

## Testing for ReDoS
Feed the pattern an **evil string**: a long run of a character the inner part
matches, followed by one character that breaks the overall match. Example for
`^(a+)+$`: `"a" * 30 + "!"`. Time it. If runtime grows super-linearly as you add
more `a`s (doubling each +5 chars), the pattern is vulnerable.

`scripts/regex_test.py --redos PATTERN` automates this probe in Python.

## Quick checklist
- [ ] No quantifier directly wraps a group containing another `+`/`*`/`{n,}`.
- [ ] No `*`/`+` over an alternation whose branches share a prefix/character.
- [ ] No two adjacent open-ended quantifiers over overlapping classes.
- [ ] Validation patterns are anchored (`^...$` / `\A...\z`).
- [ ] Open-ended quantifiers bounded with `{0,n}` where a max exists.
- [ ] Untrusted input: length-capped and/or RE2/timeout engine.
