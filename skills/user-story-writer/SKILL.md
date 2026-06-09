---
name: user-story-writer
description: Writes high-quality agile user stories that satisfy the INVEST criteria, with clear role/goal/benefit phrasing and testable Gherkin (Given/When/Then) acceptance criteria, and splits epics into thin vertical slices. Use this skill when the user asks to "write a user story", "create acceptance criteria", "break this epic into stories", "turn this requirement into a backlog item", "write Gherkin scenarios", or is grooming/refining a product backlog.
license: MIT
---

# User Story Writer

## Overview

Turn a feature idea, requirement, or epic into well-formed user stories that a team can estimate, build, and verify. Every story states **who** wants **what** and **why**, passes the **INVEST** test, and ships with **testable acceptance criteria**.

Keywords: user story, agile, scrum, backlog, INVEST, acceptance criteria, Gherkin, given when then, story splitting, epic, vertical slice, definition of done, product backlog, refinement, grooming.

## Workflow

1. **Capture the intent.** Identify the user/persona, the goal, and the underlying benefit. If the benefit is unclear, ask "so that what?" until you reach real value.
2. **Write the story statement** using the canonical form:
   `As a <role>, I want <capability> so that <benefit>.`
   Keep it to one sentence and one outcome.
3. **Apply INVEST** (see `references/invest-checklist.md`). If the story fails any letter — especially **S**mall and **T**estable — split or sharpen it.
4. **Split if too big.** Use the splitting patterns in `references/splitting-patterns.md` (workflow steps, business rules, happy/error path, data variations, CRUD operations). Each slice must be a thin **vertical** slice that delivers value end-to-end, not a horizontal layer.
5. **Write acceptance criteria** in Gherkin: one `Scenario` per rule, covering the happy path, key edge cases, and at least one failure path. Use the template in `templates/story-template.md`.
6. **Add a Definition of Done checklist** items only if they are story-specific (e.g. "feature flag added", "analytics event fired"). Leave generic DoD to the team.
7. **Self-review** against `references/invest-checklist.md` and confirm every acceptance criterion is independently verifiable.

## Decision Framework

| Symptom | Action |
| --- | --- |
| Story has "and" in the goal | Split into separate stories |
| Can't estimate it | Too big or too vague — split or clarify |
| No clear user | It may be a task/enabler, not a story — label it as such |
| Acceptance criteria describe UI pixels | Re-focus on observable behavior, not implementation |
| "As a user" (generic) | Name the real persona; "user" hides differing needs |

## Worked Example

**Epic:** "Users can reset their password."

**Story:**
> As a **registered customer**, I want to **request a password reset link by email** so that **I can regain access when I've forgotten my password**.

**Acceptance Criteria:**
```gherkin
Scenario: Request reset with a known email
  Given a registered account exists for "ana@example.com"
  When she submits the reset form with "ana@example.com"
  Then a reset email with a single-use link is sent within 1 minute
  And the page shows a neutral "If the email exists, we've sent a link" message

Scenario: Request reset with an unknown email
  Given no account exists for "ghost@example.com"
  When the reset form is submitted with "ghost@example.com"
  Then no email is sent
  And the same neutral confirmation message is shown (no account enumeration)

Scenario: Reset link expires
  Given a reset link issued more than 60 minutes ago
  When the user opens it
  Then they see "This link has expired" and can request a new one
```

See `examples/checkout-epic-split.md` for a full epic-to-stories breakdown.

## Best Practices

- Write from the **user's** perspective, not the system's.
- One story = one outcome that fits comfortably in a sprint.
- Acceptance criteria describe **observable behavior**, not implementation.
- Always include at least one negative/edge scenario.
- Use neutral, security-aware wording for auth flows (no account enumeration).
- Keep the "so that" honest — if you can't name a benefit, question the story.

## Common Pitfalls

- **Horizontal slices** ("build the database table") that deliver no user value alone.
- **Generic personas** ("as a user") masking conflicting needs.
- **Untestable criteria** ("it should be fast" — quantify it).
- **Solutioning in the story** ("add a Redis cache") instead of stating the need.
- **Giant stories** disguised by vague language; if you can't test it, you can't size it.
