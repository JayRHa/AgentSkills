# Debugging Techniques by Symptom

Detailed, actionable techniques. Load this when you've classified the symptom and need concrete moves.

## Reading a stack trace
- Read **bottom-up** for the call chain, but find the **deepest frame inside your own code** — that's usually where to start, not the library frame that finally threw.
- Note the exception *type* and *message* precisely. `KeyError: 'user_id'` is a different bug from `TypeError: 'NoneType' object is not subscriptable`.
- For wrapped/chained exceptions, read the **original** cause (`Caused by:` / `__cause__` / `from err`), not just the outer wrapper.
- Mismatched line numbers? Your running code may differ from source (stale build, wrong file, bytecode cache). Verify what's actually executing.

## Consistent crash / exception
1. Reproduce, capture full trace with locals if possible (`faulthandler`, `--showlocals`, debugger post-mortem `pdb.pm()`).
2. Inspect the state at the failing frame. What value is unexpected, and where did it come from?
3. Walk the data backward to its source. The crash is the *symptom*; the bad value entered the system earlier.

## Wrong output, no error (silent corruption)
- Treat the code as a pipeline: input → A → B → C → output.
- **Binary search the pipeline:** assert the expected invariant at the midpoint. If correct there, bug is downstream; if wrong, upstream. Repeat.
- Add assertions for invariants (sorted? non-negative? sums to total? no duplicates?) rather than eyeballing dumps.
- Compare against a known-good reference output (golden file) and diff.

## Hang / deadlock / infinite loop
- Get a snapshot of all threads/stacks while it's stuck:
  - Python: `py-spy dump --pid <pid>` or send `SIGQUIT` with faulthandler.
  - JVM: `jstack <pid>` or `kill -3 <pid>`.
  - Go: `SIGQUIT` prints all goroutine stacks; or `pprof`.
  - Native: `gdb -p <pid>` then `thread apply all bt`.
- Deadlock: identify the lock-acquisition order across threads; a cycle (A waits on B's lock, B on A's) is the smoking gun. Fix by enforcing a global lock ordering.
- Infinite loop: check the loop's termination condition and whether the variable that should converge actually changes each iteration.

## Memory growth / leak
- Confirm it's unbounded: plot RSS / heap over time under steady load. Sawtooth that returns to baseline = GC working; monotonic climb = leak.
- Snapshot the heap at two times and diff object counts by type (Python: `tracemalloc`, `objgraph`; JVM: heap dump + Eclipse MAT; Node: `--inspect` + Chrome heap snapshots).
- Usual suspects: unbounded caches/dicts, event listeners never removed, growing lists in module globals, closures capturing large objects, connection/file handles not closed.

## Works on my machine / environment-dependent
Diff the two environments **systematically**, top of stack to bottom:
- Runtime/language version (`python --version`, `node -v`, `java -version`).
- Dependency versions — diff lockfiles (`pip freeze`, `npm ls`, `go list -m all`).
- OS and arch (line endings CRLF/LF, path separators, case-sensitive FS).
- Locale, timezone, encoding (`LANG`, `TZ`) — a top cause of date/number/sort bugs.
- Config and env vars actually loaded at runtime (print them; don't assume).
- Data: is the failing input present in both? Often the bug is the *data*, not the code.
- Build artifacts: clean build on both. Stale caches lie.

## Performance regression
- **Measure, never guess.** Profile with a real profiler (`perf`, `py-spy`, `pprof`, async-profiler, Chrome DevTools).
- Capture a flamegraph before and after the suspected change; the widened frame is your culprit.
- Check for: accidental O(n^2) (nested loop over growing data), N+1 queries, lost caching/memoization, regex catastrophic backtracking, excessive allocation/GC pressure, synchronous I/O in a hot path.

## Observation tools (prefer over print where available)
- **Conditional breakpoints / watchpoints**: break only when `x > 1000` or stop when a variable *changes* (data breakpoint).
- **Logging with context**: include the correlating id (request id, pid, thread, iteration) so you can reconstruct ordering.
- **Tracing**: distributed tracing or `strace`/`dtrace`/`ltrace` to see syscalls and external calls.
- **rr / time-travel debugging** (Linux): record once, replay deterministically, step backward from the crash. Gold for heisenbugs.
- **Assertions**: encode invariants in code; they turn silent corruption into a loud, located failure.

## Language-specific quick tips
- **Python**: `python -X dev`, `-W error` to surface warnings; `breakpoint()`; `pytest -x -q --lf --pdb`; `tracemalloc` for memory.
- **JS/Node**: `--trace-warnings`, `--inspect-brk`; check `==` vs `===`; floating point; async ordering; unhandled promise rejections.
- **Go**: `-race` detector for data races; `dlv` debugger; `GODEBUG`.
- **Java/JVM**: `-ea` to enable assertions; `jstack`/`jmap`; remote debug on a port.
- **C/C++**: ASan/UBSan/TSan/Valgrind — undefined behavior and races become deterministic crashes with locations.
