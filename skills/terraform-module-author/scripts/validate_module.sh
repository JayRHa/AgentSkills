#!/usr/bin/env bash
#
# validate_module.sh — run the standard quality gate on a Terraform module.
#
# Runs, in order:
#   1. terraform fmt   (check formatting; -w to auto-fix)
#   2. terraform init  (backend disabled — safe for child modules)
#   3. terraform validate
#   4. tflint          (if installed)
#   5. terraform test  (if tests/ exists)
#
# Usage:
#   scripts/validate_module.sh [MODULE_DIR] [--fix]
#
#   MODULE_DIR  Path to the module (default: current directory)
#   --fix       Auto-format with `terraform fmt -recursive -w` instead of failing on diff
#
# Exit codes: 0 = all checks passed, non-zero = a check failed.
# Works with `tofu` too: set TF_BIN=tofu.
set -euo pipefail

TF_BIN="${TF_BIN:-terraform}"
MODULE_DIR="."
FIX=0

for arg in "$@"; do
  case "$arg" in
    --fix) FIX=1 ;;
    -h|--help)
      sed -n '2,20p' "$0" | sed 's/^# \{0,1\}//'
      exit 0 ;;
    *) MODULE_DIR="$arg" ;;
  esac
done

if [ ! -d "$MODULE_DIR" ]; then
  echo "error: module dir '$MODULE_DIR' not found" >&2
  exit 2
fi

if ! command -v "$TF_BIN" >/dev/null 2>&1; then
  echo "error: '$TF_BIN' not on PATH (set TF_BIN=tofu to use OpenTofu)" >&2
  exit 2
fi

cd "$MODULE_DIR"
echo "==> Module: $(pwd)"
echo "==> Tool:   $($TF_BIN version | head -n1)"

step() { printf '\n\033[1m==> %s\033[0m\n' "$1"; }

step "terraform fmt"
if [ "$FIX" -eq 1 ]; then
  "$TF_BIN" fmt -recursive -w .
  echo "formatted in place"
else
  if ! "$TF_BIN" fmt -recursive -check -diff .; then
    echo "error: files not formatted. Run with --fix or 'terraform fmt -recursive'." >&2
    exit 1
  fi
  echo "formatting OK"
fi

step "terraform init (backend disabled)"
"$TF_BIN" init -backend=false -input=false >/dev/null
echo "init OK"

step "terraform validate"
"$TF_BIN" validate

step "tflint"
if command -v tflint >/dev/null 2>&1; then
  tflint --init >/dev/null 2>&1 || true
  tflint
  echo "tflint OK"
else
  echo "tflint not installed — skipping (install from https://github.com/terraform-linters/tflint)"
fi

step "terraform test"
if [ -d tests ] && ls tests/*.tftest.hcl >/dev/null 2>&1; then
  "$TF_BIN" test
  echo "tests OK"
else
  echo "no tests/*.tftest.hcl — skipping"
fi

printf '\n\033[1;32m==> All checks passed.\033[0m\n'
