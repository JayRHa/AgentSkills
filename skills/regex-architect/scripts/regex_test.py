#!/usr/bin/env python3
"""regex_test.py - Test and ReDoS-probe a regular expression.

Validates a regex against positive (must-match) and negative (must-not-match)
cases, and runs a lightweight catastrophic-backtracking timing probe.

Matching semantics:
  --mode fullmatch (default)  whole-string validation (re.fullmatch)
  --mode search               substring search (re.search)

Usage examples:
  # Validate a ZIP code pattern
  python3 regex_test.py '^\\d{5}(?:-\\d{4})?$' \\
      --match 12345 --match 12345-6789 \\
      --no-match 1234 --no-match abcde --no-match '12345-678'

  # Search mode
  python3 regex_test.py 'ERROR' --mode search --match 'log: ERROR here'

  # ReDoS timing probe (feeds escalating evil strings)
  python3 regex_test.py '^(a+)+$' --redos

  # Read cases from a file (one per line: '+text' must match, '-text' must not)
  python3 regex_test.py '^[0-9]+$' --cases cases.txt

Exit code is non-zero if any case fails or a ReDoS risk is detected.
"""
import argparse
import re
import sys
import time


def compile_pattern(pattern, ignorecase, multiline, verbose, dotall):
    flags = 0
    if ignorecase:
        flags |= re.IGNORECASE
    if multiline:
        flags |= re.MULTILINE
    if verbose:
        flags |= re.VERBOSE
    if dotall:
        flags |= re.DOTALL
    return re.compile(pattern, flags)


def matches(rx, text, mode):
    if mode == "search":
        return rx.search(text) is not None
    return rx.fullmatch(text) is not None


def run_cases(rx, mode, positives, negatives):
    passed = 0
    failed = 0
    print("== Functional tests ==")
    for t in positives:
        ok = matches(rx, t, mode)
        mark = "PASS" if ok else "FAIL"
        if ok:
            passed += 1
        else:
            failed += 1
        print(f"  [{mark}] should MATCH    : {t!r}")
    for t in negatives:
        ok = not matches(rx, t, mode)
        mark = "PASS" if ok else "FAIL"
        if ok:
            passed += 1
        else:
            failed += 1
        print(f"  [{mark}] should NOT match: {t!r}")
    if not positives and not negatives:
        print("  (no functional cases provided)")
    else:
        print(f"  {passed} passed, {failed} failed")
    return failed == 0


def redos_probe(rx, mode, base_char="a", breaker="!", threshold=0.5):
    """Feed escalating 'evil' strings and time matching.

    A safe (linear) pattern stays fast; an exponential pattern's time roughly
    doubles as length grows, exceeding the threshold quickly.
    """
    print("== ReDoS timing probe ==")
    print(f"  Pattern: {rx.pattern!r}")
    risky = False
    timings = []
    for n in range(10, 46, 5):
        evil = base_char * n + breaker
        start = time.perf_counter()
        try:
            matches(rx, evil, mode)
        except Exception as exc:  # noqa: BLE001
            print(f"  n={n:>3}: error {exc!r}")
            continue
        elapsed = time.perf_counter() - start
        timings.append((n, elapsed))
        flag = ""
        if elapsed > threshold:
            flag = "  <-- SLOW (possible catastrophic backtracking)"
            risky = True
        print(f"  n={n:>3}  len={n + 1:>3}  time={elapsed * 1000:8.2f} ms{flag}")
        if elapsed > threshold:
            break
    # Heuristic: super-linear growth between the last two measurements.
    if len(timings) >= 2:
        (n1, t1), (n2, t2) = timings[-2], timings[-1]
        if t1 > 0 and t2 / max(t1, 1e-9) > 3 and t2 > 0.01:
            risky = True
    if risky:
        print("  RESULT: RISK - timing grows super-linearly. Rewrite the pattern.")
        print("          See references/redos-guide.md for safe rewrites.")
    else:
        print("  RESULT: OK - timings stayed fast and roughly linear.")
    return not risky


def load_cases_file(path):
    positives, negatives = [], []
    with open(path, encoding="utf-8") as fh:
        for raw in fh:
            line = raw.rstrip("\n")
            if not line or line.startswith("#"):
                continue
            tag, _, text = line.partition(line[1] if False else "")
            # partition trick avoided; do explicit handling:
            sign = line[0]
            text = line[1:]
            if sign == "+":
                positives.append(text)
            elif sign == "-":
                negatives.append(text)
    return positives, negatives


def main(argv=None):
    p = argparse.ArgumentParser(
        description="Test and ReDoS-probe a regular expression.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    p.add_argument("pattern", help="the regular expression to test")
    p.add_argument("--match", action="append", default=[], metavar="STR",
                   help="a string that should match (repeatable)")
    p.add_argument("--no-match", action="append", default=[], metavar="STR",
                   dest="no_match", help="a string that should NOT match (repeatable)")
    p.add_argument("--cases", metavar="FILE",
                   help="file of cases; lines start with + (match) or - (no match)")
    p.add_argument("--mode", choices=["fullmatch", "search"], default="fullmatch",
                   help="fullmatch=whole-string validation (default); search=substring")
    p.add_argument("-i", "--ignorecase", action="store_true")
    p.add_argument("-m", "--multiline", action="store_true")
    p.add_argument("-x", "--verbose-flag", dest="verbose", action="store_true",
                   help="enable re.VERBOSE (extended) mode")
    p.add_argument("-s", "--dotall", action="store_true")
    p.add_argument("--redos", action="store_true", help="run the ReDoS timing probe")
    p.add_argument("--redos-char", default="a", help="repeated char for evil string")
    p.add_argument("--redos-breaker", default="!", help="trailing char that breaks match")
    args = p.parse_args(argv)

    try:
        rx = compile_pattern(args.pattern, args.ignorecase, args.multiline,
                             args.verbose, args.dotall)
    except re.error as exc:
        print(f"ERROR: invalid pattern: {exc}", file=sys.stderr)
        return 2

    positives = list(args.match)
    negatives = list(args.no_match)
    if args.cases:
        fp, fn = load_cases_file(args.cases)
        positives += fp
        negatives += fn

    ok = True
    if positives or negatives:
        ok = run_cases(rx, args.mode, positives, negatives) and ok
        print()
    if args.redos:
        ok = redos_probe(rx, args.mode, args.redos_char, args.redos_breaker) and ok

    if not positives and not negatives and not args.redos:
        print("Pattern compiled OK. Provide --match/--no-match/--cases or --redos to test.")

    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
