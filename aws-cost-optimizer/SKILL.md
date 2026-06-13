---
name: aws-cost-optimizer
description: Systematically reduces AWS cloud spend by right-sizing over-provisioned compute, finding and eliminating idle or orphaned resources, committing to Savings Plans and Reserved Instances, and enforcing cost-allocation tagging. Use this skill when the user asks to "reduce AWS bill", "optimize cloud costs", "find idle EC2/RDS/EBS", "right-size instances", "should I buy a Savings Plan or Reserved Instance", "set up cost allocation tags", "why is my AWS bill so high", or wants a structured FinOps cost-reduction plan.
license: MIT
---

# AWS Cost Optimizer

## Overview

Keywords: AWS cost, FinOps, right-sizing, idle resources, orphaned resources, Savings Plans, Reserved Instances, RI, Spot, cost allocation tags, Cost Explorer, CUR, unblended cost, amortized cost, NAT gateway, gp2 to gp3, S3 lifecycle, Graviton, Compute Optimizer, anomaly detection.

This skill drives a repeatable cost-reduction workflow across the five highest-leverage levers: **eliminate** (idle/orphaned), **right-size** (over-provisioned), **commit** (Savings Plans / RIs), **modernize** (newer/cheaper SKUs and storage tiers), and **attribute** (tagging + showback). Always quantify monthly savings, rank by effort-vs-impact, and never recommend a change without stating its risk and rollback.

Use the bundled assets:
- `references/cost-levers.md` — the full catalog of cost-reduction levers per service with detection signals and typical savings.
- `references/savings-plans-vs-ri.md` — decision framework and break-even math for commitment purchases.
- `references/tagging-strategy.md` — cost-allocation tag taxonomy and enforcement patterns.
- `scripts/cost_analysis.py` — stdlib-only analyzer that scores resources for waste and ranks recommendations from JSON inventory.
- `templates/cost-optimization-report.md` — fill-in deliverable for stakeholders.
- `examples/right-sizing-walkthrough.md` — a concrete end-to-end example.

## Workflow

1. **Establish the baseline.** Pull the last 1–3 months from Cost Explorer or the Cost & Usage Report (CUR). Always reason in **amortized** cost (commitments spread over their term), not unblended, so commitments aren't double-counted. Break spend down by service, by linked account, and by tag. Record the top 10 cost drivers — typically EC2, RDS, S3, data transfer, and NAT gateways.

2. **Eliminate waste first (zero risk, fast).** Idle and orphaned resources are pure savings with no performance trade-off. Scan for: unattached EBS volumes, unassociated Elastic IPs, idle/empty load balancers, stopped instances still holding EBS, old EBS/RDS snapshots, idle NAT gateways, dev/test resources running 24/7, and forgotten dev environments. See `references/cost-levers.md` "Eliminate" section.

3. **Right-size over-provisioned resources.** Use CloudWatch / Compute Optimizer signals (p95 CPU, memory if the agent is installed, network, IOPS). Flag instances with sustained low utilization (e.g., p95 CPU < 40% and max < 60% over 14 days). Recommend the smallest instance that keeps headroom. Prefer downsizing one family step at a time. See `references/cost-levers.md` "Right-size".

4. **Modernize SKUs and storage.** Migrate gp2→gp3 EBS (≈20% cheaper + tunable IOPS), x86→Graviton (≈20% better price/performance), older instance generations→current (m5→m6/m7), and apply S3 lifecycle / Intelligent-Tiering. These are recurring savings with low risk after testing.

5. **Commit to what's left (after steps 2–4).** Only buy Savings Plans / RIs for the **stable baseline** that remains after eliminating and right-sizing — never commit to waste. Use `references/savings-plans-vs-ri.md` to choose Compute SP vs EC2 Instance SP vs RIs, term (1yr vs 3yr), and payment option. Target coverage of the bottom 60–80% of steady-state usage; leave the variable top on on-demand or Spot.

6. **Attribute costs with tags.** Implement the tag taxonomy in `references/tagging-strategy.md`, activate cost-allocation tags in Billing, enforce with tag policies / SCPs, and set up showback per team/product. Untagged spend above a threshold is itself a finding.

7. **Quantify, rank, and report.** Run `scripts/cost_analysis.py` over an inventory JSON to score and rank findings by monthly savings and implementation effort. Produce the deliverable from `templates/cost-optimization-report.md` with prioritized recommendations, total addressable savings, and a rollout order.

8. **Institutionalize.** Turn on AWS Cost Anomaly Detection and budgets with alerts, schedule a monthly review, and set a coverage/utilization target for commitments. Cost optimization is continuous, not a one-time project.

## Prioritization framework (effort vs. impact)

Rank every finding into one of these buckets. Do the top-left first.

| | High savings | Low savings |
|---|---|---|
| **Low effort** | DO NOW — delete orphaned EBS/EIP, gp2→gp3, stop idle, schedule dev | QUICK WIN — small snapshot cleanup, tag fixes |
| **High effort** | PLAN — right-size fleets, Graviton migration, 3yr commitments | DEFER — marginal refactors |

Decision rules:
- Never commit (SP/RI) before eliminating and right-sizing; you'd lock in waste.
- Idle/orphaned deletions are reversible-by-recreation but verify ownership first (a 7-day tag-then-wait beats immediate deletion).
- Right-sizing needs ≥14 days of metrics; a quiet week (holiday) invalidates the sample.
- For commitments, prefer 1-year No Upfront unless cash flow allows 3-year for max discount on truly stable workloads.

## Worked detection checklist

Run through these and record each as a finding (service, resource id, monthly $, action, risk):

- [ ] Unattached EBS volumes (`state == available`)
- [ ] Unassociated Elastic IPs (charged when not attached to running instance)
- [ ] Load balancers with zero healthy targets / near-zero traffic
- [ ] Idle NAT gateways (hourly + per-GB; consolidate or use VPC endpoints)
- [ ] EBS snapshots older than retention policy / orphaned (source volume gone)
- [ ] Old AMIs and their backing snapshots
- [ ] Stopped EC2 instances older than N days (still paying for EBS)
- [ ] gp2 volumes that should be gp3
- [ ] EC2/RDS with p95 CPU < 40% over 14 days (right-size candidate)
- [ ] RDS instances with no connections / idle
- [ ] Provisioned IOPS far above actual usage
- [ ] S3 buckets with no lifecycle policy and old/cold objects
- [ ] On-demand steady-state usage with no Savings Plan coverage
- [ ] x86 workloads that could run on Graviton
- [ ] Untagged resources above cost threshold
- [ ] Previous-generation instance families (m4/m5, c4/c5, r4/r5)
- [ ] Over-provisioned commitments (low SP/RI utilization)

## Best Practices

- **Reason in amortized cost** when commitments exist; unblended hides the smoothing of upfront payments.
- **Quantify everything in $/month.** "This volume is idle" is weak; "this 500 GB gp2 volume costs $50/mo and is unattached" drives action.
- **Tag before you delete.** Apply a `cost-review: candidate-delete` tag, wait a defined window, then remove. Prevents deleting something load-bearing.
- **Commit only to baseline.** Coverage target 60–80% of steady-state; never 100% — variable usage stays on-demand/Spot.
- **Right-size on p95/p99, not average.** Averages hide spikes; use percentiles plus max.
- **Validate with ≥14 days of metrics** and exclude anomalous low-traffic periods.
- **Use Spot for fault-tolerant, stateless, interruptible** workloads (batch, CI, stateless web behind ASG) — up to ~90% off.
- **Storage class transitions need lifecycle math**: retrieval costs and minimum storage durations can erase savings for frequently accessed data.
- **Data transfer is a silent driver**: cross-AZ, NAT egress, and inter-region transfer add up; prefer VPC endpoints and same-AZ placement.
- **Make it continuous**: budgets, anomaly detection, monthly reviews, and commitment-utilization dashboards.

## Common Pitfalls

- **Buying a Savings Plan before right-sizing** — locks in money on instances you were about to shrink. Always eliminate + right-size first.
- **Optimizing on unblended cost with active RIs** — distorts which service is "expensive"; switch to amortized.
- **Deleting "idle" resources without checking ownership** — that "unused" volume may be a quarterly batch job's data. Tag-and-wait.
- **Right-sizing from a single day or average CPU** — leads to under-provisioning and incidents. Use 14+ days and percentiles.
- **100% commitment coverage** — over-committing on variable workloads costs more than on-demand on the unused portion.
- **Ignoring data-transfer and NAT charges** — they don't show as a "compute" line but can be 10–20% of the bill.
- **gp3 blind migration without IOPS/throughput tuning** — gp3 baseline is 3000 IOPS/125 MB/s; high-throughput gp2 volumes may need explicit provisioning.
- **No tagging governance** — without enforced tags, you can't attribute or show back, so optimization stalls organizationally.
- **Treating it as one-off** — savings erode within months as new resources spin up; institutionalize the review.
