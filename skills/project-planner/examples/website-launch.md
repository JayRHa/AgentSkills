# Worked Example: Launch a Marketing Website

**Goal:** Launch a 5-page marketing website for a product, ready for a public announcement.

## Step 1 — Clarify
- Definition of done: 5 pages live on production domain, contact form working, passes QA.
- Deadline: soft target 3 weeks; scope is more fixed than date.
- Resources: 1 designer (50%), 1 developer (full-time), 1 content writer (part-time).
- External dependency: legal must approve copy before go-live.

## Step 2-3 — WBS + Milestones
```
1   Marketing Website Launch
1.1   Content
1.1.1   Draft page copy (5 pages)
1.1.2   Legal approval of copy        [external]
1.2   Design
1.2.1   Wireframes
1.2.2   Visual design
1.3   Build
1.3.1   Set up hosting + CI
1.3.2   Implement pages
1.3.3   Implement contact form
1.4   Launch
1.4.1   QA pass
1.4.2   Go-live + DNS cutover
```
Milestones: **M1 Design approved** (earned by 1.2.2), **M2 Feature complete** (1.3.x), **M3 Live** (1.4.2).

## Step 5 — Estimates (PERT, person-hours)
| WBS | Task | O | M | P | te |
|-----|------|---|---|---|----|
| 1.1.1 | Draft copy | 8 | 12 | 20 | 12.7 |
| 1.1.2 | Legal approval | 4 | 8 | 24 | 10.0 |
| 1.2.1 | Wireframes | 6 | 8 | 14 | 8.7 |
| 1.2.2 | Visual design | 12 | 16 | 28 | 17.3 |
| 1.3.1 | Hosting + CI | 4 | 6 | 12 | 6.7 |
| 1.3.2 | Implement pages | 16 | 24 | 40 | 25.3 |
| 1.3.3 | Contact form | 6 | 8 | 16 | 9.0 |
| 1.4.1 | QA pass | 6 | 8 | 14 | 8.7 |
| 1.4.2 | Go-live | 2 | 3 | 6 | 3.3 |

## Step 4 & 6 — Dependencies + CPM
Using rounded durations in days (1 dev-day ≈ 6 focused hours), the CPM input:
```json
[
  {"id": "copy",      "name": "Draft copy",      "duration": 2, "predecessors": []},
  {"id": "legal",     "name": "Legal approval",  "duration": 2, "predecessors": ["copy"]},
  {"id": "wire",      "name": "Wireframes",      "duration": 2, "predecessors": []},
  {"id": "visual",    "name": "Visual design",   "duration": 3, "predecessors": ["wire"]},
  {"id": "hosting",   "name": "Hosting + CI",    "duration": 1, "predecessors": []},
  {"id": "pages",     "name": "Implement pages", "duration": 4, "predecessors": ["visual", "hosting", "copy"]},
  {"id": "form",      "name": "Contact form",    "duration": 2, "predecessors": ["hosting"]},
  {"id": "qa",        "name": "QA pass",         "duration": 2, "predecessors": ["pages", "form", "legal"]},
  {"id": "golive",    "name": "Go-live",         "duration": 1, "predecessors": ["qa"]}
]
```

Run:
```
python3 scripts/critical_path.py tasks.json
```
Result: project duration **12 days**, critical path **wire -> visual -> pages -> qa -> golive**.
Note `legal` (copy→legal) has slack — it runs in parallel with design — so the long pole is design+build, not approval. The contingency buffer (~20%, ≈ 2-3 days) is added at the end of the critical path, giving a committed target of ~14-15 days, comfortably within the 3-week window.

## Step 7 — Top risks
| # | Risk | L | I | Mitigation |
|---|------|---|---|------------|
| R1 | Legal approval slips | M | H | Submit copy draft early; it's off the critical path, keep it that way |
| R2 | Visual design rework after review | M | M | Get stakeholder sign-off at wireframe stage (M1) before visual design |
| R3 | Page implementation underestimated | M | H | Time-box; descope lowest-priority page if QA date is threatened |
