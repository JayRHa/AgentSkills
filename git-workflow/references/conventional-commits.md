# Conventional Commits

A lightweight convention for commit messages that produces readable history and enables automated changelogs / semantic versioning.

## Format

```
<type>(<optional scope>): <short imperative summary>

<optional body — explain WHAT and WHY, not how; wrap ~72 cols>

<optional footer — BREAKING CHANGE:, Refs:, Closes #123, Co-Authored-By:>
```

Rules:
- Summary line: imperative mood ("add", not "added"/"adds"), no trailing period, ≤ 50 chars ideally, ≤ 72 hard max.
- Blank line between summary and body.
- Body explains motivation and context; the diff already shows the how.

## Types

| Type | Use for | SemVer |
|------|---------|--------|
| `feat` | a new feature | MINOR |
| `fix` | a bug fix | PATCH |
| `docs` | documentation only | – |
| `style` | formatting, whitespace, no code-meaning change | – |
| `refactor` | code change that neither fixes a bug nor adds a feature | – |
| `perf` | performance improvement | PATCH |
| `test` | adding or fixing tests | – |
| `build` | build system / dependencies | – |
| `ci` | CI configuration | – |
| `chore` | maintenance, tooling, no src/test change | – |
| `revert` | reverts a previous commit | – |

## Scope

Optional noun in parentheses naming the affected area: `feat(auth):`, `fix(api):`, `docs(readme):`.

## Breaking changes

Either append `!` after the type/scope, or add a `BREAKING CHANGE:` footer (or both). Triggers a MAJOR bump.
```
feat(api)!: remove deprecated v1 endpoints

BREAKING CHANGE: /v1/* routes are gone; migrate to /v2/*.
```

## Examples

```
feat(auth): add OAuth2 PKCE login flow
```
```
fix(parser): handle empty input without throwing

Return an empty AST instead of dereferencing a null token when the
source string is empty. Fixes the crash reported in #482.

Closes #482
```
```
refactor(db): extract connection pooling into its own module
```
```
chore(deps): bump eslint from 8.57 to 9.2
```

## Tips
- One concern per commit — if your summary needs "and", split the commit.
- Reference issues in the footer so they auto-link/close.
- For PR-review fixups, use `git commit --fixup=<sha>` rather than "address review comments" commits, then autosquash before merge.
