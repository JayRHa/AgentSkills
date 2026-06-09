# AWS Cost-Reduction Levers Catalog

Five lever categories, ordered by how you should apply them: Eliminate -> Right-size -> Modernize -> Commit -> Attribute. Each lever lists the detection signal, the action, typical savings, and the risk.

## 1. Eliminate (idle / orphaned) — do first, near-zero risk

| Resource | Detection signal | Action | Typical savings | Risk |
|---|---|---|---|---|
| Unattached EBS volume | `State == available` | Snapshot then delete | 100% of volume cost | Low (snapshot first) |
| Unassociated Elastic IP | EIP not attached to a running instance | Release | ~$3.6/mo each | Low |
| Idle ELB/ALB/NLB | 0 healthy targets or ~0 requests over 14d | Delete | ~$16-25/mo each | Low |
| Idle NAT gateway | Near-zero bytes processed | Delete or replace with VPC endpoints | ~$32/mo + data | Medium (routing) |
| Orphaned snapshot | Source volume/AMI gone, age > retention | Delete | $0.05/GB-mo | Low |
| Old AMIs | Unused, older than policy | Deregister + delete snapshots | Snapshot cost | Low |
| Stopped EC2 (old) | Stopped > N days, still has EBS | Terminate or archive | EBS cost | Medium (data) |
| Idle RDS | 0 connections over 14d | Snapshot + stop/delete | Full instance | Medium |
| Empty/forgotten dev env | No activity, off-hours owner | Decommission | Full stack | Medium |
| Provisioned IOPS unused | io1/io2 IOPS >> actual | Reduce or switch to gp3 | Per-IOPS charge | Low |

## 2. Right-size (over-provisioned) — needs >=14d metrics

**Signal thresholds (tune per workload):**
- CPU: p95 < 40% AND max < 60% over 14 days -> downsize candidate.
- Memory (requires CloudWatch agent): p95 < 50%.
- Network/IOPS: well below instance class ceiling.

**Actions:**
- Step down one size at a time (e.g., m6i.2xlarge -> m6i.xlarge) and observe.
- Switch instance family to match the bottleneck (compute-heavy -> c-family, memory-heavy -> r-family, balanced -> m-family, burstable low-util -> t-family).
- For databases, right-size storage and IOPS independently from compute.
- Use AWS Compute Optimizer recommendations as a starting point; validate against your own percentiles.

**Typical savings:** 20-50% on over-provisioned instances. One family/size step is usually ~50% per step but go gradually.

**Risk:** Medium — under-provisioning causes latency/incidents. Always keep headroom and validate after the change.

## 3. Modernize (cheaper SKUs / storage) — recurring savings, low risk after test

| Change | Savings | Notes |
|---|---|---|
| gp2 -> gp3 EBS | ~20% + tunable IOPS/throughput | gp3 baseline 3000 IOPS / 125 MB/s included; provision extra if needed |
| x86 -> Graviton (ARM) | ~20% better price/perf | Requires ARM-compatible build; test workload |
| Prev-gen -> current gen | ~10-20% | m5->m6i/m7i, c5->c6i, r5->r6i |
| S3 Standard -> Intelligent-Tiering | Auto-tiers cold data | Small monitoring fee; best for unpredictable access |
| S3 lifecycle to IA / Glacier | 40-95% on cold data | Mind retrieval cost + min storage duration |
| RDS -> Aurora / Graviton RDS | Varies | Evaluate per workload |
| Lambda right-size memory | Cost ~ memory*duration | Use Power Tuning to find optimum |

## 4. Commit (Savings Plans / RIs / Spot) — only on stable baseline

See `savings-plans-vs-ri.md` for the full decision framework. Summary:
- **Compute Savings Plan**: most flexible (any region/family/OS, EC2+Fargate+Lambda), ~up to 66% (3yr).
- **EC2 Instance Savings Plan**: locked to a family in a region, slightly deeper discount.
- **Reserved Instances**: for RDS, ElastiCache, Redshift, OpenSearch (no SP available there).
- **Spot**: up to ~90% off for interruptible, stateless, fault-tolerant workloads (batch, CI, ASG-backed web).

Never exceed ~60-80% coverage of steady-state. Variable top stays on-demand/Spot.

## 5. Attribute (tagging / showback) — enables all the above organizationally

See `tagging-strategy.md`. Without attribution you cannot assign savings ownership or do showback/chargeback, and optimization stalls.

## Data transfer — the silent driver

- Cross-AZ traffic is charged each direction; co-locate chatty services in one AZ where HA allows.
- NAT gateway egress is per-GB on top of the hourly fee; use VPC Gateway Endpoints for S3/DynamoDB (free) and Interface Endpoints for other services.
- Inter-region replication and CloudFront origin fetches add up; cache aggressively.
- Egress to the internet is the most expensive path; review large outbound transfers.
