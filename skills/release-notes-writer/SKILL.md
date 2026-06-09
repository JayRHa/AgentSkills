---
name: release-notes-writer
description: Transforms merged pull requests, commit logs, and changelog entries into clear, user-facing release notes grouped into Features, Improvements, Bug Fixes, and Breaking Changes. Use this skill when asked to "write release notes", "draft a changelog", "summarize this release", "turn these PRs/commits into release notes", "prepare the v1.2 release announcement", or to convert a list of merged changes into a polished, audience-appropriate notes document.
license: MIT
---

# Release Notes Writer

## Overview
This skill turns raw engineering output — merged PRs, commit messages, issue references, and changelog fragments — into release notes that a real user can read and act on. It enforces a consistent structure, a user-facing voice (benefit first, not implementation detail), correct categorization (especially surfacing breaking changes), and an upgrade/migration section when needed.

Keywords: release notes, changelog, CHANGELOG.md, version bump, breaking changes, migration guide, semver, what's new, release announcement, GitHub release, conventional commits.

Use this skill whenever the user has a set of changes (any of: PR titles, `git log` output, conventional-commit messages, a list of Jira/GitHub issues, or an existing draft) and wants them shaped into publishable notes.

## When NOT to use
- A single trivial change with no user impact — just describe it.
- Internal-only commit summaries with no audience — use a plain commit log.
- Writing the code itself — this skill writes the *notes*, not the changes.

## Inputs to gather first
Before drafting, confirm or infer:
1. **Version & date** — e.g. `v2.4.0`, `2026-06-08`. Infer semver bump from the changes (see references/categorization.md).
2. **Audience** — end users, API consumers/developers, or internal team. This changes vocabulary and depth.
3. **Source material** — PR list, commit log, or changelog fragments.
4. **Format target** — Markdown `CHANGELOG.md` (Keep a Changelog style), a GitHub Release body, a blog-style announcement, or in-app "What's New".
If any are missing, ask once, concisely. Do not block on perfect input — infer sensible defaults and state your assumptions.

## Workflow
1. **Collect changes.** If given a git range, run the helper: `python scripts/parse_commits.py --range v2.3.0..HEAD` (or pipe `git log`). It parses conventional commits, groups them, and flags `!`/`BREAKING CHANGE` as breaking. Review its output — never publish it raw.
2. **Filter noise.** Drop chore/ci/build/refactor/test/docs commits that have zero user impact. Merge duplicates and revert+reland pairs. Keep anything a user can see, feel, or must react to.
3. **Categorize** every surviving change into exactly one of: Breaking Changes, Features (✨ new), Improvements (⚡ enhancements/perf/UX), Bug Fixes (🐛), Deprecations, Security. Use the decision table in references/categorization.md.
4. **Rewrite each line** into the user-facing voice: lead with the benefit/outcome, present tense, active voice, no internal jargon, no PR/branch names in prose. Append issue/PR references in parentheses. See the rewrite patterns below and references/style-guide.md.
5. **Determine the version bump** from the highest-severity category present (breaking → major, feature → minor, fix-only → patch). State it.
6. **Write the Breaking Changes + Migration section first** if any exist — this is the highest-value content. Give before/after and concrete migration steps.
7. **Assemble** using templates/changelog-entry.md (for CHANGELOG.md) or templates/github-release.md (for a release body). Add a one-line highlight summary at the top.
8. **Self-check** against references/checklist.md. Verify ordering (Breaking → Security → Features → Improvements → Fixes → Deprecations), no empty sections, every breaking change has migration guidance, and links resolve.

## Rewrite patterns (commit -> note)
| Raw input | Rewritten user-facing note |
|---|---|
| `fix: npe in auth when token nil` | Fixed a crash that occurred when signing in with an expired session. (#412) |
| `feat(api): add cursor pagination to /users` | The `/users` endpoint now supports cursor-based pagination for faster, stable listing of large datasets. (#388) |
| `perf: cache config lookups` | Configuration screens now load up to 40% faster. (#401) |
| `feat!: rename --output to --out` | **Breaking:** The `--output` flag is renamed to `--out`. Update scripts accordingly. (#420) |

Rules: describe the *effect on the user*, not the code path. Quantify when you can. One sentence per item where possible.

## Voice and style (essentials)
- Present tense, active voice: "Adds…", "Fixes…", or noun-led "New export option for…".
- Second person for instructions ("You can now…"), never first person ("We added…") in changelogs; the announcement format may use "we".
- No internal identifiers (service names, ticket-only codes, engineer names) in user notes.
- Consistent terminology — pick one product noun and reuse it.
- Full detail lives in references/style-guide.md.

## Best Practices
- **Lead with breaking changes and highlights.** Readers skim; put what forces action up top.
- **One change, one line.** Split multi-purpose PRs into separate notes.
- **Quantify improvements** ("2x faster", "30% smaller bundle") whenever metrics exist.
- **Always pair a breaking change with a migration step.** A breaking change with no "what to do" is a support ticket waiting to happen.
- **Link everything** — PR/issue numbers, docs, migration guides.
- **Match semver to content.** If you wrote breaking changes under a patch bump, the bump is wrong.
- **Keep an `Unreleased` section** in CHANGELOG.md so notes accrue continuously.

## Common Pitfalls
- Copying commit messages verbatim (implementation jargon, no benefit).
- Burying a breaking change inside "Improvements".
- Mixing audiences — dumping API-internal changes into end-user notes.
- Empty category headers, or every change dumped under "Other".
- Vague entries: "Various bug fixes and improvements" with nothing actionable.
- Forgetting the date, version, or comparison link (`v2.3.0...v2.4.0`).
- Listing reverted-then-reapplied changes twice.

## Bundled files
- `references/style-guide.md` — voice, tense, terminology, emoji policy, and good/bad examples.
- `references/categorization.md` — decision table for category + semver, conventional-commit mapping.
- `references/checklist.md` — pre-publish QA checklist.
- `scripts/parse_commits.py` — parses a git range / commit log into categorized JSON or Markdown.
- `templates/changelog-entry.md` — Keep a Changelog style entry.
- `templates/github-release.md` — GitHub Release body template.
- `examples/sample-release.md` — full worked example from raw commits to finished notes.
