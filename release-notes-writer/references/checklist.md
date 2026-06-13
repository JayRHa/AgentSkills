# Release Notes Pre-Publish Checklist

Run through this before publishing. Treat each unchecked item as a blocker.

## Metadata
- [ ] Version number present and matches the semver bump implied by the content.
- [ ] Release date present (ISO `YYYY-MM-DD`).
- [ ] Comparison/diff link present (`v2.3.0...v2.4.0`) when a repo URL is known.

## Structure
- [ ] Categories appear in order: Breaking → Security → Features → Improvements → Bug Fixes → Deprecations.
- [ ] No empty category headers.
- [ ] No "Other / Misc" dumping ground.
- [ ] Optional highlight summary at the top for non-trivial releases.

## Content quality
- [ ] Every entry describes user impact, not internal implementation.
- [ ] Present tense, active voice, one idea per bullet.
- [ ] No engineer names, branch names, or internal-only ticket codes in prose.
- [ ] Improvements quantified where real metrics exist.
- [ ] Consistent product terminology throughout.

## Breaking changes
- [ ] Each breaking change is in the Breaking section (not hidden under Improvements).
- [ ] Each has migration guidance (old → new + concrete action).
- [ ] Before/after snippet for API/CLI/config changes.

## Links & references
- [ ] PR/issue references appended to entries.
- [ ] Links resolve (no placeholder URLs).
- [ ] Migration guide / docs linked where relevant.

## Hygiene
- [ ] Duplicate changes merged.
- [ ] Revert + re-land pairs not double-listed.
- [ ] Pure chore/ci/test/refactor commits omitted.
- [ ] Spell-check / grammar pass done.
