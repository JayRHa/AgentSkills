#!/usr/bin/env python3
"""Validate every skill in the AgentSkills library.

Skills live as top-level folders in the repo root (each folder that contains a
SKILL.md is treated as a skill). Checks, for each skill:
  - a SKILL.md exists
  - it has YAML frontmatter delimited by --- markers
  - frontmatter contains `name` and `description`
  - `name` matches the folder name (kebab-case)
  - the description is reasonably descriptive

Exit code is non-zero if any skill fails, so it can be used in CI.

Usage:
    python3 scripts/validate_skills.py
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
NON_SKILL_DIRS = {"scripts", ".github", ".git"}
KEBAB = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


def parse_frontmatter(text: str) -> dict[str, str] | None:
    if not text.startswith("---"):
        return None
    parts = text.split("---", 2)
    if len(parts) < 3:
        return None
    fm: dict[str, str] = {}
    key = None
    for line in parts[1].splitlines():
        m = re.match(r"^([A-Za-z0-9_-]+):\s*(.*)$", line)
        if m:
            key = m.group(1)
            fm[key] = m.group(2).strip()
        elif key and line.strip():
            fm[key] += " " + line.strip()
    return fm


def skill_dirs() -> list[Path]:
    return sorted(
        p for p in ROOT.iterdir()
        if p.is_dir() and p.name not in NON_SKILL_DIRS and (p / "SKILL.md").is_file()
    )


def main() -> int:
    dirs = skill_dirs()
    if not dirs:
        print(f"error: no skills found in {ROOT}", file=sys.stderr)
        return 1

    errors: list[str] = []
    count = 0
    for folder in dirs:
        count += 1
        name = folder.name
        skill_md = folder / "SKILL.md"
        fm = parse_frontmatter(skill_md.read_text(encoding="utf-8"))
        if fm is None:
            errors.append(f"{name}: missing or malformed YAML frontmatter")
            continue
        if "name" not in fm:
            errors.append(f"{name}: frontmatter missing 'name'")
        elif fm["name"].strip("'\"") != name:
            errors.append(f"{name}: frontmatter name '{fm['name']}' != folder '{name}'")
        if not KEBAB.match(name):
            errors.append(f"{name}: folder name is not kebab-case")
        desc = fm.get("description", "")
        if len(desc) < 30:
            errors.append(f"{name}: description too short ({len(desc)} chars)")

    print(f"Validated {count} skills.")
    if errors:
        print(f"\n{len(errors)} problem(s) found:", file=sys.stderr)
        for e in errors:
            print(f"  ✗ {e}", file=sys.stderr)
        return 1
    print("All skills valid. ✓")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
