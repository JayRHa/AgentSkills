# Estimation

Good plans separate **effort** from **duration** and quantify **uncertainty**.

## Effort vs Duration
- **Effort** = person-hours of actual work (e.g., 24 person-hours).
- **Duration** = calendar time from start to finish (e.g., 5 days).

```
duration = effort / (assigned_people * available_hours_per_day)
```
then inflate for: dependencies/wait time, context switching, meetings, and review cycles. A common reality check: a person delivers only ~5–6 focused hours of project work per 8-hour day.

Do NOT add parallel people to a task whose work cannot be parallelized (Brooks's Law). Two people rarely halve a one-person task.

## Three-point PERT estimates
For every non-trivial leaf, estimate three values:
- **O** = Optimistic (everything goes right)
- **M** = Most likely (normal conditions)
- **P** = Pessimistic (realistic worst case)

Expected effort (Beta-PERT):
```
te = (O + 4M + P) / 6
```
Standard deviation (uncertainty):
```
sd = (P - O) / 6
```
Use `sd` to spot risky tasks (wide O↔P spread = high uncertainty → consider a spike to reduce it).

For the whole project, expected duration ≈ sum of `te` along the critical path; variance ≈ sum of `sd^2` of critical-path tasks (so project sd = sqrt of that sum). A ~90% confident estimate ≈ `mean + 1.3 * project_sd`.

## Story points (relative estimation)
For teams that estimate relatively rather than in hours:
- Use a bounded scale (e.g., 1, 2, 3, 5, 8, 13). Anything > 13 must be split.
- Points capture size+complexity+uncertainty, not hours.
- Convert to duration via empirical **velocity** (points completed per iteration). Don't fabricate velocity; measure it.

## Calibration and anti-bias
- **Planning fallacy**: people systematically underestimate. Counter with reference-class forecasting — compare to how long *similar past work* actually took, not how long you hope.
- **Anchoring**: estimate before quoting any number out loud or seeing a deadline.
- **Unknowns**: if you can't estimate it, it's too big or too unclear — decompose or spike it.
- **Buffer at the project, not the task**: pad every task and slack disappears (Parkinson's Law: work expands to fill the time). Instead apply one project-level contingency buffer (commonly 15–30%, higher for novel work) on the critical path.

## Estimate table format
| WBS | Task | O | M | P | te | sd | Owner |
|-----|------|---|---|---|----|----|-------|
| 1.3.2 | Implement pages | 16 | 24 | 40 | 25.3 | 4.0 | Dev |

`te = (16 + 4*24 + 40)/6 = 25.3h`, `sd = (40-16)/6 = 4.0h`.
