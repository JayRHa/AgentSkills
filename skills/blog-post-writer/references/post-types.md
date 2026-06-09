# Post Types — Full Structures

Match structure to reader goal. Each type below gives the section skeleton and notes.

## 1. Tutorial / How-To
Reader goal: complete a task successfully.
```
Title: How to <outcome>
Hook: the pain this removes
What you'll build (1-2 sentences + final result/screenshot up front)
Prerequisites (versions, accounts, prior knowledge) — bullet list
Step 1..N (imperative heading, code, expected output, brief why)
Verify it works (how the reader confirms success)
Troubleshooting (top 2-3 errors and fixes)
Takeaway + next steps / link to repo
```
Notes: show the end state early so readers know it's worth it. Every step must be copy-pasteable. State exact versions — tutorials rot.

## 2. Deep Dive / "How We Built X"
Reader goal: understand the decisions and tradeoffs.
```
Title: How we <result> (+ the number)
Hook: the problem at its worst moment
The problem & why existing approaches didn't fit
Constraints (scale, latency, team, deadline)
The approach (architecture, with a diagram if useful)
Key decisions & tradeoffs (what we rejected and why)
Results — with before/after metrics
What we'd do differently
Takeaway
```
Notes: metrics are the credibility. "Faster" is worthless; "p99 800ms→90ms" is gold. Honesty about tradeoffs earns trust.

## 3. Opinion / Architecture Essay
Reader goal: be persuaded (or productively challenged).
```
Title: a clear stance
Hook: the contrarian claim
The common view (steelman it fairly)
Why it falls short (evidence, examples)
The better approach
The strongest counterargument + your response
When the conventional view IS right (nuance = credibility)
Recommendation / takeaway
```
Notes: steelman the opposing view before knocking it. Address the best counterargument, not a strawman.

## 4. Concept Explainer
Reader goal: finally understand something.
```
Title: <Concept>, explained / What is <X>?
Hook: why the concept confuses people / why it matters
Analogy (a familiar mental model)
The precise definition
A concrete worked example (code or numbers)
Common misconceptions ("people think X, actually Y")
When you'd actually use it
Takeaway / mental model to keep
```
Notes: analogy first, then precision — never only the textbook definition. Name the misconceptions explicitly.

## 5. Announcement / Release
Reader goal: decide whether to adopt/upgrade.
```
Title: <Product> <version>: <headline feature/benefit>
Hook: the one-line of what's new and why you'd care
The problem it solves
Key features (3-5, each with a tiny example)
Breaking changes / migration notes
Getting started (install + minimal example)
What's next / changelog link
```
Notes: lead with reader benefit, not internal milestones. Migration friction must be honest and prominent.

## Length guide
- Tutorial: 1,000-2,000 words.
- Deep dive / opinion: 1,200-2,500 words.
- Explainer: 800-1,500 words.
- Announcement: 500-1,200 words.
Length serves the reader — cut anything that doesn't advance the single takeaway.
