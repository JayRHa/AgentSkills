# Interactive Rebase — Complete Guide

`git rebase -i <base>` opens an editor listing the commits between `<base>` and `HEAD`, oldest at the top. You edit the list to rewrite history. Saving and closing the editor executes your plan.

> Only ever do this on commits that have NOT been shared (or that only you have pushed to your own feature branch). Never on `main`/`develop`.

## Starting points

```
git rebase -i origin/main      # rewrite everything since you diverged from main
git rebase -i HEAD~5           # rewrite the last 5 commits
git rebase -i --root           # rewrite from the very first commit (rare)
```

## The todo list

```
pick a1b2c3d feat: add login form
pick b2c3d4e wip
pick c3d4e5f fix typo
pick d4e5f6a feat: validate password strength

# Rebase 9f8e7d6..d4e5f6a onto 9f8e7d6
#
# Commands:
# p, pick   = use commit
# r, reword = use commit, edit the message
# e, edit   = use commit, stop to amend
# s, squash = meld into previous commit, keep both messages
# f, fixup  = meld into previous commit, discard this message
# d, drop   = remove commit
# (lines can be reordered; they are executed top to bottom)
```

## Action keywords

| Keyword | Short | What it does |
|---------|-------|--------------|
| `pick` | `p` | Keep the commit unchanged |
| `reword` | `r` | Keep the diff, open editor to rewrite the message |
| `edit` | `e` | Pause AT this commit so you can amend it (add files, split it) |
| `squash` | `s` | Combine with the commit above; you edit a merged message |
| `fixup` | `f` | Combine with the commit above; throw away this message |
| `drop` | `d` | Delete the commit (its changes are removed) |
| `exec` | `x` | Run a shell command at this point (e.g. `x make test`) |
| `break` | `b` | Stop here so you can inspect things, then `--continue` |

## Reordering

Just move the lines. Commits execute top-to-bottom. Moving a commit earlier may cause a conflict if it depends on a later one — resolve normally.

## Worked scenarios

### Squash "wip" + "fix typo" into the real commit
Start:
```
pick a1b2c3d feat: add login form
pick b2c3d4e wip
pick c3d4e5f fix typo
```
Edit to:
```
pick a1b2c3d feat: add login form
fixup b2c3d4e wip
fixup c3d4e5f fix typo
```
Result: one clean `feat: add login form` commit.

### Reword a vague message
```
reword b2c3d4e wip
```
Git pauses and lets you write a real message.

### Split one commit into two
Mark it `edit`:
```
edit a1b2c3d feat: add login form
```
When Git pauses:
```
git reset HEAD~          # unstage the commit's changes, keep them in working tree
git add -p               # stage the first logical chunk
git commit -m "feat: add login form markup"
git add -p               # stage the rest
git commit -m "feat: wire up login submit handler"
git rebase --continue
```

### Drop a commit entirely
```
drop c3d4e5f accidental debug logging
```

### Run tests between every commit
Insert `exec` lines (or use `--exec`):
```
git rebase -i --exec "npm test" origin/main
```
The rebase stops if any commit fails the tests, so you can fix the offending commit.

## Autosquash — the pro workflow for review fixes

When a reviewer asks for a change to commit `a1b2c3d`:
```
# make the edit, stage it, then:
git commit --fixup=a1b2c3d
# or to also rewrite the original message:
git commit --squash=a1b2c3d
```
Later, collapse everything automatically:
```
git rebase -i --autosquash origin/main
```
Git pre-arranges the `fixup!`/`squash!` commits next to their targets and pre-marks them. Enable it by default:
```
git config --global rebase.autosquash true
```

## Aborting and continuing

| Command | When |
|---------|------|
| `git rebase --continue` | After resolving a conflict / finishing an `edit` |
| `git rebase --skip` | Drop the current commit and move on |
| `git rebase --abort` | Bail out, return to the exact pre-rebase state |

## If you mess up the rebase itself

The pre-rebase tip is saved. Find it and reset:
```
git reflog                       # look for "rebase (start)" / the old HEAD
git reset --hard HEAD@{N}        # N = the entry just before the rebase
```
See reflog-recovery.md.

## Pushing the rewritten branch

```
git push --force-with-lease
```
Never plain `--force` on anything shared. `--force-with-lease` aborts if upstream has commits you haven't fetched.
