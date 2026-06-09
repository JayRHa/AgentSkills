#!/usr/bin/env python3
"""Detect facts about a project to ground a generated README.

Inspects a repository directory and reports the language/ecosystem, package
manager, likely install command, entry points, available scripts, license, and
any existing badges in a current README. Output grounds README generation so
the model uses REAL commands and names rather than inventing them.

Usage:
    python3 detect_project.py [REPO_DIR]   # defaults to current directory
    python3 detect_project.py . --json     # machine-readable output

Pure standard library. Read-only: never modifies the repo.
"""
import argparse
import json
import os
import re
import sys


def read(path):
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            return f.read()
    except (OSError, UnicodeError):
        return ""


def load_json(path):
    try:
        return json.loads(read(path))
    except (ValueError, TypeError):
        return {}


def detect(repo):
    facts = {
        "name": os.path.basename(os.path.abspath(repo)) or "project",
        "language": None,
        "package_manager": None,
        "install_command": None,
        "run_command": None,
        "scripts": {},
        "entry_points": [],
        "license": None,
        "has_contributing": os.path.exists(os.path.join(repo, "CONTRIBUTING.md")),
        "has_code_of_conduct": os.path.exists(
            os.path.join(repo, "CODE_OF_CONDUCT.md")
        ),
        "existing_readme": None,
        "existing_badges": [],
        "project_type_hint": None,
    }

    join = lambda *p: os.path.join(repo, *p)

    # Node.js
    if os.path.exists(join("package.json")):
        pkg = load_json(join("package.json"))
        facts["language"] = "JavaScript/TypeScript"
        facts["name"] = pkg.get("name") or facts["name"]
        facts["license"] = pkg.get("license") or facts["license"]
        facts["scripts"] = pkg.get("scripts", {}) or {}
        if os.path.exists(join("pnpm-lock.yaml")):
            facts["package_manager"] = "pnpm"
        elif os.path.exists(join("yarn.lock")):
            facts["package_manager"] = "yarn"
        else:
            facts["package_manager"] = "npm"
        nm = facts["package_manager"]
        if pkg.get("bin"):
            facts["project_type_hint"] = "CLI"
            facts["install_command"] = f"{nm} install -g {facts['name']}"
            bins = pkg["bin"]
            facts["entry_points"] = (
                list(bins.keys()) if isinstance(bins, dict) else [facts["name"]]
            )
        else:
            facts["install_command"] = f"{nm} install {facts['name']}"
            facts["project_type_hint"] = "library"
        run = nm if nm != "npm" else "npm run"
        if "dev" in facts["scripts"]:
            facts["run_command"] = f"{run} dev"
        elif "start" in facts["scripts"]:
            facts["run_command"] = "npm start" if nm == "npm" else f"{nm} start"

    # Python
    elif os.path.exists(join("pyproject.toml")) or os.path.exists(join("setup.py")):
        facts["language"] = "Python"
        facts["package_manager"] = "pip"
        content = read(join("pyproject.toml"))
        m = re.search(r'name\s*=\s*["\']([^"\']+)["\']', content)
        if m:
            facts["name"] = m.group(1)
        if "[project.scripts]" in content or "console_scripts" in read(
            join("setup.py")
        ):
            facts["project_type_hint"] = "CLI"
        else:
            facts["project_type_hint"] = "library"
        facts["install_command"] = f"pip install {facts['name']}"
        lic = re.search(r'license\s*=\s*["\']?\{?[^\n]*?([A-Za-z0-9.\- ]+)', content)
        if lic:
            facts["license"] = facts["license"]  # leave to LICENSE detection

    # Rust
    elif os.path.exists(join("Cargo.toml")):
        facts["language"] = "Rust"
        facts["package_manager"] = "cargo"
        content = read(join("Cargo.toml"))
        m = re.search(r'name\s*=\s*"([^"]+)"', content)
        if m:
            facts["name"] = m.group(1)
        facts["install_command"] = f"cargo install {facts['name']}"
        facts["run_command"] = "cargo run"
        facts["project_type_hint"] = (
            "CLI" if os.path.exists(join("src", "main.rs")) else "library"
        )

    # Go
    elif os.path.exists(join("go.mod")):
        facts["language"] = "Go"
        facts["package_manager"] = "go"
        m = re.search(r"module\s+(\S+)", read(join("go.mod")))
        if m:
            facts["name"] = m.group(1).rsplit("/", 1)[-1]
            facts["install_command"] = f"go install {m.group(1)}@latest"
        facts["run_command"] = "go run ."
        facts["project_type_hint"] = (
            "CLI" if os.path.exists(join("main.go")) else "library"
        )

    # Docker hint
    if os.path.exists(join("Dockerfile")) or os.path.exists(
        join("docker-compose.yml")
    ):
        if facts["project_type_hint"] in (None, "library"):
            facts["project_type_hint"] = "service"

    # License file
    for cand in ("LICENSE", "LICENSE.md", "LICENSE.txt", "COPYING"):
        if os.path.exists(join(cand)):
            txt = read(join(cand))[:400].upper()
            for spdx, needle in (
                ("MIT", "MIT LICENSE"),
                ("Apache-2.0", "APACHE LICENSE"),
                ("GPL-3.0", "GNU GENERAL PUBLIC LICENSE"),
                ("BSD-3-Clause", "BSD 3-CLAUSE"),
                ("BSD-2-Clause", "BSD 2-CLAUSE"),
                ("MPL-2.0", "MOZILLA PUBLIC LICENSE"),
                ("ISC", "ISC LICENSE"),
            ):
                if needle in txt:
                    facts["license"] = spdx
                    break
            break

    # Existing README + badges
    for cand in ("README.md", "readme.md", "README.rst"):
        if os.path.exists(join(cand)):
            facts["existing_readme"] = cand
            rd = read(join(cand))
            facts["existing_badges"] = re.findall(
                r"img\.shields\.io/[^\s)\]]+", rd
            )
            break

    return facts


def print_human(f):
    print(f"Project name      : {f['name']}")
    print(f"Language          : {f['language'] or 'unknown'}")
    print(f"Project type hint : {f['project_type_hint'] or 'unknown'}")
    print(f"Package manager   : {f['package_manager'] or 'unknown'}")
    print(f"Install command   : {f['install_command'] or '(ask the user)'}")
    print(f"Run command       : {f['run_command'] or '(ask the user)'}")
    print(f"License           : {f['license'] or '(ask the user)'}")
    print(f"Entry points      : {', '.join(f['entry_points']) or '-'}")
    if f["scripts"]:
        print("Scripts           :")
        for k, v in f["scripts"].items():
            print(f"    {k}: {v}")
    print(f"CONTRIBUTING.md   : {'yes' if f['has_contributing'] else 'no'}")
    print(f"CODE_OF_CONDUCT   : {'yes' if f['has_code_of_conduct'] else 'no'}")
    print(f"Existing README   : {f['existing_readme'] or 'none'}")
    if f["existing_badges"]:
        print(f"Existing badges   : {len(f['existing_badges'])} found")
    print()
    print("Next: confirm name/tagline/license with the user, then assemble")
    print("sections per references/section-catalog.md.")


def main(argv=None):
    ap = argparse.ArgumentParser(description="Detect project facts for a README.")
    ap.add_argument("repo", nargs="?", default=".", help="repo directory")
    ap.add_argument("--json", action="store_true", help="emit JSON")
    args = ap.parse_args(argv)

    if not os.path.isdir(args.repo):
        print(f"error: not a directory: {args.repo}", file=sys.stderr)
        return 2

    facts = detect(args.repo)
    if args.json:
        print(json.dumps(facts, indent=2))
    else:
        print_human(facts)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
