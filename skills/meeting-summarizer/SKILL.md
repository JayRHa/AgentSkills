---
name: meeting-summarizer
description: Transforms raw meeting notes, transcripts, or recordings text into a concise, scannable summary with clear sections for decisions made and owned action items (owner + due date). Use this skill when the user asks to "summarize this meeting", "turn these notes into a summary", "extract action items", "who agreed to what", "write meeting minutes", "TLDR this transcript", "pull decisions and next steps", or pastes a Zoom/Teams/Google Meet transcript and wants it condensed. Also applies to standups, 1:1s, planning sessions, retros, and client calls.
license: MIT
---

# Meeting Summarizer

## Overview

This skill converts messy meeting input (chat transcripts, dictated notes, bullet dumps, recording transcripts) into a structured, decision-oriented summary that a busy reader can absorb in under a minute. The output prioritizes the two things people actually need after a meeting: **what was decided** and **who owes what by when**.

Keywords: meeting minutes, summary, recap, action items, decisions, owners, due dates, TLDR, standup, retro, 1:1, transcript, notes.

The non-negotiable rule: **every action item must have an owner**. If the source does not name one, the action item is flagged as `OWNER: UNASSIGNED` rather than silently dropped or guessed.

## When To Use

Use this skill whenever the user wants raw meeting content distilled. Triggers include pasting a transcript, asking for "minutes", "a recap", "key takeaways", "next steps", or "the TLDR". Do not use it for live note-taking guidance or scheduling — only for processing content that already exists.

## Process

Follow these steps in order.

1. **Detect input type & length.** Identify whether the input is a verbatim transcript (timestamps, speaker labels), shorthand notes, or a mixed dump. Note the approximate length so you can size the summary.

2. **Identify metadata.** Pull (or infer where stated) the meeting title/topic, date, and attendees. Never invent a date — if absent, omit it or write `Date: not stated`.

3. **Extract the four content streams** by scanning the whole input once for each:
   - **Decisions** — anything settled, approved, chosen, or rejected. Look for trigger words: "we'll go with", "agreed", "approved", "decided", "let's do", "no to", "final".
   - **Action items** — future work someone committed to. Look for: "I'll", "can you", "take", "follow up", "by Friday", "next step", assigned verbs.
   - **Discussion / context** — the reasoning, options weighed, and notable points that aren't decisions or actions.
   - **Open questions / risks** — unresolved items, blockers, parking-lot topics.

4. **Resolve owners and dates for each action item.** Map pronouns to names using the transcript ("I'll handle it" said by Maria → owner: Maria). Convert relative dates ("by next Tuesday") to absolute dates only if a meeting date is known; otherwise keep the relative phrasing. Mark missing owners `UNASSIGNED`.

5. **Deduplicate and compress.** Merge restated points. Cut filler, small talk, and off-topic tangents. Each bullet should carry one idea, written as a terse, complete statement.

6. **Assemble the summary** using the structure in `templates/summary.md`. Lead with a 1–3 sentence TLDR, then Decisions, then Action Items (as a table), then Discussion, then Open Questions. Omit any empty section except Action Items (which always renders, even if to state "None captured").

7. **Quality-check** against `references/checklist.md` before delivering. Most importantly verify the no-orphan-actions rule and that no decision was downgraded to a discussion bullet.

## Output Structure

```
# <Meeting Topic> — Summary
Date: ... | Attendees: ...

## TLDR
1–3 sentences.

## Decisions
- ...

## Action Items
| # | Action | Owner | Due |

## Discussion Highlights
- ...

## Open Questions / Risks
- ...
```

See `templates/summary.md` for the full fill-in template and `examples/standup-recap.md` for a complete worked example.

## Decision Framework: classifying a line

Use this quick test on each notable line:

- Is it a settled choice or approval? → **Decision**.
- Does it commit a specific person to future work? → **Action Item**.
- Is it unresolved, a blocker, or a "we should look into…"? → **Open Question / Risk**.
- Is it reasoning, an option considered, or notable context? → **Discussion Highlight**.
- Is it filler, greeting, or off-topic? → **Drop**.

When something is both a decision and spawns work (e.g., "We'll launch Tuesday — Sam, prep the release notes"), record the decision in Decisions AND the task in Action Items.

## Adapting Length & Tone

- **Short input (<1 page):** keep the whole summary to ~10 bullets total.
- **Long transcript (>30 min):** group Discussion Highlights under sub-topics; keep TLDR to 3 sentences max.
- **Standup:** collapse to per-person blockers + the day's commitments.
- **Client/external call:** neutral, professional tone; spell out acronyms once; avoid internal jargon.
- **Retro:** organize Discussion under Went Well / Didn't / Try.

For tone, owner-resolution edge cases, and a helper script, see the references below.

## Helper Script

`scripts/extract_actions.py` is a zero-dependency Python tool that scans a notes/transcript file for likely action-item and decision lines using cue-word heuristics, and prints them grouped — a fast first pass before you write the polished summary. Run:

```
python3 scripts/extract_actions.py meeting.txt
python3 scripts/extract_actions.py meeting.txt --json
```

It is a *draft aid*, not a replacement for reading the full input.

## Best Practices

- Lead with the TLDR; many readers stop there.
- Write action items as imperatives starting with a verb ("Send the revised deck", not "deck needs sending").
- Always pair owner + due date; if either is missing, mark it explicitly.
- Preserve exact figures, dates, names, and dollar amounts verbatim — never round or paraphrase numbers.
- Use the attendees list to disambiguate first-name-only references.
- Keep the reader's perspective: what do they need to *do* or *know*.

## Common Pitfalls

- **Orphan actions:** dropping a task because no owner was named. Flag `UNASSIGNED` instead.
- **Hallucinated owners/dates:** never assign a person or deadline the source didn't state.
- **Burying decisions in prose:** decisions belong in their own section, not mixed into discussion.
- **Over-summarizing:** losing a key number, name, or conditional ("only if budget approved").
- **Copying filler:** greetings, "can you hear me?", scheduling chatter — drop it.
- **Inventing a date:** if the meeting date isn't in the source, don't fabricate one or convert relative dates against today.

See `references/checklist.md` for the full pre-delivery QA list and `references/owner-resolution.md` for handling tricky attribution cases.
