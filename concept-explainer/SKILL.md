---
name: concept-explainer
description: Explains complex or technical concepts clearly at the right level for the audience, using layered depth, concrete analogies, worked examples, and checks for understanding — adapting from ELI5 to expert. Use this skill when the user asks to "explain X", "ELI5", "help me understand X", "what is X and how does it work", "explain this like I'm a beginner/expert", "break down this concept", or wants a confusing topic made intuitive. Works for technical, scientific, financial, or abstract topics.
license: MIT
---

# Concept Explainer

## Overview

Make hard ideas click. Calibrate to the learner's level, build from what they already know, use a vivid analogy, then layer in precision and a concrete example. End by checking understanding.

Keywords: explain, ELI5, teach, understand, intuition, analogy, mental model, break down, simplify, deep dive, learning, tutoring.

## Workflow

1. **Calibrate the level.** Infer or ask the audience level: child / curious novice / practitioner / expert. Match vocabulary and assumed background. When unstated, default to "smart person new to this field" and offer to go deeper.
2. **Anchor to prior knowledge.** Start from something the learner already understands and bridge to the new idea ("you know how X works? This is like that, except…").
3. **Lead with one strong analogy.** Pick a single, accurate analogy (see techniques in `references/techniques.md`). State where the analogy holds and, crucially, **where it breaks down** — bad analogies that aren't bounded create misconceptions.
4. **Give the precise definition** after the intuition, not before. Intuition first, formality second.
5. **Show a concrete worked example.** Make the abstract tangible with real numbers, code, or a scenario.
6. **Layer depth progressively.** Structure as: one-sentence gist → short paragraph → deeper mechanics. Let the reader stop at the depth they need.
7. **Address the common misconception** for the topic head-on ("A lot of people think X — actually…").
8. **Check understanding.** End with a quick question, a "you'd now be able to…" statement, or an invitation to go deeper.

## Decision Framework

| Audience | Style |
| --- | --- |
| Child (ELI5) | Everyday analogy, no jargon, short sentences, concrete objects |
| Curious novice | Analogy + plain definition + one example; define each term once |
| Practitioner | Less analogy, more mechanics, trade-offs, when to use it |
| Expert | Skip basics; focus on nuance, edge cases, precise terminology |

## Worked Example (explaining "database index", novice level)

> **Gist:** An index is like the index at the back of a book — instead of reading every page to find a topic, you jump straight to it.
>
> **How it works:** A database without an index scans every row to find matches (slow, like flipping through all pages). An index keeps a sorted lookup of a column's values pointing to the matching rows, so the database can binary-search instead of scanning.
>
> **Where the analogy breaks:** unlike a book index, a database index has to be **updated on every write**, so it speeds reads but slightly slows inserts and uses extra storage.
>
> **Example:** `CREATE INDEX ON users(email)` turns "find the user with this email" from scanning a million rows into a handful of lookups.
>
> **Check:** Given that, why might you *not* index a column you rarely search but write to constantly?

See `examples/explain-recursion.md` for a multi-level explanation.

## Best Practices

- **Intuition before formality.** Never open with the textbook definition.
- **One analogy, well-bounded** — and always say where it breaks.
- Use **concrete numbers and scenarios**, not abstractions piled on abstractions.
- **Progressive disclosure**: gist → detail → depth, so readers self-select.
- Define jargon the first time; don't assume.
- Confirm understanding instead of assuming it landed.

## Common Pitfalls

- **Jargon to explain jargon** — circular and useless to a novice.
- **Unbounded analogies** that quietly create misconceptions.
- **Wrong level** — ELI5-ing an expert (condescending) or overwhelming a beginner.
- **Definition dump** with no intuition or example.
- **No worked example**, leaving the idea abstract.
- **Sacrificing accuracy for simplicity** to the point of being wrong — simplify, don't falsify.
