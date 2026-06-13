# Strict Mode Deep Dive: `set -Eeuo pipefail` + IFS

The strict-mode preamble turns silent Bash failures into loud, early aborts. But each flag has edge cases. This reference explains exactly what they do, where they DON'T fire, and the correct escape hatches.

## The preamble

```bash
#!/usr/bin/env bash
set -Eeuo pipefail
IFS=$'\n\t'
```

## `-e` / `errexit` — exit on error

Exits the script when a *simple command* returns nonzero.

### Where `-e` does NOT trigger (critical to know)

`-e` is deliberately suppressed in these contexts so they can be used as tests:

1. **Condition of `if`, `while`, `until`:** `if grep -q x f; then` — a nonzero `grep` is a normal "no match", not an abort.
2. **Operands of `&&` and `||`:** `cmd1 && cmd2` — `cmd1` failing does not abort; it short-circuits.
3. **Negated with `!`:** `! cmd` never aborts on `cmd`'s failure.
4. **Any command in a list except the last**, when the list is itself in one of the above contexts.

Consequence: this does NOT abort even though `false` fails, because it's the condition of `if`:
```bash
if some_function; then ...; fi   # errexit OFF inside some_function's last command path
```

### `local`/`declare` masks exit status

```bash
local result="$(might_fail)"   # BUG: exit status is local's (0), not might_fail's
```
The assignment builtin succeeds even if the command substitution failed, so `-e` never sees the failure. Fix by separating:
```bash
local result
result="$(might_fail)"          # now errexit sees might_fail's status
```

### Intentionally tolerating a failure

When you *expect* a command may fail and want to continue:
```bash
if ! output="$(flaky_cmd)"; then
  output="fallback"
fi

# or, append `|| true` for fire-and-forget:
optional_cleanup || true
```
Document WHY with a comment so reviewers don't 'fix' it.

## `-u` / `nounset` — error on unset variables

Referencing an unset variable aborts. Catches typos and missing positional args.

### Safe defaults under `-u`

Bare `$1` or `${arr[@]}` on an empty array can trip `-u` in some Bash versions. Use default expansions:
```bash
arg="${1:-}"                 # empty if unset
name="${NAME:-anonymous}"    # fallback value
for x in "${list[@]:-}"; do  # tolerate empty array (Bash < 4.4)
```
`${var:?message}` is the assertive form — abort with a message if unset/empty:
```bash
: "${API_TOKEN:?must be set in the environment}"
```

## `-o pipefail` — pipeline returns first nonzero status

Without it, a pipeline's exit status is only the *last* command's. So `curl ... | jq` reports success even if `curl` died. With `pipefail`, the pipeline fails if any stage fails.

### Tolerating expected pipe failures (e.g. SIGPIPE from `head`)
```bash
set +o pipefail
big_producer | head -n 10
set -o pipefail
# Or capture and ignore the specific status:
status=0; big_producer | head -n 10 || status=$?
```
`head` closing the pipe early makes the producer exit 141 (SIGPIPE); pipefail would surface that as a failure.

## `-E` / `errtrace` — propagate ERR trap

Without `-E`, an `ERR` trap set at top level does NOT fire inside functions, command substitutions, or subshells. With `-E`, it is inherited everywhere. Always include it if you use an `ERR` trap. (Similarly, `-T`/`functrace` propagates DEBUG and RETURN traps.)

## `IFS=$'\n\t'`

The Internal Field Separator controls how unquoted expansions are split into words. Default is space+tab+newline, so an unquoted `$var` containing spaces splits unexpectedly. Restricting IFS to newline and tab means accidental unquoted expansions break far less often — but quoting is still the real fix.

Set IFS locally for a single read to preserve whitespace and split on a custom delimiter:
```bash
while IFS= read -r line; do ...; done < file          # preserve whole lines
IFS=, read -r -a fields <<< "$csv_row"                 # split CSV into array
while IFS= read -r -d '' f; do ...; done < <(find . -print0)   # NUL-safe
```

## Putting it together: a guarded block

```bash
#!/usr/bin/env bash
set -Eeuo pipefail
IFS=$'\n\t'

main() {
  local input="${1:?usage: $0 <file>}"
  [[ -r "$input" ]] || { printf 'cannot read: %s\n' "$input" >&2; exit 1; }

  local count
  count="$(grep -c . -- "$input")" || count=0   # tolerate no-match
  printf 'non-empty lines: %s\n' "$count"
}

main "$@"
```

## Quick reference: escape hatches

| Need | Pattern |
|------|---------|
| Allow one command to fail | `cmd || true` |
| Capture status, keep going | `cmd && rc=0 || rc=$?` |
| Default for possibly-unset var | `"${var:-default}"` |
| Abort if var unset/empty | `"${var:?message}"` |
| Temporarily disable errexit | `set +e; ...; set -e` |
| NUL-safe filename loop | `while IFS= read -r -d '' f; do ...; done < <(find . -print0)` |
