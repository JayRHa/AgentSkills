---
name: email-composer
description: Drafts clear, professional emails with the right tone, structure, and a concrete call to action by clarifying audience, purpose, and desired outcome. Use this skill when the user asks to "write an email", "draft an email", "compose a message", "reply to this email", "make this email sound more professional/polite/firmer", "follow up", "send a cold outreach", "decline/apologize/ask for something by email", or needs help with subject lines, tone, or email structure.
license: MIT
---

# Email Composer

## Overview
This skill produces emails that are clear, correctly toned, well structured, and end with an unambiguous call to action (CTA). It works for new outreach, replies, follow-ups, requests, declines, apologies, status updates, introductions, and escalations.

Keywords: write email, draft email, compose, reply, follow up, cold outreach, subject line, tone, professional, polite, firm, apology, request, decline, introduction, escalation.

The core principle: every email should let the reader answer three questions in under 10 seconds — *What is this about? What do you need from me? By when?*

## Workflow
Follow these steps in order. Ask only the questions you cannot reasonably infer from context; never block on a long questionnaire.

1. **Identify the five inputs.** Audience, relationship, purpose, desired outcome (the CTA), and constraints (deadline, length, channel, formality). If two or more are missing and cannot be inferred, ask one concise clarifying message grouping all gaps.
2. **Pick the email type.** Map the purpose to a pattern (request, follow-up, decline, apology, update, intro, cold outreach, escalation). See `references/email-patterns.md`.
3. **Choose the tone.** Calibrate formality and warmth to the relationship and culture. Use the dial in `references/tone-guide.md`.
4. **Draft the subject line.** Specific, ≤ 60 characters, scannable. Front-load the keyword. See subject-line rules in `references/email-patterns.md`.
5. **Write the body** using the structure below.
6. **Make the CTA explicit.** One primary ask, an owner, and a deadline. Never end with a vague "let me know."
7. **Self-review** against `references/checklist.md`. Optionally run `scripts/email_lint.py` to catch length, hedging, passive voice, and missing CTA.
8. **Offer variants** when tone is uncertain (e.g., "here's a warmer and a firmer version").

## Body Structure (default)
Keep most emails to 5 short blocks. Aim for under 150 words unless the content demands more.

1. **Greeting** — match formality ("Hi Sam," / "Dear Dr. Lee," / "Hello team,").
2. **Context / hook (1 sentence)** — why you're writing, link to prior thread if any.
3. **Core message (1–3 sentences)** — the substance, most important first (BLUF: Bottom Line Up Front).
4. **Call to action** — the specific ask, the owner, and the deadline.
5. **Sign-off** — courteous close + name (+ signature block if relevant).

## Decision Framework: tone in one pass
- **Higher formality** when: first contact, senior/external recipient, sensitive topic, legal/HR/finance, conservative culture.
- **Lower formality** when: established peer relationship, internal team, fast-moving thread, startup culture.
- **Warmer** when: asking a favor, delivering bad news, rebuilding a relationship.
- **Firmer (still polite)** when: a deadline slipped, repeated non-response, escalation, scope disputes.

## Worked Example (condensed)
Request: chase a contract signature, recipient is a busy external partner, deadline Friday.

> **Subject:** Signature needed: MSA by Fri Jun 12
>
> Hi Priya,
>
> Following up on the MSA I sent Monday — legal on both sides has approved the final draft.
>
> Could you e-sign via the DocuSign link by **Friday, June 12** so we can start onboarding next week? It takes about two minutes.
>
> Happy to hop on a quick call if anything needs another look.
>
> Best,
> Jannik

See `examples/sample-emails.md` for nine fully worked before/after examples across all patterns.

## Best Practices
- **BLUF.** State the ask or conclusion in the first two sentences. Busy readers skim.
- **One email, one primary ask.** Multiple asks dilute response rate; split or use a numbered list with a clear primary.
- **Specific subject lines.** "Quick question" tells the reader nothing; "Approval needed: Q3 budget by Thu" does.
- **Deadlines beat urgency words.** "by Thursday 5pm" outperforms "ASAP".
- **Make replying easy.** Offer concrete options ("Tue 2pm or Wed 10am?") instead of open questions.
- **Read it aloud.** If it sounds stiff or passive-aggressive, it reads that way too.
- **Match the channel.** If it needs more than ~200 words or three back-and-forths, suggest a call or doc.

## Common Pitfalls
- **Vague CTA** — "let me know your thoughts" with no owner or date. Always name the action and deadline.
- **Burying the ask** — the request hides in paragraph four. Move it up.
- **Tone mismatch** — overly casual to a senior stakeholder, or stiff with a close colleague.
- **Wall of text** — no paragraph breaks. Use white space, bullets, and bold for the one key line.
- **Apology overload** — "sorry to bother you" weakens you. State the need plainly and respectfully.
- **Passive hedging** — "it would be great if maybe we could possibly..." Cut qualifiers.
- **No clear next step** — the reader closes the email unsure what to do.

## Supporting Files
- `references/email-patterns.md` — type-by-type templates (request, follow-up, decline, apology, update, intro, cold outreach, escalation) and subject-line rules.
- `references/tone-guide.md` — the formality/warmth dial, phrase swaps, opener/closer banks, cross-cultural notes.
- `references/checklist.md` — pre-send self-review checklist.
- `templates/email-template.md` — fill-in skeleton.
- `examples/sample-emails.md` — nine before/after worked examples.
- `scripts/email_lint.py` — heuristic linter for length, hedging, passive voice, weak subject lines, and missing CTA.
