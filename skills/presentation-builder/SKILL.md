---
name: presentation-builder
description: Outlines compelling presentations built around a single core message, a clear narrative arc, one idea per slide, and concrete speaker notes. Use this skill when the user wants to create, outline, structure, or improve a slide deck, talk, pitch, keynote, conference presentation, sales demo, lecture, or any "build me slides / a presentation / a pitch deck" request — including requests like "turn this doc into slides", "help me prepare a talk", "make a deck about X", or "tighten my presentation".
license: MIT
---

# Presentation Builder

## Overview

This skill turns a topic, document, or rough idea into a tight, persuasive presentation outline. It enforces three rules that separate good decks from forgettable ones:

1. **One core message** — the whole deck exists to make ONE point land.
2. **A narrative arc** — slides progress like a story (tension → resolution), not a list of facts.
3. **One idea per slide** — each slide advances the argument by exactly one step, with spoken-word speaker notes.

Keywords: presentation, slide deck, slides, pitch deck, keynote, talk, lecture, demo, storytelling, narrative arc, speaker notes, outline, slide outline, deck structure, conference talk, sales pitch.

The output is a structured outline (slide-by-slide), NOT a visually rendered deck. Hand the outline to PowerPoint, Google Slides, Keynote, or a tool like Marp/reveal.js.

## When to use vs. not use

- USE for: structuring a new deck, converting a document/report into slides, reordering a rambling deck, writing speaker notes, sharpening a pitch.
- DON'T over-engineer for: a single status slide, or when the user already has a finished deck and only wants visual styling (that's a design task, not a structure task).

## Workflow

Follow these steps in order. Do not skip the discovery step — a deck built without knowing the audience and the ask is the #1 cause of bad presentations.

### Step 1 — Discover the four anchors

Before writing any slide, establish (ask the user if unknown, max 3-4 crisp questions):

| Anchor | Question to answer |
|--------|-------------------|
| **Audience** | Who is in the room? What do they already know, care about, and fear? |
| **Goal / Ask** | What should they DO or DECIDE after the talk? (One verb.) |
| **Core message** | The single sentence they should remember tomorrow. |
| **Constraints** | Time limit, slide count, format (live/async), tone. |

If the user gave a document, infer drafts of these from it, then confirm the core message before proceeding.

### Step 2 — Lock the core message

Write the core message as ONE declarative sentence (see `references/storytelling-frameworks.md` → "Core Message Test"). Every slide must earn its place by supporting this sentence. If a slide doesn't, cut it.

### Step 3 — Choose a narrative arc

Pick the arc that fits the goal. Defaults:

- **Pitch / persuade / sell** → "What is — What could be" (problem/possibility oscillation, ending on a call to action).
- **Inform / teach** → "Pyramid" (answer first, then supporting groups of ideas).
- **Report / update** → "Situation → Complication → Resolution → Next steps."
- **Inspire / keynote** → "Hero's journey lite" (status quo → catalyst → struggle → transformation).

See `references/storytelling-frameworks.md` for full descriptions and when to use each.

### Step 4 — Draft the slide spine

Lay out section headers first (3-5 sections for a typical talk), then slides under each. Use the canonical spine:

1. **Hook** (1 slide) — a question, surprising stat, or vivid scene. No agenda slide as slide 1.
2. **Stakes** (1-2) — why this matters now, to THIS audience.
3. **Core message** (1) — state it plainly, early.
4. **Body** (3-7) — the argument, one idea per slide, each building on the last.
5. **Proof** (1-3) — evidence, demo, case study, data.
6. **Call to action** (1) — the specific ask / next step.
7. **Close** (1) — restate core message; memorable final line.

Adjust counts to the time budget (rule of thumb: ~1-2 minutes per content slide; see `scripts/pacing.py`).

### Step 5 — Write each slide using the slide contract

Every slide gets the fields in `templates/slide-outline.md`:
- **Slide title** — a full assertion ("Sales fell because onboarding broke"), NOT a topic label ("Sales").
- **One idea** — the single point.
- **On-slide content** — minimal: a phrase, one chart, or one image cue. No paragraphs.
- **Speaker notes** — what you actually SAY (conversational, 30-90 sec worth).
- **Transition** — one line linking to the next slide ("But there's a catch...").

### Step 6 — Self-review with the checklist

Run every slide and the whole deck through `references/deck-review-checklist.md`. Fix violations. Most common: topic-label titles, multi-idea slides, missing call to action, no transitions.

### Step 7 — Deliver

Output the full outline using `templates/slide-outline.md` structure. Offer to: (a) generate Marp/reveal.js markdown, (b) tighten to a shorter time, or (c) write a 30-second elevator version of the core message.

## Decision Heuristics

- **Assertion titles** — if a title could be a slide in any deck, it's too vague. Make it say something.
- **The "so what?" test** — after each slide, the audience should never think "so what?". The transition answers it.
- **Cut to clarify** — when unsure whether to include a slide, cut it. Fewer slides, more impact.
- **Data needs a verdict** — never show a chart without stating what it proves on the slide title.
- **Demos > descriptions** — if you can show it, show it; replace a "features" slide with a proof slide.
- **One emotion per section** — curiosity, concern, hope, urgency. Map the emotional beat.

## Best Practices

- Open with tension, not logistics. Save the agenda (if any) for after the hook.
- State the core message in the first 90 seconds AND at the end. Repetition is the medium.
- Write speaker notes as speech, not bullet points — read them aloud to test.
- Use the 1-7-7 sanity guide loosely (≤7 lines, ≤7 words) but prefer even less; aim for one phrase.
- Each chart answers one question. Title the chart with the answer.
- End on a sentence, not a "Thank you / Questions?" slide. Land the message, then thank.

## Common Pitfalls

- **Topic titles** ("Background", "Results") instead of assertions. Always rewrite.
- **The everything slide** — multiple ideas crammed together. Split it.
- **Reading the slide** — slide text duplicates speech. Slide = visual aid; notes = words.
- **Burying the ask** — call to action vague or missing. Make it one concrete verb + deadline.
- **No arc** — a flat list of facts. Add tension/resolution beats.
- **Death by data** — slide after slide of charts with no narrative thread.
- **Skipping audience analysis** — generic deck that lands with no one.

## Bundled Files

- `references/storytelling-frameworks.md` — narrative arcs, the core-message test, emotional mapping, opening/closing patterns.
- `references/deck-review-checklist.md` — per-slide and whole-deck review checklist.
- `templates/slide-outline.md` — the fill-in outline format for the final deliverable.
- `examples/saas-pitch-deck.md` — a complete worked example (input brief → finished outline).
- `scripts/pacing.py` — computes slide budget and flags over/under-packed decks from time + slide count.
