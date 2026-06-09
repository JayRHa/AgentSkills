---
name: okr-writer
description: Writes strong OKRs (Objectives and Key Results) with outcome-focused, inspiring objectives and measurable, ambitious, time-bound key results. Use this skill when the user asks to write, draft, review, critique, or improve OKRs, goals, or quarterly/annual objectives, when they mention "objectives and key results", "set goals for the team", "turn this strategy into OKRs", "are these good key results", or when distinguishing outcomes from outputs/tasks for planning and performance.
license: MIT
---

# OKR Writer

## Overview

OKRs (Objectives and Key Results) are a goal-setting framework that links an inspiring qualitative **Objective** ("what we want to achieve") to 2-5 quantitative **Key Results** ("how we measure progress"). This skill produces OKRs that are outcome-focused (changes in behavior, value, or state — not task lists), measurable (a number anyone can verify), and appropriately ambitious.

Keywords: OKR, objective, key result, goal setting, KPI vs OKR, outcome vs output, stretch goal, quarterly planning, north star, measurable goals, scoring, grading.

Use this skill to: draft new OKRs from a vague goal or strategy, rewrite weak/task-based OKRs into outcome-based ones, review and score a draft set, or cascade company OKRs to teams.

## Core Definitions

- **Objective** — A memorable, qualitative, inspirational statement of WHAT you want to accomplish in the period. No numbers. Answers "where do we want to go?"
- **Key Result** — A quantitative measure of HOW you'll know you got there. Has a metric, a baseline, and a target. Answers "how do we know we arrived?"
- **Output** — Something you produce or do (ship a feature, run 3 campaigns). NOT a key result on its own.
- **Outcome** — A change that results from outputs (activation rate rises from 40% to 55%). This is what good key results measure.
- **Initiative / Task** — The work you do to move a key result. Tracked separately, never as the OKR itself.

## Workflow

Follow these steps in order. Do not skip the diagnosis step — most weak OKRs come from skipping it.

1. **Clarify intent and scope.** Ask (or infer) four things: the *team/owner*, the *time horizon* (quarter, year), the *strategic theme or problem* this serves, and the *current baseline* for any metric mentioned. If a baseline is unknown, flag it — a key result without a baseline is unscoreable.

2. **Find the outcome.** Restate the user's goal as "If we succeed, what will be measurably different about the world / customer / business?" If they hand you a task ("rebuild onboarding"), ask "so that what happens?" until you reach a metric. See `references/outcome-vs-output.md`.

3. **Draft the Objective.** Write one short, qualitative, inspiring sentence. No metrics, no jargon, no "and" stitching two goals together. It should be repeatable from memory. Use the patterns in `references/objective-patterns.md`.

4. **Draft 2-5 Key Results.** Each must follow the metric formula: `<verb> <metric> from <baseline> to <target> by <date>`. Cover the outcome from multiple angles and include at least one *counter-balancing / quality* KR so the team can't game the headline number. See `references/key-result-formulas.md`.

5. **Calibrate ambition.** Decide committed vs aspirational (stretch). For aspirational OKRs, target ~70% confidence — hitting 100% means it was sandbagged. State the confidence level explicitly.

6. **Self-review with the rubric.** Run every OKR through `references/review-rubric.md` (or `scripts/okr_lint.py` for automated checks). Fix any KR that is a task, lacks a number, lacks a baseline, or just measures activity.

7. **Present.** Output using `templates/okr-template.md`. Include owner, period, confidence, and the initiatives separately from the KRs.

## The Key Result Formula

Every key result should be reducible to:

> **{Direction verb} {metric} from {baseline} to {target} by {deadline}.**

Examples:
- "Increase 30-day user retention from 42% to 55% by end of Q3."
- "Reduce average support first-response time from 9h to under 2h by Sept 30."
- "Grow ARR from $4.2M to $5.0M by year end."

If you can write "Done / Not done" instead of a number, it is probably a task, not a key result. Binary milestones are allowed sparingly (e.g., "Achieve SOC 2 Type II certification") but prefer graded metrics.

## Decision Heuristics

- **Task vs Key Result test:** Ask "Could we do this perfectly and still fail the objective?" If yes, it's an output/initiative, not a KR. Demote it.
- **Vanity vs value test:** Would the metric impress a board slide but not reflect real value (e.g., "signups" with no activation)? Pair it with an activation/retention KR or replace it.
- **Gaming test:** "How would a lazy/clever team hit this number without delivering the intent?" Add a counter-metric to close the loophole.
- **Memorability test:** Can a team member recite the Objective without reading it? If not, shorten.
- **Quantity test:** More than 5 KRs per Objective dilutes focus; more than 3-5 Objectives per team scatters effort. Cut.

## Worked Example (compressed)

Weak input: *"Improve our mobile app and ship the redesign."*

Diagnosis: This is an output. The implied outcome is usage/satisfaction. Baseline needed.

Strong OKR:
- **Objective:** Make the mobile app the channel customers love most.
- **KR1:** Raise mobile App Store rating from 3.6 to 4.5 by end of Q4.
- **KR2:** Increase share of weekly active users on mobile from 31% to 50%.
- **KR3:** Cut mobile crash-free-session rate gaps: improve from 98.1% to 99.5% (counter-balance for shipping fast).
- *Initiatives (not KRs):* ship redesign, add biometric login, fix top 10 crashes.

See `examples/saas-growth-okrs.md` and `examples/rewrite-weak-okrs.md` for full examples.

## Best Practices

- Limit to **3-5 Objectives** per team, **2-5 Key Results** per Objective.
- Objectives are qualitative and inspiring; Key Results are quantitative and boring-precise.
- Always record a **baseline** and a **deadline** within the OKR period.
- Separate **Initiatives** (the work) from **Key Results** (the result). Track both, grade only KRs.
- Mark each set as **committed** (must hit 100%) or **aspirational** (target ~70%).
- Make OKRs **public** across the org; cascade by alignment, not literal copy-paste.
- Set, then **grade at period end** on a 0.0-1.0 scale; reflect, don't punish stretch misses.

## Common Pitfalls

- **Task lists masquerading as KRs** ("Launch v2", "Hire 3 engineers") — these are initiatives.
- **No baseline** — "Increase revenue" with no start point can't be scored.
- **Sandbagging** — targets the team already knows they'll hit; nothing learned.
- **Too many OKRs** — everything is a priority, so nothing is.
- **Vanity metrics** — page views, raw signups, lines of code.
- **Objectives with numbers** — that's a key result wearing an objective's hat.
- **Stitched objectives** — "Grow revenue AND improve quality AND hire" — split them.
- **Set-and-forget** — no mid-period check-ins or end-period grading.

## Supporting Files

- `references/outcome-vs-output.md` — how to convert outputs into outcomes, the "so that" laddering technique, and a large lookup table.
- `references/objective-patterns.md` — sentence patterns and a bank of strong/weak objective examples.
- `references/key-result-formulas.md` — KR metric types, the formula, counter-metrics, and verb lists.
- `references/review-rubric.md` — the scoring rubric to grade any draft OKR set.
- `templates/okr-template.md` — fill-in template for presenting a final OKR set.
- `examples/saas-growth-okrs.md` — a complete company → team cascade example.
- `examples/rewrite-weak-okrs.md` — before/after rewrites of common bad OKRs.
- `scripts/okr_lint.py` — runnable linter that flags task-like, baseline-less, or number-less key results.
