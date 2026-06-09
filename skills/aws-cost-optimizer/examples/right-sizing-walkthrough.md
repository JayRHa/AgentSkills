# Worked Example: From High Bill to Ranked Savings Plan

## Scenario

A team's AWS bill jumped to ~$1,800/month. Stakeholder asks: "Why is our bill so high and what can we cut without breaking prod?"

## Step 1 — Baseline (amortized)

Cost Explorer (last 30 days, amortized), grouped by service:

| Service | $/mo |
|---|---|
| EC2 | 980 |
| RDS | 320 |
| NAT gateway | 32 |
| EBS | 145 |
| EIP | 3.60 |
| Snapshots | 15 |
| Other | 304 |

No Savings Plans exist. Tag coverage is partial.

## Step 2 — Build the inventory

Export resources (CLI/Compute Optimizer) into `inventory.json`. We use the script's sample shape:

```bash
python3 scripts/cost_analysis.py --sample > inventory.json
```

The inventory captures the real findings: one unattached gp2 volume, one gp2 volume in use, an unassociated EIP, an over-provisioned m-class EC2 (p95 CPU 12%), a long-stopped EC2, an idle RDS, an idle NAT, and an orphaned snapshot.

## Step 3 — Run the analyzer

```bash
python3 scripts/cost_analysis.py --inventory inventory.json --format table
```

Output (ranked by monthly savings):

```
ID                 TYPE         ACTION                          $/MO  EFFORT RISK   OWNER
--------------------------------------------------------------------------------------------------------------
i-0big             ec2          rightsize_ec2                 300.00  high   medium payments
db-idle            rds          stop_idle_rds                 320.00  medium medium UNTAGGED
vol-0idle          ebs          delete_unattached_ebs          50.00  low    low    data
i-0stopped         ec2          terminate_stopped_ec2          40.00  medium medium qa
nat-0z             nat          review_idle_nat                32.00  medium medium net
snap-0old          snapshot     delete_orphaned_snapshot       15.00  low    low    UNTAGGED
vol-0gp2           ebs          gp2_to_gp3                     16.00  low    low    web
eipalloc-0x        eip          release_eip                     3.60  low    low    UNTAGGED

Total addressable savings: $776.60/month  (~$9319.20/year)
```

## Step 4 — Apply the prioritization framework

- **DO NOW (low effort, high/med savings):** delete unattached EBS ($50), gp2->gp3 ($16), release EIP ($3.60), delete orphaned snapshot ($15). Ships today. ~$84.60/mo, zero perf risk.
- **VERIFY THEN ACT (medium):** idle RDS ($320) and idle NAT ($32) — confirm with owners; the RDS is UNTAGGED so tag-and-wait 7 days before stopping. Stopped EC2 ($40) — confirm no data needed, then terminate.
- **PLAN (high effort, high savings):** right-size `i-0big` ($300) — p95 12% / max 28% over 21 days justifies one step down (e.g. m6i.2xlarge -> m6i.xlarge). Validate 14 days post-change.

## Step 5 — Sequence the commitment LAST

Do NOT buy a Savings Plan yet. After right-sizing `i-0big` and removing idle resources, the EC2 steady-state baseline drops from ~$980 to roughly ~$620/mo. THEN:

- Cover ~70% of the new baseline with a **1-year No Upfront Compute Savings Plan**.
- Break-even check (see `references/savings-plans-vs-ri.md`): with on-demand $0.10/hr and SP ~$0.07/hr, break-even utilization is 70% — comfortably met at 70% coverage of a stable baseline.
- Estimated additional ~25% off the covered portion.

Had we bought the SP before right-sizing, we'd have committed to the $980 (including the soon-to-be-shrunk instance) and locked in waste for a year — the classic pitfall.

## Step 6 — Attribute and institutionalize

- Two findings are UNTAGGED. Add mandatory `team`/`owner` tags and enforce via IaC `default_tags` + a report-only SCP.
- Enable AWS Budgets ($1,400 alert) and Cost Anomaly Detection.
- Schedule a monthly review using `templates/cost-optimization-report.md`.

## Result

~$777/mo of pure-waste + right-size savings identified immediately (~43% of bill), plus an additional commitment discount on the cleaned-up baseline — without buying any commitment on resources that were about to disappear.
