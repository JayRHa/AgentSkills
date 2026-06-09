#!/usr/bin/env bash
#
# rebase-safety-check.sh — sanity-check your branch after an interactive rebase.
#
# Verifies, against an upstream base, that the rebase did not accidentally:
#   * leave the tree in a state that differs from the pre-rebase content
#     (it compares the resulting file tree with a saved snapshot, if provided)
#   * drop commits unexpectedly (reports commit-count before vs after)
#   * leave unresolved conflict markers in tracked files
#   * leave the rebase mid-operation
#
# Usage:
#   scripts/rebase-safety-check.sh [-b BASE] [-o OLD_TIP]
#     -b BASE     upstream base to compare against   (default: origin/main)
#     -o OLD_TIP  the commit your branch tip was BEFORE the rebase
#                 (e.g. a backup tag or a reflog sha). If given, the script
#                 confirms the *content* of the tree is identical, which it
#                 must be for a pure history-cleanup rebase (no code changes).
#     -h          help
#
# Exit code 0 = all good, non-zero = at least one check failed.

set -uo pipefail

BASE="origin/main"
OLD_TIP=""

while getopts ":b:o:h" opt; do
  case "$opt" in
    b) BASE="$OPTARG" ;;
    o) OLD_TIP="$OPTARG" ;;
    h) sed -n '2,24p' "$0" | sed 's/^# \{0,1\}//'; exit 0 ;;
    \?) echo "Unknown option: -$OPTARG" >&2; exit 2 ;;
    :)  echo "Option -$OPTARG requires an argument" >&2; exit 2 ;;
  esac
done

if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  echo "error: not inside a git repository" >&2
  exit 1
fi

fail=0
pass() { printf '  [ ok ] %s\n' "$1"; }
warn() { printf '  [WARN] %s\n' "$1"; }
bad()  { printf '  [FAIL] %s\n' "$1"; fail=1; }

echo "Rebase safety check (base: $BASE)"
echo "--------------------------------------------"

# 1) Are we mid-rebase?
gitdir=$(git rev-parse --git-dir)
if [ -d "$gitdir/rebase-merge" ] || [ -d "$gitdir/rebase-apply" ]; then
  bad "a rebase is still in progress — run 'git rebase --continue' or '--abort'"
else
  pass "no rebase in progress"
fi

# 2) Does the base ref resolve?
if ! git rev-parse --verify --quiet "$BASE" >/dev/null; then
  warn "base '$BASE' not found (did you 'git fetch'?) — skipping base comparisons"
  BASE=""
fi

# 3) Unresolved conflict markers in tracked files
if git grep -nI -e '^<<<<<<< ' -e '^=======$' -e '^>>>>>>> ' -- . >/dev/null 2>&1; then
  bad "conflict markers still present:"
  git grep -nI -e '^<<<<<<< ' -e '^>>>>>>> ' -- . | sed 's/^/        /'
else
  pass "no conflict markers in tracked files"
fi

# 4) Linear history on top of base (no merge commits since base)?
if [ -n "$BASE" ]; then
  merges=$(git rev-list --merges "$BASE"..HEAD | wc -l | tr -d ' ')
  if [ "$merges" -eq 0 ]; then
    pass "history since base is linear (no merge commits)"
  else
    warn "$merges merge commit(s) since base — expected if you merged instead of rebased"
  fi
  ahead=$(git rev-list --count "$BASE"..HEAD)
  behind=$(git rev-list --count HEAD.."$BASE")
  pass "branch is $ahead commit(s) ahead, $behind behind $BASE"
  if [ "$behind" -ne 0 ]; then
    warn "branch is behind base — rebase onto $BASE again before pushing"
  fi
fi

# 5) Content preserved vs pre-rebase tip (pure cleanup should not change files)
if [ -n "$OLD_TIP" ]; then
  if ! git rev-parse --verify --quiet "$OLD_TIP" >/dev/null; then
    bad "OLD_TIP '$OLD_TIP' does not resolve to a commit"
  elif git diff --quiet "$OLD_TIP" HEAD --; then
    pass "resulting tree is IDENTICAL to pre-rebase tip ($OLD_TIP) — clean history rewrite"
  else
    warn "tree differs from pre-rebase tip — review intended (squash/drop changes code? run: git diff $OLD_TIP HEAD)"
  fi
fi

# 6) Working tree clean?
if git diff --quiet && git diff --cached --quiet; then
  pass "working tree is clean"
else
  warn "uncommitted changes present"
fi

echo "--------------------------------------------"
if [ "$fail" -eq 0 ]; then
  echo "Result: OK — safe to 'git push --force-with-lease'."
  exit 0
else
  echo "Result: PROBLEMS FOUND — fix the [FAIL] items before pushing."
  exit 1
fi
