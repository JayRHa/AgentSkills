# Worked Example: README for a CLI Tool

This shows the expected output of the skill for a fictional CLI named **gitleaf**
(a Git branch visualizer). It demonstrates grounded facts, a strong quick start,
a commands table, and a complete closing block.

---

## Input the skill was given

- Detected: Node.js CLI, published to npm as `gitleaf`, MIT license, repo
  `acme/gitleaf`, has a `gitleaf` bin and subcommands `tree`, `diff`, `prune`.
- User-provided tagline: "Visualize your Git branches as a living tree."

## Generated README.md

````markdown
# gitleaf

> Visualize your Git branches as a living tree.

[![Build](https://img.shields.io/github/actions/workflow/status/acme/gitleaf/ci.yml)](https://github.com/acme/gitleaf/actions)
[![npm](https://img.shields.io/npm/v/gitleaf)](https://www.npmjs.com/package/gitleaf)
[![Downloads](https://img.shields.io/npm/dm/gitleaf)](https://www.npmjs.com/package/gitleaf)
[![License](https://img.shields.io/github/license/acme/gitleaf)](./LICENSE)

![gitleaf rendering a branch tree in the terminal](docs/demo.gif)

## Features
- **At-a-glance topology** — see all branches and their merge bases as a tree.
- **Stale-branch detection** — highlights branches with no commits in 30+ days.
- **Zero config** — runs in any Git repository, no setup required.

## Quick Start
```bash
npm install -g gitleaf
cd your-repo
gitleaf tree
```
You'll see a colorized tree of every branch and where it diverged from `main`.

## Installation

### npm (recommended)
```bash
npm install -g gitleaf
```

### From source
```bash
git clone https://github.com/acme/gitleaf
cd gitleaf
npm install && npm link
```

**Requirements:** Node.js 18+ and Git 2.30+.

## Usage
Render the current repo's branch tree:
```bash
gitleaf tree
```

Compare two branches:
```bash
gitleaf diff main feature/login
```

Delete merged branches interactively:
```bash
gitleaf prune --merged
```

## Commands
| Command            | Description                                  |
|--------------------|----------------------------------------------|
| `tree`             | Render all branches as a tree from `main`    |
| `diff <a> <b>`     | Show commits unique to each branch           |
| `prune [--merged]` | Delete merged or stale branches              |
| `--help`           | Show usage for any command                    |

## Configuration
| Option        | Type    | Default  | Description                        |
|---------------|---------|----------|------------------------------------|
| `--base`      | string  | `main`   | Branch to compute divergence from  |
| `--stale-days`| number  | `30`     | Days of inactivity to flag stale   |
| `--no-color`  | boolean | `false`  | Disable ANSI colors                |

## Contributing
Contributions are welcome! Please read [CONTRIBUTING.md](./CONTRIBUTING.md).
```bash
git clone https://github.com/acme/gitleaf
npm install && npm test
```

## License
[MIT](./LICENSE) © Acme Inc.
````

---

## Why this is good
- Title + tagline + badges convey what/why instantly.
- Quick Start reaches a result in three copy-paste lines.
- Real npm package name and bin/subcommands (grounded, not invented).
- Flags and commands are tables, not prose.
- License and Contributing are present and linked.
