# Rollback procedures

The non-negotiable: at every step you can return to a known-good state.
Record the baseline SHA (step 1 of the workflow) before touching anything.

## Pre-flight
```sh
git status                 # must be clean before starting
git rev-parse HEAD         # <-- record this as BASELINE
```

## Roll back a single failed upgrade (not yet committed)
If you bumped one package, regenerated the lockfile, and tests went red:
```sh
git restore --source=HEAD --staged --worktree \
  package.json package-lock.json      # adjust to your manifest+lockfile
# then reinstall from the restored lockfile:
npm ci                                 # or: pip install -r, cargo build --locked, etc.
```

## Roll back the most recent committed upgrade
```sh
git revert --no-edit HEAD              # creates a clean revert commit
# OR, if the commit is local-only and you prefer to drop it entirely:
git reset --hard HEAD~1
# reinstall to sync the environment with the lockfile state:
npm ci
```
Prefer `git revert` on shared branches (preserves history); use `git reset`
only on local, unpushed work.

## Roll back the entire session to baseline
```sh
git reset --hard <BASELINE>            # the SHA recorded pre-flight
npm ci                                  # resync env to the restored lockfile
```

## Lockfile-only drift (manifest fine, lockfile churned)
Regenerate from the manifest with the pinned PM version:
```sh
git checkout <BASELINE> -- package-lock.json   # restore known-good lock
npm ci
```

## Per-ecosystem resync command (run after any rollback)
| Ecosystem | Resync env to lockfile |
|-----------|------------------------|
| npm | `npm ci` |
| yarn | `yarn install --immutable` |
| pnpm | `pnpm install --frozen-lockfile` |
| poetry | `poetry install --sync` |
| uv | `uv sync` |
| pip | `pip install -r requirements.txt` |
| cargo | `cargo build --locked` |
| go | `go mod download` |
| bundler | `bundle install` |
| composer | `composer install` |

## Rules
- Never leave the working tree in a broken (red) state at end of session.
- One upgrade per commit makes `git revert <sha>` surgical — that is the whole
  point of isolating majors.
- After any rollback, re-run the test suite to confirm you are green again.
- If you used `--force`/`--legacy-peer-deps`, note it; rollback must undo that
  too (it may have written incompatible transitive versions to the lockfile).
