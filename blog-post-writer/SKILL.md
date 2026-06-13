---
name: blog-post-writer
description: Writes engaging technical blog posts with a strong hook, clear structure, concrete examples, and a memorable takeaway. Use this skill when the user asks to "write a blog post", "draft an article", "turn this into a blog post", "write up a tutorial", "explain X in a post", "create a dev.to / Medium / Hashnode article", or wants help with an engineering blog, technical write-up, announcement post, or developer-facing essay. Covers ideation, outlining, drafting, hooks, headlines, code examples, SEO basics, and editing for clarity.
license: MIT
---

# Blog Post Writer

## Overview
This skill produces publishable technical blog posts that readers actually finish: a hook that earns the first scroll, a spine of clear sections, runnable examples, and a takeaway the reader can act on. Keywords: blog post, technical article, dev blog, tutorial, write-up, engineering blog, Medium, dev.to, Hashnode, announcement, essay, headline, hook, SEO.

Use it for tutorials, deep dives, "how we built X" stories, opinion/architecture pieces, release announcements, and concept explainers.

## When To Use
- "Write a blog post about <topic>."
- "Turn these notes / this PR / this RFC into an article."
- "I need a catchy intro and outline for a post on <topic>."
- "Edit / tighten this draft."

## Process
Follow these steps in order. Do not skip step 1 — most weak posts fail on audience and angle, not prose.

1. **Clarify the brief.** Establish (ask only if unknown): topic, target reader and their skill level, the single takeaway, desired length, tone, and platform. If the user gave a draft or notes, infer these and confirm the angle in one line.
2. **Find the angle.** Pick ONE controlling idea (the "so what"). Reject topics that are really 3 posts; split them. Write a one-sentence thesis you can defend.
3. **Outline.** Produce a section skeleton (H2s) before prose. Use `templates/outline.md`. Aim for 4-7 sections plus intro and conclusion.
4. **Write the hook.** Draft the opening using a pattern from `references/hooks.md`. The first two sentences must create tension or promise a payoff. No "In today's fast-paced world."
5. **Draft body.** One idea per section. Lead each section with its point, then support with example/code/data. Keep paragraphs 2-4 sentences.
6. **Add examples.** Every abstract claim gets a concrete instance: code, a command, a number, a before/after, or a short scenario. Code must be minimal, correct, and runnable.
7. **Write the takeaway.** End with what the reader should now do or believe — a checklist, next step, or crisp summary. Never end on "In conclusion."
8. **Title + meta.** Generate 3-5 headline options (see `references/headlines.md`) and a 150-160 char meta description.
9. **Edit.** Run the pass in `references/editing-checklist.md`. Then run `scripts/readability.py` on the draft for objective metrics. Cut 10%.

## Structure Template
```
Title (benefit-driven, specific)
Hook (2-4 sentences: tension/promise)
Context (why this matters now, who it's for) — keep short
Body section 1..N (point → example → implication)
Takeaway (action/summary)
CTA (optional: comment, follow, try the repo)
```

## Decision Framework: Post Type
- **Tutorial / how-to** → numbered steps, prerequisites block, copy-paste code, end state screenshot/output. Reader goal: *do it*.
- **Deep dive / "how we built"** → problem → constraints → approach → tradeoffs → result with metrics. Reader goal: *understand decisions*.
- **Opinion / architecture** → thesis → evidence → counterargument → recommendation. Reader goal: *be persuaded*.
- **Concept explainer** → analogy → precise definition → example → common misconceptions. Reader goal: *get it*.
- **Announcement** → what's new in one line → why it matters → key features → migration/getting started. Reader goal: *should I adopt this*.

See `references/post-types.md` for full structures and worked skeletons.

## Hook Heuristics (quick)
Lead with one of: a sharp question the reader is already asking, a surprising fact/number, a relatable failure, a bold claim you'll prove, or a tiny story. Promise the payoff explicitly within the first paragraph. See `references/hooks.md`.

## Best Practices
- One takeaway per post. If you can't state it in a sentence, the post isn't ready.
- Show, don't assert: replace adjectives ("blazing fast") with numbers ("p99 dropped from 800ms to 90ms").
- Front-load value — readers skim; make each H2 a self-contained mini-point.
- Use "you" and active voice. Write like you'd explain it to a smart colleague.
- Code blocks: minimal, labeled language, tested, with expected output shown.
- Vary sentence length; short sentences land points.
- Add internal signposts ("First… Next… The catch…") for scannability.

## Common Pitfalls
- Burying the lede under throat-clearing intro paragraphs.
- Trying to cover everything — scope creep kills focus.
- Abstract advice with no example.
- Untested or pseudo-code presented as runnable.
- Walls of text; no headers, no whitespace.
- Generic title ("Thoughts on X") that wins no clicks.
- Ending with a weak "Hope this helps!" instead of a real takeaway.

## Supporting Files
- `references/hooks.md` — hook patterns with examples and anti-patterns.
- `references/headlines.md` — headline formulas, SEO and length rules.
- `references/post-types.md` — full per-type structures and skeletons.
- `references/editing-checklist.md` — line-by-line self-edit pass.
- `templates/outline.md` — fill-in outline to start any post.
- `examples/sample-post.md` — a complete worked post from brief to draft.
- `scripts/readability.py` — stdlib readability + filler-word metrics for a draft.
