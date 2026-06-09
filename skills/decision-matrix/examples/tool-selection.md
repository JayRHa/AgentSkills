# Worked Example: Selecting a Project-Management Tool

This example shows the full flow from framing to recommendation, including the JSON input
for `scripts/decision_matrix.py` and its output.

## 1. Frame

> Decision: Which project-management tool should our 12-person team adopt for the next 2 years?

## 2. Options

- Tool A (cheap, basic)
- Tool B (mid-market, polished)
- Tool C (enterprise, integration-heavy)

## 3. Constraints (applied first, pass/fail)

- Must support SSO  -> all three pass.
- Monthly cost <= $30/user  -> all three pass.

No option is eliminated, so all three enter the matrix.

## 4. Criteria & weights (set before scoring)

| Criterion     | Weight | Direction |
|---------------|:------:|-----------|
| Ease of use   |   5    | benefit   |
| Integrations  |   4    | benefit   |
| Support       |   2    | benefit   |
| Price ($/user/mo) | 4  | cost (lower better) |

## 5. Scores / raw values

Qualitative criteria scored 1-5. Price uses raw dollars (the script inverts it).

| Criterion     | Tool A | Tool B | Tool C |
|---------------|:------:|:------:|:------:|
| Ease of use   |   3    |   5    |   4    |
| Integrations  |   3    |   4    |   5    |
| Support       |   4    |   3    |   5    |
| Price         |  $10   |  $20   |  $28   |

## 6. Input file

`tool-selection.json`:

```json
{
  "title": "PM tool selection",
  "scale_max": 5,
  "criteria": [
    {"name": "Ease of use",  "weight": 5},
    {"name": "Integrations", "weight": 4},
    {"name": "Support",      "weight": 2},
    {"name": "Price",        "weight": 4, "direction": "cost"}
  ],
  "options": {
    "Tool A": {"Ease of use": 3, "Integrations": 3, "Support": 4, "Price": 10},
    "Tool B": {"Ease of use": 5, "Integrations": 4, "Support": 3, "Price": 20},
    "Tool C": {"Ease of use": 4, "Integrations": 5, "Support": 5, "Price": 28}
  }
}
```

## 7. Run it

```
python3 scripts/decision_matrix.py tool-selection.json --sensitivity
```

Representative output (Price column shows the inverted, normalized scores — $10 -> 5.00,
$28 -> 1.00):

```
== PM tool selection ==

Criterion       Wt  Tool B  Tool C  Tool A
--------------  --  ------  ------  ------
Ease of use     5   5.00    4.00    3.00
Integrations    4   4.00    5.00    3.00
Support         2   3.00    5.00    4.00
Price (cost)    4   3.00    1.00    5.00
--------------  --  ------  ------  ------
INDEX (0-100)       77.3    73.3    72.0

Recommended: Tool B  (index 77.3/100)
Margin over runner-up (Tool C): 4.0 pts  <-- NEAR TIE, inspect closely

Sensitivity (winner stability vs. +/-25% on each weight):
  [ok]   Ease of use: winner stays Tool B
  [FLIP] Integrations: +25% -> Tool C
  [ok]   Support: winner stays Tool B
  [FLIP] Price: -25% -> Tool C
  Top-2 margin: 4.0 index points -> FRAGILE / near-tie
```

## 8. Interpretation

Tool B edges out Tool C by only 4 points — a near-tie. Sensitivity shows the winner flips
to Tool C if Integrations matters 25% more, or if Price matters 25% less. So the real
question for the team is: **how much do we value integrations vs. price?** The matrix has
narrowed three options to a crisp two-way trade-off and named the deciding factor. If
integrations are strategically critical, choose Tool C; if cost discipline dominates,
Tool B. Document whichever assumption you commit to.
