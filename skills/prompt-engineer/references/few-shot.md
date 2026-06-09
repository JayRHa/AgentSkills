# Few-Shot Examples

Few-shot = showing the model input→output demonstrations before the real input.

## How many
- **0-shot**: try first for capable models on simple, well-described tasks.
- **1-shot**: when the exact output format matters and is hard to describe.
- **2-5 shot**: when there are edge cases, ambiguous categories, or a tricky format. This is the sweet spot for most tasks.
- **More than ~8**: rarely helps; costs tokens and can cause the model to overfit to surface patterns. Consider fine-tuning or retrieval instead.

## Selection (what to include)
- Cover the **hard and edge cases**, not the obvious ones. The model usually handles easy cases without help.
- Include at least one example of each **class/label** for classification.
- Include the **boundary/uncertain** case and show the correct "safe" behavior (e.g., returning null, choosing "other").
- Make examples **diverse** in surface form so the model learns the rule, not a template.
- Ensure examples are **correct** — one wrong demonstration poisons the pattern.

## Ordering
- For classification, **balance and shuffle** labels; avoid grouping all of one class together (models can anchor on recency/position).
- Put the **most representative** example near the start; a tricky edge case can go last (recency).
- Keep ordering **fixed** during evaluation so results are comparable.

## Formatting
- Use a **consistent, parseable delimiter** between input and output across all examples and the real query.
- Match the example output format **byte-for-byte** to what you want back.
- Label the parts clearly:
```
Input: <text>...
Output: {"label": "billing"}

Input: <text>...
Output: {"label": "technical"}

Input: <text>{{real input}}</text>
Output:
```
- For chat APIs, you can encode shots as alternating user/assistant turns — often cleaner and respects role boundaries.

## Dynamic / retrieval-based few-shot
For large, varied inputs, retrieve the k most similar labeled examples per query (semantic search over a labeled pool) instead of a fixed set. Improves accuracy at the cost of a retrieval step and variable prompt size.

## Pitfalls
- Demonstrations that subtly conflict with your written rules → the model follows the examples.
- All examples sharing an irrelevant trait (e.g., all short) → model assumes the trait is required.
- Stale examples after a format change → update examples whenever the schema changes.
