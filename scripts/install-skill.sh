#!/usr/bin/env bash
# Install one or more skills from this library into your local Claude Code skills directory.
#
# Usage:
#   ./scripts/install-skill.sh code-reviewer unit-test-author     # install specific skills
#   ./scripts/install-skill.sh --all                              # install everything
#   ./scripts/install-skill.sh --project code-reviewer            # install into ./.claude/skills
#
# By default skills are copied to ~/.claude/skills (personal scope).
# Skills live as top-level folders in the repo root (each contains a SKILL.md).
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SRC="$REPO_ROOT"
DEST="$HOME/.claude/skills"
SELECTED=()
ALL=false

while [[ $# -gt 0 ]]; do
  case "$1" in
    --all) ALL=true; shift ;;
    --project) DEST="$(pwd)/.claude/skills"; shift ;;
    --dest) DEST="$2"; shift 2 ;;
    -h|--help) sed -n '2,12p' "${BASH_SOURCE[0]}" | sed 's/^# \{0,1\}//'; exit 0 ;;
    *) SELECTED+=("$1"); shift ;;
  esac
done

mkdir -p "$DEST"

install_one() {
  local name="$1"
  if [[ ! -f "$SRC/$name/SKILL.md" ]]; then
    echo "✗ skill not found: $name" >&2
    return 1
  fi
  rm -rf "${DEST:?}/$name"
  cp -R "$SRC/$name" "$DEST/$name"
  echo "✓ installed $name -> $DEST/$name"
}

if [[ "$ALL" == true ]]; then
  for d in "$SRC"/*/; do
    name="$(basename "$d")"
    [[ "$name" == "0-template" || "$name" == "scripts" ]] && continue
    [[ -f "$SRC/$name/SKILL.md" ]] || continue
    install_one "$name"
  done
elif [[ ${#SELECTED[@]} -gt 0 ]]; then
  for name in "${SELECTED[@]}"; do install_one "$name"; done
else
  echo "Nothing to do. Pass skill names, or --all. See --help." >&2
  exit 1
fi

echo "Done. Restart Claude Code or run /reload to pick up new skills."
