# Worked Example: Choosing a database for the orders service

This is a complete, realistic ADR produced by the skill. Use it as the quality bar — note the
explicit drivers, the scored matrix, the narrative that justifies the winner, and the honest
negative consequences.

---

# ADR-0003: Use PostgreSQL for the orders service

- **Status:** Accepted
- **Date:** 2026-06-08
- **Deciders:** Orders team (A. Patel, lead), Platform architecture review
- **Technical Story:** JIRA ORD-412

## Context

We are building a new orders service that records customer orders, line items, and their
state transitions (placed -> paid -> fulfilled -> closed). It must be the system of record
for financial data.

**Facts:**
- Orders are strongly relational: orders have many line items, link to customers and SKUs.
- We require ACID transactions: a payment and its order-state change must commit atomically.
- Expected peak load year one is ~400 writes/sec and ~3k reads/sec. This is modest.
- The team has deep SQL experience and operates PostgreSQL elsewhere in the company.
- We run on AWS; managed options exist for all candidates.

**Assumptions:**
- Load grows <5x over three years (if order volume 10x's, revisit sharding/partitioning).
- We will not need multi-region active-active writes within the planning horizon.

## Decision Drivers

- **Transactional integrity** — atomic multi-row commits across orders and payments.
- **Relational fit** — natural modeling of orders/line-items/customers and ad-hoc queries.
- **Operational simplicity** — managed offering, backups, observability, on-call burden.
- **Team familiarity** — ramp-up time and ability to debug under pressure.
- **Cost at expected scale** — total cost of ownership at year-one load.
- **Vendor lock-in** — portability of data and skills.

## Considered Options

1. **PostgreSQL (Amazon RDS / Aurora)** — managed relational database.
2. **MongoDB Atlas** — managed document database.
3. **Amazon DynamoDB** — managed key-value / wide-column store.

### Option A: PostgreSQL (RDS/Aurora)

Relational schema with foreign keys; transactions wrap order + payment writes.

- Good: Full ACID, foreign keys, and rich SQL for reporting and ad-hoc queries.
- Good: Team operates and debugs it daily; lowest ramp-up.
- Good: Portable SQL and data; low lock-in.
- Bad: Horizontal write scaling needs deliberate work (partitioning/read replicas) if we 10x.

### Option B: MongoDB Atlas

Orders stored as documents with embedded line items.

- Good: Flexible schema; embedding line items can simplify single-document reads.
- Bad: Multi-document ACID exists but is less battle-tested for our payment-critical path.
- Bad: Team has limited operational experience; higher on-call risk.
- Bad: Relational reporting queries are awkward.

### Option C: Amazon DynamoDB

Single-table design keyed by order id with access-pattern-driven indexes.

- Good: Effortless horizontal scaling and predictable latency at very high load.
- Good: Fully managed, minimal operational overhead.
- Bad: Requires up-front access-pattern modeling; ad-hoc/reporting queries are painful.
- Bad: Transactions are limited (25 items) and the model is the least familiar to the team.
- Bad: Strong AWS lock-in for both data and skills.

## Options Matrix

| Driver | PostgreSQL | MongoDB | DynamoDB |
|--------|:----------:|:-------:|:--------:|
| Transactional integrity | ++ | o | - |
| Relational fit | ++ | - | -- |
| Operational simplicity | + | o | ++ |
| Team familiarity | ++ | - | - |
| Cost at expected scale | + | o | + |
| Vendor lock-in | ++ | + | -- |

## Decision Outcome

**Chosen option: PostgreSQL on Amazon RDS.**

The orders service is the financial system of record, so transactional integrity and
relational fit dominate the other drivers — and PostgreSQL leads both decisively. DynamoDB
wins operational simplicity, but our expected load is modest, RDS is also a managed service,
and DynamoDB's weak transactions and poor ad-hoc query story are disqualifying for
payment-critical relational data. MongoDB offers no compensating advantage over PostgreSQL
for this relational, transactional workload while adding operational risk for a team without
deep MongoDB experience. PostgreSQL's main weakness — horizontal write scaling — does not bind
at year-one load and is addressable with partitioning and read replicas before it does.

## Consequences

**Positive:**
- Atomic order+payment commits with foreign-key integrity out of the box.
- Lowest ramp-up and on-call risk; the team can debug it under production pressure today.
- Standard SQL enables reporting and analytics without a separate query layer initially.

**Negative:**
- If write volume grows beyond ~10x, we must invest in partitioning, read replicas, or
  sharding — work DynamoDB would have avoided.
- A single primary is a write bottleneck; we accept failover (seconds of downtime) rather
  than multi-master writes.

**Neutral / Follow-ups:**
- Add a dashboard alert when sustained write throughput exceeds 60% of instance capacity;
  that is the trigger to revisit this ADR.
- Define the schema migration process (e.g., Flyway/Liquibase) in a follow-up ticket.
- Re-evaluate if a multi-region active-active requirement appears (would supersede this ADR).

## Links

- Supersedes: none
- Superseded by: none
- Related: ADR-0001 (Run services on AWS), ADR-0002 (Use managed services over self-hosted)
