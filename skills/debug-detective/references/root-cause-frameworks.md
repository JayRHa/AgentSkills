# Root-Cause Frameworks

Structured ways to drive from symptom to true cause. Use whichever fits; they compose.

## The Scientific Method (the backbone)
1. **Observe** — gather facts about the failure (no interpretation yet).
2. **Question** — what specifically is wrong vs. expected?
3. **Hypothesize** — propose a *falsifiable* cause that predicts an observation.
4. **Predict** — "if this is true, then experiment X will show Y." Write it down first.
5. **Experiment** — run the smallest test that distinguishes true/false. One variable.
6. **Conclude** — accept, refine, or reject. Refuted hypotheses shrink the space — that's progress.
Loop until the cause explains every observation with no gaps.

## 5 Whys
Ask "why?" repeatedly until you reach an actionable root, not a restated symptom.
> Symptom: API returned 500.
> 1. Why? Unhandled `NullPointerException` in `OrderService`.
> 2. Why was it null? `customer` came back null from the repository.
> 3. Why null? The query matched no row for that id.
> 4. Why no row? The id was a *soft-deleted* customer, filtered by a default scope.
> 5. Why did we look it up at all? Checkout doesn't validate customer status before pricing.
> **Root cause:** missing customer-status precondition in checkout (not "add a null check").
Stop when the next "why" leaves your system's control.

## Delta Debugging (minimize the difference)
Find the minimal change between a passing and a failing case.
- **Minimize input**: repeatedly cut the failing input in half; keep whichever half still fails. Converge on the smallest triggering input.
- **Minimize change set**: between a good and bad version, bisect the diff (commits, config lines, feature flags) to the single responsible delta. `git bisect` is delta debugging over history.
- **Minimize environment**: toggle one env/config variable at a time between the working and broken environments.

## Fault Tree (top-down decomposition)
Start at the symptom as the root; branch into all possible immediate causes; recurse. Prune branches you can disprove cheaply. What remains is your candidate set, ranked by likelihood.

## Differential diagnosis (compare two worlds)
When something works in world A but not world B (machine, branch, user, time), enumerate every difference and eliminate them one by one. The bug lives in a difference you haven't checked. Make the list exhaustive — the cause is often the difference you assumed was irrelevant.

## Distinguishing cause levels
- **Root cause**: the defect that, if removed, prevents the bug. Fix this.
- **Trigger**: the condition that exercised the defect (a specific input, load, timing). Useful for the repro and regression test.
- **Contributing factor**: makes it worse/more likely but isn't the defect (e.g., missing timeout amplifies a slow query). Worth noting; sometimes worth fixing too.
A correct fix targets the root cause and a good regression test reproduces the trigger.
