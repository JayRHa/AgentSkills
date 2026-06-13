# Contributing to AgentSkills

Thanks for helping grow the largest open library of Agent Skills! Contributions of new skills, improvements, and fixes are all welcome.

## What is a skill?

A skill is a top-level folder in the repo root containing a `SKILL.md` file plus optional supporting files (references, scripts, examples, templates). Claude (and other compatible agents like Codex, Gemini CLI, and Cursor) automatically discover a skill from its `description` and load the full body only when it is relevant — so skills are cheap until used.

Skills follow the open [Agent Skills standard](https://agentskills.io).

## Skill anatomy

```text
my-skill/
├── SKILL.md            # Required. Frontmatter + instructions.
├── references/         # Optional. Deep reference docs, checklists, tables.
│   └── guide.md
├── scripts/            # Optional. Runnable helper scripts.
│   └── run.py
├── examples/           # Optional. Worked input -> output examples.
│   └── sample.md
└── templates/          # Optional. Fill-in templates.
    └── template.md
```

### `SKILL.md` frontmatter

```yaml
---
name: my-skill            # kebab-case, must equal the folder name
description: >            # what it does + when to use it (triggers!)
  One or two dense sentences. Start with what the skill does, then
  "Use this skill when ..." with concrete trigger phrases. Third person.
license: MIT
---
```

The `description` is the single most important field — it is the only text the agent reads to decide whether to load your skill. Put the key use case first and include explicit trigger phrases.

### Body guidelines

- **Be concise but complete.** Once loaded, the body stays in context — every line is a recurring token cost. State what to do, not why at length.
- Include a clear **`## Workflow`** (numbered steps), **`## Best Practices`**, and **`## Common Pitfalls`**.
- Move bulky reference material into `references/` and point to it from `SKILL.md` ("See `references/checklist.md`").
- Scripts must actually run. Prefer the standard library. Add a usage docstring.
- No placeholders, no `TODO`, no truncated content.

## How to contribute

1. **Got an idea?** [Open an issue](../../issues/new) describing the skill you'd like to see.
2. **Got a skill?** Copy [`0-template`](./0-template) into a new top-level folder, fill it in, and open a pull request.
3. Run `python3 scripts/validate_skills.py` before submitting — it checks that every skill has valid frontmatter and a matching folder name.

## Quality checklist

- [ ] Folder name is kebab-case and matches `name:` in the frontmatter
- [ ] `description` starts with what it does and includes trigger phrases
- [ ] Body has a clear workflow, best practices, and pitfalls
- [ ] At least one supporting file (reference, script, example, or template)
- [ ] Scripts run with no external dependencies (or document them)
- [ ] `validate_skills.py` passes

Happy skill building! 🛠️
