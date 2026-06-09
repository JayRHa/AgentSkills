# Profiling Tools by Language

Pick a tool that attributes cost to code. Avoid eyeballing scattered timers for
anything non-trivial — they bias you toward what you already suspect.

Two profiler families:
- **Deterministic / instrumenting** (e.g. cProfile): exact call counts, higher
  overhead, can distort timing of tiny functions.
- **Sampling / statistical** (e.g. py-spy, perf, async-profiler): low overhead,
  production-safe, great for finding hot paths via flamegraphs.

Use a sampling profiler to find the hot path; use timing/benchmarks to verify.

---

## Python

### Wall-clock & micro-benchmarks
```bash
python -m timeit -n 1000 -r 5 "sum(range(1000))"      # tiny snippets
python -X importtime app.py 2>importtime.log           # slow startup/imports
```

### Deterministic profile (function-level)
```bash
python -m cProfile -s cumtime app.py            # sort by cumulative time
python -m cProfile -o prof.out app.py           # save for analysis
python -c "import pstats; pstats.Stats('prof.out').sort_stats('tottime').print_stats(20)"
```
- `tottime`: time in the function itself (the hot code).
- `cumtime`: time including callees (find the expensive call tree).

### Line-level
```bash
pip install line_profiler
kernprof -l -v script.py     # decorate target funcs with @profile
```

### Sampling profiler (low overhead, flamegraphs, prod-safe)
```bash
pip install py-spy
py-spy record -o flame.svg --pid <PID>      # attach to running process
py-spy record -o flame.svg -- python app.py # launch and record
py-spy top --pid <PID>                       # live top-like view
py-spy dump --pid <PID>                       # stack of a hung process
```

### Memory
```bash
python -m tracemalloc ...                     # stdlib snapshots / top allocators
pip install memray && memray run app.py && memray flamegraph memray-*.bin
```

---

## Node.js / JavaScript

### CPU profile
```bash
node --prof app.js                            # writes isolate-*.log
node --prof-process isolate-*.log > profile.txt
node --cpu-prof --cpu-prof-dir=./prof app.js  # .cpuprofile for Chrome DevTools
```
Load the `.cpuprofile` in Chrome DevTools > Performance for a flame chart.

### Live / sampling
```bash
node --inspect app.js          # chrome://inspect -> Profiler tab
clinic flame -- node app.js     # npm i -g clinic ; flamegraph
clinic doctor -- node app.js    # diagnoses event-loop / GC / I/O issues
0x app.js                       # npm i -g 0x ; quick flamegraph
```

### Memory / leaks
- DevTools > Memory > Heap snapshot; take two snapshots and compare retained size.
- `node --inspect` then `--expose-gc` to force GC between snapshots.
- Watch for the event loop being blocked (`clinic doctor`).

### Browser / web frontend
- Chrome DevTools **Performance** panel: record, look for long tasks (>50ms),
  layout thrash (purple), scripting (yellow), painting (green).
- **Lighthouse** for Core Web Vitals (LCP, CLS, INP).
- **Coverage** tab for unused JS/CSS. **Network** tab for waterfall & payload size.
- Key levers: reduce bundle size, defer/lazy-load, cache, avoid synchronous
  layout reads after writes, debounce/throttle handlers.

---

## Go

```go
import _ "net/http/pprof"   // exposes /debug/pprof on your HTTP server
```
```bash
go test -bench=. -benchmem -cpuprofile cpu.out -memprofile mem.out
go tool pprof -http=:8080 cpu.out          # interactive flamegraph in browser
go tool pprof cpu.out                       # then: top, list <func>, web
go tool pprof http://localhost:6060/debug/pprof/profile?seconds=30
go test -bench=. -benchmem                  # ns/op, B/op, allocs/op
```
- `top`: hottest functions. `list <Func>`: line-level cost. `web`: call graph.
- `-benchmem` exposes allocations — often the real Go bottleneck (GC pressure).

---

## Java / JVM

```bash
# async-profiler (low overhead, flamegraphs)
./profiler.sh -d 30 -f flame.html <PID>      # CPU
./profiler.sh -e alloc -d 30 -f alloc.html <PID>   # allocations
```
- **JFR (Java Flight Recorder):** `-XX:StartFlightRecording=duration=60s,filename=rec.jfr`
  then open in JDK Mission Control.
- Watch GC logs (`-Xlog:gc*`) for pause times driving p99.
- `jstack <PID>` for thread dumps to find lock contention / blocked threads.

---

## SQL / Databases

The single highest-leverage profiling target for most apps.

### Postgres
```sql
EXPLAIN (ANALYZE, BUFFERS, FORMAT TEXT) SELECT ...;  -- real timing + I/O
```
Read bottom-up. Red flags: `Seq Scan` on large tables, high `rows` estimates,
`Nested Loop` over big sets, sorts spilling to disk, mismatched estimated vs
actual rows (stale stats — run `ANALYZE`).
```sql
-- find slow queries (needs pg_stat_statements)
SELECT query, calls, mean_exec_time, total_exec_time
FROM pg_stat_statements ORDER BY total_exec_time DESC LIMIT 20;
```

### MySQL
```sql
EXPLAIN ANALYZE SELECT ...;
SET profiling = 1; SELECT ...; SHOW PROFILES;
```
Use the slow query log; look for `type: ALL` (full scan) and missing keys.

### Application ORM
- Log every SQL statement in a request to spot **N+1** (same query in a loop).
- Tools: Django Debug Toolbar, `EXPLAIN` via the ORM, Rails `bullet` gem,
  SQLAlchemy `echo=True`.

---

## Reading a flamegraph

- **X-axis = share of samples (cost), NOT time order.** Width = how much total
  time. Wider frame = more expensive.
- **Y-axis = stack depth.** Top frame is what was actually running.
- Look for the **widest top-of-stack plateaus** — that's your hot path.
- Wide frames near the bottom that narrow upward = cost spread across callees;
  optimize the caller's strategy, not one leaf.
- A single dominant tall+wide tower = one clear bottleneck (good news).

## Reading a cProfile/pstats table

- Sort by `tottime` to find the function burning CPU in its own body.
- Sort by `cumtime` to find the expensive subtree / entry point.
- High `ncalls` with small per-call time = called too often → cache or hoist.
