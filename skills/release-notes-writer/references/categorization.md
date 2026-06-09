# Categorization & Versioning Reference

Use this to (a) place each change in exactly one category and (b) decide the semver bump.

## Categories (in display order)
1. **Breaking Changes** — anything that forces a consumer to change their code, config, commands, or workflow to keep working.
2. **Security** — vulnerability fixes, hardening, dependency CVE patches with user relevance.
3. **Features** — net-new user-visible capability that did not exist before.
4. **Improvements** — enhancements to existing features, performance gains, UX/quality-of-life polish.
5. **Bug Fixes** — corrections to behavior that was wrong.
6. **Deprecations** — still works, but scheduled for removal; tell users the replacement and timeline.

Notes that don't fit any of the above (internal refactors, CI, tests, formatting, dependency bumps with no user effect) are **omitted** from user-facing notes. Do not create an "Other / Misc" dumping ground.

## Decision table

| Question | If yes → |
|---|---|
| Does the user have to change something to keep working? | Breaking Changes |
| Is it a security vuln/CVE fix or hardening users care about? | Security |
| Is it a capability that didn't exist before? | Features |
| Does it make an existing thing faster/nicer/more capable? | Improvements |
| Did it correct behavior that was wrong/broken? | Bug Fixes |
| Does it still work but warn it'll be removed later? | Deprecations |
| None of the above (chore/ci/test/refactor/style/internal dep)? | Omit |

If two apply, the **higher row wins** (a security fix that's also breaking goes under Breaking with a security note).

## Conventional Commits → category

| Commit type | Category | Notes |
|---|---|---|
| `feat:` | Features | |
| `feat!:` / `BREAKING CHANGE:` | Breaking Changes | also a feature, but breaking dominates |
| `fix:` | Bug Fixes | |
| `fix!:` | Breaking Changes | |
| `perf:` | Improvements | quantify if possible |
| `security:` / `fix(security)` | Security | |
| `deprecate:` | Deprecations | |
| `refactor:` `test:` `chore:` `ci:` `build:` `style:` `docs:` | Omit | unless it has direct user impact (e.g. user-facing docs link, build output users consume) |

For non-conventional messages, infer from the verb and the diff intent.

## Semver bump
Pick the bump from the **highest-severity** category present:

| Highest category present | Bump | Example |
|---|---|---|
| Breaking Changes | **major** | 2.3.1 → 3.0.0 |
| Features (no breaking) | **minor** | 2.3.1 → 2.4.0 |
| Only Improvements/Fixes/Security | **patch** | 2.3.1 → 2.3.2 |
| Pre-1.0 (0.x) | breaking → minor, features/fixes → patch | 0.4.2 → 0.5.0 |

Validation rule: if the notes contain a Breaking Changes section but the version is a patch/minor bump, the version is wrong — flag it.

## Migration guidance requirement
Every Breaking Change entry MUST include, inline or in a Migration section:
- **What changed** (old → new).
- **What the user must do** (concrete step / command / code edit).
- A before/after snippet when the change is to an API, CLI, or config.
