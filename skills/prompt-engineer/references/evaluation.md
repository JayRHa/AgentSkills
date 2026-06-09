# Prompt Evaluation

You cannot optimize what you do not measure. Build a small eval before iterating.

## 1. Build a golden set
- 10-50 representative cases to start; grow it as you find failures (every production bug becomes a new test case).
- Each case: `input`, `expected` (or rubric), and optionally `tags` (edge case, class, difficulty).
- Include the hard 20%: ambiguous, adversarial, empty/missing-data, and out-of-scope cases.
- Keep a **held-out** slice you don't look at while iterating, to catch overfitting.

## 2. Pick a scoring method

| Output kind | Scorer |
|---|---|
| Exact label / number | Exact match / normalized exact match |
| JSON object | Field-by-field match + schema-valid check |
| Short factual answer | Contains / regex / set overlap |
| Free text quality | Rubric (LLM-as-judge) or human rating |
| Two competing prompts | Pairwise preference (judge or human) |

Prefer automatic, deterministic scorers whenever the output is checkable.

## 3. LLM-as-judge
When quality is subjective (helpfulness, tone, faithfulness):
- Give the judge a **rubric** with a fixed scale (e.g., 1-5) and a description of each level.
- Require a **short justification** field before the score (improves reliability).
- Run the judge at **temperature 0**.
- **Calibrate**: have a human label ~10-20 cases, compare to the judge, adjust the rubric until they agree.
- Mitigate bias: randomize answer order in pairwise judging (position bias); strip identifying markers; don't let a model judge its own outputs preferentially when avoidable.

Example judge prompt:
```
Score the <answer> for faithfulness to the <source> on a 1-5 scale.
5=fully supported, no unsupported claims; 1=mostly fabricated.
First write a one-sentence justification, then the score.
Return JSON: {"justification": string, "score": 1|2|3|4|5}
```

## 4. Pairwise comparison
To choose between prompt A and B, run both on the golden set and have a judge (or human) pick the better output per case. Report win rate. Counterbalance order (run A-first and B-first) to cancel position bias.

## 5. Reporting & sanity
- Report **pass rate** (or mean rubric score) per variant, plus a breakdown by tag.
- With small sets, treat tiny deltas skeptically; a 1/20 difference is noise. Prefer clear, consistent wins.
- Track **regressions**: a change that fixes case X may break case Y — that's why you keep the full set.
- Log: prompt version, params, date, score. Use `templates/prompt-spec.md`.

## 6. Iterate loop
1. Baseline: score the current prompt.
2. Hypothesize one change (clearer rule, an example, a format tweak).
3. Change ONE variable.
4. Re-run eval. Keep if it wins on the full set (not just the targeted case).
5. Repeat until diminishing returns.

Use `scripts/eval_prompts.py` to automate steps 1 and 4.
