#!/usr/bin/env python3
"""bench.py - a small, statistically sane benchmark harness.

Times a Python expression or a shell command over N runs and reports
min / median / mean / stdev wall-clock time. Supports an A/B compare mode
to prove a before/after optimization actually helped.

Usage:
  # Benchmark a Python expression (optionally with --setup run once per measured call)
  python bench.py --py "sum(range(100000))"
  python bench.py --py "f(data)" --setup "from mod import f; data=list(range(10000))" -n 50

  # Benchmark a shell command
  python bench.py --cmd "./build/app --input big.json" -n 20 --warmup 3

  # Compare two variants (A = baseline, B = optimized); prints speedup
  python bench.py --compare \
      --py "slow(data)" \
      --py-b "fast(data)" \
      --setup "from mod import slow, fast; data=list(range(10000))" -n 50

Notes:
  * Uses time.perf_counter for Python and wall-clock for shell commands.
  * --warmup runs are executed and discarded (JIT/cache warmup).
  * Exit code is non-zero if a shell command fails.
  * Pure stdlib. Python 3.8+.
"""
import argparse
import shlex
import statistics
import subprocess
import sys
import time
from typing import Callable, List


def _fmt(seconds: float) -> str:
    if seconds < 1e-6:
        return f"{seconds * 1e9:.1f} ns"
    if seconds < 1e-3:
        return f"{seconds * 1e6:.1f} us"
    if seconds < 1.0:
        return f"{seconds * 1e3:.2f} ms"
    return f"{seconds:.3f} s"


def time_runs(fn: Callable[[], None], n: int, warmup: int) -> List[float]:
    for _ in range(warmup):
        fn()
    samples: List[float] = []
    for _ in range(n):
        start = time.perf_counter()
        fn()
        samples.append(time.perf_counter() - start)
    return samples


def make_py_runner(expr: str, setup: str) -> Callable[[], None]:
    ns: dict = {}
    if setup:
        exec(compile(setup, "<setup>", "exec"), ns)
    code = compile(expr, "<expr>", "exec")

    def run() -> None:
        exec(code, ns)

    return run


def make_cmd_runner(cmd: str) -> Callable[[], None]:
    argv = shlex.split(cmd)

    def run() -> None:
        proc = subprocess.run(argv, stdout=subprocess.DEVNULL,
                              stderr=subprocess.DEVNULL)
        if proc.returncode != 0:
            raise RuntimeError(
                f"command failed (exit {proc.returncode}): {cmd}")

    return run


def report(label: str, samples: List[float]) -> float:
    median = statistics.median(samples)
    mean = statistics.mean(samples)
    stdev = statistics.stdev(samples) if len(samples) > 1 else 0.0
    print(f"  {label}")
    print(f"    runs   : {len(samples)}")
    print(f"    min    : {_fmt(min(samples))}")
    print(f"    median : {_fmt(median)}")
    print(f"    mean   : {_fmt(mean)}  (stdev {_fmt(stdev)})")
    print(f"    max    : {_fmt(max(samples))}")
    return median


def build_runner(py: str, cmd: str, setup: str) -> Callable[[], None]:
    if py:
        return make_py_runner(py, setup)
    if cmd:
        return make_cmd_runner(cmd)
    raise SystemExit("error: provide --py or --cmd")


def main(argv: List[str]) -> int:
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--py", help="Python expression/statement to benchmark (variant A)")
    p.add_argument("--cmd", help="Shell command to benchmark (variant A)")
    p.add_argument("--py-b", dest="py_b", help="Variant B Python expr (compare mode)")
    p.add_argument("--cmd-b", dest="cmd_b", help="Variant B shell command (compare mode)")
    p.add_argument("--setup", default="", help="Python setup run once (shared by A and B)")
    p.add_argument("-n", "--runs", type=int, default=20, help="measured runs (default 20)")
    p.add_argument("--warmup", type=int, default=3, help="discarded warmup runs (default 3)")
    p.add_argument("--compare", action="store_true", help="A/B compare mode")
    args = p.parse_args(argv)

    if args.runs < 1:
        raise SystemExit("error: --runs must be >= 1")

    runner_a = build_runner(args.py, args.cmd, args.setup)
    print("baseline (A):")
    samples_a = time_runs(runner_a, args.runs, args.warmup)
    median_a = report("A", samples_a)

    if not args.compare:
        return 0

    if not (args.py_b or args.cmd_b):
        raise SystemExit("error: --compare needs --py-b or --cmd-b")
    runner_b = build_runner(args.py_b, args.cmd_b, args.setup)
    print("optimized (B):")
    samples_b = time_runs(runner_b, args.runs, args.warmup)
    median_b = report("B", samples_b)

    print("\ncomparison (median):")
    if median_b == 0:
        print("  B is too fast to measure reliably")
        return 0
    speedup = median_a / median_b
    delta = (median_b - median_a) / median_a * 100.0
    verdict = "FASTER" if speedup > 1 else "SLOWER"
    print(f"  A median = {_fmt(median_a)}")
    print(f"  B median = {_fmt(median_b)}")
    print(f"  speedup  = {speedup:.2f}x  ({delta:+.1f}% change)  -> B is {verdict}")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main(sys.argv[1:]))
    except KeyboardInterrupt:
        sys.exit(130)
    except RuntimeError as exc:
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(1)
