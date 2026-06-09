# Branch Naming & Branching Models

## Naming convention

```
<type>/<short-kebab-slug>
```
Optionally include a tracker id: `feat/PROJ-123-oauth-login`.

| Prefix | Purpose |
|--------|---------|
| `feat/` | new feature |
| `fix/` | bug fix |
| `hotfix/` | urgent production fix |
| `chore/` | tooling, deps, housekeeping |
| `docs/` | documentation |
| `refactor/` | restructuring without behavior change |
| `test/` | tests only |
| `release/` | release preparation (e.g. `release/1.4.0`) |
| `experiment/` or `spike/` | throwaway exploration |

Guidelines:
- Lowercase, hyphen-separated, descriptive but short.
- Avoid spaces, uppercase (except tracker ids), and deep slashes.
- Delete merged branches to keep the list clean: `git branch -d feat/x` and `git push origin --delete feat/x`.

## Branching models

### Trunk-Based (recommended for most teams)
- One long-lived branch: `main`, always releasable.
- Short-lived feature branches merged via PR within a day or two.
- Feature flags hide incomplete work.
- Minimizes merge pain; pairs well with rebase-before-merge.

### GitHub Flow
- `main` is deployable.
- Branch off `main`, open a PR early, merge when green and reviewed.
- Simple, ideal for continuous deployment.

### Git Flow (heavier, release-oriented)
- Long-lived `main` (production) and `develop` (integration).
- Supporting branches: `feature/*` off develop, `release/*`, `hotfix/*` off main.
- Useful for scheduled releases / multiple supported versions; usually overkill for web apps shipping continuously.

## Keeping a branch current
- Private branch: `git fetch && git rebase origin/main` for linear history.
- Shared branch: `git merge origin/main` (never rebase what others have).

## Merge strategies into main
| Strategy | Result |
|----------|--------|
| Squash merge | one commit per PR; cleanest `main` history |
| Rebase merge | replays PR commits linearly onto main |
| Merge commit (`--no-ff`) | preserves branch shape and a merge point |

Pick one team-wide and stay consistent.
