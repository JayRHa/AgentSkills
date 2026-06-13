# Dependency Upgrade Report

**Repo:** <name>  
**Date:** <YYYY-MM-DD>  
**Baseline commit (rollback anchor):** `<SHA>`  
**Ecosystem:** <npm | pip | cargo | go | ...>  
**Verification command:** `<e.g. npm test && npm run build>`

## Summary
- Upgraded: <N> packages (<M> major, <K> minor/patch)
- Deferred: <count>
- Security advisories resolved: <count>
- Final test status: <green / green with notes>

## Upgraded

| Package | Old | New | Tier | Code changes | Changelog |
|---------|-----|-----|------|--------------|-----------|
| <pkg>   | x.y.z | a.b.c | major | <renamed API X, config key Y> | <url> |
| <pkg>   | x.y.z | x.y.w | patch | none | — |

Each major upgrade is an isolated commit:
- `<sha>` chore(deps): upgrade <pkg> x.y.z -> a.b.c
- `<sha>` chore(deps): upgrade <pkg> ...

## Security
- <CVE-id / advisory>: resolved by <pkg> <version>. Auditor re-run: clean.
- <CVE-id>: NO fixed version available. Mitigation: <...>. Tracking: <issue>.

## Deferred (and why)
- <pkg> <cur> -> <target>: blocked by <peer dep / ESM-only / breaking change
  needing larger refactor>. Recommendation: <...>.

## Verification performed
- [ ] Test suite green on final state
- [ ] Build succeeds
- [ ] Smoke test / app boots (if applicable)
- [ ] Auditor re-run shows advisories resolved
- [ ] Lockfile committed alongside each manifest change

## Rollback
To undo a single upgrade: `git revert <sha> && <resync cmd>`.  
To undo everything: `git reset --hard <BASELINE> && <resync cmd>`.
