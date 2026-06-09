---
name: adr-author
description: Authors Architecture Decision Records (ADRs) that capture context, considered options with trade-offs, the chosen decision, and its consequences. Use this skill when the user wants to write, draft, document, or revise an architecture decision, an ADR, a design decision record, a technical decision log, or asks "why did we choose X" / "we need to record this decision" / "document this trade-off" for things like database choice, framework selection, API style, build vs. buy, or deprecating a component.
license: MIT
---

# ADR Author

## Overview

An Architecture Decision Record (ADR) is a short, immutable document that captures one
architecturally significant decision: the forces at play (context), the realistic options,
the option chosen, and the consequences that follow. ADRs form an append-only log so future
maintainers can reconstruct *why* the system looks the way it does — not just *what* it does.

This skill produces rigorous ADRs that distinguish facts from opinions, force an honest
options comparison, and make consequences (good, bad, and neutral) explicit.

**Keywords:** ADR, architecture decision record, design decision, technical decision log,
MADR, Nygard, trade-off analysis, options matrix, decision rationale, superseded decision,
build vs buy, framework selection, database choice, API style, architecture governance.

## When a Decision Deserves an ADR

Write an ADR when the decision is **architecturally significant** — it is costly to reverse,
affects multiple teams/components, or constrains future choices. Use the checklist in
`references/significance-checklist.md`. If none of the criteria fire, capture it as a code
comment or a ticket instead, not an ADR.

## Workflow

1. **Confirm significance.** Run the decision through `references/significance-checklist.md`.
   If it does not qualify, tell the user and suggest a lighter-weight record.

2. **Assign an ID and locate the log.** ADRs live in a directory such as `docs/adr/` or
   `doc/architecture/decisions/`. Number them sequentially with a zero-padded prefix:
   `0001-use-postgresql.md`, `0002-adopt-rest-over-graphql.md`. Use
   `scripts/new_adr.py` to scan the directory, compute the next number, and scaffold the file.

3. **Gather context.** Interview the user (or read the codebase) to extract the *forces*:
   business drivers, technical constraints, team skills, deadlines, existing systems,
   non-functional requirements (performance, security, cost, operability). Separate
   objective facts from assumptions — label assumptions explicitly.

4. **Enumerate real options.** List 2-4 genuinely viable options. "Do nothing" is often a
   valid option and should appear when relevant. Reject straw-man options. For each option,
   describe how it works and its pros/cons against the forces from step 3.

5. **Build the options matrix.** Score options against the decision criteria (the
   non-functional requirements that matter most here). See the worked example in
   `examples/database-selection.md`. The matrix makes the trade-off legible; it does not
   replace judgment.

6. **State the decision.** One clear sentence in active voice: "We will use X." Then explain
   the rationale tied directly to the forces and the matrix. Name who decided and when.

7. **Spell out consequences.** Enumerate positive, negative, and neutral consequences.
   Negative consequences are mandatory — every decision has costs. Include follow-up actions,
   new risks, and what becomes harder.

8. **Set status and links.** Status is one of `Proposed`, `Accepted`, `Rejected`,
   `Deprecated`, `Superseded by ADR-NNNN`. Link related and superseded ADRs bidirectionally.

9. **Write the file** from `templates/adr-template.md`, keep it under ~2 pages, and present
   it. Remind the user that accepted ADRs are immutable — to change a decision, write a new
   ADR that supersedes the old one rather than editing it.

## ADR Document Structure

Use the canonical structure (a pragmatic blend of Nygard and MADR):

- **Title** — `ADR-NNNN: <short imperative phrase>`
- **Status** — Proposed / Accepted / Rejected / Deprecated / Superseded by ADR-NNNN
- **Date** — ISO date the status last changed
- **Context** — the forces, constraints, and problem statement (facts vs. assumptions)
- **Decision Drivers** — the criteria that matter (the columns of your options matrix)
- **Considered Options** — each option with how-it-works + pros/cons
- **Decision Outcome** — the chosen option and the rationale
- **Consequences** — positive, negative, neutral; follow-ups and new risks
- **Links** — supersedes / superseded-by / related ADRs and external references

## Decision Framework: Picking and Comparing Options

Compare options against weighted **decision drivers**, not on vibes:

1. Identify the 3-6 drivers that actually matter for *this* decision (e.g., operability,
   team familiarity, cost, latency, vendor lock-in, time-to-market).
2. Optionally weight them if some clearly dominate.
3. Score each option per driver (`++`, `+`, `o`, `-`, `--`, or 1-5).
4. Read the matrix, then **write the narrative** — the matrix informs, judgment decides.
   Document *why* the winning option wins even if it doesn't top every column.

See `examples/database-selection.md` for a complete matrix and narrative.

## Worked Example

`examples/database-selection.md` shows a full ADR choosing between PostgreSQL, MongoDB, and
DynamoDB for a new service — including the drivers, the scored options matrix, the decision
narrative, and honest negative consequences. Use it as the quality bar.

## Best Practices

- **One decision per ADR.** If you're tempted to use "and", split it.
- **Write in the present tense, active voice.** "We will…", not "It was decided that…".
- **Capture the decision when it's made**, while the context is fresh and the alternatives
  are still remembered. ADRs written months later lose the forces.
- **Make assumptions explicit.** Tag anything not verifiable as an assumption; it tells
  future readers what to re-check if reality diverges.
- **Always list negative consequences.** An ADR with only upsides is marketing, not a record.
- **Keep it short.** Two pages max. Detail belongs in linked design docs, not the ADR.
- **Treat accepted ADRs as immutable.** Supersede, don't edit. The log's value is its history.
- **Link bidirectionally.** When ADR-0012 supersedes ADR-0007, update both files.
- **Number consistently** with zero-padding so the directory sorts correctly.
- **Store ADRs in the repo**, next to the code they govern, so they version with it.

## Common Pitfalls

- **Straw-man options.** Listing only the chosen option plus throwaway alternatives. Future
  readers see through it and lose trust in the log. List options you genuinely weighed.
- **Conflating context with decision.** Context describes the problem and forces *before*
  you decided; it must not leak the conclusion.
- **Omitting "do nothing".** Often the real baseline; failing to consider it hides cost.
- **No consequences, or only good ones.** The most-skipped, most-valuable section.
- **Editing an accepted ADR** to reflect a new choice — this destroys the rationale trail.
  Write a superseding ADR instead.
- **Over-long ADRs** that nobody reads. If it needs a design doc, write one and link it.
- **Writing an ADR for a trivial decision.** Use the significance checklist; don't dilute
  the log with reversible, local choices.
- **Vague titles** like "Database decision". Prefer "ADR-0003: Use PostgreSQL for the orders
  service".
