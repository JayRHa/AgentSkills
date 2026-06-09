# Worked Example: Cleaning a Messy Feature Branch Before a PR

## Situation

You built a feature over a few days. The history is noisy:
```
$ git log --oneline origin/main..HEAD
d4e5f6a fix lint
c3d4e5f oops forgot file
b2c3d4e wip
a1b2c3d feat: add CSV export endpoint
9f8e7d6 wip more work
8e7d6c5 feat: start CSV export
```
Meanwhile `main` advanced. Goal: rebase onto latest `main` and collapse this into **two** clean, atomic commits before opening a PR.

## Step 0 — Safety net

```
$ git fetch origin
$ git tag backup-csv-export        # escape hatch; or just trust the reflog
$ git rev-parse HEAD
d4e5f6a...                          # note the pre-rebase tip
```

## Step 1 — Rebase onto latest main and open the todo list

```
$ git rebase -i origin/main
```
Git opens:
```
pick 8e7d6c5 feat: start CSV export
pick 9f8e7d6 wip more work
pick a1b2c3d feat: add CSV export endpoint
pick b2c3d4e wip
pick c3d4e5f oops forgot file
pick d4e5f6a fix lint
```

## Step 2 — Plan: two logical commits

We want:
1. "feat: add CSV export service" (the data/serialization layer)
2. "feat: add CSV export HTTP endpoint" (the route)

Edit the todo list to squash the wip/oops/lint noise into the right parents and reword the keepers:
```
reword 8e7d6c5 feat: start CSV export
fixup  9f8e7d6 wip more work
reword a1b2c3d feat: add CSV export endpoint
fixup  b2c3d4e wip
fixup  c3d4e5f oops forgot file
fixup  d4e5f6a fix lint
```
Save and close.

## Step 3 — Reword as Git pauses

First pause (for `8e7d6c5`), write:
```
feat(export): add CSV export service

Serialize records to RFC 4180 CSV with configurable delimiter and
header row. Streams rows to avoid buffering large result sets.
```
Second pause (for `a1b2c3d`), write:
```
feat(api): add GET /export.csv endpoint

Expose the CSV export service over HTTP with auth and pagination
parameters. Returns text/csv with a content-disposition header.
```

## Step 4 — Resolve any conflicts

If a hunk conflicts because `main` moved, Git pauses:
```
$ git status        # shows unmerged file
# edit file, remember: during REBASE the bottom (>>>>>>>) side is YOUR change
$ git add src/export/csv.ts
$ git rebase --continue
```
(If it goes wrong: `git rebase --abort` returns to `d4e5f6a`.)

## Step 5 — Verify the result

```
$ git log --oneline origin/main..HEAD
1aa2bb3 feat(api): add GET /export.csv endpoint
0cc1dd2 feat(export): add CSV export service
```
Run the safety check (content must be unchanged vs the old tip, since we only reorganized history):
```
$ scripts/rebase-safety-check.sh -b origin/main -o backup-csv-export
  [ ok ] no rebase in progress
  [ ok ] no conflict markers in tracked files
  [ ok ] history since base is linear (no merge commits)
  [ ok ] branch is 2 commit(s) ahead, 0 behind origin/main
  [ ok ] resulting tree is IDENTICAL to pre-rebase tip (backup-csv-export) — clean history rewrite
  [ ok ] working tree is clean
Result: OK — safe to 'git push --force-with-lease'.
```

## Step 6 — Push and clean up

```
$ git push --force-with-lease
$ git tag -d backup-csv-export     # remove the safety net once confident
```

## If you realize you squashed too much

The pre-rebase state is still recoverable:
```
$ git reflog
$ git reset --hard backup-csv-export   # or the reflog sha, e.g. HEAD@{6}
```
Then redo the rebase with a corrected plan.
