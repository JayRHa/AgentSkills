---
name: book-summarizer
description: Distills a book into a clear, faithful summary at the depth the reader wants — from a one-paragraph gist to chapter-by-chapter notes — surfacing the core thesis, key ideas, memorable examples, and actionable takeaways without distortion. Use this skill when a user asks to "summarize this book", "give me the key takeaways from X", "what's the main idea of X", "TL;DR of X", "chapter summary", or wants the actionable points or a book-club discussion guide.
license: MIT
---

# Book Summarizer

## Overview
This skill produces a faithful, well-structured summary of a book at the requested depth — a one-line gist, an executive summary, key takeaways, or chapter-by-chapter notes — capturing the central thesis, the supporting ideas, the most memorable examples, and what the reader can actually *do* with it.

**Keywords**: book summary, key takeaways, TL;DR, main idea, chapter summary, executive summary, book notes, book club, nonfiction, study notes.

## When to use vs. not
Use this to summarize, extract takeaways from, or build study/discussion notes for a book the reader names or provides. **Accuracy first:** if you don't actually know a book's content, say so rather than inventing — never fabricate quotes, statistics, or plot points. For very recent or obscure titles, ask the user to paste text or confirm details. Note that a summary is no substitute for reading when nuance matters (e.g., for academic citation).

## Inputs to gather first
1. **The book** (title + author — confirm you have the right one).
2. **Depth wanted** — one-liner, ~1 page, key takeaways, or chapter-by-chapter.
3. **Purpose** — decide whether to read it, apply it, prep a discussion, study for an exam, or recall it.
4. **Fiction or nonfiction** (changes the structure — themes/plot vs. thesis/arguments).
5. **Spoiler tolerance** for fiction.

## Workflow
1. **Confirm the book and your confidence.** State the title/author and that you can summarize it accurately. If unsure, ask for text or flag the uncertainty up front.
2. **Identify the spine.** For **nonfiction**: the central thesis and the 3–7 big ideas that support it. For **fiction**: premise, central conflict, themes, and arc (respecting spoiler preference). See `references/summary-structures.md`.
3. **Summarize at the requested depth:**
   - *One-liner:* the single core message in a sentence.
   - *Executive (~1 page):* thesis + key ideas + why it matters.
   - *Takeaways:* a ranked, actionable bullet list.
   - *Chapter-by-chapter:* 2–4 lines per chapter capturing each one's point.
4. **Keep the best evidence.** Preserve the one or two examples, studies, or scenes that make each idea stick — concrete beats abstract.
5. **Add actionable takeaways** (for nonfiction): what to *do* differently, as concrete steps.
6. **Stay faithful + neutral.** Represent the author's argument accurately before adding any critique. Separate "what the book says" from "my take." Flag where the book is contested if relevant.
7. **(Optional) discussion/study layer.** Book-club questions, key terms, or quiz prompts on request.

## Decision framework
| Reader wants to… | Deliver |
| --- | --- |
| Decide whether to read it | One-liner + 3 takeaways + who it's for |
| Apply the ideas | Key takeaways as concrete actions |
| Recall a book they read | Executive summary + memorable examples |
| Study / cite | Chapter-by-chapter + key terms (+ caveat to verify in source) |
| Run a book club | Themes + 5–8 discussion questions |

## Worked example
See `examples/atomic-habits.md` for layered summaries (one-liner → takeaways → structure) of a well-known nonfiction title.

## Best Practices
- **Lead with the core message** — the reader should get the thesis in the first sentence.
- **Faithful before critical** — represent the argument accurately, then optionally evaluate.
- **Keep concrete examples** — they're what makes ideas memorable.
- **Make nonfiction actionable** — turn ideas into steps.
- **Match depth to purpose** — don't give chapter notes to someone who wants a TL;DR.
- **Flag uncertainty** rather than inventing.

## Common Pitfalls
- **Fabricating** quotes, data, or plot when the book isn't actually known — always avoid.
- **Listing chapters** without extracting each chapter's *point*.
- **Injecting opinion** as if it were the author's.
- **Losing the thesis** in a pile of details.
- **Spoiling fiction** without asking.
- **Over-summarizing** to the point the nuance that matters is gone — note when reading the source is necessary.
