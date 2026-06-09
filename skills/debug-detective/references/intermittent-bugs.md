# Playbook: Intermittent Bugs, Flaky Tests & Heisenbugs

Intermittent bugs feel like luck. They aren't. They are deterministic at the level you haven't observed yet (timing, ordering, hidden state). Your job is to make the hidden variable visible.

## Step 1 — Quantify the failure rate
A bug that fails "sometimes" must be turned into a number. Loop it:
```sh
fail=0; total=200
for i in $(seq $total); do
  <run-the-test> >/dev/null 2>&1 || fail=$((fail+1))
done
echo "$fail / $total failed"
```
Now you have a baseline. Every change is judged against this rate (need enough runs for significance — a 1/50 bug needs hundreds of runs to trust a "fix").

## Step 2 — Amplify the failure
Make it fail *more often* so experiments are fast:
- **Add concurrency / load**: run the test in parallel, add competing threads.
- **Shrink timeouts and sleeps**: tighter timing exposes races.
- **Randomize ordering**: shuffle test order (`pytest-randomly`, `go test -shuffle`); flakiness that depends on order reveals shared state.
- **Stress the scheduler**: `stress-ng`, CPU pinning, or run on a busy machine.
- **Inject delays** at suspected race points (`sleep`/`yield`) to widen the window.

## Step 3 — Find the hidden variable
Flaky causes, in rough order of frequency:

| Cause | Tell-tale sign | Probe |
|---|---|---|
| Test order / shared state | Fails only in certain order, passes in isolation | Run the one test alone vs. in suite; shuffle order |
| Race condition / data race | Fails under load, more cores → more failures | Thread sanitizer (`-race`, TSan); add logging w/ thread id |
| Time/date dependence | Fails near midnight, month/year boundaries, DST | Freeze time (`freezegun`, fake clock); set `TZ` |
| Unseeded randomness | Different each run | Set/seed RNG; log the seed; replay with it |
| Network / external service | Fails when slow/offline | Mock the dependency; add timeout + retry visibility |
| Resource exhaustion | Fails after many runs (leak) | Watch fds/memory across runs |
| Floating-point / hash order | Tiny diffs, set/dict iteration order | Sort before compare; set `PYTHONHASHSEED` |
| Uninitialized memory (native) | Garbage values vary | ASan/MSan/Valgrind |

## Step 4 — The heisenbug rule
If adding logging, a debugger, or a `sleep` makes the bug **disappear or change**, that is *evidence*, not frustration: you've perturbed timing → it's almost certainly a **race condition or timing dependency**. Pivot immediately to concurrency tools (sanitizers, lock-ordering analysis) instead of more printf.

## Step 5 — Capture a failing run
Because it's rare, instrument so that *when* it fails you have everything:
- Log the RNG seed, thread interleaving, timestamps, and relevant state on every run; keep only the failing artifacts.
- Use record-and-replay (`rr` on Linux) to capture one failure, then replay deterministically forever and step backward to the cause.
- Run under a sanitizer so the failing run produces a precise report, not a vague flake.

## Step 6 — Verify the fix honestly
A flaky fix can't be verified by one green run. Re-run the **amplified** loop enough times that the original failure rate would have surfaced many times over (e.g., if it was 1/20, run 500+). Only then claim it fixed.

## Anti-patterns
- Adding `retry` to a flaky test to make CI green — this hides a real concurrency/timing bug.
- Adding `sleep(2)` to "fix" a race — it reduces the rate, doesn't eliminate it, and rots over time. Synchronize on the actual condition instead.
- Marking the test `@skip`/`@flaky` and moving on without a tracking issue.
