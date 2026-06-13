# Section Catalog

Reference for every README section: purpose, contents, and when to include it.
Use the matrix at the bottom to pick sections by project type.

---

## Header Block

### Title (H1) — always
Exactly one `#` heading: the human-friendly project name. Optionally include a
logo image above it. Never use multiple H1s anywhere in the document.

### Tagline — always
A single line directly under the title describing what the project does in
plain language, ideally under 12 words. Rendered as a blockquote works well:

```markdown
> A fast, zero-config static site generator for Markdown.
```

### Badges — recommended
A row of 4-7 status badges (build, version, coverage, license). Keep them
relevant. See `badges.md`.

### Hero / Demo — when it adds clarity
A screenshot for visual apps, an animated GIF for CLIs/TUIs, or an asciinema
link. Always provide alt text. Skip for pure libraries where it adds nothing.

---

## Table of Contents — long READMEs only
Include only when the README has roughly 6+ H2 sections. Link to anchors
(GitHub auto-generates anchors as lowercase, spaces→hyphens, punctuation
removed).

```markdown
## Table of Contents
- [Features](#features)
- [Quick Start](#quick-start)
- [Usage](#usage)
- [Configuration](#configuration)
- [Contributing](#contributing)
- [License](#license)
```

---

## Features — recommended
3-6 bullets, each benefit-first (what the user gets), not implementation-first.
Use a leading emoji or bold lead-in for scannability but don't overdo it.

```markdown
## Features
- **Zero config** — works out of the box, no setup file required.
- **Fast** — incremental builds in milliseconds.
- **Extensible** — plugin API for custom transforms.
```

---

## Quick Start — almost always
The highest-value section. Get the reader to a working result with copy-paste.
Keep it to the shortest happy path. Example:

```markdown
## Quick Start
```bash
npm install -g mytool
mytool init my-project
cd my-project && mytool dev
```
Open http://localhost:3000.
```

---

## Installation — when install is non-trivial or has multiple methods
List every supported method (package manager, binary download, source, Docker).
Note prerequisites and supported versions/platforms.

```markdown
## Installation

### npm
```bash
npm install mypackage
```

### From source
```bash
git clone https://github.com/OWNER/REPO
cd REPO && make install
```
```

---

## Usage — almost always
Show the most common tasks with real, runnable code. Order from simplest to
more advanced. For libraries, show the canonical import + call.

---

## Configuration — when configurable
Prefer a table. Document defaults and accepted values. Cover both config-file
keys and environment variables.

```markdown
## Configuration
| Option      | Type    | Default | Description                  |
|-------------|---------|---------|------------------------------|
| `port`      | number  | `3000`  | Port the dev server binds to |
| `verbose`   | boolean | `false` | Enable debug logging         |

### Environment variables
| Variable      | Description                  |
|---------------|------------------------------|
| `API_TOKEN`   | Auth token for the remote API |
```

---

## API / Commands — for libraries and CLIs
Reference-style documentation of public functions or subcommands/flags. For
large surfaces, summarize here and link to full docs.

```markdown
## Commands
| Command         | Description                |
|-----------------|----------------------------|
| `init [name]`   | Scaffold a new project     |
| `build`         | Produce a production build  |
| `--help`        | Show help                  |
```

---

## Examples — when usage benefits from scenarios
Real end-to-end scenarios beyond the basic usage snippet. Link to an
`examples/` directory if one exists.

---

## Roadmap — optional
A short checklist of planned work. Keep current or omit.

```markdown
## Roadmap
- [x] Core engine
- [ ] Plugin system
- [ ] Windows binaries
```

---

## Contributing — recommended
Link to `CONTRIBUTING.md` if present; otherwise a short inline blurb covering
how to file issues, the PR flow, and how to run tests locally.

```markdown
## Contributing
Contributions are welcome! Please read [CONTRIBUTING.md](./CONTRIBUTING.md)
first. To get started:
```bash
git clone https://github.com/OWNER/REPO
npm install && npm test
```
```

---

## License — always
State the license and link the `LICENSE` file. One line is enough.

```markdown
## License
[MIT](./LICENSE) © Your Name
```

---

## Acknowledgments — optional
Credit inspirations, dependencies, or contributors.

---

## Project-Type Matrix

| Section        | Library | CLI | Web App | Service/API | Mono-repo | Tiny |
|----------------|:-------:|:---:|:-------:|:-----------:|:---------:|:----:|
| Title+Tagline  |   ✓     | ✓   |   ✓     |     ✓       |    ✓      |  ✓   |
| Badges         |   ✓     | ✓   |   ✓     |     ✓       |    ✓      |  ·   |
| Hero/Demo      |   ·     | ✓   |   ✓✓    |     ·       |    ·      |  ·   |
| TOC            |   ?     | ?   |   ?     |     ?       |    ✓      |  ·   |
| Features       |   ✓     | ✓   |   ✓     |     ✓       |    ✓      |  ?   |
| Quick Start    |   ✓     | ✓✓  |   ✓✓    |     ✓       |    ?      |  ✓   |
| Installation   |   ✓✓    | ✓   |   ✓     |     ✓       |    ✓      |  ✓   |
| Usage          |   ✓✓    | ✓   |   ✓     |     ✓       |    ?      |  ✓   |
| Configuration  |   ?     | ✓   |   ✓     |     ✓✓      |    ?      |  ·   |
| API/Commands   |   ✓✓    | ✓✓  |   ?     |     ✓✓      |    ?      |  ·   |
| Examples       |   ✓     | ✓   |   ?     |     ✓       |    ✓      |  ·   |
| Contributing   |   ✓     | ✓   |   ✓     |     ✓       |    ✓      |  ?   |
| License        |   ✓     | ✓   |   ✓     |     ✓       |    ✓      |  ✓   |

Legend: `✓✓` essential · `✓` include · `?` situational · `·` usually omit
