# Conflict Resolution Protocol

A conflict happens when two changes touch the same lines and Git can't auto-merge. The operation (merge, rebase, cherry-pick, stash pop) pauses and marks the files.

## Step-by-step

1. **See what's conflicted**
   ```
   git status
   ```
   Conflicted files appear under "Unmerged paths".

2. **Open each file and find the markers**
   ```
   <<<<<<< HEAD
   code from your current branch
   =======
   code from the incoming change
   >>>>>>> feature-x
   ```

3. **Decide the correct result.** Often it's not "pick one side" — it's combining both. Delete all three marker lines and leave the final intended code.

4. **Mark resolved & continue**
   ```
   git add <file>
   git rebase --continue      # during a rebase
   git merge --continue       # during a merge
   git cherry-pick --continue # during a cherry-pick
   ```

5. **Bail out** anytime to return to the pre-operation state:
   ```
   git rebase --abort
   git merge --abort
   git cherry-pick --abort
   ```

## CRITICAL: marker sides differ between merge and rebase

- **During a MERGE:** `HEAD` (top) = the branch you are ON (yours). Bottom = the branch being merged IN.
- **During a REBASE:** the sides are *swapped*. `HEAD` (top) = the upstream/base commits being replayed onto; the bottom (`>>>>>>>`) = YOUR commit being replayed. This trips people up constantly — during a rebase, "your" changes are the bottom side.

When unsure which side is which, use the verbose form:
```
git config merge.conflictStyle diff3
```
This adds a third section showing the common ancestor:
```
<<<<<<< ours
...
||||||| base
original common code
=======
...
>>>>>>> theirs
```
Seeing the base makes the correct merge obvious.

## Useful inspection during a conflict

```
git diff                       # show the conflict hunks
git log --merge -p <file>      # commits from both sides touching this file
git checkout --ours <file>     # take your side wholesale (merge semantics)
git checkout --theirs <file>   # take their side wholesale
git checkout --conflict=diff3 <file>  # re-show with base section
```
Note: `--ours`/`--theirs` also swap meaning during a rebase — `--ours` is the base, `--theirs` is your replayed commit.

## rerere — reuse recorded resolution

For long-lived branches or repeated rebases where the same conflict keeps reappearing:
```
git config --global rerere.enabled true
```
Git records how you resolved a conflict and replays that resolution automatically next time the identical conflict appears. Huge time-saver during iterative rebases.

## Resolving with a merge tool

```
git mergetool                  # launches your configured visual tool
```
Configure one (examples):
```
git config --global merge.tool vimdiff
# or: meld, kdiff3, vscode (code --wait), etc.
```
For VS Code:
```
git config --global merge.tool vscode
git config --global mergetool.vscode.cmd 'code --wait $MERGED'
```
After resolving in the tool, `git add` is usually automatic; then `--continue`.

## Conflict checklist

- [ ] Searched every file for remaining `<<<<<<<`, `=======`, `>>>>>>>` markers (`git grep -n '<<<<<<<'`).
- [ ] The resolved code compiles / tests pass — a syntactically valid merge can still be logically wrong.
- [ ] `git add`ed every resolved file.
- [ ] Correct side semantics confirmed (especially during rebase).
- [ ] Ran `--continue` (not just saved the files).

## Avoiding conflicts

- Rebase / merge from the base frequently so divergence stays small.
- Keep commits and PRs small and focused.
- Coordinate on files that multiple people edit heavily.
- Enable `rerere` for repeated rebases.
