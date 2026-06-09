#!/usr/bin/env bash
#
# refactor_check.sh — verify a refactoring is behavior-preserving.
#
# It does three things:
#   1. Snapshots the set of exported/public symbols in the given paths and
#      diffs them against a baseline (detects accidental public API changes).
#   2. Runs the project's test command.
#   3. Optionally runs lint/type-check commands if present.
#
# A clean refactoring should leave the API snapshot UNCHANGED and tests GREEN.
#
# Usage:
#   scripts/refactor_check.sh baseline [PATH ...]   # capture API baseline before refactoring
#   scripts/refactor_check.sh verify   [PATH ...]   # after refactoring: diff API + run tests
#
# Env overrides (auto-detected if unset):
#   TEST_CMD   e.g. "pytest -q" or "npm test" or "go test ./..."
#   LINT_CMD   e.g. "ruff check ." or "npm run lint"
#   TYPE_CMD   e.g. "mypy ." or "npx tsc --noEmit"
#
# Exit code 0 = safe, non-zero = something changed or failed.

set -uo pipefail

MODE="${1:-}"
shift || true
PATHS=("$@")
[ ${#PATHS[@]} -eq 0 ] && PATHS=(".")

SNAP_DIR=".refactor_check"
BASELINE="$SNAP_DIR/api_baseline.txt"
CURRENT="$SNAP_DIR/api_current.txt"
mkdir -p "$SNAP_DIR"

red()   { printf '\033[31m%s\033[0m\n' "$*"; }
green() { printf '\033[32m%s\033[0m\n' "$*"; }
yellow(){ printf '\033[33m%s\033[0m\n' "$*"; }

# Extract a language-agnostic, sorted list of public symbol declarations.
# Heuristic and intentionally simple: catches the common cases across
# Python / JS / TS / Go / Java without parsing.
snapshot_api() {
  local out="$1"; shift
  : > "$out"
  for p in "${PATHS[@]}"; do
    grep -rEn \
      -e '^[[:space:]]*export[[:space:]]+(default[[:space:]]+)?(async[[:space:]]+)?(function|class|const|let|var|interface|type|enum)[[:space:]]+[A-Za-z_]' \
      -e '^[[:space:]]*(public|protected)[[:space:]].*\b[A-Za-z_][A-Za-z0-9_]*[[:space:]]*\(' \
      -e '^[[:space:]]*def[[:space:]]+[A-Za-z_][A-Za-z0-9_]*[[:space:]]*\(' \
      -e '^[[:space:]]*class[[:space:]]+[A-Za-z_]' \
      -e '^[[:space:]]*func[[:space:]]+([A-Z]|\([^)]*\)[[:space:]]*[A-Z])' \
      --include='*.py' --include='*.js' --include='*.jsx' \
      --include='*.ts' --include='*.tsx' --include='*.go' \
      --include='*.java' --include='*.rb' \
      "$p" 2>/dev/null \
      | sed -E 's/[[:space:]]+/ /g' \
      | grep -vE '(^|[^A-Za-z])(def|func) +_[A-Za-z]' \
      >> "$out"
  done
  # Normalize: drop line numbers, sort, unique. Keep file + signature shape.
  sed -E 's/:[0-9]+:/:/' "$out" | sort -u -o "$out"
}

detect_cmd() {
  local var="$1"; local val="${!var:-}"
  [ -n "$val" ] && { echo "$val"; return; }
  if [ "$var" = "TEST_CMD" ]; then
    [ -f pyproject.toml ] || [ -f pytest.ini ] || [ -f setup.cfg ] && command -v pytest >/dev/null && { echo "pytest -q"; return; }
    [ -f package.json ] && grep -q '"test"' package.json && { echo "npm test --silent"; return; }
    [ -f go.mod ] && { echo "go test ./..."; return; }
    [ -f Cargo.toml ] && { echo "cargo test"; return; }
    [ -f pom.xml ] && { echo "mvn -q test"; return; }
  fi
  echo ""
}

run_cmd() {
  local label="$1"; local cmd="$2"
  [ -z "$cmd" ] && { yellow "skip $label (no command detected)"; return 0; }
  yellow "==> $label: $cmd"
  bash -c "$cmd"
}

case "$MODE" in
  baseline)
    snapshot_api "$BASELINE"
    green "API baseline captured: $(wc -l < "$BASELINE" | tr -d ' ') public symbols -> $BASELINE"
    echo "Refactor now, then run: $0 verify ${PATHS[*]}"
    ;;

  verify)
    rc=0
    if [ ! -f "$BASELINE" ]; then
      red "No baseline found. Run '$0 baseline ${PATHS[*]}' before refactoring."
      exit 2
    fi
    snapshot_api "$CURRENT"
    if diff -u "$BASELINE" "$CURRENT" > "$SNAP_DIR/api_diff.txt"; then
      green "PUBLIC API unchanged."
    else
      red "PUBLIC API CHANGED — this may not be a pure refactoring:"
      cat "$SNAP_DIR/api_diff.txt"
      rc=1
    fi

    TEST_CMD="$(detect_cmd TEST_CMD)"
    LINT_CMD="${LINT_CMD:-}"
    TYPE_CMD="${TYPE_CMD:-}"

    run_cmd "tests" "$TEST_CMD" || rc=1
    run_cmd "lint"  "$LINT_CMD" || rc=1
    run_cmd "types" "$TYPE_CMD" || rc=1

    if [ "$rc" -eq 0 ]; then
      green "REFACTOR CHECK PASSED — behavior-preserving as far as can be verified."
    else
      red "REFACTOR CHECK FAILED — review the diff/test output above. Consider reverting the last step."
    fi
    exit "$rc"
    ;;

  *)
    sed -n '2,40p' "$0" | sed 's/^# \{0,1\}//'
    exit 2
    ;;
esac
