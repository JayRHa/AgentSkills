---
name: interview-prep
description: Prepares a candidate for a specific job interview — generating likely questions, coaching STAR-method stories, drilling behavioral and role-specific answers, and producing smart questions to ask back. Use this skill when a user asks to "help me prep for an interview", "what questions will they ask", "practice interview questions", "build STAR stories", "prepare for a behavioral/technical/system-design interview", or wants a mock interview for a given role and company.
license: MIT
---

# Interview Prep

## Overview
This skill builds a focused interview-prep plan for a *specific* role: the questions most likely to come up, polished STAR stories from the candidate's real experience, crisp answers to the hard ones (weaknesses, gaps, "why us"), and strong questions to ask the interviewer. It can also run a mock interview loop with feedback.

**Keywords**: interview, interview prep, behavioral interview, STAR method, mock interview, technical interview, system design, tell me about yourself, why this company, salary question, questions to ask.

## When to use vs. not
Use this to prepare for upcoming interviews (phone screen, behavioral, technical, panel, final). It coaches *the candidate's own* stories — it does not invent experience. For pure coding/system-design content, pair with engineering skills; this skill focuses on structure, narrative, and delivery.

## Inputs to gather first
1. **Role + company + the job description.**
2. **Interview stage & format** (recruiter screen, hiring-manager, technical, panel, final).
3. The candidate's **key projects/achievements** to mine for stories.
4. **Known concerns**: gaps, a pivot, thin experience in one area, nerves.
5. Whether they want a **study plan** or a **live mock**.

## Workflow
1. **Map the question surface.** From the JD + stage, generate the realistic question set: ~5 behavioral, ~3 role-specific, plus the universals ("tell me about yourself," "why this company," "biggest weakness"). See `references/question-bank.md`.
2. **Build a story bank.** Identify 4–6 of the candidate's experiences and shape each into a **STAR** story (Situation, Task, Action, Result). Tag each story with the competencies it demonstrates (leadership, conflict, failure, ambiguity, impact) so one story can answer several questions. See `references/star-method.md`.
3. **Craft "Tell me about yourself."** A 60–90 second present → past → future arc tuned to the role. Not a life history.
4. **Pre-write the hard ones.** "Greatest weakness" (real + mitigation), "why leaving," employment gap, "why this company" (specific + true), and the salary question (deflect-then-range). See `references/tricky-questions.md`.
5. **Prepare questions to ask back.** 4–6 thoughtful questions about the role, team, success metrics, and challenges — never things a 30-second site visit answers.
6. **Run a mock (optional).** Ask one question at a time, let the candidate answer, then give specific feedback: structure, concreteness, length, filler. Iterate.
7. **Logistics + close.** Confirm format/time-zone/dress, who they're meeting, a pre-interview warmup, and a thank-you-note plan.

## Decision framework
| Interview type | Drill mostly… |
| --- | --- |
| Recruiter screen | "Tell me about yourself", motivation, salary range, logistics |
| Hiring manager | Behavioral STAR stories tied to the team's real problems |
| Technical | Role skills + thinking-out-loud + one or two STAR stories on hard bugs |
| Panel / cross-functional | Collaboration, conflict, influence-without-authority stories |
| Final / executive | Vision, "why us", culture-add, long-term goals |

## Worked example
See `examples/behavioral-star.md` for a raw experience turned into a polished STAR answer with interviewer-style feedback.

## Best Practices
- **STAR with the result first or last, never buried.** Quantify the result.
- **One strong story can cover many questions** — reuse with a different emphasis.
- **Be specific and concise.** 90 seconds–2 minutes per behavioral answer.
- **Research the company** enough to make "why us" undeniably specific.
- **Prepare questions that show you've thought about the actual job.**
- **Practice out loud**, not just in your head — delivery is half the score.

## Common Pitfalls
- **Rambling** with no structure — interviewers lose the thread.
- **Vague results** ("it went well") instead of metrics or concrete outcomes.
- **Memorizing scripts** so tightly the delivery sounds robotic — internalize beats, not words.
- **Trash-talking a past employer** when asked why you're leaving.
- **"I don't have any questions"** — reads as disinterest.
- **A fake weakness** ("I work too hard") — interviewers see through it.
