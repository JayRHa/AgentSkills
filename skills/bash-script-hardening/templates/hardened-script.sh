#!/usr/bin/env bash
#
# <script-name> — <one-line description>
#
# Usage: <script-name> [options] <args>
# A hardened Bash template: strict mode, traps, logging, arg parsing,
# dependency checks, and safe temp handling. Copy and adapt.
#
# Exit codes:
#   0  success
#   1  generic runtime error
#   2  usage error (bad/missing arguments)
# 127  missing dependency

set -Eeuo pipefail
IFS=$'\n\t'

# --- constants --------------------------------------------------------------
readonly SCRIPT_NAME="${0##*/}"
readonly SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
: "${LOG_LEVEL:=info}"   # debug|info|warn|error, override via env

# --- logging (to stderr; stdout stays clean for data) -----------------------
log()  { printf '%s [%s] %s\n' "$(date +%FT%TZ)" "$1" "${*:2}" >&2; }
debug() { [[ "$LOG_LEVEL" == debug ]] && log DEBUG "$@" || true; }
info()  { log INFO  "$@"; }
warn()  { log WARN  "$@"; }
error() { log ERROR "$@"; }
die()   { error "$@"; exit 1; }

# --- cleanup & error traps --------------------------------------------------
tmpdir=""
cleanup() {
  local rc=$?
  [[ -n "$tmpdir" && -d "$tmpdir" ]] && rm -rf -- "$tmpdir"
  trap - EXIT
  exit "$rc"
}
trap cleanup EXIT
trap 'error "failed at line $LINENO (exit $?)"' ERR
trap 'die "interrupted"' INT TERM

# --- helpers ----------------------------------------------------------------
usage() {
  cat >&2 <<EOF
Usage: $SCRIPT_NAME [options] <input>

Options:
  -o, --output FILE   write result to FILE (default: stdout)
  -v, --verbose       enable debug logging
  -h, --help          show this help

Environment:
  LOG_LEVEL  debug|info|warn|error (default: info)
EOF
}

require_cmd() {
  command -v "$1" >/dev/null 2>&1 || { error "missing dependency: $1"; exit 127; }
}

# --- argument parsing -------------------------------------------------------
main() {
  local output="" verbose=0
  local -a positional=()

  while (( $# )); do
    case "$1" in
      -o|--output) output="${2:?--output needs a value}"; shift 2 ;;
      -v|--verbose) verbose=1; LOG_LEVEL=debug; shift ;;
      -h|--help) usage; exit 0 ;;
      --) shift; positional+=("$@"); break ;;
      -*) error "unknown option: $1"; usage; exit 2 ;;
      *) positional+=("$1"); shift ;;
    esac
  done

  if (( ${#positional[@]} < 1 )); then
    error "missing required <input> argument"
    usage
    exit 2
  fi
  local input="${positional[0]}"

  # --- dependency & input validation ---
  require_cmd awk
  [[ -r "$input" ]] || die "cannot read input: $input"

  # --- safe temp workspace ---
  tmpdir="$(mktemp -d)"
  debug "workspace: $tmpdir"
  local staged="$tmpdir/staged.txt"

  # --- do the work (example: count non-empty lines) ---
  awk 'NF { c++ } END { print c+0 }' -- "$input" > "$staged"

  if [[ -n "$output" ]]; then
    cp -- "$staged" "$output"
    info "wrote result to $output"
  else
    cat -- "$staged"
  fi
}

main "$@"
