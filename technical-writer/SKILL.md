---
name: technical-writer
description: Produces clear, well-structured technical documentation — guides, API docs, READMEs, tutorials, reference pages, and release notes — by analyzing audience, choosing the right document type, applying plain-language and information-architecture principles, and including runnable examples. Use this skill when the user asks to write or improve docs, a README, a how-to guide, a tutorial, API/reference documentation, onboarding material, release notes, or wants prose made clearer, simpler, or better organized for a specific reader.
license: MIT
---

# Technical Writer

## Overview

Keywords: technical documentation, docs, README, how-to guide, tutorial, reference, API docs, onboarding, release notes, plain language, audience analysis, information architecture, style guide, editing, clarity.

This skill turns raw knowledge — code, features, processes, half-written notes — into documentation a real reader can act on. Good technical writing is not "explain everything"; it is "help this specific reader accomplish this specific task with the least friction." That means choosing the correct document type, ordering information so the reader is never blocked, writing in plain language, and proving claims with concrete, copy-pasteable examples.

Use the bundled resources:
- `references/doc-types.md` — the four Diátaxis document types (tutorial, how-to, reference, explanation), when to use each, and structural templates.
- `references/style-guide.md` — plain-language rules, sentence/word patterns, formatting conventions, accessibility, and an editing checklist.
- `scripts/readability.py` — a stdlib-only readability and writing-smell analyzer (grade level, passive voice, long sentences, weasel words). Runs on any `.md` or `.txt`.
- `templates/how-to-guide.md` — a fill-in template for a task-oriented guide.
- `examples/before-after.md` — a worked rewrite of a weak doc section into a strong one.

## Workflow

Follow these steps in order. Do not start writing prose until steps 1–3 are done.

1. **Identify the reader and their job.** Ask or infer: Who reads this? (end user, integrating developer, ops engineer, new teammate, executive.) What is their current knowledge level? What single task or question brings them here? What do they need to be true when they leave? Write this down in one sentence: *"This doc helps [reader] [accomplish task] so that [outcome]."*

2. **Choose the document type.** Use `references/doc-types.md` and the decision table below. Mixing types in one document is the most common cause of confusing docs — keep a tutorial out of your reference, keep explanation out of your how-to.

3. **Outline the information architecture.** List the sections in the order the reader needs them. Front-load the answer; put prerequisites before steps, steps before troubleshooting, common cases before edge cases. For anything longer than a screen, add a short overview/TOC at top so readers can scan.

4. **Draft for the reader, not the author.** Write in plain language per `references/style-guide.md`: short sentences, active voice, "you" for the reader, present tense, one idea per paragraph. Lead each section with its conclusion.

5. **Add concrete examples.** Every abstract instruction needs a concrete instance: a real command with real flags, a real request/response, a real config snippet. Show expected output. Examples must be complete and runnable — no `...`, no `<your-thing-here>` unless immediately explained.

6. **Edit ruthlessly.** Cut filler, deduplicate, fix passive voice and jargon. Run `scripts/readability.py` on the draft to catch long sentences, passive voice, and weasel words. Verify every command, link, and code block actually works.

7. **Add scannability and navigation.** Descriptive headings (not "Introduction"), bulleted lists for parallel items, numbered lists for ordered steps, tables for option/parameter sets, callouts for warnings. Ensure a reader skimming only headings still gets the gist.

## Decision Framework — which document type?

| Reader's intent | Document type | Optimize for |
|---|---|---|
| "I'm new, teach me by doing" | **Tutorial** | A guaranteed successful first experience; hold their hand |
| "I have a specific task, tell me the steps" | **How-to guide** | Speed to the goal; assume basic competence |
| "I need to look up exact details" | **Reference** | Completeness, accuracy, consistency, easy lookup |
| "I want to understand why / how it works" | **Explanation** | Context, concepts, trade-offs, the bigger picture |
| "What changed in this version?" | **Release notes / changelog** | Scannable list grouped by impact (added/changed/fixed/removed) |
| "How do I install and start?" | **README / getting started** | Shortest path from zero to first success |

If a request spans multiple intents, write multiple documents (or clearly separated sections) and cross-link them.

## Plain-language quick rules

- Prefer the short, common word: *use* not *utilize*, *help* not *facilitate*, *about* not *approximately*.
- One sentence, one idea. Aim under ~20 words; break up anything over ~25.
- Active voice with a clear actor: "Run the migration" not "The migration should be run."
- Address the reader as "you." Use imperatives for steps: "Open the file."
- Define a term or acronym on first use; then stay consistent — never switch synonyms for the same concept.
- Lead with the conclusion (BLUF — bottom line up front), then supporting detail.
- Replace vague quantifiers (*several, various, robust, simply, just, easily*) with specifics or delete them.

See `references/style-guide.md` for the full list and the editing checklist.

## Worked example (condensed)

Before: *"In order to facilitate the initialization of the application, it is necessary that the configuration file should be created by the user prior to the execution of the startup process."*

After: *"Before you start the app, create a `config.yml` file. See the example below."*

The rewrite cuts 30 words to 16, removes passive voice, adds "you," names the concrete artifact, and points to an example. See `examples/before-after.md` for a full section-length rewrite.

## Best Practices

- Write the one-sentence purpose statement first and keep it visible while drafting; cut anything that doesn't serve it.
- Show, don't just tell — pair every instruction with a runnable example and its expected output.
- Make the happy path effortless; push edge cases, caveats, and deep theory into clearly labeled later sections or separate explanation docs.
- Use consistent terminology, casing, and formatting; pick one term per concept and never deviate.
- Test your own instructions by following them literally on a clean setup — fix every gap a real first-timer would hit.
- Use semantic headings so the document is navigable by skim and by screen reader; keep heading levels properly nested.
- Date and version reference docs and release notes so readers know if they're current.

## Common Pitfalls

- **Curse of knowledge:** skipping steps that feel "obvious" to you but block a newcomer. Have someone unfamiliar try it.
- **Mixing doc types:** dumping conceptual theory into a step list, or burying lookup tables inside a tutorial. Split them.
- **Wall of text:** no headings, no lists, no examples. Break it up; let readers scan.
- **Placeholder examples that don't run:** `command --flag <value>` with no real value or output. Provide a real, working instance.
- **Vague hedging:** "this should generally work in most cases" tells the reader nothing. Be specific or test it.
- **Documenting the implementation instead of the task:** readers want to accomplish a goal, not read a tour of your code.
- **Stale docs:** instructions that no longer match the product. Tie doc updates to the change that triggered them.
