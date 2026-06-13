---
name: performance-profiler
license: MIT
description: >-
  Systematically finds and fixes performance bottlenecks by measuring first,
  profiling hot paths, reducing algorithmic and I/O cost, and verifying gains
  with before/after benchmarks. Use this skill when code, an endpoint, a page,
  a query, or a job is "slow", "laggy", "timing out", "using too much CPU/memory",
  or "doesn't scale"; when asked to optimize, speed up, profile, or benchmark
  something; when chasing high latency / low throughput, p99 spikes, memory
  leaks, N+1 queries, or excessive allocations; or before/after a perf-sensitive
  change to prove it actually helped. Covers Python, Node/JS, Go, Java, SQL,
  and HTTP/web frontends.
---

# Performance Profiler

## Overview

Make slow things fast — correctly and provably. This skill enforces a
measure-driven loop: never optimize on a hunch, always profile to find the real
hot path, fix the biggest contributor first, then re-measure to confirm the win
and guard against regressions.

Keywords: performance, profiling, optimization, bottleneck, latency, throughput,
p99, slow, benchmark, flamegraph, CPU profile, memory leak, allocations, N+1
query, caching, big-O, complexity, hot path, regression.

The cardinal rule: **measure first**. Most "obvious" optimizations target the
wrong code. Profilers routinely show that 90% of time sits in a place nobody
suspected.

## Workflow

Follow this loop. Do not skip steps — especially step 1 and step 6.

1. **Define the goal and a metric.** Pick ONE primary metric and a target:
   wall-clock latency (p50/p95/p99), throughput (req/s, rows/s), CPU time,
   peak memory (RSS), or allocations. Write down the current value and the
   target. "Make it faster" is not a goal; "cut p95 from 800ms to under 200ms"
   is.

2. **Reproduce reliably.** Build a repeatable scenario with representative data
   volume. A bottleneck at 10 rows may vanish at 10M and vice-versa. Disable
   noise: warm caches, JIT warmup, fixed input, quiet machine, multiple runs.

3. **Measure the baseline.** Time/benchmark the whole operation before touching
   anything. Save the numbers. Use `scripts/bench.py` for a quick statistically
   sane wall-clock benchmark of a Python callable or shell command.

4. **Profile to find the hot path.** Use a real profiler (not scattered print
   timers) to attribute cost. Find the function/line/query consuming the most
   time or memory. See `references/profiling-tools.md` for the right tool per
   language and how to read its output.

5. **Diagnose and fix the top contributor.** Apply the cheapest effective fix
   from the optimization hierarchy (see below). Change ONE thing at a time so
   each change's impact is attributable.

6. **Re-measure and verify.** Re-run the exact baseline benchmark. Confirm the
   metric improved and correctness is unchanged. Quantify: "p95 800ms → 180ms,
   -77%". If no improvement, revert and re-profile.

7. **Repeat or stop.** Return to step 4 for the next hot path, or stop when the
   target is met. Add a regression guard (a benchmark assertion or CI check) so
   the win doesn't rot.

## Optimization hierarchy

Apply fixes in this order — cheapest/highest-leverage first. Most wins come from
the top three.

1. **Do less work.** Remove redundant computation, dead code, needless copies,
   logging in hot loops. Cache or memoize pure, repeated results. Hoist
   invariants out of loops. Compute lazily / short-circuit.
2. **Reduce algorithmic complexity.** Replace O(n²) with O(n log n) or O(n):
   use a hash set/map for membership and lookups, sort once instead of
   repeatedly scanning, use the right data structure. See
   `references/complexity-cheatsheet.md`.
3. **Fix I/O and data access.** Batch round-trips, eliminate N+1 queries, add
   the right index, select only needed columns, stream instead of buffering,
   use connection pooling, paginate. I/O usually dwarfs CPU.
4. **Parallelize / concurrency.** Overlap independent I/O (async), use a worker
   pool for CPU-bound work, vectorize (NumPy/SIMD). Only after single-thread
   work is minimized — parallelizing a bad algorithm just burns more cores.
5. **Reduce allocations / memory pressure.** Reuse buffers, avoid intermediate
   collections, use generators/iterators, pick compact representations, cut GC
   churn.
6. **Lower-level / micro-optimizations.** Compiled extensions, better serializer,
   tuned runtime flags, JIT-friendly code. Last resort — small payoff, high
   maintenance cost.

## Decision framework

- **CPU-bound vs I/O-bound first.** If wall time >> CPU time, you are waiting on
  I/O (disk, network, DB, locks) — chase step 3/4, not micro-CPU tuning. If wall
  time ≈ CPU time, attack the algorithm (step 1/2).
- **Latency vs throughput.** Caching and batching help throughput; they may not
  help a single cold request's latency. Optimize for the metric you committed to.
- **Tail vs average.** p99 spikes are usually GC pauses, lock contention, cold
  caches, or a slow dependency — not the average path. Profile the slow requests
  specifically.
- **Amdahl's law.** Speeding a section that's 5% of runtime can yield at most a
  5% gain. Always spend effort proportional to a section's share of total cost.

## Best Practices

- Profile in a configuration that resembles production (data size, build flags,
  release/optimized mode — never profile a debug build and extrapolate).
- Change one variable per measurement; keep a running log of (change → metric).
- Run benchmarks multiple times; report median and spread, not a single run.
- Keep correctness tests green throughout — a fast wrong answer is worthless.
- Commit the baseline numbers and the proof of improvement alongside the change.
- Prefer eliminating work over doing the same work faster.
- Add a regression benchmark to CI for anything you fought hard to speed up.

## Common Pitfalls

- **Optimizing without profiling** — fixing code that isn't the bottleneck.
- **Premature optimization** — complicating code for gains the user never feels.
- **Micro-benchmark lies** — measuring a case the optimizer elides, or one with
  unrepresentative data/caching, then shipping a non-win.
- **Benchmarking debug builds** or with profiler overhead included.
- **Single-run conclusions** — noise mistaken for signal.
- **Premature parallelism** — adding threads/async over an O(n²) core.
- **Cache without invalidation strategy** — turns a speed bug into a correctness bug.
- **Ignoring the tail** — celebrating a better mean while p99 still times out.

## Supporting files

- `references/profiling-tools.md` — per-language profiler commands (Python,
  Node/JS, Go, Java, SQL, web/browser), what each measures, and how to read
  flamegraphs and call trees.
- `references/complexity-cheatsheet.md` — big-O of common operations and data
  structures, plus the canonical "swap this for that" optimization patterns
  (N+1 fix, set-membership, memoization, batching).
- `scripts/bench.py` — runnable benchmark harness: times a Python expression or
  a shell command over N runs and reports min/median/mean/stdev with a clean
  comparison mode for before/after.
- `examples/optimize-n-plus-one.md` — full worked example taking a slow endpoint
  from 1.9s to 60ms through the whole loop (measure → profile → fix → verify).
