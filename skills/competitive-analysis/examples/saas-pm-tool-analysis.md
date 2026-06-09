# Worked Example: Mid-Market PM Tool Competitive Analysis

This shows the skill end-to-end for a fictional company, **FlowDeck**, a project/work management SaaS targeting 50-500 person software teams.

## 1. Objective
Decide where FlowDeck should differentiate over the next 12 months versus Asana, Monday.com, and Linear.

## 2. Market Definition
- Category: work/project management software
- Buyer / ICP: VP Eng or Head of PMO at a 50-500 person software company
- Geography: North America + EU
- JTBD: When coordinating cross-functional software delivery, the buyer wants one source of truth that both engineers and executives will actually use, so they can ship predictably and report status without manual rollups.

## 3. Competitor Set
| Competitor | Tier | One-line positioning |
|---|---|---|
| Linear | Direct | "The issue tracker built for high-performance software teams." |
| Asana | Direct | "Cross-team work management for the whole company." |
| Monday.com | Direct | "A flexible Work OS anyone can configure." |
| Jira | Indirect | Heavyweight dev tracking (incumbent). |
| Status quo | Substitute | Spreadsheets + Slack + manual status decks. |

## 4. Evidence Table (abridged)
| Dimension | FlowDeck | Linear | Asana | Monday | Source/date |
|---|---|---|---|---|---|
| Dev workflow fit | Good | Excellent | Fair | Fair | product docs, 2026-05 |
| Ease of use | Good | Good | Good | Excellent | G2, 2026-05 |
| Cross-team reporting | Good | Weak | Fair | Fair | review analysis, 2026-05 |
| Entry price (/user/mo) | $8 | $8 | $10.99 | $9 | pricing pages, 2026-05 |
| Integrations | 40+ | 50+ | 200+ | 200+ | marketplaces, 2026-05 |

## 5. Weighted Comparison Matrix

Input (`pm.json`):
```json
{
  "dimensions": [
    {"name": "Ease of use", "weight": 25},
    {"name": "Dev workflow fit", "weight": 25},
    {"name": "Price", "weight": 20},
    {"name": "Integrations", "weight": 15},
    {"name": "Cross-team reporting", "weight": 15}
  ],
  "competitors": [
    {"name": "FlowDeck", "scores": {"Ease of use": 4, "Dev workflow fit": 4, "Price": 4, "Integrations": 3, "Cross-team reporting": 4}},
    {"name": "Linear",   "scores": {"Ease of use": 4, "Dev workflow fit": 5, "Price": 4, "Integrations": 4, "Cross-team reporting": 2}},
    {"name": "Asana",    "scores": {"Ease of use": 4, "Dev workflow fit": 3, "Price": 3, "Integrations": 5, "Cross-team reporting": 3}},
    {"name": "Monday",   "scores": {"Ease of use": 5, "Dev workflow fit": 3, "Price": 4, "Integrations": 5, "Cross-team reporting": 3}}
  ]
}
```

Run:
```
python3 scripts/compare_matrix.py pm.json
```

Output:
```
## Weighted Comparison Matrix

| Dimension | Weight | FlowDeck | Linear | Asana | Monday |
|---|---|---|---|---|---|
| Ease of use | 25 | 4 | 4 | 4 | 5 |
| Dev workflow fit | 25 | 4 | 5 | 3 | 3 |
| Price | 20 | 4 | 4 | 3 | 4 |
| Integrations | 15 | 3 | 4 | 5 | 5 |
| Cross-team reporting | 15 | 4 | 2 | 3 | 3 |
| **Weighted score (0-100)** |  | **78.0** | **80.0** | **70.0** | **78.0** |

**Ranking:** 1. Linear (80.0)  2. FlowDeck (78.0)  2. Monday (78.0)  3. Asana (70.0)
```

Reading: Linear edges ahead on raw weighted score driven by dev-fit, but it is the **weakest on cross-team reporting** — the exact axis the buyer's JTBD cares about and where no leader is strong.

## 6. Positioning Map
Axes: dev-depth (Y) vs. cross-team breadth/reporting (X).
```
High dev | Linear        | <WHITE SPACE: FlowDeck>
         | Jira          |
---------+---------------+----------------------
         | Spreadsheets  | Asana / Monday
Low dev  |_______________|______________________
         Low breadth        High breadth/reporting
```
White space: **dev-grade speed AND exec-grade cross-team reporting** — currently unoccupied.

## 7. SWOT (FlowDeck)
| Strengths | Weaknesses |
|---|---|
| - Strong cross-team reporting (review-confirmed) | - Only 40 integrations vs 200 (G2, 2026-05) |
| - Competitive entry price | - Lower brand awareness than Asana/Monday |

| Opportunities | Threats |
|---|---|
| - No leader owns dev+exec reporting | - Monday/Asana could add dev features |
| - Jira fatigue in mid-market | - Linear moving upmarket |

## 8. Five Forces (snapshot)
| Force | Rating | Why |
|---|---|---|
| Rivalry | High | Several well-funded incumbents |
| New entrants | Medium | Low capital, but distribution is hard |
| Substitutes | High | Spreadsheets + Jira deeply entrenched |
| Buyer power | Medium | Easy to switch, many options |
| Supplier power | Low | Commodity cloud infra |

## 9. Recommendations
| # | Recommendation | Type | Rationale | Effort | Impact |
|---|---|---|---|---|---|
| 1 | Own "unified dev + exec reporting" in messaging and product | Differentiate | Unoccupied white space matching the JTBD | M | H |
| 2 | Close integration gap to ~100 connectors | Defend | 200-count rivals make this table stakes | H | M |
| 3 | Publish win/loss-backed battlecard vs Linear emphasizing reporting | Differentiate | Linear's clearest weakness | L | M |

## 10. Data Gaps
- Actual churn/retention by segment (no public data; need win/loss interviews).
- Enterprise pricing for all three (quote-based; gather from sales).
