---
name: prompt-engineer
description: Designs, refines, and systematically evaluates LLM prompts using structure, role framing, few-shot examples, explicit output contracts, and reasoning scaffolds. Use this skill when the user wants to write or improve a prompt, build a system prompt, craft few-shot examples, reduce hallucination or refusals, enforce a JSON/structured output, design an LLM-as-judge or eval rubric, debug inconsistent or low-quality model outputs, or compare prompt variants ("optimize this prompt", "why is the model ignoring my instructions", "make it return valid JSON", "write a prompt that...", "evaluate these prompts").
license: MIT
---

# Prompt Engineer

## Overview
This skill turns vague intent into a precise, testable prompt and provides a repeatable loop for measuring and improving prompt quality. It covers prompt anatomy, role/system framing, few-shot example selection, output contracts (JSON/schema), reasoning scaffolds (chain-of-thought, decomposition), and rigorous evaluation (golden sets, rubrics, LLM-as-judge, pairwise comparison).

Keywords: prompt engineering, system prompt, few-shot, chain-of-thought, output format, JSON mode, structured output, hallucination, refusal, LLM-as-judge, eval rubric, prompt optimization, A/B prompt, temperature, prompt template.

Use this skill whenever the user is authoring, debugging, or comparing prompts — not when they need a finished answer to the underlying question itself.

## When to use vs. not
- USE: "Write/improve a prompt", "make output reliably JSON", "model ignores instructions", "build an eval for my prompt", "pick few-shot examples", "reduce hallucinations".
- DON'T USE: the user just wants the task done once (answer the question directly). Only invoke prompt engineering when the *prompt artifact* is the deliverable or the problem.

## Process
Follow these steps in order. Skip a step only with a stated reason.

1. **Clarify the job.** Pin down: the task, the consumer of the output (human vs. parser/code), success criteria, hard constraints (length, format, forbidden content), and failure modes seen so far. If two or more of these are unknown and the prompt is non-trivial, ask before writing.
2. **Choose the prompt pattern.** Match the task to a pattern using the table in `references/patterns.md` (extraction, classification, generation, transformation, agentic/tool-use, judge). The pattern dictates structure and which scaffolds matter.
3. **Draft with the anatomy.** Assemble the prompt from the canonical sections below. Put durable instructions in the system prompt; put per-request data in the user message.
4. **Add an output contract.** If a machine reads the output, specify an exact schema, give a filled example, and instruct "output only the JSON, no prose". See `references/output-contracts.md`.
5. **Add reasoning scaffold only if needed.** Use step-by-step / decomposition for multi-step reasoning. Keep reasoning OUT of structured output (use a separate field or a scratchpad you discard).
6. **Select few-shot examples** (2-5) that cover edge cases and the exact target format. Order matters; cover the hard cases. See `references/few-shot.md`.
7. **Set decoding params.** Recommend temperature/top-p for the task (deterministic extraction → low temp; creative → higher). See the params table in `references/patterns.md`.
8. **Build an eval.** Create a small golden set (10-50 cases) and a scoring method (exact match, rubric, or pairwise LLM-judge). Use `scripts/eval_prompts.py` to run variants and compute pass rates. See `references/evaluation.md`.
9. **Iterate.** Change ONE variable at a time, re-run the eval, keep what wins. Record results in the table from `templates/prompt-spec.md`.

## Prompt anatomy (canonical section order)
Put these in roughly this order; omit sections that don't apply.

1. **Role / persona** — who the model is and its expertise ("You are a senior tax accountant...").
2. **Task** — one imperative sentence of what to do.
3. **Context / inputs** — background, the data to operate on, delimited clearly (XML-style tags or fenced blocks).
4. **Instructions / rules** — numbered constraints, do's and don'ts, edge-case handling.
5. **Reasoning directive** — e.g., "Think step by step in a <scratchpad> before answering" (only if needed).
6. **Output format** — exact schema/shape + a concrete example.
7. **Examples (few-shot)** — input→output pairs demonstrating format and edge cases.
8. **Guardrails** — what to do when uncertain, missing data, or out of scope ("If the document lacks a date, return null — do not guess").

## Quick heuristics
- **Be specific over polite.** Replace "please try to" with direct imperatives.
- **Show, don't tell** the format: one example beats a paragraph of description.
- **Delimit inputs** with tags like `<document>...</document>` so data can't be confused with instructions (also reduces prompt-injection surface).
- **Positive instructions** ("respond in formal English") work better than negative ("don't be informal"); when you must forbid, also state the desired behavior.
- **Give an out.** Always tell the model what to do when it can't comply, or it will hallucinate.
- **Constrain reasoning location.** Let it think, but in a place you can strip, so structured output stays clean.
- **One variable per iteration** so eval deltas are attributable.

## Best Practices
- Keep stable instructions in the system prompt; keep variable data in the user turn (enables prompt caching and cleaner evals).
- Prefer machine-checkable output (JSON, enum labels) so evals can be automated.
- Cover the hardest 20% of cases in few-shot examples; easy cases rarely need demonstration.
- Version every prompt and store eval scores beside it (`templates/prompt-spec.md`).
- For judges, score on a rubric with a fixed scale and require a short justification field; calibrate the judge against human labels on a few cases.
- Lower temperature for anything parsed downstream; reserve higher temperature for ideation/variety.

## Common Pitfalls
- **Vague success criteria** → unmeasurable prompt; you can't optimize what you don't score.
- **Reasoning inside JSON** → invalid/parse-failing output; move reasoning to a separate field or scratchpad.
- **Conflicting instructions** ("be concise" + "be thorough") → unpredictable behavior; rank or reconcile them.
- **Overfitting to demo cases** → great on examples, poor in production; keep a held-out eval set.
- **No uncertainty path** → confident hallucinations; always define the "I don't know / null" behavior.
- **Changing many things at once** → can't tell what helped; isolate variables.
- **Eyeballing instead of measuring** → confirmation bias; run `scripts/eval_prompts.py` on a golden set.

## Bundled resources
- `references/patterns.md` — task→pattern mapping, per-pattern templates, decoding params, anti-injection notes.
- `references/output-contracts.md` — enforcing JSON/schema, common failure fixes, validation strategy.
- `references/few-shot.md` — how many examples, selection, ordering, formatting.
- `references/evaluation.md` — building golden sets, scoring methods, LLM-as-judge, statistical sanity.
- `templates/prompt-spec.md` — fill-in spec capturing the prompt, params, and eval results.
- `examples/email-classifier.md` — full worked example from vague request to evaluated prompt.
- `scripts/eval_prompts.py` — runnable harness that scores prompt variants against a golden set (exact-match and pluggable scorers).
