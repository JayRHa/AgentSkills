#!/usr/bin/env python3
"""Heuristic linter for unit-test quality smells.

Scans test files and flags common problems that make test suites weak or
flaky:
  - tests with no assertion (can't fail)
  - skipped / xfail / disabled tests left in
  - focused tests left in (.only / fdescribe / fit / t.Run with FOCUS)
  - sleep-based timing (source of flakiness)
  - real time / random without seeding (datetime.now, Math.random, rand)
  - empty test bodies (pass / {})

This is a heuristic aid, not a substitute for review. It is language-aware
for Python, JS/TS, Go, Java, Ruby, C#, and Rust by file extension.

Usage:
    python check_tests.py PATH [PATH ...]
    python check_tests.py tests/            # recurse a directory
    python check_tests.py --quiet src/      # only print problems

Exit code: 0 if no problems found, 1 otherwise (CI-friendly).
"""
from __future__ import annotations

import argparse
import os
import re
import sys
from dataclasses import dataclass
from typing import Iterable

TEST_EXTS = {".py", ".js", ".jsx", ".ts", ".tsx", ".go", ".java", ".rb", ".cs", ".rs"}

# Patterns that indicate a file is a test file by name.
TEST_NAME_RE = re.compile(r"(test|spec)", re.IGNORECASE)

# An assertion is present if any of these tokens appear.
ASSERT_TOKENS = re.compile(
    r"\b(assert|expect|require\.|t\.Error|t\.Fatal|t\.Errorf|t\.Fatalf|"
    r"should|Should\(|verify\(|assertThat|assertEquals|assertTrue|"
    r"assertThrows|raise_error|to_not|to\b|panic!|assert_eq!|assert_ne!|assert!)",
)

SKIP_RE = re.compile(
    r"(@pytest\.mark\.skip|@pytest\.mark\.xfail|@unittest\.skip|"
    r"\.skip\(|xit\(|xdescribe\(|it\.skip|describe\.skip|test\.skip|"
    r"t\.Skip\(|@Disabled|@Ignore|#\[ignore\]|pending\()",
)

FOCUS_RE = re.compile(
    r"(\.only\(|fdescribe\(|fit\(|fcontext\(|it\.only|describe\.only|test\.only)",
)

SLEEP_RE = re.compile(
    r"(time\.sleep\(|Thread\.sleep\(|setTimeout\(|sleep\(|"
    r"std::thread::sleep|time\.Sleep\(|usleep\()",
)

NONDET_RE = re.compile(
    r"(datetime\.now\(|datetime\.utcnow\(|Date\.now\(|new Date\(\)|"
    r"Math\.random\(|System\.currentTimeMillis|time\.Now\(|rand\.\w+\(|"
    r"Random\(\)|SystemTime::now)",
)


@dataclass
class Finding:
    path: str
    line: int
    code: str
    message: str

    def format(self) -> str:
        return f"{self.path}:{self.line}: [{self.code}] {self.message}"


def iter_files(paths: Iterable[str]) -> Iterable[str]:
    for p in paths:
        if os.path.isdir(p):
            for root, _dirs, files in os.walk(p):
                # Skip common vendor / build dirs.
                if any(seg in root for seg in ("node_modules", ".git", "target", "dist", "build", "vendor")):
                    continue
                for f in files:
                    if os.path.splitext(f)[1] in TEST_EXTS:
                        yield os.path.join(root, f)
        elif os.path.isfile(p):
            yield p


def is_test_file(path: str) -> bool:
    base = os.path.basename(path)
    return bool(TEST_NAME_RE.search(base)) or "__tests__" in path.replace("\\", "/")


def detect_test_func_starts(lines: list[str]) -> list[int]:
    """Return 0-based line indices that look like the start of a test function."""
    starts = []
    func_re = re.compile(
        r"(def\s+test\w*\s*\(|"            # python
        r"func\s+Test\w*\s*\(|"           # go
        r"(it|test)\s*\(\s*[\"'`]|"       # js/ts/ruby
        r"\bfn\s+\w+\s*\(.*\)\s*\{?\s*$|" # rust (paired with #[test] nearby)
        r"@Test|\[Fact\]|\[Theory\])",    # java / xunit annotations
    )
    for i, line in enumerate(lines):
        if func_re.search(line):
            starts.append(i)
    return starts


def check_file(path: str) -> list[Finding]:
    findings: list[Finding] = []
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as fh:
            lines = fh.readlines()
    except OSError as exc:  # pragma: no cover - defensive
        return [Finding(path, 0, "IO", f"could not read: {exc}")]

    for i, raw in enumerate(lines, start=1):
        line = raw.rstrip("\n")
        if SKIP_RE.search(line):
            findings.append(Finding(path, i, "SKIP", "skipped/disabled test left in suite"))
        if FOCUS_RE.search(line):
            findings.append(Finding(path, i, "FOCUS", "focused test (.only/fit/fdescribe) will hide siblings"))
        if SLEEP_RE.search(line):
            findings.append(Finding(path, i, "SLEEP", "sleep-based timing is a flakiness source; use fake timers/sync"))
        if NONDET_RE.search(line):
            findings.append(Finding(path, i, "NONDET", "non-deterministic time/random; inject or seed it"))

    # Assertion-less / empty test bodies: scan each test function's body until
    # the next test start or EOF and check for an assertion token.
    starts = detect_test_func_starts(lines)
    for idx, start in enumerate(starts):
        end = starts[idx + 1] if idx + 1 < len(starts) else len(lines)
        body = "".join(lines[start:end])
        if not ASSERT_TOKENS.search(body):
            findings.append(
                Finding(path, start + 1, "NOASSERT",
                        "test appears to have no assertion (cannot fail)")
            )
    return findings


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("paths", nargs="+", help="files or directories to scan")
    parser.add_argument("--quiet", action="store_true", help="only print findings")
    parser.add_argument("--all-files", action="store_true",
                        help="check every file, not only those named *test*/*spec*")
    args = parser.parse_args(argv)

    all_findings: list[Finding] = []
    scanned = 0
    for path in iter_files(args.paths):
        if not args.all_files and not is_test_file(path):
            continue
        scanned += 1
        all_findings.extend(check_file(path))

    for f in sorted(all_findings, key=lambda x: (x.path, x.line)):
        print(f.format())

    if not args.quiet:
        print(f"\nScanned {scanned} test file(s); {len(all_findings)} finding(s).",
              file=sys.stderr)

    return 1 if all_findings else 0


if __name__ == "__main__":
    raise SystemExit(main())
