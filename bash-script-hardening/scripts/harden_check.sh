#!/usr/bin/env bash
#
# harden_check.sh — heuristic auditor for Bash hardening defects.
#
# Scans one or more shell scripts and reports common safety problems that
# ShellCheck may miss or that warrant a hardening review: missing strict mode,
# missing IFS, no cleanup trap, predictable temp paths, use of eval, parsing ls,
# and legacy backticks. Exits non-zero if any HIGH-severity issue is found.
#
# This is a lightweight, dependency-free complement to shellcheck, NOT a
# replacement. Run shellcheck too.
#
# Usage:
#   harden_check.sh [--strict] FILE [FILE...]
#   harden_check.sh --strict ./bin/*.sh
#
# Options:
#   --strict   treat MEDIUM issues as failures too (exit non-zero)
#   -h|--help  show this help
#
# Exit codes:
#   0  no failing issues
#   1  failing issue(s) found
#   2  usage error

set -Eeuo pipefail
IFS=$'\n\t'

strict=0
declare -a files=()

usage() {
  sed -n '2,/^set /{/^set /d;p}' "$0" | sed 's/^#//; s/^ //'
}

while (( $# )); do
  case "$1" in
    --strict) strict=1; shift ;;
    -h|--help) usage; exit 0 ;;
    --) shift; files+=("$@"); break ;;
    -*) printf 'unknown option: %s\n' "$1" >&2; exit 2 ;;
    *) files+=("$1"); shift ;;
  esac
done

if (( ${#files[@]} == 0 )); then
  printf 'usage: %s [--strict] FILE [FILE...]\n' "${0##*/}" >&2
  exit 2
fi

fail=0

report() {
  # report SEVERITY FILE MESSAGE
  local sev=$1 file=$2 msg=$3
  printf '[%-6s] %s: %s\n' "$sev" "$file" "$msg"
  case "$sev" in
    HIGH) fail=1 ;;
    MEDIUM) (( strict )) && fail=1 ;;
  esac
}

check_file() {
  local file=$1
  [[ -r "$file" ]] || { report HIGH "$file" "cannot read file"; return; }

  local body
  body="$(cat -- "$file")"

  # --- shebang ---
  if ! head -n1 -- "$file" | grep -Eq '^#!.*(bash|sh)\b'; then
    report MEDIUM "$file" "missing or non-shell shebang on line 1"
  fi

  # --- strict mode ---
  if ! grep -Eq '^[[:space:]]*set[[:space:]].*-[A-Za-z]*e' <<<"$body"; then
    report HIGH "$file" "no 'set -e' (errexit) found"
  fi
  if ! grep -Eq '^[[:space:]]*set[[:space:]].*-[A-Za-z]*u' <<<"$body"; then
    report HIGH "$file" "no 'set -u' (nounset) found"
  fi
  if ! grep -q 'pipefail' <<<"$body"; then
    report MEDIUM "$file" "no 'pipefail' found"
  fi
  if ! grep -q 'IFS=' <<<"$body"; then
    report MEDIUM "$file" "IFS not set (word-splitting hazard)"
  fi

  # --- traps / cleanup ---
  if ! grep -Eq '^[[:space:]]*trap[[:space:]]' <<<"$body"; then
    report MEDIUM "$file" "no 'trap' for cleanup/error handling"
  fi

  # --- dangerous patterns (strip comments first, naively) ---
  local code
  code="$(grep -v -E '^[[:space:]]*#' <<<"$body" || true)"

  if grep -Eq '\beval\b' <<<"$code"; then
    report HIGH "$file" "use of 'eval' (injection risk) — avoid or justify"
  fi
  if grep -Eq '\$\(ls\b|\`ls\b|for[[:space:]].*in[[:space:]].*\bls\b' <<<"$code"; then
    report HIGH "$file" "parsing 'ls' output (use globs or find -print0)"
  fi
  if grep -q '`' <<<"$code"; then
    report MEDIUM "$file" "legacy backticks (use \$( ... ) instead)"
  fi
  if grep -Eq '/tmp/[^ "'\''`]*\$\$|/tmp/[A-Za-z0-9_]+\.\$\$' <<<"$code"; then
    report HIGH "$file" "predictable temp path with \$\$ (use mktemp)"
  fi
  if grep -Eq '\bread\b(?![^|;&]*-r)' <<<"$code" 2>/dev/null; then
    : # grep -P not guaranteed; do a simpler check below
  fi
  if grep -Eq '\bread[[:space:]]+[A-Za-z_]' <<<"$code" && ! grep -Eq '\bread[[:space:]]+-r' <<<"$code"; then
    report MEDIUM "$file" "'read' without -r (mangles backslashes)"
  fi
  if grep -Eq '\brm[[:space:]]+-rf?[[:space:]]+"?\$' <<<"$code" && ! grep -q ':?}' <<<"$code"; then
    report MEDIUM "$file" "'rm -rf \$var' without \${var:?} guard"
  fi
}

for f in "${files[@]}"; do
  check_file "$f"
done

if (( fail )); then
  printf '\nHardening issues found.\n' >&2
else
  printf '\nNo failing hardening issues.\n' >&2
fi
exit "$fail"
