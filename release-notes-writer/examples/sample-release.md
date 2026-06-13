# Worked Example: from raw commits to finished release notes

## 1. Raw input (`git log v1.4.2..HEAD --oneline` style)

```
a1b2c3d feat(export): add CSV and JSON export to reports (#341)
b2c3d4e fix: crash when opening a report with no data (#352)
c3d4e5f perf: cache dashboard queries (#349)
d4e5f6a feat!: require API key for /v1/reports endpoints (#360)

  BREAKING CHANGE: all /v1/reports requests now require an `Authorization: Bearer <key>` header.
e5f6a7b chore: bump eslint to 9.0 (#361)
f6a7b8c refactor: split report service into modules (#362)
a7b8c9d fix(ui): date picker showed wrong month in Safari (#358)
b8c9d0e perf: lazy-load chart library, smaller initial bundle (#355)
c9d0e1f docs: update README badges (#363)
```

## 2. Run the parser (starting point)

```
python scripts/parse_commits.py --range v1.4.2..HEAD
```

The parser groups by type, flags `feat!` + `BREAKING CHANGE` as Breaking, suggests a **major** bump, and omits the `chore`/`refactor`/`docs` commits. Its raw output still reads like commit messages — so we rewrite.

## 3. Categorize + decide version
- Breaking present → **major** bump: `1.4.2 → 2.0.0`.
- Omit: eslint bump (#361), service refactor (#362), README badges (#363) — no user impact.

## 4. Rewrite into user-facing voice
- `feat(export)` → benefit-led, mention both formats.
- `feat!` → Breaking section with migration snippet.
- `perf` items → quantify ("smaller initial bundle", "dashboards load faster").
- `fix` items → describe the symptom that's gone.

## 5. Finished CHANGELOG.md entry

```markdown
## [2.0.0] - 2026-06-08

> Reports can now be exported to CSV and JSON, and the API is more secure. This release
> requires an API key for report endpoints — see the migration note below before upgrading.

### 💥 Breaking Changes
- **Breaking:** The `/v1/reports` endpoints now require authentication. Requests without a
  valid API key are rejected. (#360)
  - Migration: send your key on every report request:
    ```diff
    - GET /v1/reports
    + GET /v1/reports
    + Authorization: Bearer <your-api-key>
    ```
    Generate a key in Settings → API Keys.

### ✨ Features
- You can now export any report to CSV or JSON directly from the report toolbar. (#341)

### ⚡ Improvements
- Dashboards load noticeably faster thanks to cached queries. (#349)
- The app starts faster: the charting library now loads on demand, shrinking the initial
  download. (#355)

### 🐛 Bug Fixes
- Fixed a crash when opening a report that contained no data. (#352)
- Fixed the date picker showing the wrong month in Safari. (#358)

[2.0.0]: https://github.com/ORG/REPO/compare/v1.4.2...v2.0.0
```

## 6. Why this is correct
- Breaking change is at the top, with a concrete before/after and the action to take.
- Improvements are quantified qualitatively where exact numbers weren't available.
- Bug fixes describe the symptom users saw, not the code.
- Noise commits (lint, refactor, docs) were dropped.
- The version bump (major) matches the presence of breaking changes.
