# Savings Plans vs Reserved Instances — Decision Framework

Goal: cover the **stable baseline** of usage (after eliminating + right-sizing) with the right commitment, at the right term and payment option.

## Step 0 — Prerequisite

Do NOT buy commitments until idle resources are removed and right-sizing is done. Committing to over-provisioned or idle usage locks in waste for 1-3 years.

## Step 1 — Pick the instrument

```
Is the spend EC2 / Fargate / Lambda compute?
  YES -> Use a Savings Plan (RIs are legacy for EC2; SPs are more flexible)
         |- Need max flexibility across family/region/OS/service? -> Compute Savings Plan
         |- Workload pinned to one instance family in one region? -> EC2 Instance Savings Plan (deeper discount)
  NO  -> Is it RDS / ElastiCache / Redshift / OpenSearch / DynamoDB?
         -> Use Reserved Instances / Reserved Nodes / Reserved Capacity (no SP available)
         -> DynamoDB: Reserved Capacity for steady provisioned throughput
```

## Step 2 — Pick coverage level

- Plot daily/hourly usage. The flat bottom band = baseline you can commit to.
- Target **60-80% coverage** of steady-state. The spiky top stays on-demand or Spot.
- 100% coverage is an anti-pattern: any dip means you pay for unused commitment.

## Step 3 — Pick term and payment

| Choice | Discount | When |
|---|---|---|
| 1-year, No Upfront | Lowest commitment discount | Default; preserves flexibility, low risk |
| 1-year, All Upfront | A bit deeper | Have cash, want a bit more off |
| 3-year, No Upfront | Deeper | Very stable workload, confident 3yr horizon |
| 3-year, All Upfront | Deepest (~up to 66% Compute SP) | Stable + cash available + long horizon |

Rule of thumb: 1-year No Upfront unless the workload is provably stable for 3 years.

## Break-even math

Let:
- `OD` = on-demand hourly rate
- `C`  = committed (SP/RI) hourly-equivalent rate
- `U`  = fraction of the term the committed capacity is actually used (utilization)

Effective committed cost per used hour = `C / U`.
You save vs on-demand only while `C / U < OD`, i.e. utilization must stay above `C / OD`.

Example: OD = $0.10/hr, C = $0.06/hr.
- Break-even utilization = 0.06 / 0.10 = 60%.
- If the committed capacity is used >60% of the time -> you save. Below 60% -> you'd have been cheaper on-demand.
- This is exactly why coverage stays at 60-80%: it keeps utilization comfortably above break-even.

Upfront break-even (All Upfront vs No Upfront): compute payback months = `upfront_amount / monthly_savings_vs_no_upfront`. If payback < term, All Upfront wins on total cost (ignoring cost of capital).

## Spot vs commitment

- Spot is not a commitment; it's opportunistic capacity at up to ~90% off, interruptible with 2-min notice.
- Use Spot for: batch, CI/CD, big-data, rendering, stateless web behind an ASG with mixed instances policy.
- Do NOT use Spot for: stateful single-node databases, anything that can't tolerate interruption.
- Best practice: ASG with `On-Demand base + Spot for the rest`, plus a Savings Plan covering the on-demand base.

## Monitoring after purchase

- Watch **SP/RI utilization** (should stay near 100% of the commitment) and **coverage** (60-80%).
- Low utilization = over-committed -> let it expire, don't renew at that level.
- Low coverage + high on-demand = under-committed -> buy more on the proven baseline.
