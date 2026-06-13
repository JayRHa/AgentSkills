# ShellCheck: Common Codes and Correct Fixes

[ShellCheck](https://www.shellcheck.net) is the static analyzer for shell scripts. Run it on every script and treat findings as build failures. This reference covers the codes you will hit most, what they mean, and the right fix (not just a suppression).

## Running it

```bash
shellcheck script.sh                 # analyze
shellcheck -s bash script.sh         # force bash dialect
shellcheck -S error script.sh        # only errors (CI gate)
shellcheck -x script.sh              # follow `source`d files
find . -name '*.sh' -exec shellcheck {} +
```

Suppress a single line ONLY with justification:
```bash
# shellcheck disable=SC2086  # word splitting is intentional: building flags
rm $flags
```
Disable for a whole file by putting the directive at the top, before any code.

## High-impact codes

### SC2086 — Double quote to prevent globbing and word splitting
The single most common real bug.
```bash
cp $src $dst            # BAD: splits/globs
cp "$src" "$dst"        # GOOD
mycmd "${args[@]}"      # GOOD for arrays
```

### SC2046 — Quote command substitution to prevent word splitting
```bash
kill $(pidof foo)       # BAD
kill "$(pidof foo)"     # works for single value; for multiple, use an array or mapfile
mapfile -t pids < <(pidof foo); kill "${pids[@]}"
```

### SC2155 — Declare and assign separately to avoid masking return values
```bash
local x="$(cmd)"        # BAD: masks cmd's exit status
local x; x="$(cmd)"     # GOOD
```

### SC2164 — Use `cd ... || exit` in case cd fails
```bash
cd /some/dir            # BAD: continues in wrong dir if it fails
cd /some/dir || exit 1  # GOOD
```

### SC2068 — Double quote array expansions to avoid re-splitting
```bash
mycmd $@                # BAD
mycmd "$@"              # GOOD
for a in $arr; ...      # BAD
for a in "${arr[@]}"; ...  # GOOD
```

### SC2034 — Variable appears unused
Usually a typo or a forgotten use. If intentional (e.g. exported for sourced scripts), rename to leading-underscore or add a disable with a reason.

### SC2006 — Use `$(...)` instead of legacy backticks
```bash
foo=`date`              # BAD: backticks don't nest, eat backslashes
foo="$(date)"           # GOOD
```

### SC2059 — Don't use variables in the printf format string
```bash
printf "$msg\n"         # BAD: format-string injection if msg has %
printf '%s\n' "$msg"    # GOOD
```

### SC2115 — Use `${var:?}` to ensure expansion isn't empty before `rm -rf`
```bash
rm -rf "$dir/"*         # BAD if dir is empty -> rm -rf /*
rm -rf "${dir:?}/"*     # GOOD: aborts if dir is empty/unset
```

### SC2162 — `read` without `-r` mangles backslashes
```bash
read line               # BAD
IFS= read -r line       # GOOD
```

### SC2128 — Expanding an array without an index gives only the first element
```bash
echo "$arr"             # only arr[0]
echo "${arr[*]}"        # all, joined by IFS[0]
printf '%s\n' "${arr[@]}"  # all, one per line
```

### SC2012 — Use `find` instead of parsing `ls`
```bash
for f in $(ls);          # BAD
for f in ./*; do ...     # GOOD (with nullglob)
find . -type f -print0 | while IFS= read -r -d '' f; do ...; done  # robust
```

### SC1090 / SC1091 — Can't follow non-constant / not-found source
```bash
source "$config"
# shellcheck source=/dev/null   # if path is dynamic and you accept it
```

## Suggested CI gate

```bash
#!/usr/bin/env bash
set -Eeuo pipefail
fail=0
while IFS= read -r -d '' f; do
  shellcheck -S warning "$f" || fail=1
done < <(find . -name '*.sh' -not -path './.git/*' -print0)
exit "$fail"
```

## Severity levels
`error` > `warning` > `info` > `style`. Gate CI at `warning` or stricter; fix `style` items too for clean, idiomatic scripts.
