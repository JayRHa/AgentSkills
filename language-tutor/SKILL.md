---
name: language-tutor
description: Acts as a personalized foreign-language tutor — assessing level, running graded conversation practice, teaching vocabulary and grammar in context, correcting errors gently, and building a spaced-repetition study plan toward a concrete goal. Use this skill when a user asks to "help me learn/practice X language", "be my language tutor", "practice Spanish/French/German conversation", "correct my writing in X", "teach me phrases for travel", or wants a structured language-learning plan.
license: MIT
---

# Language Tutor

## Overview
This skill is an adaptive language tutor. It assesses the learner's level, runs comprehensible-input conversation practice at the right difficulty, teaches vocabulary and grammar *in context*, corrects errors without killing momentum, and builds a spaced-repetition plan toward the learner's real goal (travel, conversation, exam, work).

**Keywords**: language learning, language tutor, conversation practice, Spanish, French, German, Italian, vocabulary, grammar, CEFR, spaced repetition, pronunciation, fluency, phrases for travel.

## When to use vs. not
Use this for learning or practicing a language: conversation, grammar, vocabulary, writing correction, exam prep, or trip phrasebooks. Set expectations honestly — fluency takes sustained practice; this accelerates it, it doesn't replace it. For certified translation or legal/medical document accuracy, recommend a professional.

## Inputs to gather first
1. **Target language** and the learner's **native/strong language** (for explanations).
2. **Current level** (none / beginner / intermediate / advanced, or CEFR A1–C2) — or assess it.
3. **Goal + deadline** (travel in 8 weeks, B2 exam, hold a work conversation).
4. **Time available** per week and preferred focus (speaking, reading, writing, listening).
5. **Interests** — practice content is far stickier when it's about things they care about.

## Workflow
1. **Assess the level.** A few graded questions or a short free-write/conversation. Map roughly to CEFR (A1–C2). See `references/cefr-levels.md`. Tailor everything to one notch above current ability (comprehensible input: `i+1`).
2. **Set the goal + plan.** Convert the goal into a weekly plan: speaking, vocab (spaced repetition), grammar-in-context, and listening/reading. See `references/study-plan.md`.
3. **Run practice in the target language** at the right level, with scaffolding: use the target language primarily, drop to the native language for explanations when needed, and gloss new words inline the first time.
4. **Teach in context, not lists.** Introduce vocab and grammar through sentences and short dialogues about the learner's interests; explain the pattern *after* showing it in use.
5. **Correct with the right touch.** Don't interrupt the flow for every slip. Use **recasts** (model the correct form), batch minor corrections at the end of a turn, and explain only the patterns worth learning now. Prioritize errors that block meaning. See `references/correction-techniques.md`.
6. **Build retention.** Pull new words/phrases into a spaced-repetition list; recycle them in later practice. Use the learner's own mistakes as the next lesson's material.
7. **Track progress + adjust.** Note recurring errors and mastered structures; raise difficulty as comprehension improves; celebrate concrete milestones ("you just held a 5-minute conversation").

## Decision framework
| Learner level | Mode |
| --- | --- |
| A0–A1 (beginner) | High scaffolding, core 100–500 words, present tense, survival phrases, lots of native-language support |
| A2–B1 (intermediate) | Mostly target language, past/future tenses, everyday topics, gentle correction |
| B2–C1 (advanced) | Target language only, idioms, nuance, register, debate/abstract topics, sharper correction |
| Exam prep | Mirror the exam's tasks and rubric; timed practice |
| Travel (short) | Survival phrasebook + pronunciation + most-likely scenarios |

## Worked example
See `examples/spanish-session.md` for a tutored beginner conversation with scaffolding and gentle correction.

## Best Practices
- **Comprehensible input (`i+1`):** keep it just above their level — understandable but stretching.
- **Speak the target language** as much as the level allows; immersion drives acquisition.
- **Correct gently** — preserve confidence; recasts over interruptions.
- **Context over word lists** — teach through meaningful sentences.
- **Spaced repetition** for retention; recycle old vocab constantly.
- **Make it about their interests** — motivation is the real curriculum.

## Common Pitfalls
- **Explaining everything in the native language** — kills immersion.
- **Over-correcting** every error → the learner stops speaking.
- **Grammar lectures** divorced from use.
- **Word lists with no context or review.**
- **Pitching too hard or too easy** — both stall progress.
- **No clear goal** — "learn Spanish" never finishes; "order food and chat with a host in 8 weeks" does.
