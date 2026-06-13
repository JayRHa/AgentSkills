# Keep a Changelog — Reference

Canonical rules distilled from keepachangelog.com (v1.1.0) plus practical entry-writing guidance.

## File anatomy

```
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.5.0] - 2026-06-08
### Added
- ...
### Fixed
- ...

## [1.4.2] - 2026-05-20
### Security
- ...

[Unreleased]: https://github.com/org/repo/compare/v1.5.0...HEAD
[1.5.0]: https://github.com/org/repo/compare/v1.4.2...v1.5.0
[1.4.2]: https://github.com/org/repo/releases/tag/v1.4.2
```

## The six groups (exact names, this order)

| Group       | Meaning                                                        |
|-------------|----------------------------------------------------------------|
| Added       | New features / capabilities now available.                     |
| Changed     | Changes to existing functionality (defaults, output, behavior).|
| Deprecated  | Features still present but slated for removal; warn users.      |
| Removed     | Features deleted in this release.                              |
| Fixed       | Bug fixes.                                                     |
| Security    | Vulnerability fixes / hardening.                              |

Omit empty groups. Never rename or add groups.

## Guiding principles (from the spec)

- Changelogs are **for humans**, not machines.
- There is an **entry for every version**.
- The **same types of changes are grouped**.
- **Versions and sections are linkable** (anchors / compare URLs).
- The **latest version comes first**.
- The **release date of each version is displayed** (`YYYY-MM-DD`).
- State whether the project **follows SemVer**.

## Writing user-facing entries

Rewrite developer-speak into reader-speak. Lead with the observable change.

| Commit message (raw)                 | Good changelog entry                                         | Group    |
|--------------------------------------|-------------------------------------------------------------|----------|
| `fix npe in parser`                  | Fixed crash when parsing files without a trailing newline.  | Fixed    |
| `add --json flag`                    | Added `--json` flag for machine-readable output. (#88)      | Added    |
| `bump tz lib for cve-2026-1234`      | Updated date library to patch CVE-2026-1234.                 | Security |
| `change default timeout 30->10`      | Changed default request timeout from 30s to 10s.            | Changed  |
| `remove deprecated /v1 api`          | Removed the deprecated `/v1` REST API. Use `/v2`.           | Removed  |
| `mark legacy export deprecated`      | Deprecated the XML export; it will be removed in 3.0.0.      | Deprecated|
| `refactor internal cache`            | (omit — no user-visible impact)                             | —        |

### Style rules
- One change per bullet; one line per bullet.
- Start with the change itself; reference IDs go at the end: `... (#412)`.
- Use backticks for flags, commands, code identifiers, and file paths.
- Prefer concrete nouns/verbs: "Fixed timezone offset in exported timestamps" not "fixed bug".
- Mention migration hints for Removed/Deprecated/breaking Changed ("Use `X` instead").
- Credit external contributors: `... (#412, thanks @user)`.

## SemVer cheat sheet

`MAJOR.MINOR.PATCH[-prerelease][+build]`

- Breaking change (Removed, or incompatible Changed) → bump **MAJOR**, reset MINOR & PATCH to 0.
- New backward-compatible feature (Added / Deprecated) → bump **MINOR**, reset PATCH to 0.
- Backward-compatible fix only (Fixed / Security) → bump **PATCH**.
- Highest applicable bump wins across all Unreleased entries.
- `0.y.z`: still initial development; the public API may break on MINOR bumps.
- Pre-release: `1.0.0-alpha.1 < 1.0.0-beta.1 < 1.0.0-rc.1 < 1.0.0`.

## Release checklist

- [ ] Every Unreleased item is grouped under a canonical `### Group`.
- [ ] Determine bump type from the accumulated entries (highest wins).
- [ ] Replace `## [Unreleased]` content with `## [x.y.z] - YYYY-MM-DD`.
- [ ] Add a fresh empty `## [Unreleased]` at the top.
- [ ] Update/add bottom compare links (`[Unreleased]`, `[x.y.z]`).
- [ ] Run `changelog_tool.py validate`.
- [ ] Tag the release in VCS to match (e.g. `git tag v1.5.0`).
