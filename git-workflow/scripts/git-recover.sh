#!/usr/bin/env bash
#
# git-recover.sh — surface lost/unreachable commits to help recover work.
#
# Lists, newest first:
#   1) recent HEAD reflog entries (the usual recovery source)
#   2) dangling/unreachable commits found by git fsck (deleted branches,
#      dropped stashes, orphaned rebase commits)
# Each candidate shows its sha, date, author and subject so you can identify
# the one to recover with:  git branch <name> <sha>   or   git cherry-pick <sha>
#
# Usage:
#   scripts/git-recover.sh [-n COUNT] [-g]
#     -n COUNT   number of reflog entries to show (default 30)
#     -g         also show full diffstat for each dangling commit
#     -h         help
#
# Safe & read-only: it never modifies the repository.

set -euo pipefail

COUNT=30
SHOW_STAT=0

while getopts ":n:gh" opt; do
  case "$opt" in
    n) COUNT="$OPTARG" ;;
    g) SHOW_STAT=1 ;;
    h)
      sed -n '2,20p' "$0" | sed 's/^# \{0,1\}//'
      exit 0
      ;;
    \?) echo "Unknown option: -$OPTARG" >&2; exit 2 ;;
    :)  echo "Option -$OPTARG requires an argument" >&2; exit 2 ;;
  esac
done

if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  echo "error: not inside a git repository" >&2
  exit 1
fi

hr() { printf '%s\n' "------------------------------------------------------------"; }

echo "== Recent HEAD reflog (most recent first) =="
echo "Recover with:  git reset --hard HEAD@{N}   (N = entry number)"
hr
git reflog --date=short -n "$COUNT" \
  --format='%C(yellow)%gd%C(reset) %C(green)%gs%C(reset) -> %C(auto)%h%C(reset) %s'
echo

echo "== Dangling / unreachable commits (deleted branches, dropped stashes, orphaned rebase commits) =="
echo "Recover with:  git branch <name> <sha>   OR   git cherry-pick <sha>"
hr

# Collect unreachable commit shas via fsck. --no-reflogs makes truly orphaned
# objects visible. Suppress the noisy progress/notice lines.
mapfile -t SHAS < <(
  git fsck --no-reflogs --unreachable 2>/dev/null \
    | awk '/unreachable commit/ {print $3}'
)

if [ "${#SHAS[@]}" -eq 0 ]; then
  echo "(none found)"
else
  # Sort by commit date, newest first.
  for sha in "${SHAS[@]}"; do
    ts=$(git show -s --format='%ct' "$sha" 2>/dev/null || echo 0)
    printf '%s %s\n' "$ts" "$sha"
  done | sort -rn | while read -r _ts sha; do
    git show -s --date=short \
      --format='%C(auto)%h%C(reset)  %C(cyan)%ad%C(reset)  %C(blue)%an%C(reset)  %s' "$sha"
    if [ "$SHOW_STAT" -eq 1 ]; then
      git show --stat --oneline "$sha" | tail -n +2 | sed 's/^/    /'
      echo
    fi
  done
fi

echo
echo "Tip: do NOT run 'git gc --prune=now' until you have recovered what you need."
