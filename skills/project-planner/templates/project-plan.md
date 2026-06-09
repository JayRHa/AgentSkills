# Project Plan: <Project Name>

## 1. Goal & Definition of Done
- **Objective:** <one sentence — the single end deliverable>
- **Definition of done:** <observable, testable completion criteria>
- **Deadline / driver:** <hard date or "none"; is scope or date fixed?>
- **Owner / sponsor:** <name>

## 2. Scope
- **In scope:** <bullets>
- **Out of scope (non-goals):** <bullets>

## 3. Assumptions
- <each assumption made during planning — resources, availability, externals>

## 4. Work Breakdown Structure (WBS)
```
1   <Root deliverable>
1.1   <Work package group>
1.1.1   <Leaf task — verb + object + done-criterion>
1.1.2   <Leaf task>
1.2   <Work package group>
1.2.1   <Leaf task>
```

## 5. Milestones
| Milestone | Meaning (state change) | Earned by (WBS) | Target |
|-----------|------------------------|-----------------|--------|
| M1 <name> | <e.g., Design approved> | 1.1, 1.2 | <date> |

## 6. Estimates (PERT)
| WBS | Task | O | M | P | te | sd | Owner |
|-----|------|---|---|---|----|----|-------|
| 1.1.1 | <task> | | | | | | |

_te = (O + 4M + P)/6, sd = (P − O)/6. Effort in person-hours._

## 7. Dependencies & Schedule
| WBS | Task | Duration | Predecessors (type) | ES | EF | LS | LF | Slack | Critical |
|-----|------|----------|---------------------|----|----|----|----|------|----------|
| 1.1.1 | <task> | | <e.g., 1.1.2 FS> | | | | | | |

- **Critical path:** <task chain>
- **Project duration (min):** <value>
- **Schedule/contingency buffer:** <%, applied to critical path>

(Compute ES/EF/LS/LF/slack with `scripts/critical_path.py`.)

## 8. Risk Register
| # | Risk | Likelihood (L/M/H) | Impact (L/M/H) | Mitigation / Contingency | Owner |
|---|------|--------------------|----------------|--------------------------|-------|
| R1 | <risk> | | | | |

## 9. Open Questions
- <unresolved items needing a decision>
