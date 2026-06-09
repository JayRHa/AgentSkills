# Badge Catalog (shields.io)

All badges below use [shields.io](https://shields.io). Replace `OWNER`, `REPO`,
`PACKAGE`, and `BRANCH` placeholders. Aim for 4-7 relevant badges — relevance
over decoration.

## Wrapping badges in links
Make badges clickable by wrapping the image in a link. Pattern:

```markdown
[![Build](https://img.shields.io/github/actions/workflow/status/OWNER/REPO/ci.yml)](https://github.com/OWNER/REPO/actions)
```

Put all header badges on consecutive lines (or one line) directly under the
tagline; they render as a single row.

---

## CI / Build

```markdown
![Build](https://img.shields.io/github/actions/workflow/status/OWNER/REPO/ci.yml)
![Build (branch)](https://img.shields.io/github/actions/workflow/status/OWNER/REPO/ci.yml?branch=main)
```

## Test Coverage

```markdown
![Codecov](https://img.shields.io/codecov/c/github/OWNER/REPO)
![Coveralls](https://img.shields.io/coverallsCoverage/github/OWNER/REPO)
```

## Package Version

```markdown
![npm](https://img.shields.io/npm/v/PACKAGE)
![PyPI](https://img.shields.io/pypi/v/PACKAGE)
![crates.io](https://img.shields.io/crates/v/PACKAGE)
![Maven Central](https://img.shields.io/maven-central/v/GROUP/ARTIFACT)
![Go module](https://img.shields.io/github/v/tag/OWNER/REPO?label=go.mod)
![NuGet](https://img.shields.io/nuget/v/PACKAGE)
![GitHub release](https://img.shields.io/github/v/release/OWNER/REPO)
```

## Downloads / Popularity

```markdown
![npm downloads](https://img.shields.io/npm/dm/PACKAGE)
![PyPI downloads](https://img.shields.io/pypi/dm/PACKAGE)
![Docker pulls](https://img.shields.io/docker/pulls/OWNER/IMAGE)
![GitHub stars](https://img.shields.io/github/stars/OWNER/REPO?style=social)
![GitHub forks](https://img.shields.io/github/forks/OWNER/REPO?style=social)
```

## License

```markdown
![License](https://img.shields.io/github/license/OWNER/REPO)
![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)
```

## Language / Runtime

```markdown
![Python](https://img.shields.io/pypi/pyversions/PACKAGE)
![Node](https://img.shields.io/node/v/PACKAGE)
![Top language](https://img.shields.io/github/languages/top/OWNER/REPO)
```

## Code Style / Quality

```markdown
![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)
![Code style: prettier](https://img.shields.io/badge/code_style-prettier-ff69b4.svg)
![Ruff](https://img.shields.io/badge/linting-ruff-261230.svg)
![Conventional Commits](https://img.shields.io/badge/Conventional%20Commits-1.0.0-yellow.svg)
```

## Community

```markdown
![Discord](https://img.shields.io/discord/SERVER_ID?label=discord)
![Contributors](https://img.shields.io/github/contributors/OWNER/REPO)
![Issues](https://img.shields.io/github/issues/OWNER/REPO)
![PRs welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)
```

## Custom static badge

Format: `https://img.shields.io/badge/<LABEL>-<MESSAGE>-<COLOR>`.
Spaces become `%20` or `_`, and a literal `-` becomes `--`.

```markdown
![status](https://img.shields.io/badge/status-beta-orange)
![made with](https://img.shields.io/badge/made%20with-TypeScript-3178c6)
```

Colors: `brightgreen`, `green`, `yellowgreen`, `yellow`, `orange`, `red`,
`blue`, `lightgrey`, `success`, `important`, `critical`, `informational`,
`inactive`, or any hex (e.g. `3178c6`).

## Style modifiers

Append `?style=<name>`: `flat` (default), `flat-square`, `plastic`, `for-the-badge`,
`social`. Add `&logo=<simpleicon>&logoColor=white` for an icon, e.g.
`?logo=github&logoColor=white`. Keep one style consistent across the row.
