#!/usr/bin/env bash
#
# git_bisect_helper.sh — Automate `git bisect run` to find the commit that
# introduced a bug (a regression).
#
# Strategy: you give a known-GOOD commit (bug absent), a known-BAD commit
# (bug present, defaults to HEAD), and a test command. The test command must
# exit 0 when the code is GOOD and non-zero when BAD. git bisect then performs
# a binary search over history and reports the first bad commit.
#
# Usage:
#   scripts/git_bisect_helper.sh --good <ref> [--bad <ref>] -- <test command...>
#
# Examples:
#   # A failing test command marks BAD (exit!=0); passing marks GOOD (exit 0)
#   scripts/git_bisect_helper.sh --good v1.2.0 -- pytest tests/test_login.py -q
#
#   # Build then run a repro script
#   scripts/git_bisect_helper.sh --good abc123 --bad HEAD -- \
#       bash -c 'make -s && ./repro.sh'
#
# Notes:
#   * If "good" actually fails the test or "bad" passes it, your good/bad are
#     swapped or the test polarity is inverted — this script sanity-checks both
#     endpoints first and aborts with guidance.
#   * Exit code 125 from the test tells git bisect to SKIP an untestable commit
#     (e.g., it won't build). Use that in your command if needed.
#   * The repo is always returned to its original state via `git bisect reset`.

set -euo pipefail

GOOD=""
BAD="HEAD"
TEST_CMD=()

usage() {
  sed -n '2,40p' "$0" | sed 's/^# \{0,1\}//'
  exit "${1:-0}"
}

# ---- parse args ----
while [[ $# -gt 0 ]]; do
  case "$1" in
    --good) GOOD="${2:-}"; shift 2 ;;
    --bad)  BAD="${2:-}";  shift 2 ;;
    -h|--help) usage 0 ;;
    --) shift; TEST_CMD=("$@"); break ;;
    *) echo "Unknown argument: $1" >&2; usage 1 ;;
  esac
done

if [[ -z "$GOOD" ]]; then
  echo "ERROR: --good <ref> is required." >&2; usage 1
fi
if [[ ${#TEST_CMD[@]} -eq 0 ]]; then
  echo "ERROR: a test command after -- is required." >&2; usage 1
fi

if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  echo "ERROR: not inside a git repository." >&2; exit 1
fi

ORIG_REF="$(git rev-parse --abbrev-ref HEAD)"
if [[ "$ORIG_REF" == "HEAD" ]]; then
  ORIG_REF="$(git rev-parse HEAD)"  # detached: remember the SHA
fi

cleanup() {
  git bisect reset >/dev/null 2>&1 || true
}
trap cleanup EXIT

run_test() {
  # Run the user's command; return its exit code untouched.
  "${TEST_CMD[@]}"
}

echo "==> Sanity-checking endpoints before bisect"
echo "    GOOD ref: $GOOD   BAD ref: $BAD"
echo "    Test cmd: ${TEST_CMD[*]}"

echo "--> Verifying BAD ($BAD) actually fails the test..."
git checkout -q "$BAD"
if run_test; then
  echo "WARNING: test PASSED at BAD ($BAD). Expected it to fail." >&2
  echo "         Your --bad ref may not contain the bug, or the test polarity" >&2
  echo "         is inverted (test must exit non-zero when bug present)." >&2
  exit 2
fi
echo "    OK: BAD fails as expected."

echo "--> Verifying GOOD ($GOOD) actually passes the test..."
git checkout -q "$GOOD"
if ! run_test; then
  echo "WARNING: test FAILED at GOOD ($GOOD). Expected it to pass." >&2
  echo "         Pick an older --good ref where the bug is truly absent." >&2
  exit 2
fi
echo "    OK: GOOD passes as expected."

echo "==> Starting git bisect"
git checkout -q "$ORIG_REF" || true
git bisect start
git bisect bad "$BAD"
git bisect good "$GOOD"

echo "==> Running automated bisect (this checks out commits and runs your test)"
# git bisect run treats exit 0 = good, 1..124/126/127 = bad, 125 = skip.
git bisect run "${TEST_CMD[@]}" | tee /tmp/bisect_output.$$ || true

echo
echo "==> First bad commit (culprit):"
grep -A0 "is the first bad commit" /tmp/bisect_output.$$ || \
  echo "    See output above; look for 'is the first bad commit'."
rm -f /tmp/bisect_output.$$

echo "==> Done. Repo will be reset to $ORIG_REF on exit."
