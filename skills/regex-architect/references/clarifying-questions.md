# Clarifying Questions Before Writing a Regex

Ask these (or infer confidently from context) before producing a pattern. Skip a
question only when the answer is unambiguous from the request.

## 1. Flavor / runtime (always)
- Which language or tool will run this? (Python `re`, JavaScript, Java, .NET, Go/Rust
  RE2, PCRE/grep/ripgrep, sed/awk?)
- Why it matters: named-group syntax, lookarounds, `\A`/`\z`, possessive quantifiers,
  and Unicode `\d` all differ. RE2 forbids lookarounds/backreferences entirely.

## 2. Operation
- Validate (is the WHOLE string valid)? → anchored `^...$` / `fullmatch`.
- Search/extract (find substrings)? → unanchored; maybe capture groups + global flag.
- Replace? → need capture groups and replacement template.
- Split? → pattern matches the delimiter.

## 3. Examples (ask for concrete data)
- Give 2-3 strings that MUST match.
- Give 2-3 strings that MUST NOT match (the negatives reveal the real spec).
- Any tricky edge cases (empty string, leading zeros, unicode, very long input)?

## 4. Semantics
- Case sensitive?
- Multiline input — should `^`/`$` match per-line or whole-string?
- Unicode text, or ASCII only? Should `\d` accept non-ASCII digits?
- Are leading/trailing spaces allowed?

## 5. Safety / performance
- Is the input untrusted or unbounded (web form, log ingestion, public API)?
- Is there a maximum sensible length? (Enables bounded quantifiers + length cap.)
- Does the platform support a regex timeout?

## 6. Maintainability
- Should the result be a single compact pattern, or a verbose/commented version?
- Do they need named capture groups for downstream extraction?

## Inference defaults (when the user does not specify)
- Assume validation → anchored, and SAY that you anchored it.
- Assume the most common runtime mentioned in the conversation; otherwise show PCRE
  and note JS/Python differences.
- Assume untrusted input for anything described as a form, API, or log → design for
  linear time.
- Always include both the pattern AND a short explanation.
