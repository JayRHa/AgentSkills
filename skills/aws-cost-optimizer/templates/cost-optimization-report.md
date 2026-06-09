# AWS Cost Optimization Report

**Account / Org:** <account-id or org name>
**Period analyzed:** <YYYY-MM-DD to YYYY-MM-DD>
**Cost basis:** Amortized (commitments smoothed)
**Prepared by:** <name>  **Date:** <YYYY-MM-DD>

## 1. Executive summary

- Current monthly spend: **$<X>**
- Total addressable savings identified: **$<Y>/month (~$<Y*12>/year)**
- Percentage reduction: **<Z>%**
- Quick wins (low effort) account for **$<Q>/month** and can ship this week.

## 2. Spend baseline

| Driver | Monthly $ | % of bill | Trend |
|---|---|---|---|
| EC2 | | | |
| RDS | | | |
| S3 | | | |
| Data transfer | | | |
| NAT gateways | | | |
| Other | | | |

Top linked accounts / teams by spend:

| Team / account | Monthly $ | Tagged? |
|---|---|---|
| | | |

## 3. Findings (ranked by impact)

> Generated/assisted by `scripts/cost_analysis.py`.

| Priority | Resource | Action | $/mo saved | Effort | Risk | Owner |
|---|---|---|---|---|---|---|
| 1 | | | | low | low | |
| 2 | | | | | | |

## 4. Recommendations by lever

### Eliminate (do now)
- [ ] <orphaned EBS / EIP / idle ELB / NAT — $/mo>

### Right-size (plan, needs >=14d metrics)
- [ ] <instance/db, current size -> proposed size, $/mo, validation plan>

### Modernize
- [ ] <gp2->gp3, Graviton, gen upgrade, S3 lifecycle — $/mo>

### Commit (after eliminate + right-size)
- [ ] Recommended instrument: <Compute SP / EC2 SP / RI>
- [ ] Coverage target: <60-80%> of steady-state baseline
- [ ] Term / payment: <1yr No Upfront / 3yr All Upfront>
- [ ] Estimated savings: $<>/mo

### Attribute (tagging)
- [ ] Mandatory tags rolled out: cost-center, team, environment, project, owner
- [ ] Cost-allocation tags activated in Billing
- [ ] Enforcement: <tag policy / SCP / IaC default_tags>
- [ ] Untagged spend: $<>/mo (target: <X>%)

## 5. Rollout plan

| Week | Actions | Owner | Expected savings |
|---|---|---|---|
| 1 | Eliminate quick wins, gp2->gp3 | | |
| 2-3 | Right-size validated instances | | |
| 4 | Purchase commitments on baseline | | |
| Ongoing | Tagging enforcement, anomaly detection, monthly review | | |

## 6. Guardrails

- [ ] AWS Budgets with alert thresholds set per team
- [ ] Cost Anomaly Detection enabled
- [ ] SP/RI utilization + coverage dashboard
- [ ] Monthly cost review scheduled

## 7. Risks & rollback

| Change | Risk | Rollback |
|---|---|---|
| Delete EBS | Data loss | Snapshot taken before deletion |
| Right-size | Under-provisioning | Revert to prior size; keep 14d watch |
| Commitment | Over-commit | Coverage capped at <=80% |
