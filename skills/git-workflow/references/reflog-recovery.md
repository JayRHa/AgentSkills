# Recovery with git reflog

The **reflog** records every move of `HEAD` (and of each branch). Even after a bad `reset --hard`, a botched rebase, or a deleted branch, the commits still exist as long as the reflog references them — they are simply unreachable from any branch. They survive until garbage collection (default: unreachable & unreferenced objects ~2 weeks; reflog entries ~90 days).

> What the reflog CANNOT recover: changes that were never committed and never stashed. `git reset --hard` discards uncommitted working-tree changes for good. Stash or commit before destructive commands.

## Read the reflog

```
git reflog                     # HEAD movements, most recent first
git reflog show <branch>       # a specific branch's history of tips
git log -g --oneline           # reflog as log output
```
Entries look like:
```
9f8e7d6 HEAD@{0}: rebase (finish): returning to refs/heads/feat/x
a1b2c3d HEAD@{1}: commit: feat: add validation
c3d4e5f HEAD@{2}: reset: moving to HEAD~3
```
`HEAD@{N}` is a reference you can use anywhere a commit-ish is expected.

## Recovery recipes

### Undo a bad `git reset --hard`
You reset and lost commits. Find the tip from before the reset:
```
git reflog
git reset --hard HEAD@{1}       # whatever entry was the good tip
```

### Recover a deleted branch
You ran `git branch -D feat/x` and need it back:
```
git reflog                      # find the last commit of that branch
# or, if HEAD never pointed there, search dangling commits:
git fsck --no-reflogs --unreachable | grep commit
git branch feat/x <sha>         # recreate the branch at that commit
```

### Recover after a botched rebase
```
git reflog
# find the entry labeled "rebase (start)" or the HEAD just before it
git reset --hard HEAD@{N}
```

### Rescue a detached HEAD
You checked out a commit, made commits, then switched away and got the "you are leaving commits behind" warning:
```
git reflog                      # find the sha of your detached work
git branch rescue <sha>         # or: git switch -c rescue <sha>
```
Next time, before leaving a detached HEAD, run `git switch -c <name>` first.

### You committed to the wrong branch (e.g. straight to main)
Move the commits to a feature branch and reset main back:
```
git branch feat/x               # mark current commits with a new branch
git reset --hard origin/main    # rewind main to upstream (your commits are safe on feat/x)
git switch feat/x
```
If you already pushed those commits to main, do NOT reset shared history — `git revert` them on main instead and re-apply on the feature branch.

### Recover a single lost commit (cherry-pick it back)
```
git reflog                      # or git fsck --unreachable
git cherry-pick <sha>
```

### Recover a dropped stash
```
git fsck --no-reflogs --unreachable | grep commit
# inspect candidates, then:
git stash apply <sha>
```
Stash entries are also in `git reflog stash` until cleared.

## Finding orphaned commits when the reflog isn't enough

```
git fsck --full --no-reflogs --unreachable --lost-found
```
Dangling commits are written under `.git/lost-found/commit/`. Inspect with `git show <sha>` and recover with `git branch`/`git cherry-pick`.

The bundled `scripts/git-recover.sh` automates surfacing these candidates with one-line previews.

## Safety habits

- Before `reset --hard`/`rebase`/force-push: `git tag backup/$(date +%s)` or just rely on the reflog.
- Enable longer reflog retention if you want a bigger safety net:
  ```
  git config --global gc.reflogExpire "180 days"
  git config --global gc.reflogExpireUnreachable "90 days"
  ```
- Don't run `git gc --prune=now` while trying to recover — it can delete the very objects you need.
