# Worked Example: Fragile Script -> Hardened Script

A backup helper that tars a directory, uploads it, and removes the local copy. The original "works on my machine" — until a path has a space, the upload fails, or it runs from the wrong directory.

## BEFORE (fragile)

```bash
#!/bin/bash
# backup.sh DIR

DIR=$1
TMP=/tmp/backup.$$.tar.gz

tar czf $TMP $DIR
scp $TMP backup@host:/backups/`date +%F`.tar.gz
rm $TMP
echo "done"
```

### Defects

| # | Problem | Consequence |
|---|---------|-------------|
| 1 | No `set -euo pipefail` | `tar` fails -> `scp` runs on a half-written file -> `rm` deletes evidence; script still prints "done" |
| 2 | `DIR=$1` then `$DIR` unquoted | Path with spaces becomes multiple args to `tar`; `$1` unset -> tars `$PWD` |
| 3 | `/tmp/backup.$$.tar.gz` | Predictable name: race / symlink-attack vector; collides on PID reuse |
| 4 | No cleanup on failure | A crash after `tar` leaves a large temp file forever |
| 5 | Backtick `` `date` `` | Legacy; SC2006 |
| 6 | No dependency / arg checks | Cryptic failures if `scp` missing or no arg given |
| 7 | `echo` for status | Mixes into stdout; mangles special chars |

## AFTER (hardened)

```bash
#!/usr/bin/env bash
#
# backup.sh — archive a directory and upload it, then clean up.
# Usage: backup.sh <dir>
set -Eeuo pipefail
IFS=$'\n\t'

readonly REMOTE="backup@host:/backups"
tmpfile=""

log() { printf '%s %s\n' "$(date +%FT%TZ)" "$*" >&2; }
die() { log "ERROR: $*"; exit 1; }

cleanup() {
  local rc=$?
  [[ -n "$tmpfile" && -f "$tmpfile" ]] && rm -f -- "$tmpfile"
  exit "$rc"
}
trap cleanup EXIT
trap 'die "failed at line $LINENO"' ERR

require() { command -v "$1" >/dev/null 2>&1 || die "missing dependency: $1"; }
require tar
require scp

dir="${1:?usage: backup.sh <dir>}"
[[ -d "$dir" ]] || die "not a directory: $dir"

tmpfile="$(mktemp -t backup.XXXXXX.tar.gz)"
stamp="$(date +%F)"

log "archiving $dir"
tar -czf "$tmpfile" -- "$dir"

log "uploading to $REMOTE/$stamp.tar.gz"
scp -- "$tmpfile" "$REMOTE/$stamp.tar.gz"

log "backup complete"
# tmpfile removed by EXIT trap
```

### What changed, mapped to defects

- **1** -> `set -Eeuo pipefail`: any failure aborts; the `ERR` trap reports the line; `rm` no longer runs after a failed `tar` because the EXIT trap only removes the temp file, never the source.
- **2** -> `"${1:?...}"` validates the arg with a usage message; every expansion quoted; `--` separates options from paths.
- **3** -> `mktemp` creates an unpredictable, exclusive temp file.
- **4** -> `EXIT` trap removes `tmpfile` on success, error, or signal.
- **5** -> `$(date +%F)` replaces backticks.
- **6** -> `require tar`/`require scp` and the directory check fail fast with clear messages.
- **7** -> status goes to stderr via `log`, keeping stdout clean.

## Verifying

```bash
shellcheck backup.sh                 # expect: clean
./scripts/harden_check.sh backup.sh  # expect: no failing issues

# Failure-path test: a missing dir must abort with code 1 and leave no temp file.
./backup.sh /does/not/exist; echo "exit=$?"   # exit=1, no /tmp leftovers
```

The lesson: hardening is not cosmetic. Defect #1 alone means the fragile version can **delete the only copy of data after silently failing to back it up** — the exact failure mode strict mode plus traps eliminates.
