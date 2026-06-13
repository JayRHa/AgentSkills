# Worked Example — Adding entries and cutting a release

## 1. Starting point

`CHANGELOG.md` after the last release (`1.4.2`):

```markdown
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.4.2] - 2026-05-20
### Security
- Updated bundled TLS library to patch CVE-2026-0991.

[Unreleased]: https://github.com/acme/widget/compare/v1.4.2...HEAD
[1.4.2]: https://github.com/acme/widget/compare/v1.4.0...v1.4.2
```

## 2. Three changes land

Raw commits:
```
add --json flag to export command
fix: crash when config file is empty
refactor: extract config loader (no behavior change)
```

Classify and rewrite (drop the internal refactor):

- `add --json flag` → **Added** → "Added `--json` flag to the `export` command for machine-readable output. (#88)"
- `fix crash on empty config` → **Fixed** → "Fixed a crash when the config file is empty. (#91)"
- `refactor config loader` → **omit** (no user impact)

Unreleased now reads:

```markdown
## [Unreleased]
### Added
- Added `--json` flag to the `export` command for machine-readable output. (#88)
### Fixed
- Fixed a crash when the config file is empty. (#91)
```

## 3. Choose the version

The Unreleased section contains an **Added** item → MINOR bump.
Current `1.4.2` → new **`1.5.0`** (reset PATCH to 0).

## 4. Cut the release (2026-06-08)

Mechanically with the helper:

```
python3 scripts/changelog_tool.py release CHANGELOG.md 1.5.0 2026-06-08 > CHANGELOG.tmp && mv CHANGELOG.tmp CHANGELOG.md
```

Then update the compare links by hand. Final file:

```markdown
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.5.0] - 2026-06-08
### Added
- Added `--json` flag to the `export` command for machine-readable output. (#88)
### Fixed
- Fixed a crash when the config file is empty. (#91)

## [1.4.2] - 2026-05-20
### Security
- Updated bundled TLS library to patch CVE-2026-0991.

[Unreleased]: https://github.com/acme/widget/compare/v1.5.0...HEAD
[1.5.0]: https://github.com/acme/widget/compare/v1.4.2...v1.5.0
[1.4.2]: https://github.com/acme/widget/compare/v1.4.0...v1.4.2
```

## 5. Validate and tag

```
python3 scripts/changelog_tool.py validate CHANGELOG.md
# VALID: 3 version section(s), newest first.
git add CHANGELOG.md && git commit -m "Release 1.5.0"
git tag v1.5.0
```

## Counter-example — when it's a MAJOR bump

If the Unreleased section instead contained:

```markdown
### Removed
- Removed the deprecated `/v1` REST API. Use `/v2` instead.
```

that is a breaking change → bump **MAJOR**: `1.4.2` → **`2.0.0`** (reset MINOR and PATCH to 0).
