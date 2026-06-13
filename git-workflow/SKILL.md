---
name: git-workflow
description: Guides safe, professional Git usage — branching strategies, atomic clean commits, conventional commit messages, interactive rebase (squash/fixup/reword/reorder), merge vs rebase decisions, conflict resolution, and recovery of lost work via reflog. Use this skill when the user asks to create or clean up a branch, write or amend commits, squash or reorder history, rebase onto main, resolve merge conflicts, undo a bad commit/merge/reset, recover deleted commits or branches, find lost work, fix a detached HEAD, force-push safely, or generally "clean up my git history" before opening a PR.
license: MIT
---

# Git Workflow

## Overview

This skill provides a disciplined, safe workflow for everyday Git: branching, crafting clean atomic commits, rewriting history with interactive rebase, resolving conflicts, and recovering from mistakes using the reflog. The guiding principle is **safety first** — never destroy work you cannot recover, always know your escape hatch before running a history-rewriting command.

Keywords: git, branch, commit, rebase, interactive rebase, squash, fixup, reword, cherry-pick, merge, conflict, conflict resolution, reflog, recover lost commits, undo, reset, revert, detached HEAD, force-push, stash, clean history, conventional commits, PR prep.

**Golden rules**
1. Never rewrite history that others have already pulled (shared branches like `main`/`develop`). Rewrite only your own unmerged feature branches.
2. Before any `rebase`, `reset --hard`, or force-push, note the current commit: `git rev-parse HEAD` or just trust the reflog — it remembers.
3. Prefer `git push --force-with-lease` over `--force`. It refuses to clobber commits you haven't seen.
4. Commit early, commit often locally; clean up into atomic commits before sharing.
5. If something looks lost, it almost certainly isn't — go to `git reflog` (see references/reflog-recovery.md).

## Workflow

### 1. Orient before acting
Always understand current state first:
```
git status            # working tree + branch
git log --oneline -10 # recent history
git branch -vv        # branches + tracking
```

### 2. Branch
- Update the base first: `git switch main && git pull --ff-only`.
- Create the branch: `git switch -c feat/short-description`.
- Naming: `<type>/<slug>` e.g. `feat/oauth-login`, `fix/null-deref`, `chore/bump-deps`, `docs/readme`. See references/branch-naming.md.

### 3. Make atomic commits
- One logical change per commit. Stage selectively: `git add -p` to split a working tree into focused hunks.
- Write a Conventional Commit message (see references/conventional-commits.md):
  ```
  feat(auth): add OAuth2 PKCE login flow

  Body explaining WHY, wrapped at ~72 cols. Reference issues.
  ```
- Verify before committing: re-read `git diff --staged`.

### 4. Keep up to date with the base
Choose merge vs rebase intentionally (see decision framework below). For a private feature branch, rebasing keeps history linear:
```
git fetch origin
git rebase origin/main
```

### 5. Clean up history before opening a PR
Squash noise ("wip", "fix typo"), reword unclear messages, reorder for logical flow:
```
git rebase -i origin/main
```
Full guidance and the command cheat sheet: references/interactive-rebase.md. Validate the result before pushing: scripts/rebase-safety-check.sh.

### 6. Resolve conflicts methodically
When a rebase/merge stops on a conflict, follow the step-by-step protocol in references/conflict-resolution.md. Summary:
```
git status                 # see conflicted files
# edit files, remove <<<<<<< ======= >>>>>>> markers
git add <resolved-files>
git rebase --continue      # or: git merge --continue
# abort anytime: git rebase --abort / git merge --abort
```

### 7. Share
```
git push -u origin feat/short-description           # first push
git push --force-with-lease                         # after a rebase/amend
```

### 8. Recover when things go wrong
Nothing is lost until garbage collection runs (default ~30–90 days). See references/reflog-recovery.md and run scripts/git-recover.sh to surface candidate lost commits.

## Decision Framework: Merge vs Rebase

| Situation | Use |
|-----------|-----|
| Updating your private, unpushed feature branch with latest `main` | `git rebase origin/main` (linear history) |
| Branch is shared / others have it checked out | `git merge origin/main` (don't rewrite shared history) |
| Combining a finished feature into `main` (team prefers linear) | rebase then fast-forward / squash-merge |
| Combining a feature, preserving full context & merge point | `git merge --no-ff` |
| You just want to grab one commit from another branch | `git cherry-pick <sha>` |

Rule of thumb: **rebase local, merge shared.**

## Interactive Rebase Quick Reference

In the `git rebase -i` todo list, set the action keyword on each line:

| Keyword | Effect |
|---------|--------|
| `pick` | keep the commit as-is |
| `reword` (r) | keep changes, edit the message |
| `edit` (e) | stop to amend the commit (split, add files) |
| `squash` (s) | merge into previous commit, combine messages |
| `fixup` (f) | merge into previous commit, discard this message |
| `drop` (d) | remove the commit entirely |
| reorder | move lines up/down to reorder commits |

Targeted fixup workflow (best for PR review fixes):
```
git commit --fixup=<sha>          # creates "fixup! ..." commit
git rebase -i --autosquash origin/main   # auto-positions & marks it fixup
```

## Recovery Cheat Sheet

| Problem | Fix |
|---------|-----|
| Bad last commit, want to redo message | `git commit --amend` |
| Undo last commit, keep changes staged | `git reset --soft HEAD~1` |
| Undo last commit, keep changes unstaged | `git reset HEAD~1` |
| Discard last commit AND its changes | `git reset --hard HEAD~1` (recoverable via reflog) |
| Revert a commit already pushed/shared | `git revert <sha>` (new commit, safe) |
| Lost commits after bad reset/rebase | `git reflog` then `git reset --hard <sha>` |
| Deleted a branch by accident | `git reflog` → find tip sha → `git branch <name> <sha>` |
| Detached HEAD with work to keep | `git switch -c rescue-branch` immediately |
| Accidentally committed to `main` | branch it off, then reset `main`: see references/reflog-recovery.md |
| Drop unstaged local changes | `git restore <file>` / `git restore .` |
| Stash WIP to switch context | `git stash push -m "msg"` → `git stash pop` |

## Best Practices
- Make the first line of a commit ≤ 50 chars, imperative mood ("add", not "added").
- Run `scripts/rebase-safety-check.sh` after a rebase to confirm no commits were silently dropped and the tree still matches expectations.
- Use `git add -p` to keep commits atomic instead of `git add .`.
- Prefer `git switch`/`git restore` over the overloaded `git checkout`.
- Tag the pre-rebase state if nervous: `git tag backup-before-rebase`. Delete it when done.
- Configure `git config rerere.enabled true` to let Git remember conflict resolutions across repeated rebases.

## Common Pitfalls
- **Force-pushing a shared branch** and erasing teammates' commits. Use `--force-with-lease`, and never on `main`.
- **Rebasing `main`/`develop`** — rewriting public history breaks everyone. Use `revert` instead.
- **`git reset --hard` without checking** — you lose uncommitted working-tree changes permanently (these are NOT in the reflog). Stash first.
- **Resolving a conflict by deleting the wrong side** — read both sides; the markers are `<<<<<<< HEAD` (current/your side during merge) vs `>>>>>>> branch` (incoming). During rebase the sides are swapped — see references/conflict-resolution.md.
- **Committing generated files / secrets** — review `git diff --staged`; use `.gitignore`.
- **Assuming work is gone after a botched rebase** — check `git reflog` before doing anything else.

## Bundled Files
- `references/interactive-rebase.md` — complete interactive rebase guide with worked scenarios.
- `references/conflict-resolution.md` — step-by-step conflict protocol, marker semantics, rerere, tools.
- `references/reflog-recovery.md` — recover lost commits, branches, resets, detached HEAD, wrong-branch commits.
- `references/conventional-commits.md` — message format, types, scopes, breaking changes, examples.
- `references/branch-naming.md` — naming conventions and branching models.
- `scripts/git-recover.sh` — list recently dangling/unreachable commits with previews to aid recovery.
- `scripts/rebase-safety-check.sh` — sanity-check history after a rebase against the upstream base.
- `examples/squash-feature-branch.md` — end-to-end worked example of cleaning a messy branch.
