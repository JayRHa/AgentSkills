# Dependencies and the Critical Path

## Dependency types
Default and most common is Finish-to-Start.
- **FS (Finish-to-Start)**: B can't start until A finishes. (Most common.)
- **SS (Start-to-Start)**: B can't start until A starts.
- **FF (Finish-to-Finish)**: B can't finish until A finishes.
- **SF (Start-to-Finish)**: B can't finish until A starts. (Rare.)

Lead/lag can modify a link (e.g., FS + 2d lag = wait 2 days after A finishes; SS − 1d lead = B can start 1 day after A starts).

## Hard vs soft dependencies
- **Hard (mandatory)**: physics/logic require it (can't deploy before you build).
- **Soft (discretionary)**: a preference or convention. Challenge soft dependencies — removing them enables parallelism and shortens the schedule.
- **External**: depends on a third party (vendor, approval, delivery). Track explicitly; these are common delay sources.

## Building the network
Model tasks as nodes with `duration` and `predecessors` (Activity-on-Node). Avoid cycles — a dependency cycle means the plan is impossible and must be re-modeled.

## Forward pass (earliest times)
Process tasks in topological order:
```
ES(task) = max(EF of all predecessors)   # 0 if no predecessors
EF(task) = ES(task) + duration(task)
```
Project duration = max EF across all tasks.

## Backward pass (latest times)
Process in reverse topological order:
```
LF(task) = min(LS of all successors)      # project_duration if no successors
LS(task) = LF(task) - duration(task)
```

## Slack (float) and the critical path
```
total_slack = LS - ES   (equivalently LF - EF)
```
- **Critical path** = the chain of tasks with **zero total slack**. It is the longest path through the network and equals the minimum possible project duration.
- Tasks with slack > 0 can shift without affecting the end date — that's where flexibility lives.
- A project can have more than one critical path.

## Compressing the schedule
When the critical path is too long:
- **Fast-tracking**: run critical tasks in parallel that were planned sequentially (convert FS → SS where safe). Adds risk/rework, no extra cost.
- **Crashing**: add resources to critical tasks to shorten them. Adds cost; watch Brooks's Law.
- Only compress tasks **on** the critical path — speeding up non-critical tasks doesn't move the deadline.
- After any compression, recompute — the critical path may shift to a different chain.

## Worked mini-example
Tasks: A(3) → C(2); B(2) → C; C → D(4).
- Forward: ES/EF — A 0/3, B 0/2, C 3/5 (waits for A), D 5/9. Project = 9.
- Backward: D 5/9, C 3/5, A 0/3, B LF=3 so LS=1.
- Slack: A=0, C=0, D=0 (critical), B = 1 (one day of float).
- Critical path: A → C → D, length 9.

Use `scripts/critical_path.py` to compute this for any task list.
