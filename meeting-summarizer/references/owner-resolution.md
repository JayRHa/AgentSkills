# Owner & Due-Date Resolution Guide

Attributing tasks correctly is the highest-value part of a meeting summary. Use these rules.

## Resolving owners

| Source phrasing | Owner resolution |
|-----------------|------------------|
| "I'll do X" (said by Dev) | Dev |
| "Can you take X?" → "sure" (replied by Priya) | Priya |
| "Maria will handle X" | Maria |
| "We should do X" (no one accepts) | UNASSIGNED |
| "Someone needs to X" | UNASSIGNED |
| "The team will X" | Team (group owner is acceptable) |
| "Let's get marketing to X" | Marketing (team) — flag if no individual named |

### Rules

1. **Map speaker to pronoun.** "I'll" belongs to whoever is speaking. Use speaker labels/timestamps.
2. **Require explicit acceptance for delegated tasks.** "Can you do X?" only creates an owned action if the person agrees. If the answer is unclear, mark `UNASSIGNED` and note it.
3. **Disambiguate first names** against the attendee list. If two attendees share a first name, use last initial.
4. **Never assign by seniority or guess.** The most senior person is not the default owner.
5. **Group owners are allowed** (Team, Marketing) but prefer an individual; flag group-only ownership as a mild risk in Open Questions if the task is important.

## Resolving due dates

1. **Absolute is best.** Convert relative phrases to absolute dates ONLY when the meeting date is reliably known.
   - Meeting on 2026-06-08, "by Friday" → 2026-06-12 (the coming Friday).
   - "next Tuesday" → the Tuesday of the following week, not the immediate one.
2. **No meeting date?** Keep the relative phrase verbatim ("by Friday", "EOD tomorrow"). Do NOT compute against today's date — the meeting may be old.
3. **No date stated at all?** Use `—` in the Due cell. Do not invent urgency.
4. **Preserve qualifiers.** "Targeting Thursday but depends on legal" → keep the dependency.

## Edge cases

- **Conditional tasks:** "If the client says yes, send the contract" → record with the condition intact; owner still required.
- **Recurring tasks:** "I'll send weekly updates" → owner Dev, Due "weekly (recurring)".
- **Reassigned mid-meeting:** use the final owner stated.
- **Multiple owners:** list both ("Dev & Priya") only if the source truly splits the work; otherwise pick the accountable lead.
