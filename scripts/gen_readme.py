#!/usr/bin/env python3
"""Generate README.md from the skills on disk.

Scans skills/, reads each SKILL.md's name + description, groups by the category
map below, and writes a polished README with badges, a Mermaid diagram, the full
catalog, quick start, and contributing sections.

Usage:
    python3 scripts/gen_readme.py
"""
from __future__ import annotations
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILLS = ROOT / "skills"
REPO = "JayRHa/AgentSkills"

CATEGORY = {
    "Engineering": ["code-reviewer","unit-test-author","refactoring-guide","debug-detective","api-designer","regex-architect","sql-optimizer","dockerfile-pro","git-workflow","dependency-upgrader","performance-profiler","error-handling-patterns"],
    "DevOps & Cloud": ["github-actions-builder","terraform-module-author","kubernetes-manifest-author","nginx-config-pro","incident-postmortem","observability-setup","secrets-manager","bash-script-hardening","cron-scheduler","aws-cost-optimizer"],
    "Data & ML": ["pandas-data-cleaning","sql-schema-designer","data-pipeline-architect","chart-chooser","json-schema-author","ab-test-analyzer","prompt-engineer","rag-pipeline-designer"],
    "Writing & Docs": ["technical-writer","readme-generator","changelog-keeper","blog-post-writer","release-notes-writer","adr-author","email-composer","meeting-summarizer","proofreader","api-docs-writer"],
    "Productivity & Business": ["okr-writer","swot-analyzer","project-planner","decision-matrix","presentation-builder","user-story-writer","competitive-analysis","job-description-writer"],
    "Security": ["threat-modeler","security-auditor","secure-password-policy","gdpr-data-mapper","vulnerability-triage","secure-code-review"],
    "Learning": ["concept-explainer","flashcard-generator","study-plan-builder"],
    "Creative & Life": ["mermaid-diagram-builder","meal-plan-builder","trip-planner"],
}

EMOJI = {
    "Engineering":"🧑‍💻","DevOps & Cloud":"☁️","Data & ML":"📊","Writing & Docs":"✍️",
    "Productivity & Business":"📈","Security":"🔒","Learning":"🎓","Creative & Life":"🎨",
}


def read_desc(folder: str) -> str:
    md = (SKILLS / folder / "SKILL.md").read_text(encoding="utf-8")
    parts = md.split("---", 2)
    fm = parts[1] if len(parts) >= 3 else md
    desc, key = "", None
    for line in fm.splitlines():
        m = re.match(r"^(\w+):\s*(.*)$", line)
        if m:
            key = m.group(1)
            if key == "description":
                desc = m.group(2).strip().lstrip(">").strip()
        elif key == "description" and line.strip():
            desc += " " + line.strip()
        elif m and key != "description":
            key = m.group(1)
    # first sentence only, for a tight table cell
    first = re.split(r"(?<=[.])\s+(?=[A-Z])", desc.strip())[0]
    return first.strip()


def existing(folder: str) -> bool:
    return (SKILLS / folder / "SKILL.md").is_file()


def count_files(folder: str) -> int:
    d = SKILLS / folder
    return sum(1 for p in d.rglob("*") if p.is_file()) if d.is_dir() else 0


def main() -> int:
    present = {p.name for p in SKILLS.iterdir() if p.is_dir() and p.name != "0-template"}
    total = sum(1 for c in CATEGORY.values() for f in c if f in present)
    total_files = sum(count_files(f) for c in CATEGORY.values() for f in c if f in present)

    out: list[str] = []
    out.append('<div align="center">\n')
    out.append("# 🛠️ AgentSkills\n")
    out.append("**The largest community-driven library of Agent Skills for Claude, Codex, Gemini CLI, Cursor & friends.**\n")
    out.append("Plug-and-play `SKILL.md` packages — instructions, references, scripts, and examples — that teach AI agents to do real work.\n")
    out.append(
        f"[![Skills](https://img.shields.io/badge/skills-{total}-f4c542?style=for-the-badge&logo=anthropic)](./skills)\n"
        f"[![GitHub stars](https://img.shields.io/github/stars/{REPO}?style=for-the-badge&logo=github&color=f4c542)](https://github.com/{REPO}/stargazers)\n"
        f"[![GitHub forks](https://img.shields.io/github/forks/{REPO}?style=for-the-badge&logo=github&color=4078c0)](https://github.com/{REPO}/network/members)\n"
        f"[![License: MIT](https://img.shields.io/badge/License-MIT-28a745?style=for-the-badge)](./LICENSE)\n"
    )
    out.append(
        '<p>\n  <a href="https://jannikreinhard.com/">Blog</a> ·\n'
        '  <a href="https://www.linkedin.com/in/jannik-r/">LinkedIn</a> ·\n'
        '  <a href="https://x.com/jannik_reinhard">X</a>\n</p>\n'
    )
    out.append("---\n")
    out.append(f"`{total} Skills` | `{len(CATEGORY)} Categories` | `{total_files}+ Files` | `Open Standard` | `Community Maintained`\n")
    out.append("</div>\n")

    out.append("## What is this?\n")
    out.append(
        "This repository is a growing, **production-ready** library of [Agent Skills](https://agentskills.io). "
        "Each skill is a self-contained folder with a `SKILL.md` (instructions + when to use it) plus supporting "
        "**references, runnable scripts, examples, and templates**. Compatible agents — Claude Code, the Claude apps, "
        "Codex, Gemini CLI, Cursor and more — automatically discover a skill from its description and load the full "
        "body only when it's relevant, so skills are cheap until used.\n"
    )
    out.append("> **Browse [`skills/`](./skills)** to explore everything — from code review and Terraform to threat modeling, RAG design, and trip planning.\n")
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

    out.append("## Skill Catalog\n")
    for cat, folders in CATEGORY.items():
        rows = [f for f in folders if f in present]
        if not rows:
            continue
        out.append(f"### {EMOJI.get(cat,'')} {cat} ({len(rows)})\n")
        out.append("| Skill | What it does |\n| --- | --- |\n")
        for f in rows:
            out.append(f"| [`{f}`](./skills/{f}) | {read_desc(f)} |\n")
        out.append("")
    out.append("---\n")

    out.append("## Anatomy of a Skill\n")
    out.append("```text\nskills/code-reviewer/\n"
               "├── SKILL.md            # frontmatter (name + description) + the workflow\n"
               "├── references/         # deep checklists & domain knowledge (loaded on demand)\n"
               "├── scripts/            # runnable helpers\n"
               "├── examples/           # worked input -> output\n"
               "└── templates/          # fill-in document templates\n```\n")
    out.append("See [`CONTRIBUTING.md`](./CONTRIBUTING.md) for the full format and how to add your own.\n")
    out.append("---\n")

    out.append("## Contributing\n")
    out.append("We love contributions! \n\n"
               "| | How to contribute |\n|---|---|\n"
               f"| **Got an idea?** | [Open an issue](https://github.com/{REPO}/issues/new) describing the skill you'd like to see |\n"
               "| **Got a skill?** | Copy [`skills/0-template`](./skills/0-template), fill it in, run `python3 scripts/validate_skills.py`, and open a PR |\n")
    out.append("---\n")

    out.append('<div align="center">\n\n### Disclaimer\n\n'
               "*This is a community repository. The skills are provided as-is — review them before use.*\n\n"
               "<br>\n\n**If this library helps you, please give it a :star:**\n\n</div>\n")

    (ROOT / "README.md").write_text("\n".join(out) + "\n", encoding="utf-8")
    print(f"Wrote README.md — {total} skills across {len([c for c in CATEGORY if any(f in present for f in CATEGORY[c])])} categories, {total_files} files.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
