#!/usr/bin/env python3
"""Generate README.md from the skills on disk.

Skills live as top-level folders in the repo root (each contains a SKILL.md).
This scans them, reads each SKILL.md's name + description, groups by the category
map below, and writes a polished README with badges, a Mermaid diagram, the full
catalog, quick start, and contributing sections.

Usage:
    python3 scripts/gen_readme.py
"""
from __future__ import annotations
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REPO = "JayRHa/AgentSkills"

# Folders at the repo root that are NOT skills.
NON_SKILL_DIRS = {"scripts", ".github", ".git"}

CATEGORY = {
    "Engineering": ["code-reviewer","unit-test-author","refactoring-guide","debug-detective","api-designer","regex-architect","sql-optimizer","dockerfile-pro","git-workflow","dependency-upgrader","performance-profiler","error-handling-patterns"],
    "DevOps & Cloud": ["github-actions-builder","terraform-module-author","kubernetes-manifest-author","nginx-config-pro","incident-postmortem","observability-setup","secrets-manager","bash-script-hardening","cron-scheduler","aws-cost-optimizer"],
    "Data & ML": ["pandas-data-cleaning","sql-schema-designer","data-pipeline-architect","chart-chooser","json-schema-author","ab-test-analyzer","prompt-engineer","rag-pipeline-designer"],
    "Writing & Communication": ["technical-writer","readme-generator","changelog-keeper","blog-post-writer","release-notes-writer","adr-author","email-composer","meeting-summarizer","proofreader","api-docs-writer","public-speaking-coach","mermaid-diagram-builder"],
    "Productivity & Business": ["okr-writer","swot-analyzer","project-planner","decision-matrix","presentation-builder","user-story-writer","competitive-analysis","job-description-writer"],
    "Security": ["threat-modeler","security-auditor","secure-password-policy","gdpr-data-mapper","vulnerability-triage","secure-code-review"],
    "Career & Job Search": ["resume-writer","cover-letter-writer","interview-prep","salary-negotiator"],
    "Learning": ["concept-explainer","flashcard-generator","study-plan-builder","language-tutor","book-summarizer"],
    "Health & Wellness": ["meal-plan-builder","workout-planner","habit-builder"],
    "Home & Lifestyle": ["trip-planner","personal-budget-planner","event-planner","gift-advisor"],
}

EMOJI = {
    "Engineering":"🧑‍💻","DevOps & Cloud":"☁️","Data & ML":"📊","Writing & Communication":"✍️",
    "Productivity & Business":"📈","Security":"🔒","Career & Job Search":"💼","Learning":"🎓",
    "Health & Wellness":"💪","Home & Lifestyle":"🏡",
}


def read_desc(folder: str) -> str:
    md = (ROOT / folder / "SKILL.md").read_text(encoding="utf-8")
    parts = md.split("---", 2)
    fm = parts[1] if len(parts) >= 3 else md
    desc, key = "", None
    for line in fm.splitlines():
        m = re.match(r"^(\w+):\s*(.*)$", line)
        if m:
            key = m.group(1)
            if key == "description":
                val = m.group(2).strip()
                # Ignore YAML block-scalar indicators (>, >-, |, |-, etc.).
                desc = "" if re.fullmatch(r"[>|][+-]?", val) else val
        elif key == "description" and line.strip():
            desc += (" " if desc else "") + line.strip()
    # first sentence only, for a tight table cell
    first = re.split(r"(?<=[.])\s+(?=[A-Z])", desc.strip())[0]
    return first.strip()


def existing(folder: str) -> bool:
    return (ROOT / folder / "SKILL.md").is_file()


def count_files(folder: str) -> int:
    d = ROOT / folder
    return sum(1 for p in d.rglob("*") if p.is_file()) if d.is_dir() else 0


def main() -> int:
    present = {
        p.name for p in ROOT.iterdir()
        if p.is_dir() and p.name not in NON_SKILL_DIRS and p.name != "0-template"
        and (p / "SKILL.md").is_file()
    }
    total = sum(1 for c in CATEGORY.values() for f in c if f in present)
    total_files = sum(count_files(f) for c in CATEGORY.values() for f in c if f in present)
    used_categories = [c for c in CATEGORY if any(f in present for f in CATEGORY[c])]

    # Warn about skills present on disk but not mapped to a category.
    mapped = {f for c in CATEGORY.values() for f in c}
    unmapped = sorted(present - mapped)
    if unmapped:
        print(f"warning: {len(unmapped)} skill(s) not in any category: {', '.join(unmapped)}")

    out: list[str] = []
    out.append('<div align="center">\n')
    out.append("# 🛠️ AgentSkills\n")
    out.append("**The largest community-driven library of Agent Skills for Claude, Codex, Gemini CLI, Cursor & friends.**\n")
    out.append("Plug-and-play `SKILL.md` packages — instructions, references, scripts, and examples — that teach AI agents to do real work, from code review to career coaching.\n")
    out.append(
        f"[![Skills](https://img.shields.io/badge/skills-{total}-f4c542?style=for-the-badge&logo=anthropic)](#-skill-catalog)\n"
        f"[![Categories](https://img.shields.io/badge/categories-{len(used_categories)}-8E2DE2?style=for-the-badge)](#-skill-catalog)\n"
        f"[![GitHub stars](https://img.shields.io/github/stars/{REPO}?style=for-the-badge&logo=github&color=f4c542)](https://github.com/{REPO}/stargazers)\n"
        f"[![License: MIT](https://img.shields.io/badge/License-MIT-28a745?style=for-the-badge)](./LICENSE)\n"
    )
    out.append(
        '<p>\n  <a href="https://jannikreinhard.com/">Blog</a> ·\n'
        '  <a href="https://www.linkedin.com/in/jannik-r/">LinkedIn</a> ·\n'
        '  <a href="https://x.com/jannik_reinhard">X</a>\n</p>\n'
    )
    out.append(f"`{total} Skills` · `{len(used_categories)} Categories` · `{total_files}+ Files` · `Open Standard` · `Community Maintained`\n")
    out.append("</div>\n")

    out.append("## What is this?\n")
    out.append(
        "This repository is a growing, **production-ready** library of [Agent Skills](https://agentskills.io). "
        "Each skill is a self-contained folder with a `SKILL.md` (instructions + when to use it) plus supporting "
        "**references, runnable scripts, examples, and templates**. Compatible agents — Claude Code, the Claude apps, "
        "Codex, Gemini CLI, Cursor and more — automatically discover a skill from its description and load the full "
        "body only when it's relevant, so skills are cheap until used.\n"
    )
    out.append("> Each skill is a folder right here in the repo root. Browse the [catalog](#-skill-catalog) below — from code review and Terraform to threat modeling, interview prep, budgeting, and trip planning.\n")
    out.append("---\n")

    out.append("## How It Works\n")
    out.append("```mermaid\nflowchart LR\n"
               "    Lib[Skill library] --> Pick[Pick a skill]\n"
               "    Pick --> Install[Install into .claude/skills]\n"
               "    Install --> Discover[Agent reads description]\n"
               "    Discover --> Match{Relevant to task?}\n"
               "    Match -- No --> Idle[Stays unloaded, ~0 cost]\n"
               "    Match -- Yes --> Load[Load SKILL.md + refs]\n"
               "    Load --> Run[Agent follows the workflow]\n"
               "    Run --> Result[High-quality output]\n```\n")
    out.append("---\n")

    out.append("## Quick Start\n")
    out.append("### Install a skill into Claude Code\n```bash\n"
               f"git clone https://github.com/{REPO}.git\n"
               "cd AgentSkills\n\n"
               "# install specific skills (personal scope: ~/.claude/skills)\n"
               "./scripts/install-skill.sh code-reviewer terraform-module-author\n\n"
               "# or install everything\n"
               "./scripts/install-skill.sh --all\n\n"
               "# or into the current project (./.claude/skills)\n"
               "./scripts/install-skill.sh --project code-reviewer\n```\n")
    out.append("Then restart your agent. Ask something that matches a skill's description, or invoke it directly with `/code-reviewer`.\n")
    out.append("You can also just copy any skill folder into your own `.claude/skills/` directory.\n")
    out.append("---\n")

    out.append("## 📚 Skill Catalog\n")
    for cat in CATEGORY:
        rows = [f for f in CATEGORY[cat] if f in present]
        if not rows:
            continue
        out.append(f"### {EMOJI.get(cat,'')} {cat} ({len(rows)})\n")
        table = ["| Skill | What it does |", "| --- | --- |"]
        for f in rows:
            table.append(f"| [`{f}`](./{f}) | {read_desc(f)} |")
        out.append("\n".join(table) + "\n")
    out.append("---\n")

    out.append("## Anatomy of a Skill\n")
    out.append("```text\ncode-reviewer/\n"
               "├── SKILL.md            # frontmatter (name + description) + the workflow\n"
               "├── references/         # deep checklists & domain knowledge (loaded on demand)\n"
               "├── scripts/            # runnable helpers\n"
               "├── examples/           # worked input -> output\n"
               "└── templates/          # fill-in document templates\n```\n")
    out.append("See [`CONTRIBUTING.md`](./CONTRIBUTING.md) for the full format and how to add your own.\n")
    out.append("---\n")

    out.append("## Contributing\n")
    out.append("We love contributions!\n")
    out.append("| | How to contribute |\n|---|---|\n"
               f"| **Got an idea?** | [Open an issue](https://github.com/{REPO}/issues/new) describing the skill you'd like to see |\n"
               "| **Got a skill?** | Copy [`0-template`](./0-template), fill it in, run `python3 scripts/validate_skills.py`, and open a PR |\n")
    out.append("---\n")

    out.append('<div align="center">\n')
    out.append("### Disclaimer\n")
    out.append("*This is a community repository. The skills are provided as-is — review them before use.*\n")
    out.append("**If this library helps you, please give it a :star:**\n")
    out.append("</div>\n")

    (ROOT / "README.md").write_text("\n".join(out) + "\n", encoding="utf-8")
    print(f"Wrote README.md — {total} skills across {len(used_categories)} categories, {total_files} files.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
