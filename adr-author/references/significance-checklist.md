# Is This Decision ADR-Worthy?

An Architecture Decision Record is for **architecturally significant** decisions. Use this
checklist to decide whether to write one. If two or more criteria fire, write an ADR. If
none fire, prefer a code comment, a commit message, or a ticket.

## Significance criteria

Write an ADR if the decision is **costly or hard to reverse**:

- [ ] Reversing it later would require a migration, a rewrite, or coordinated multi-team work.
- [ ] It locks in a vendor, a protocol, a data format, or a public contract.
- [ ] It shapes the structure of the system (layers, boundaries, deployment topology).

Write an ADR if the decision has **broad blast radius**:

- [ ] More than one team or component depends on the choice.
- [ ] It affects a cross-cutting concern: security, observability, auth, persistence, build.
- [ ] It sets a precedent others will copy.

Write an ADR if there were **real trade-offs**:

- [ ] Two or more credible options existed and reasonable engineers could disagree.
- [ ] The choice optimizes some qualities at the expense of others (e.g., latency vs. cost).
- [ ] The rationale is non-obvious and would be asked about in six months.

Write an ADR if it is **governance-relevant**:

- [ ] It establishes or changes a standard, convention, or policy.
- [ ] An auditor, new hire, or future maintainer would need to know *why*, not just *what*.

## When NOT to write an ADR

- The decision is local, cheap to reverse, and obvious (variable naming, a single function's
  implementation, a one-line config tweak).
- There was only one viable option (no trade-off to record).
- The information belongs in a runbook, README, or design doc instead.

For these, capture intent in a code comment or commit message and move on.

## Common architecturally-significant decision types

| Category | Examples |
|----------|----------|
| Data | Database engine, schema strategy, event sourcing, caching layer |
| Integration | REST vs. gRPC vs. GraphQL, sync vs. async, message broker choice |
| Structure | Monolith vs. services, module boundaries, layering rules |
| Platform | Cloud provider, container orchestration, runtime/language |
| Cross-cutting | AuthN/AuthZ approach, logging/tracing stack, error-handling strategy |
| Lifecycle | Build vs. buy, adopting/deprecating a framework, versioning policy |

## Status lifecycle

```
Proposed ──accept──> Accepted ──time──> Deprecated
   │                    │
   └──reject──> Rejected └──replaced──> Superseded by ADR-NNNN
```

- **Proposed** — drafted, under review, not yet binding.
- **Accepted** — agreed and in force. Immutable from here on.
- **Rejected** — considered and explicitly declined (still valuable to record).
- **Deprecated** — no longer recommended but not yet replaced.
- **Superseded by ADR-NNNN** — a newer ADR replaces this decision. Link both ways.
