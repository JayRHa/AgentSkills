# Code Review: <PR title or change description>

**Scope:** <base>...<head> | <N files, +adds/-dels>
**Reviewed:** <date>

## Verdict

> **<Approve | Approve with nits | Request changes | Block>**

**Summary:** <X Critical, X High, X Medium, X Low, X Nit>. <One-sentence overall assessment.>

<Optional: one line on what the change does and whether it achieves its stated intent.>

---

## Findings

### Critical

<For each — delete heading if none:>

**[Critical] <Category> — `path/to/file.ext:LINE`**
What: <one-line description of the problem>
Why it matters: <concrete failure scenario / impact>
Fix:
```diff
- <buggy line>
+ <fixed line>
```

### High

**[High] <Category> — `path/to/file.ext:LINE`**
What: <...>
Why it matters: <...>
Fix: <suggested change or diff>

### Medium

**[Medium] <Category> — `path/to/file.ext:LINE`**
What: <...>
Fix: <...>

### Low

**[Low] <Category> — `path/to/file.ext:LINE`** — <one-liner + fix>

### Nits

- `path:LINE` — <brief nit>
- `path:LINE` — <brief nit>

---

## What's good

- <Briefly note something done well — keeps the review balanced.>

## Open questions

- <Anything where intent was unclear and you reviewed against an assumption.>

---

*Categories: Correctness | Security | Quality | Tests | Performance | Style*
*Confidence: prefix uncertain findings with "Possible:" and state what would confirm.*
