---
name: proofreader
description: Edits prose for grammar, spelling, punctuation, clarity, concision, and consistent style while preserving the author's meaning, voice, and intent. Use this skill when the user asks to proofread, copyedit, polish, clean up, tighten, fix grammar in, or improve the readability of text such as emails, essays, blog posts, documentation, cover letters, reports, or marketing copy. Triggers include "proofread this", "fix the grammar", "edit for clarity", "make this more concise", "check my writing", "copyedit", or "tighten this up".
license: MIT
---

# Proofreader

## Overview

This skill performs careful proofreading and copyediting of prose. It fixes objective errors (grammar, spelling, punctuation, agreement) and improves clarity, concision, and stylistic consistency — **without changing the author's meaning, voice, tone, or intent**.

Keywords: proofread, copyedit, grammar check, clarity, concision, tighten, polish, style consistency, line edit, readability.

Use it for emails, essays, articles, blog posts, documentation, reports, cover letters, academic writing, and marketing copy. Do **not** use it to rewrite content from scratch, change the argument, fabricate facts, or alter the author's distinctive style.

## The Cardinal Rule

**Preserve meaning.** Every edit must keep the author's intended message intact. When an edit would shift meaning, emphasis, register, or voice, flag it as a *suggestion* rather than applying it silently. If a sentence is ambiguous, do not guess — ask or annotate both readings.

## Workflow

Follow these steps in order. Do a separate pass for each level rather than fixing everything in one chaotic sweep.

1. **Clarify scope.** Determine the register and goal: who is the audience, what is the medium (formal email vs. casual blog), and which English variant applies (US/UK/AU/CA). If unknown, default to US English and the tone already present in the text, and note the assumption.

2. **Pass 1 — Correctness.** Fix unambiguous errors: spelling, typos, subject–verb agreement, verb tense, pronoun agreement, articles, prepositions, and punctuation (commas, apostrophes, semicolons, hyphens vs. en/em dashes). These are non-negotiable and applied directly. See `references/grammar-rules.md`.

3. **Pass 2 — Clarity.** Resolve ambiguity, dangling/misplaced modifiers, unclear pronoun references, faulty parallelism, and awkward construction. Convert needless passive voice to active **only when it does not change emphasis**. Break up overlong run-on sentences.

4. **Pass 3 — Concision.** Cut redundancies, filler, and wordy phrases without losing nuance. Replace bloated phrases with tight equivalents (see `references/concision-cheatsheet.md`). Never cut so aggressively that meaning or politeness is lost.

5. **Pass 4 — Consistency.** Enforce one consistent style throughout: spelling variant, serial (Oxford) comma usage, capitalization, hyphenation, number formatting, date format, quotation style, and terminology. Match whatever the author already does most often unless it is wrong. See `references/style-consistency.md`.

6. **Deliver.** Return the corrected text first. Then provide a concise change log grouped by category, distinguishing **applied fixes** (objective) from **suggestions** (judgment calls the author should approve). Use the format in `templates/edit-report.md`.

## Decision Framework: Fix vs. Suggest

| Situation | Action |
|-----------|--------|
| Spelling, typo, agreement, clear punctuation error | **Fix silently** |
| Wordiness, redundancy, obvious filler | **Fix**, note in log |
| Passive→active that keeps emphasis | **Fix**, note in log |
| Passive→active that shifts emphasis/blame | **Suggest** |
| Tone/word choice that affects voice | **Suggest** |
| Reordering for flow that changes emphasis | **Suggest** |
| Ambiguous meaning (two valid readings) | **Annotate** — do not guess |
| Possible factual error or contradiction | **Flag** — never silently "correct" facts |
| Stylistic preference with no clear rule | **Leave**, optionally mention |

## Heuristics

- **Read aloud** mentally: if you stumble, the reader will too.
- **One idea per sentence** for clarity; combine only related ideas.
- **Strong verbs over nominalizations**: "decide" beats "make a decision."
- **Cut "that," "very," "really," "just," "in order to"** when they add nothing.
- **Prefer the shorter word** when meaning is identical (use > utilize).
- **Keep the author's idioms and personality** — polished, not sanitized.
- **Don't over-edit.** If a sentence is correct and clear, leave it alone. Restraint is a feature.

## Best Practices

- Edit in passes; do not mix correctness with style judgments.
- Always separate objective fixes from subjective suggestions in the report.
- Match the existing dominant style instead of imposing your own.
- Preserve formatting, markdown, code blocks, and intentional line breaks.
- Quote the original snippet alongside each suggestion so the author can compare.
- When unsure whether something is intentional (e.g., a sentence fragment for effect), ask or flag rather than "fixing" it.

## Common Pitfalls

- **Changing meaning** while "improving" a sentence — the worst failure.
- **Flattening voice** into generic corporate prose.
- **Over-deleting** until nuance, hedging, or politeness disappears.
- **Inconsistent fixes** (correcting "color" in one place, leaving "colour" elsewhere).
- **"Correcting" correct grammar** based on myths (splitting infinitives, ending with prepositions, starting with "And").
- **Editing code, names, quotes, or citations** that must stay verbatim.
- **Hypercorrection**: "between you and I," "whom" where "who" is right.

See `references/grammar-rules.md`, `references/concision-cheatsheet.md`, and `references/style-consistency.md` for detailed reference material. Use `scripts/proof_check.py` for a quick automated first-pass scan of common mechanical issues. Use `templates/edit-report.md` for the deliverable format and `examples/sample-edit.md` for a full worked example.
