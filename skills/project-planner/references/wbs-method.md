# Work Breakdown Structure (WBS) Method

A WBS is a deliverable-oriented hierarchical decomposition of the total scope of work. It answers "what must be produced", not "who does what" or "in what order" (that comes later, in dependencies/scheduling).

## The two governing rules

### 1. The 100% Rule
The children of any node must together represent **100%** of the work of that parent — no more, no less.
- No gaps: if a parent is "Launch website", the children must cover everything needed to launch.
- No overlap: each piece of work belongs to exactly one leaf. Overlap causes double-counting in estimates.
- No invented work: don't add children that aren't part of the parent's scope.

Apply the 100% rule at every level, including the top (the root = the full project deliverable).

### 2. The 8/80 Rule
Keep decomposing until each **leaf** (work package) is between **8 and 80 hours** of effort.
- < 8h: too granular; merge into a sibling or parent.
- > 80h: too coarse to estimate or track; split further.
- Rule of thumb: a leaf should fit within one reporting period and have a single accountable owner.

## Decompose by deliverable, not activity
Prefer noun-based, outcome-based nodes ("Authenticated user flow", "Approved visual design") over verb-based activity buckets ("Coding", "Testing"). Deliverables make the 100% rule checkable; activity buckets hide gaps.

Exception: at the **leaf** level, write each work package as `verb + object + done-criterion` so it is actionable, e.g. "Implement password reset email (sends within 30s, link expires in 1h)".

## Numbering
Use hierarchical decimal numbering so every node has a stable WBS code:

```
1     Website Launch (root deliverable)
1.1   Content
1.1.1   Draft all page copy
1.1.2   Source/produce imagery
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

## The 7±2 guideline
If one parent has more than ~7 direct children, introduce an intermediate grouping level. Humans plan and review better with shallow, balanced trees.

## Milestones vs work packages
- **Work package**: has effort and duration; produces a deliverable.
- **Milestone**: zero duration; a checkpoint marking that a set of work packages is complete ("Design approved", "Feature-complete", "Live"). Milestones are the heartbeat of the schedule and the natural reporting/gate points.

Every milestone must be *earned* by completed work packages — never schedule a milestone with no preceding work.

## WBS Dictionary (optional but recommended)
For each leaf, optionally capture: ID, name, description, deliverable/acceptance criteria, owner/role, effort estimate, predecessors, and assumptions. This removes ambiguity and is the source for the schedule.

## Quality checklist
- [ ] Root = the single end deliverable.
- [ ] 100% rule holds at every level (no gaps, no overlap).
- [ ] Every leaf is 8–80h.
- [ ] Leaves are actionable (verb + object + done-criterion).
- [ ] No parent has > ~7 children (else group).
- [ ] Milestones identified and earned by work packages.
- [ ] No scheduling/sequence info baked into the WBS (that lives in dependencies).
