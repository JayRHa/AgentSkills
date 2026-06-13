---
name: study-plan-builder
description: Builds a realistic, personalized learning roadmap for a skill or subject — with milestones, curated resource types, active practice, spaced review, and progress checkpoints — fit to the learner's deadline and weekly time budget. Use this skill when the user asks to "make a study plan", "create a learning roadmap", "help me learn X in N weeks", "plan how to study for an exam", "build a curriculum", or wants a structured path to master a topic. Grounded in learning-science principles (spacing, retrieval, interleaving).
license: MIT
---

# Study Plan Builder

## Overview

Produce a week-by-week learning plan that someone can actually follow. Work backward from the goal and deadline, sequence topics by dependency, and bake in **active practice** and **spaced review** rather than passive reading. Apply the evidence-based methods in `references/learning-science.md`.

Keywords: study plan, learning roadmap, curriculum, syllabus, exam prep, skill acquisition, spaced repetition, interleaving, milestones, schedule, time budget, deliberate practice.

## Workflow

1. **Define the goal concretely.** Turn "learn Python" into an observable outcome ("build and deploy a small Flask API", "pass the PCEP exam"). A measurable goal sets the scope.
2. **Establish constraints.** Capture: deadline, hours/week available, current level, and preferred resource types. If unknown, assume ~5 hrs/week and beginner, and say so.
3. **Decompose into topics** and order them by **dependency** (fundamentals before applications). Group into milestones — each a meaningful, demonstrable capability.
4. **Allocate time** across the calendar working backward from the deadline; leave ~15% buffer for slippage and review. Don't overschedule.
5. **Design each week** with the mix in `references/learning-science.md`: input (read/watch) → **active practice** (exercises/projects) → **retrieval** (recall, flashcards, self-quiz). Practice should dominate over passive input.
6. **Schedule spaced review** of earlier material at expanding intervals, and **interleave** related topics rather than blocking one at a time.
7. **Add checkpoints.** Every milestone ends with a concrete deliverable or self-test that proves mastery before moving on.
8. **Render the plan** using `templates/study-plan.md`. Include resources (by type, not a rigid single source), weekly goals, practice tasks, and review items.
9. **Add an adjustment rule** — what to do if behind (cut scope, not review) or ahead (deepen/project).

## Decision Framework

| Situation | Plan choice |
| --- | --- |
| Hard deadline (exam) | Work backward from date; front-load content, back-load practice tests |
| Open-ended skill | Project-driven milestones; learn just-in-time for each project |
| Very limited time | Ruthless scope cut to the 20% that delivers 80%; daily micro-sessions |
| Building a habit | Short, consistent daily blocks beat rare long ones |
| Prerequisite gaps | Insert a "foundations" milestone before the main track |

## Worked Example (excerpt)

**Goal:** "Comfortable writing SQL queries for analytics in 6 weeks, 5 hrs/week."

- **M1 (wk 1–2): Foundations** — SELECT, WHERE, ORDER BY, basic functions. *Deliverable:* answer 20 single-table questions on a sample DB.
- **M2 (wk 3–4): Joins & aggregation** — JOINs, GROUP BY, HAVING, subqueries. *Deliverable:* a 10-query report on a 3-table schema. *Review:* re-test M1 questions (spaced).
- **M3 (wk 5): Window functions & CTEs.** *Deliverable:* rewrite 3 subquery reports using window functions.
- **M4 (wk 6): Capstone + review.** *Deliverable:* end-to-end analysis from a raw dataset; mixed-topic self-quiz (interleaved).

See `templates/study-plan.md` for the full structure.

## Best Practices

- **Goal first, measurable.** No plan without a concrete target.
- **Practice > passive input.** Schedule more doing than reading/watching.
- **Space and interleave** earlier topics; don't cram or block.
- **Checkpoints with deliverables** gate progression.
- **Build in buffer** (~15%) and a rule for falling behind (cut scope, keep review).
- **Resource types, not dogma** — suggest a book/course/docs/practice mix and let the learner pick.

## Common Pitfalls

- **Passive plans** ("read chapters 1–10") with no practice or retrieval.
- **Overscheduling** with zero buffer — one bad week derails everything.
- **No spaced review**, so early material is forgotten by the exam.
- **Vague goals** that can't tell you when you're done.
- **Blocking** one topic for weeks instead of interleaving for durable learning.
- **Ignoring prerequisites**, causing a wall mid-plan.
