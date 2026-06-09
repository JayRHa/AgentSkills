# ADR-NNNN: <Short imperative title, e.g. "Use PostgreSQL for the orders service">

- **Status:** Proposed | Accepted | Rejected | Deprecated | Superseded by ADR-NNNN
- **Date:** YYYY-MM-DD
- **Deciders:** <names / roles who made or approved this decision>
- **Technical Story:** <optional link to ticket, RFC, or design doc>

## Context

<Describe the problem and the forces at play. What is driving this decision? Include business
drivers, technical constraints, non-functional requirements, deadlines, existing systems, and
team capabilities. State the problem before stating the solution. Separate facts from
assumptions.>

**Facts:**
- <objective, verifiable fact>
- <objective, verifiable fact>

**Assumptions:**
- <assumption that, if wrong, would change the decision>

## Decision Drivers

<The criteria used to evaluate options. These become the columns of the options matrix.>

- <driver 1, e.g. operational simplicity>
- <driver 2, e.g. team familiarity>
- <driver 3, e.g. total cost of ownership>
- <driver 4, e.g. read/write latency at target scale>

## Considered Options

1. **<Option A>** — <one-line summary>
2. **<Option B>** — <one-line summary>
3. **<Option C / Do nothing>** — <one-line summary>

### Option A: <name>

<How it works in this context.>

- Good: <pro tied to a decision driver>
- Good: <pro>
- Bad: <con tied to a decision driver>

### Option B: <name>

<How it works in this context.>

- Good: <pro>
- Bad: <con>
- Bad: <con>

### Option C: <name>

<How it works in this context.>

- Good: <pro>
- Bad: <con>

## Options Matrix

<Score each option against each driver: ++ strong, + good, o neutral, - weak, -- poor.>

| Driver | Option A | Option B | Option C |
|--------|:--------:|:--------:|:--------:|
| <driver 1> | ++ | o | - |
| <driver 2> | + | ++ | - |
| <driver 3> | o | - | ++ |
| <driver 4> | + | + | o |

## Decision Outcome

**Chosen option: <Option X>.**

<Explain why this option was chosen. Tie the rationale to the decision drivers and the matrix.
Explain why it wins even where it does not top every column, and why the rejected options were
rejected.>

## Consequences

**Positive:**
- <good thing that follows from this decision>

**Negative:**
- <cost, risk, or capability we give up — this section is mandatory>

**Neutral / Follow-ups:**
- <new work this creates, things to revisit, metrics to watch>

## Links

- Supersedes: <ADR-NNNN or none>
- Superseded by: <ADR-NNNN or none>
- Related: <ADR-NNNN, design doc, RFC>
