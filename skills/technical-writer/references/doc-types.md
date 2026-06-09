# Documentation Types (Diátaxis)

Most good technical documentation falls into one of four types. Each serves a different reader need. Keeping them separate is the single biggest lever for clear docs. This file describes each type, when to use it, what to optimize for, and a structural template.

## The four-quadrant model

| | Study (learning) | Work (doing) |
|---|---|---|
| **Practical steps** | Tutorial | How-to guide |
| **Theoretical knowledge** | Explanation | Reference |

- **Tutorial** = learning + doing → "teach me by building something"
- **How-to guide** = work + doing → "help me solve this specific problem"
- **Reference** = work + knowledge → "tell me the exact details"
- **Explanation** = study + knowledge → "help me understand the concept"

---

## 1. Tutorial

**Reader intent:** "I'm new and want to learn by doing."

**Optimize for:** a guaranteed successful first experience. The reader will trust you (and the product) if they finish and it worked.

**Rules:**
- Hold the reader's hand. Every step must succeed; never assume.
- One clear, concrete outcome (e.g., "build a working todo API").
- Minimize choices and tangents — there is one path.
- Defer explanation: say what to do, not exhaustively why. Link to explanation docs.
- State exactly what they'll have at the end and roughly how long it takes.

**Template:**
```
# Build <concrete thing> (Tutorial)
What you'll build: <one sentence + screenshot/output preview>
Time: ~N minutes  |  Prerequisites: <minimal, with links>

## Step 1: <action verb + goal>
<exact commands/code>
<expected output>

## Step 2: ...
...

## What you built
<recap + next steps / links to how-to and explanation>
```

---

## 2. How-to guide

**Reader intent:** "I have a specific task; give me the steps."

**Optimize for:** speed to the goal. Assume basic competence.

**Rules:**
- Title is a task, phrased as the reader's goal: "How to rotate API keys."
- Start from a realistic situation; state prerequisites and assumptions.
- A focused sequence of steps. Address the main case; note important variations.
- Omit teaching detours — link out for concepts.
- End when the task is done; add a short troubleshooting/verification section if useful.

**Template:** see `templates/how-to-guide.md`.

---

## 3. Reference

**Reader intent:** "I need to look up an exact detail."

**Optimize for:** accuracy, completeness, consistency, fast lookup.

**Rules:**
- Structure mirrors the product's structure (one entry per command/endpoint/param).
- Be exhaustive and neutral — describe, don't instruct or persuade.
- Consistent layout for every entry so readers learn the pattern once.
- Use tables for parameters, options, return values, error codes.
- No narrative; readers jump in and out.

**Template (per item):**
```
## <name>
<one-line description>

**Syntax / signature:** `...`

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| ... | ... | yes/no | ... | ... |

**Returns:** <type + meaning>
**Errors:** <codes + when they occur>
**Example:** `<minimal runnable example + output>`
```

---

## 4. Explanation

**Reader intent:** "Help me understand how/why this works."

**Optimize for:** understanding, context, and informed decisions.

**Rules:**
- Discuss concepts, design decisions, trade-offs, history, alternatives.
- It's okay to be discursive and opinionated here (unlike reference).
- No step-by-step instructions — link to how-to/tutorial for action.
- Use diagrams and analogies; connect to the bigger picture.

**Template:**
```
# Understanding <concept>
## The problem it solves
## How it works (mental model + diagram)
## Design trade-offs / alternatives considered
## When to use it (and when not to)
## See also (how-to, reference, tutorial links)
```

---

## Special-purpose documents

### README
The front door. Shortest path from zero to first success.
Order: one-line description → what/why → quick install → minimal usage example → links to deeper docs → license/contributing.
Keep it short; link out rather than inlining everything.

### Release notes / changelog
Scannable, grouped by impact. Use [Keep a Changelog] grouping:
`Added`, `Changed`, `Deprecated`, `Removed`, `Fixed`, `Security`.
Lead each entry with the user-visible effect, not the internal cause. Call out breaking changes prominently with migration steps.

### Onboarding doc
A tutorial + how-to hybrid for new teammates: environment setup (verified on a clean machine), how to run/test, where things live, who to ask, first task.

---

## Cross-linking

Readers move between needs. From a tutorial, link to the relevant how-to and reference. From a how-to, link to explanation for the "why." Never force a reference reader through a tutorial to find a value.
