# Worked Example: From Vague Request to Evaluated Prompt

## 1. The vague request
> "Write me a prompt to sort support emails."

## 2. Clarify (Process step 1)
Asked and resolved:
- **Task**: classify each incoming support email into one category.
- **Consumer**: a router script (machine-parsed) → needs strict output.
- **Categories**: billing, technical, account, other.
- **Success criteria**: >=95% exact-match on a golden set; never invent a category.
- **Failure modes seen**: previous prompt returned sentences like "This looks like a billing issue." instead of a label.

## 3. Pattern (step 2)
Classification → enum/JSON output, low temperature, optional rationale only for debugging.

## 4. First draft (steps 3-4)
```
You classify customer support emails for a routing system.
Label the <email> as exactly one of: billing, technical, account, other.
Rules:
- Choose the single best fit; if it spans two, pick the primary intent.
- Charges, refunds, invoices, pricing -> billing.
- Bugs, crashes, errors, outages -> technical.
- Login, profile, password, settings -> account.
- Anything else (praise, spam, unclear) -> other.
- If you cannot tell, use other. Never invent a category.

<email>{{input}}</email>

Output ONLY this JSON, no prose, no code fences:
{"label": "billing"|"technical"|"account"|"other"}
```

## 5. Few-shot for the edge case (step 6)
The ambiguous "charged but feature broken" case was misrouted. Added one shot demonstrating the precedence rule (billing wins when money is the core complaint):
```
<email>I paid for Pro but the export button is greyed out.</email>
{"label": "billing"}
```

## 6. Params (step 7)
temperature=0, max_tokens=20, stop sequence `}`.

## 7. Build the eval (step 8)
Golden set: `scripts/golden.sample.json` (5 cases incl. an edge/ambiguous one).
Scorer: `json` (compares the `label` field).

Run:
```
python scripts/eval_prompts.py \
  --golden scripts/golden.sample.json \
  --prompt v1.txt --prompt v2.txt \
  --scorer json --show 3
```

## 8. Result & iteration (step 9)
- v1 (no few-shot): mean 0.80 — failed the ambiguous billing/technical case.
- v2 (added the precedence shot): mean 1.00 on the set; ambiguous tag went 0.0 → 1.0.
- Kept v2. Added the failing case permanently to the golden set to guard against regressions.

## Takeaways
- The fix was a single targeted example + an explicit precedence rule — changed one variable at a time.
- A machine-checkable output (`json` scorer) made the win unambiguous and automatable.
