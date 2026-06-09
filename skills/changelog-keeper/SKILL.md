---
name: changelog-keeper
description: Maintains a CHANGELOG.md in the Keep a Changelog format with Semantic Versioning, grouping user-facing entries under Added/Changed/Deprecated/Removed/Fixed/Security and cutting dated releases from an Unreleased section. Use this skill when the user asks to "update the changelog", "add a changelog entry", "cut a release", "bump the version", "what changed since the last release", or to create/clean up a CHANGELOG.md or release notes.
license: MIT
---

# Changelog Keeper

## Overview

Keywords: changelog, CHANGELOG.md, Keep a Changelog, keepachangelog, semantic versioning, semver, release notes, version bump, Unreleased, changelog entry, release.

This skill maintains a human-readable `CHANGELOG.md` following the [Keep a Changelog](https://keepachangelog.com) convention and [Semantic Versioning](https://semver.org). It writes entries that describe *what changed for users*, not raw commit messages, groups them under the six canonical change types, accumulates them under `## [Unreleased]`, and cuts dated, versioned releases when shipping.

Use it to: start a new changelog, add an entry for a change, cut a release (move Unreleased to a dated version + bump the version number), draft release notes from a git diff/log, or audit/repair an existing changelog's structure.

The six canonical groups (use these exact names, in this order):
**Added · Changed · Deprecated · Removed · Fixed · Security**

## Workflow

1. **Locate or create the changelog.** Look for `CHANGELOG.md` at the repo root. If none exists, create one from `templates/CHANGELOG.template.md`. Never invent a parallel file (e.g. `changes.txt`).

2. **Classify the change** into exactly one of the six groups. Use the decision table below. If a change spans groups (e.g. removed a flag *and* added its replacement), write one entry per group.

3. **Write a user-facing entry.** Each entry is a single bullet, imperative or descriptive, focused on observable behavior. Translate commit-speak into user-speak. See `references/keep-a-changelog.md` for entry-writing rules and good/bad examples.

4. **Place it under `## [Unreleased]`** in the correct `### Group` subsection. Create the subsection if absent. Keep the canonical group order. Do NOT add a date — Unreleased is undated by definition.

5. **Link issues/PRs** at the end of the bullet when available (e.g. `(#412)`), and credit external contributors when appropriate.

6. **Cut a release when asked to ship/tag/bump.**
   - Pick the new version using SemVer (see decision rule below).
   - Rename `## [Unreleased]` content to `## [x.y.z] - YYYY-MM-DD` (today's date, ISO 8601).
   - Insert a fresh empty `## [Unreleased]` above it.
   - Update comparison links at the bottom if the file uses them.
   - The helper does steps 2–3 mechanically: `python3 scripts/changelog_tool.py release CHANGELOG.md 1.3.0 2026-06-08`.

7. **Validate.** Run `python3 scripts/changelog_tool.py validate CHANGELOG.md` to confirm structure, group names, dates, and newest-first ordering.

## Decision framework — which group?

| If the change…                                              | Group        |
|-------------------------------------------------------------|--------------|
| introduces a new feature, endpoint, option, or capability   | **Added**    |
| alters existing behavior, defaults, output, or wording      | **Changed**  |
| marks something as soon-to-be-removed (still works for now)  | **Deprecated**|
| deletes a feature, flag, endpoint, or file (now gone)        | **Removed**  |
| corrects a bug, crash, regression, or wrong result          | **Fixed**    |
| addresses a vulnerability or hardens against attack          | **Security** |

Internal-only changes (refactors, test additions, CI tweaks, dependency bumps with no user impact) usually do NOT belong in the changelog. If a dependency bump fixes a CVE, log it under **Security**; if it changes behavior, **Changed**.

## Decision rule — which version (SemVer)?

Given `MAJOR.MINOR.PATCH`:
- **MAJOR** — any breaking change: something under **Removed**, or a backward-incompatible item under **Changed**.
- **MINOR** — new functionality, backward-compatible: items under **Added** or **Deprecated** (and no breaking changes).
- **PATCH** — backward-compatible bug fixes only: **Fixed** / **Security** with no Added/Removed/breaking Changed.
- Pre-1.0.0 (`0.y.z`): treat MINOR as the "breaking allowed" lever; anything can change.
- Pre-releases: append `-alpha.1`, `-rc.2`, etc. (e.g. `2.0.0-rc.1`).

Pick the *highest* bump implied by the accumulated Unreleased entries.

## Worked example

Starting Unreleased:
```
## [Unreleased]
### Added
- `--json` flag for machine-readable output (#88)
### Fixed
- Crash when config file is empty (#91)
```
This contains an `Added` item → **MINOR** bump. Current version `1.4.2` → new `1.5.0`. Cutting the release on 2026-06-08 produces:
```
## [Unreleased]

## [1.5.0] - 2026-06-08
### Added
- `--json` flag for machine-readable output (#88)
### Fixed
- Crash when config file is empty (#91)
```
See `examples/release-walkthrough.md` for the full before/after including comparison links.

## Drafting from git history

When asked "what changed since the last release", gather raw material then translate it:
```
git log v1.4.2..HEAD --pretty=format:'%s' --no-merges
```
Do not paste commit subjects verbatim. Map each meaningful commit to a group and rewrite it as a user-facing bullet. Drop noise (merge commits, `wip`, formatting-only). Reference `references/keep-a-changelog.md` for the rewrite patterns.

## Best Practices

- Keep one `## [Unreleased]` at the top, always present, always undated.
- Newest version first; oldest last. Dates in `YYYY-MM-DD` (ISO 8601).
- Wrap version numbers in brackets: `## [1.5.0]`. Use bracketed link references at the bottom for GitHub compare URLs when the project uses them.
- Write for the reader who upgrades, not the developer who committed. "Fixed timezone offset in exported timestamps" beats "fix tz bug".
- One bullet = one change. Lead with the verb/noun, keep it to a line.
- Add a `### Security` note for every security-relevant fix, even small ones.
- Add a top blurb line: "All notable changes to this project will be documented in this file."
- Run the validator before committing.

## Common Pitfalls

- **Dumping git log into the file.** Commit messages are not changelog entries. Always rewrite.
- **Inventing group names.** Only the six canonical groups are valid; the validator rejects others.
- **Dating the Unreleased section.** It must stay undated until released.
- **Wrong version order** (oldest first) or **missing dates** on released versions — both flagged by the validator.
- **Over-logging.** Internal refactors and no-op dependency bumps clutter the file; omit them.
- **Under-bumping.** A `Removed` or breaking `Changed` entry forces a MAJOR bump even if "it feels minor".
- **Forgetting comparison links.** If the file uses `[1.5.0]: https://.../compare/v1.4.2...v1.5.0` references, update them on every release.
