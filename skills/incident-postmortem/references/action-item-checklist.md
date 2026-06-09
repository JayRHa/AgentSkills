# Action Item Checklist

Action items are the only part of a postmortem that changes the future. A postmortem with vague or unowned action items has zero preventive value.

## Every action item MUST have

- [ ] **A clear, concrete change** — what specifically will be built/changed (not "improve X").
- [ ] **An owner** — exactly one named person accountable (teams don't own; people do).
- [ ] **A due date** — a real date, prioritized against severity.
- [ ] **A priority** — P0/P1/P2 (P0 for SEV1 prevention work).
- [ ] **A type** — Prevent | Detect-faster | Mitigate-faster | Process.
- [ ] **A tracking link** — a ticket ID; the postmortem references it, the ticket references the postmortem.

## Type coverage rule

Aim to produce action items across the lifecycle, not just prevention:

- **Prevent** — stop this class of incident from happening (add the missing load gate).
- **Detect-faster** — shrink time-to-detect (alert on the leading indicator, not the symptom).
- **Mitigate-faster** — shrink time-to-mitigate (add one-click rollback; write the runbook).
- **Process** — improve the response itself (escalation policy, comms template, IC rotation).

If all your action items are "Prevent", you've ignored that detection and response are also fixable.

## Vague → concrete (rewrite examples)

| Vague (reject) | Concrete (accept) |
|----------------|-------------------|
| "Add more monitoring" | "Add an alert on DB CPU > 80% for 2 min, paging the platform on-call (owner: Priya, P1, due 2026-06-20, ticket OPS-481)" |
| "Be more careful with deploys" | "Require a 5-minute canary stage with auto-abort on >1% error rate for all checkout-service deploys (owner: Sam, P0, due 2026-06-15, ticket OPS-482)" |
| "Improve the runbook" | "Write a DB-saturation playbook covering connection draining and read-replica failover; link from the on-call dashboard (owner: Lee, P1, due 2026-06-22, ticket OPS-483)" |
| "Communicate better" | "Adopt the status-page update template; IC posts an update every 15 min during SEV1/2 (owner: Dana, P2, due 2026-06-30, ticket OPS-484)" |

## SMART quick check

For each item, verify it is **S**pecific, **M**easurable (you can tell when it's done), **A**ssigned, **R**ealistic, **T**ime-bound.

## Anti-patterns

- One giant action item bundling five changes — split it; each needs its own owner and date.
- "Investigate whether..." with no decision point — fine as a spike, but give it a deadline and a deliverable.
- Action items owned by "the team" or "TBD" — assign a real person before publishing.
- Action items with no ticket — they will be forgotten; create the ticket during the review meeting.
