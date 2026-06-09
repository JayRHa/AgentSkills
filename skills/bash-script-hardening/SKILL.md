---
name: bash-script-hardening
description: Writes robust, safe, shellcheck-clean Bash scripts using strict mode, defensive quoting, error traps, safe temp files, and signal handling. Use this skill when authoring or reviewing shell/Bash scripts, when asked to "harden a bash script", "add strict mode", "fix shellcheck warnings", "make this script safe", debug silent failures, unquoted-variable bugs, word-splitting/globbing issues, or to add cleanup traps and error handling.
license: MIT
---

# Bash Script Hardening

## Overview

Most Bash bugs are silent: an unset variable expands to nothing, a failed command is ignored, an unquoted path word-splits, and the script marches on corrupting state. This skill makes Bash scripts **fail loudly, fail early, and clean up after themselves**.

Keywords: bash, shell, strict mode, `set -euo pipefail`, IFS, quoting, word splitting, globbing, ShellCheck, trap, ERR, EXIT, cleanup, mktemp, signal handling, defensive scripting, POSIX, exit codes, here-doc, arrays.

Use this skill to author a new script from a hardened template, retrofit an existing script, or review a script for safety defects.

## Workflow

1. **Set the shebang and strict mode.** Use `#!/usr/bin/env bash` and the canonical strict-mode preamble (see below). Never rely on `/bin/sh` if Bash features are used.
2. **Lock down word splitting.** Set `IFS=$'\n\t'` so unquoted expansions don't split on spaces.
3. **Quote everything.** Every variable expansion and command substitution gets double quotes unless you have a deliberate, commented reason not to.
4. **Use arrays for lists and command arguments.** Never build commands by concatenating strings.
5. **Add a cleanup trap.** Register an `EXIT` trap that removes temp files and restores state, plus an `ERR` trap for diagnostics.
6. **Handle errors explicitly where strict mode is insufficient** (conditionals, command substitution in older Bash, pipelines you intend to tolerate).
7. **Create temp files safely** with `mktemp`, and reference them through the cleanup trap.
8. **Validate inputs and dependencies** up front: required args, required commands (`command -v`), required env vars.
9. **Run ShellCheck** and resolve every finding; suppress only with a justified `# shellcheck disable=SCxxxx` comment.
10. **Test failure paths**, not just the happy path.

Reference files:
- `references/strict-mode.md` — deep dive on `set -euo pipefail`, IFS, and the gotchas/escape hatches.
- `references/shellcheck-codes.md` — the most common ShellCheck codes, what they mean, and the correct fix.
- `templates/hardened-script.sh` — drop-in starting template with strict mode, traps, arg parsing, logging.
- `scripts/harden_check.sh` — static auditor that flags missing strict mode, unquoted vars, and other red flags.
- `examples/before-after.md` — a real fragile script transformed into a hardened one, line by line.

## The canonical strict-mode preamble

```bash
#!/usr/bin/env bash
set -Eeuo pipefail
IFS=$'\n\t'
```

What each flag buys you:

| Flag | Effect | Why it matters |
|------|--------|----------------|
| `-e` (`errexit`) | Exit on any command returning non-zero | Stops a broken script from continuing on corrupt state |
| `-u` (`nounset`) | Error on use of unset variables | Catches typos like `"$fle"` and missing args |
| `-o pipefail` | A pipeline fails if **any** stage fails | `cmd \| grep x` no longer hides `cmd` crashing |
| `-E` (`errtrace`) | ERR trap is inherited by functions/subshells | Your error trap actually fires inside functions |
| `IFS=$'\n\t'` | Split only on newline/tab, not spaces | Filenames with spaces stop silently breaking loops |

> `-e` has sharp edges. Read `references/strict-mode.md` for where it does NOT trigger (e.g. inside `if`, `&&`, `||`, the last command of a function used as a condition) and the correct patterns to keep error checking explicit there.

## Quoting and word-splitting rules

- **Always** quote expansions: `"$var"`, `"${arr[@]}"`, `"$(cmd)"`.
- Use `"${arr[@]}"` (quoted, `@`) to preserve elements; never `${arr[*]}` for argument lists.
- Prefer `[[ ... ]]` over `[ ... ]` in Bash — it does not word-split or glob inside.
- Use `printf '%s\n' "$x"` instead of `echo "$x"` for arbitrary data (echo mangles `-n`, backslashes).
- Loop over files with globs or `find -print0 | while IFS= read -r -d ''`, never `for f in $(ls)`.

```bash
# WRONG — word-splits and globs
for f in $(ls *.txt); do rm $f; done

# RIGHT
shopt -s nullglob
for f in ./*.txt; do
  rm -- "$f"
done
```

## Traps and cleanup

Register cleanup once, early, and make it idempotent:

```bash
cleanup() {
  local rc=$?
  # remove temp artifacts; restore anything you changed
  [[ -n "${tmpdir:-}" && -d "$tmpdir" ]] && rm -rf -- "$tmpdir"
  return $rc
}
trap cleanup EXIT

on_err() {
  local rc=$? line=$1
  printf 'ERROR: line %s exited with status %s\n' "$line" "$rc" >&2
}
trap 'on_err "$LINENO"' ERR
```

The `EXIT` trap runs on normal exit, error exit (with `-e`), and most signals — making it the single reliable place to clean up. See `templates/hardened-script.sh` for the full pattern including signal-specific traps.

## Safe temp files

```bash
tmpdir="$(mktemp -d)"          # never hand-craft /tmp/$$ paths (race + predictable)
tmpfile="$(mktemp "$tmpdir/XXXXXX.json")"
# tmpdir is removed by the EXIT trap above
```

Never use `/tmp/myscript.$$` — predictable names are a symlink-attack vector and collide.

## Input and dependency validation

```bash
require_cmd() {
  command -v "$1" >/dev/null 2>&1 || { printf 'Missing dependency: %s\n' "$1" >&2; exit 127; }
}
require_cmd jq
require_cmd curl

: "${API_TOKEN:?API_TOKEN must be set}"   # nounset-style guard for required env

if (( $# < 1 )); then
  printf 'usage: %s <input-file>\n' "${0##*/}" >&2
  exit 2
fi
```

## Hardening checklist

- [ ] `#!/usr/bin/env bash` shebang
- [ ] `set -Eeuo pipefail` and `IFS=$'\n\t'`
- [ ] Every variable/command-substitution expansion is double-quoted
- [ ] Lists and argv built as arrays, expanded with `"${arr[@]}"`
- [ ] `EXIT` trap cleans temp files; `ERR` trap reports failures
- [ ] Temp files via `mktemp`/`mktemp -d`, removed in trap
- [ ] Required commands checked with `command -v`
- [ ] Required args and env vars validated with clear usage + nonzero exit
- [ ] `--` used before user-supplied paths in `rm`, `cp`, etc.
- [ ] No `eval`; no parsing `ls`; no unquoted `$(...)`
- [ ] Meaningful, distinct exit codes (2 usage, 127 missing dep, etc.)
- [ ] `shellcheck` passes clean (disables are justified inline)

## Best Practices

- **Make scripts re-runnable (idempotent).** Guard mutations so a re-run after partial failure is safe.
- **Separate config from logic.** Read tunables from env with documented defaults: `: "${TIMEOUT:=30}"`.
- **Log to stderr, data to stdout.** Keep stdout pure so the script composes in pipelines.
- **Use functions** with `local` variables; avoid global mutation. Declare `local` separately from command substitution to avoid masking exit codes (`local x; x="$(cmd)"`).
- **Pin behavior, not the environment.** Use full option names in comments; prefer `printf` over `echo`.
- **Fail with the right exit code.** Reserve nonzero codes for distinct failure classes so callers can branch.
- **Run ShellCheck in CI** and treat it as a gate. See `references/shellcheck-codes.md`.

## Common Pitfalls

- **`local x=$(cmd)` swallows errors.** The `local` builtin's own success masks `cmd`'s exit status even under `-e`. Split into two lines.
- **`-e` does not fire inside `if`/`&&`/`||`/`!` or the condition of a loop.** Don't assume strict mode covers everything; check return codes explicitly there.
- **`cmd | while read ...` runs the loop in a subshell** — variables set inside are lost in older Bash. Use process substitution `while read ...; do ...; done < <(cmd)` instead.
- **`set -e` + a function whose last command "fails" as a test** silently disables errexit for that function's body. Avoid using such functions as `if` conditions when you also rely on `-e` inside them.
- **Unquoted `$@` vs `"$@"`.** Bare `$@` re-splits arguments; always `"$@"`.
- **`read` without `-r`** mangles backslashes; always `read -r`, and set `IFS=` per-read to preserve leading/trailing whitespace.
- **Predictable temp paths** (`/tmp/$$`) cause races and symlink attacks — always `mktemp`.
- **`rm -rf "$dir/"*` when `$dir` is empty/unset** can target `/`. Quote, validate, and use `--`; consider `${dir:?}` to abort on empty.
