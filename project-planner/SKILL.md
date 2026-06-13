---
name: project-planner
description: Decomposes a goal into a work breakdown structure (WBS) with milestones, task dependencies, and effort estimates, then produces a schedule, critical path, and risk list. Use this skill when the user wants to plan a project, "break this down into tasks", build a work breakdown structure, create a project plan or roadmap, estimate effort/timeline, identify dependencies or the critical path, sequence work, or turn a goal/spec into an actionable, scheduled task list.
license: MIT
---

# Project Planner

## Overview
Turns a fuzzy goal into a concrete, scheduled plan. Produces a Work Breakdown Structure (WBS), milestones, an explicit dependency graph, defensible effort estimates, a critical path, and a risk register.

Keywords: project plan, work breakdown structure, WBS, milestones, dependencies, critical path, estimation, scheduling, roadmap, task decomposition, Gantt, sequencing.

Use this skill whenever the input is a goal/spec/idea and the desired output is "what needs to happen, in what order, and roughly how long".

## When to use
- "Plan the migration to X" / "Break this feature into tasks" / "Build a roadmap for Q3".
- The user has a deliverable but no task list, sequence, or estimate.
- An existing task list needs dependencies, estimates, or a critical path added.

## Workflow
Follow these steps in order. Do not skip clarification.

1. **Clarify the goal and constraints.** Capture: the single end deliverable ("done" definition), hard deadline (if any), team/resource availability, and any fixed external dependencies. Ask at most 3–5 sharp questions if these are missing. See `references/clarifying-questions.md`.
2. **Decompose into a WBS.** Break the goal top-down into deliverable-oriented work packages using the 100% rule (children fully cover the parent, no overlap). Stop decomposing at the 8/80 rule: each leaf task is 8–80 hours of work. Number hierarchically (1, 1.1, 1.1.1). See `references/wbs-method.md`.
3. **Define milestones.** Mark zero-duration checkpoints that signal a meaningful state change (e.g., "Design approved", "Beta deployed"). Every milestone must map to completed work packages.
4. **Map dependencies.** For each leaf task list its predecessors and the dependency type (FS/SS/FF/SF, default Finish-to-Start). Distinguish hard (mandatory) from soft (preferred) dependencies. See `references/dependencies-and-critical-path.md`.
5. **Estimate effort.** Estimate each leaf task using three-point PERT: `te = (O + 4M + P) / 6`. Record Optimistic/Most-likely/Pessimistic. Convert effort to duration using availability and parallelism. See `references/estimation.md`.
6. **Compute the schedule and critical path.** Forward pass for early start/finish, backward pass for late start/finish, slack = LS − ES. The critical path is the zero-slack chain; its length is the minimum project duration. Use `scripts/critical_path.py` to compute this automatically from your task list.
7. **Identify risks.** List top risks with likelihood × impact, and a mitigation or contingency buffer for each. Add schedule buffer to the critical path, not to individual tasks.
8. **Produce the plan document.** Fill in `templates/project-plan.md`. Present the WBS, milestone table, dependency/critical-path summary, estimate table, and risk register.

## Estimation quick reference
- Always estimate **effort** (person-hours) separately from **duration** (calendar time). Duration = effort ÷ (people × daily-available-hours), inflated by dependencies and context-switching.
- Use PERT three-point estimates; never a single number for anything non-trivial.
- Apply a global contingency buffer (typically 15–30%) at the project level based on novelty, not per-task padding.
- Decompose anything you cannot estimate confidently — uncertainty is a signal the task is too big.

## Decision heuristics
- **Too big to estimate?** Split it (8/80 rule).
- **More than ~7 children under one parent?** Add an intermediate grouping level.
- **A task everyone depends on?** It is likely on the critical path — protect it and start it early.
- **Long pole with high uncertainty?** Prototype/spike it first as its own early task to retire risk.
- **Soft dependency blocking parallelism?** Challenge it; reordering may shorten the critical path.

## Best Practices
- Decompose by deliverables and outcomes, not by activities or org charts.
- Every leaf task has a verb, a clear "done" criterion, an owner (or role), an estimate, and predecessors.
- Make dependencies explicit; an implicit dependency is a missed delay.
- Re-estimate and recompute the critical path whenever scope changes.
- Keep the WBS and the schedule in sync; the schedule is derived from the WBS, never invented separately.

## Common Pitfalls
- Confusing milestones with tasks (milestones have zero duration).
- Padding every task instead of buffering the project — hides real slack and invites Parkinson's Law.
- Listing tasks with no dependencies, producing a flat "everything at once" plan.
- Estimating duration directly and forgetting that one person can't do two parallel tasks.
- Decomposing by team ("Frontend work") rather than by deliverable, causing gaps and overlaps.
- Ignoring the critical path, then compressing non-critical tasks that don't move the deadline.

## Bundled files
- `references/wbs-method.md` — decomposition rules, numbering, 100%/8-80 rules, worked breakdown.
- `references/estimation.md` — PERT, effort vs duration, story points, calibration.
- `references/dependencies-and-critical-path.md` — dependency types, forward/backward pass, slack, crashing/fast-tracking.
- `references/clarifying-questions.md` — the question checklist for step 1.
- `scripts/critical_path.py` — computes ES/EF/LS/LF, slack, critical path, and project duration from a JSON task list.
- `templates/project-plan.md` — the output document template.
- `examples/website-launch.md` — a full worked example from goal to scheduled plan.
