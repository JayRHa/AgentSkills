---
name: job-description-writer
description: Writes inclusive, accurate, and compelling job descriptions with a clear role summary, outcome-oriented responsibilities, must-have vs. nice-to-have requirements, impact framing, and compensation/logistics. Use this skill when the user asks to "write a job description", "create a job posting", "draft a JD", "post a role", "rewrite this job ad to be more inclusive", "turn this requirements list into a posting", or needs help defining responsibilities, qualifications, leveling, or salary ranges for a hire.
license: MIT
---

# Job Description Writer

## Overview
Keywords: job description, JD, job posting, job ad, role, hiring, recruiting, responsibilities, requirements, qualifications, inclusive hiring, salary range, level, seniority, EEO, talent acquisition.

This skill produces job descriptions that attract qualified, diverse candidates and accurately represent the role. A strong JD does three jobs at once: it **markets** the role and company, it **filters** for fit (without over-filtering), and it sets **expectations** for the first year. The most common failure modes are inflated requirement lists that deter qualified candidates (especially underrepresented groups), vague responsibilities that describe activity instead of outcomes, and biased or coded language.

Always optimize for: **clarity, inclusivity, accuracy, and measurable impact.**

## Workflow

1. **Gather inputs.** Collect the essentials before writing. If the user hasn't provided them, ask concise clarifying questions (batch them). Minimum needed: job title, level/seniority, team & reporting line, top 3-5 outcomes the hire owns, location/remote policy, employment type, and any compensation data. See `references/intake-questions.md` for the full checklist.

2. **Define outcomes first, then responsibilities.** Before listing duties, write what success looks like at 30/90/365 days. Convert each outcome into 5-8 responsibility bullets phrased as ownership ("Own X", "Drive Y", "Ship Z") rather than activity ("Responsible for attending meetings").

3. **Split requirements into Must-have vs. Nice-to-have.** Keep must-haves to 4-7 genuinely non-negotiable items. Everything aspirational goes under nice-to-have. Strip proxy requirements (degree, exact years) unless legally or functionally essential. See `references/inclusive-language.md` for substitutions.

4. **Add impact + level context.** State why the role exists, who it affects, and how performance is measured. Calibrate scope language to the level (see the leveling table below).

5. **Scrub for bias and accessibility.** Run `scripts/jd_lint.py` to flag biased/coded terms, gendered language, jargon, requirement inflation, and missing sections. Apply fixes.

6. **Add logistics, comp, and EEO statement.** Include salary range (transparency is legally required in many jurisdictions and improves applies), benefits highlights, application process, and an equal-opportunity statement.

7. **Assemble using the template.** Fill `templates/job-description-template.md`. Keep total length to roughly 400-700 words for the body; longer postings reduce completion rates.

## Structure of a Great JD

| Section | Purpose | Keep it |
|---|---|---|
| Title | Searchable, standard, level-clear | "Senior Backend Engineer" not "Backend Ninja" |
| Hook (2-3 sentences) | Why the role + company matter | Specific, no buzzword soup |
| About the team | Context and mission | 2-4 sentences |
| What you'll do | Outcome-based responsibilities | 5-8 bullets, verb-led |
| What you'll bring | Must-have requirements | 4-7 bullets, no inflation |
| Nice to have | Aspirational extras | Optional, clearly labeled |
| Impact / success | How impact is measured | 30/90/365 or KPIs |
| Compensation & benefits | Range + highlights | Be transparent |
| Logistics | Location, type, process | Clear next steps |
| EEO statement | Inclusion commitment | Required |

## Leveling / Scope Calibration

Match the language to the level so candidates self-select accurately.

| Level | Scope verb | Typical responsibility framing | Typical experience signal |
|---|---|---|---|
| Junior / IC1 | Contributes to | "Complete well-scoped tasks with guidance" | 0-2 yrs equivalent |
| Mid / IC2-3 | Owns | "Own features end-to-end; unblock yourself" | 2-5 yrs equivalent |
| Senior / IC4 | Drives | "Drive projects across the team; mentor others" | 5+ yrs equivalent |
| Staff / IC5+ | Leads / influences | "Set technical direction; influence org strategy" | Deep domain mastery |
| Manager | Builds & develops | "Hire, grow, and lead a team; own delivery & growth" | Prior leadership |

Avoid the trap of "years of experience" as the primary gate. Prefer demonstrated capability statements.

## Worked Example
See `examples/jd-example.md` for a raw input (messy requirements dump) transformed into a finished, inclusive job description, including before/after of biased lines.

## Best Practices
- **Outcomes over activities.** "Reduce checkout latency by owning the payments service" beats "Work on backend systems."
- **Cap the must-have list.** Research shows candidates (women especially) often don't apply unless they meet ~100% of listed requirements. Shorter lists widen the pool.
- **Use "you" and active voice.** It reads as an invitation, not a spec sheet.
- **Show the salary range.** Transparency increases qualified applies and is legally mandated in many places.
- **Name concrete tech/tools** but mark transferable skills as acceptable ("or similar").
- **Lead with mission and team** so candidates understand the "why."
- **One title, standard naming** so the role is searchable on job boards.
- **Run the linter** (`scripts/jd_lint.py`) before finalizing; treat it as a checklist, not gospel.

## Common Pitfalls
- **Requirement inflation:** listing "nice-to-haves" as "must-haves" (e.g., 5 frameworks, a degree, and 10 years for a mid role). Move them or cut them.
- **Coded/gendered language:** "rockstar," "ninja," "aggressive," "dominant," "he/his," "young and energetic." Replace per `references/inclusive-language.md`.
- **Wall-of-text responsibilities** describing process instead of impact.
- **Missing comp or EEO** sections — both hurt apply rates and can create legal exposure.
- **Generic hooks** ("We are a fast-paced, dynamic team...") that say nothing. Be specific about the product, the team, and the problem.
- **Mismatched level signals:** senior pay with junior scope, or vice versa, causes drop-off and bad hires.
- **Accessibility-blocking phrasing:** "must be able to lift 50 lbs" or "valid driver's license" when not essential to the job can exclude qualified candidates and raise ADA concerns — only include genuine bona fide requirements.

## Files
- `references/intake-questions.md` — questions to ask before writing.
- `references/inclusive-language.md` — biased→inclusive substitution tables and rules.
- `scripts/jd_lint.py` — stdlib-only linter that flags issues in a draft JD.
- `templates/job-description-template.md` — fill-in template.
- `examples/jd-example.md` — full before/after worked example.
