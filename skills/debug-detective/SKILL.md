---
name: debug-detective
license: MIT
description: Systematically root-causes software bugs using a reproduce → isolate → hypothesize → bisect → verify methodology, replacing guess-and-check debugging with a disciplined, evidence-driven investigation. Use this skill when a user reports a bug, a test is failing intermittently or consistently, behavior differs between environments, a regression appeared after a change, something "used to work" and now doesn't, an error/stack trace needs root-causing, or when asked to "debug", "find the root cause", "figure out why X happens", or "track down" a defect. Triggers include crashes, wrong output, flaky tests, hangs/deadlocks, memory leaks, performance regressions, heisenbugs, and works-on-my-machine problems.
---

# Debug Detective

## Overview

Debugging fails when it becomes random poking — changing lines, re-running, hoping. This skill enforces a **scientific, evidence-first** process: you never change code to "see what happens" until you have a falsifiable hypothesis backed by an observation. The goal is to find the *root cause*, not to make the symptom disappear.

Keywords: debug, root cause, bug, regression, crash, stack trace, flaky test, intermittent, heisenbug, deadlock, memory leak, race condition, bisect, repro, reproduce, isolate, hypothesis, works on my machine.

Core principle: **A bug you cannot reproduce is a bug you cannot confirm fixed.** Spend your effort earning a reliable reproduction first; everything else gets faster after that.

## Workflow

Follow these phases in order. Do not skip ahead — a fix found by skipping is usually a coincidence, not a cure.

### 1. Capture & Reproduce
- Collect the exact symptom: error message, stack trace, wrong vs. expected output, exit code, screenshot, logs.
- Record the environment: OS, runtime/language version, dependency versions, config, env vars, data, concurrency, time/locale.
- Build a **minimal reliable reproduction** — the smallest command/input that triggers the bug. Note how often it fails (100%? 1 in 20?).
- If it is intermittent, quantify the rate and try to raise it (loop it, add load, shrink timeouts) before proceeding. See `references/intermittent-bugs.md`.
- **Gate:** Do not continue until you can trigger the bug on demand (or have a measured failure rate). Write the repro down.

### 2. Isolate
- Shrink the surface area. Remove inputs, disable features, stub dependencies until the bug still reproduces with the least machinery. (Delta-debugging mindset.)
- Establish the boundary: which layer/module/function is the last place behavior is correct, and the first place it is wrong?
- Add observation points (logging, breakpoints, assertions, `print` of invariants) — observe, don't fix.

### 3. Hypothesize
- State a single, **falsifiable** hypothesis: "The crash happens because `users` is `None` when the cache misses." A good hypothesis predicts an observation you haven't made yet.
- Rank candidate hypotheses by likelihood × cheapness-to-test. Test the cheapest discriminating one first.
- For each, write the prediction *before* you run the experiment. See `references/hypothesis-log.md` for the format and use `templates/investigation-log.md` to track them.

### 4. Experiment / Bisect
- Run the smallest experiment that confirms or refutes the hypothesis. One variable per experiment.
- If a regression ("worked before"), use `git bisect` to find the offending commit. Run `scripts/git_bisect_helper.sh` to automate it with a test command.
- Update the log with the actual result. Refuted hypotheses are progress — they shrink the search space.

### 5. Diagnose Root Cause
- Confirm you can *explain the full causal chain* from root cause to symptom. If there's a gap ("and then somehow..."), you're not done.
- Distinguish the **root cause** from **contributing factors** and the **trigger**. Ask "why" until you reach something actionable (see 5-Whys in `references/root-cause-frameworks.md`).

### 6. Fix & Verify
- Fix the root cause, not the symptom. Prefer the narrowest correct change.
- **Verify:** run the original repro — it must now pass. Then run it the way that previously failed (loop the flaky case, original environment, original data).
- **Regression-guard:** add a test that fails without the fix and passes with it. This is non-negotiable for a real bug.
- Check for siblings: the same root cause often manifests elsewhere. Search the codebase for the same pattern.

### 7. Document
- Record root cause, fix, and how it was verified. Note any latent issues found. Use `templates/investigation-log.md`.

## Decision Framework: which technique by symptom

| Symptom | First move | Key reference |
|---|---|---|
| Consistent crash / exception | Read the full stack trace bottom-up; find the deepest frame in *your* code | `references/techniques.md` |
| "Worked before this change" | `git bisect` | `scripts/git_bisect_helper.sh` |
| Flaky / 1-in-N failure | Raise failure rate, look for shared state / ordering / time / concurrency | `references/intermittent-bugs.md` |
| Wrong output, no error | Binary-search the data pipeline; assert invariants at each stage | `references/techniques.md` |
| Hang / deadlock | Get a thread dump / `py-spy dump`; find who holds what lock | `references/techniques.md` |
| Memory growth | Snapshot heap over time; diff allocations; check unbounded caches/listeners | `references/techniques.md` |
| Works on my machine | Diff the two environments systematically (versions, config, data, locale, TZ) | `references/techniques.md` |
| Performance regression | Profile, don't guess; compare flamegraphs before/after | `references/techniques.md` |

## Best Practices
- **Change one thing at a time.** Multiple simultaneous changes destroy your ability to attribute cause.
- **Write the prediction before the experiment.** Forces honesty and prevents post-hoc rationalization.
- **Trust observations over intuition.** When the data contradicts your mental model, the model is wrong.
- **Read the actual error.** Most "mysterious" bugs are explained in a log line nobody read fully.
- **Keep the repro fast.** Tighten the loop; a 2-second repro lets you run 100 experiments, a 5-minute one lets you run 6.
- **Version-control your investigation.** Commit experimental changes on a scratch branch so you can revert cleanly.
- **Binary search everything** — commits, inputs, config, time ranges. It turns linear searches into logarithmic ones.

## Common Pitfalls
- **Fixing the symptom:** wrapping a `null` in a guard without asking why it was `null`. The real bug moves downstream.
- **Confirmation bias:** running only experiments that support your favorite theory. Design experiments that could *refute* it.
- **Premature fixing:** editing code before you can reproduce. You'll never know if it worked.
- **Heisenbug denial:** adding logging makes it disappear → that's a *clue* (timing/race), not bad luck.
- **Skipping the regression test:** the bug will return and nobody will know it regressed.
- **Tunnel vision on recent changes:** the trigger may be new code, but the root cause can be old latent code newly exercised.
- **Ignoring "it can't be that":** the bug *is* in the place you're sure is correct. That's why you haven't found it.

## Bundled Resources
- `references/techniques.md` — detailed per-symptom techniques, tooling, and language-specific tips.
- `references/intermittent-bugs.md` — playbook for flaky tests, races, and heisenbugs.
- `references/root-cause-frameworks.md` — 5 Whys, fault trees, delta debugging, and the scientific method applied to code.
- `references/hypothesis-log.md` — how to write and rank falsifiable hypotheses.
- `scripts/git_bisect_helper.sh` — automated `git bisect run` wrapper for regression hunting.
- `templates/investigation-log.md` — fill-in template to track a debugging session end to end.
- `examples/null-pointer-investigation.md` — a full worked example from report to verified fix.
