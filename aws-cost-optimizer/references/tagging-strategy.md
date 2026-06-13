# Cost-Allocation Tagging Strategy

Tags are the foundation of cost attribution (showback/chargeback) and of automated optimization (so scripts know who owns a resource before deleting it).

## Core tag taxonomy

Use a small, mandatory set plus optional tags. Keep keys consistent (case-sensitive in AWS).

| Tag key | Required | Purpose | Example values |
|---|---|---|---|
| `cost-center` | Yes | Chargeback to finance unit | `cc-1023`, `marketing` |
| `team` | Yes | Owning team for showback | `payments`, `platform` |
| `environment` | Yes | Separate prod vs non-prod spend; enables off-hours scheduling | `prod`, `staging`, `dev`, `test` |
| `project` | Yes | Group spend by initiative/product | `checkout`, `data-lake` |
| `owner` | Yes | Human/contact for the resource | `jane@corp.com` |
| `application` | Recommended | Map spend to an app | `api-gateway-svc` |
| `data-classification` | Optional | Governance | `public`, `internal`, `pii` |
| `cost-review` | Tooling | Optimization lifecycle marker | `candidate-delete`, `keep` |
| `auto-stop` | Tooling | Off-hours scheduler opt-in | `true`, `false` |

## Enforcement patterns

1. **Activate cost-allocation tags** in Billing console (and via Tag Editor) so they appear in Cost Explorer / CUR. Note the next-day activation delay.
2. **AWS Organizations Tag Policies** — define allowed keys/values and report non-compliant resources.
3. **Service Control Policies (SCP)** — deny creation of resources missing mandatory tags (e.g., deny `ec2:RunInstances` without `team` and `environment`). Apply gradually; start in report-only.
4. **IaC enforcement** — set default tags at the provider level (Terraform `default_tags`, CloudFormation stack-level tags, CDK `Tags.of(app).add(...)`). This is the most reliable layer.
5. **Drift detection** — periodic scan for untagged or mis-tagged resources; surface untagged spend as a finding.

## Showback workflow

1. Group Cost Explorer by `team` (or `cost-center`) for monthly spend per owner.
2. Allocate shared/untagged costs (e.g., support, shared NAT) via a proportional split or a `shared` bucket.
3. Publish a monthly per-team dashboard. Visibility alone reduces spend.
4. Set per-team budgets with alert thresholds.

## Terraform default_tags example

```hcl
provider "aws" {
  region = "eu-central-1"
  default_tags {
    tags = {
      team        = "platform"
      environment = "prod"
      project     = "checkout"
      cost-center = "cc-1023"
      owner       = "jane@corp.com"
      managed-by  = "terraform"
    }
  }
}
```

## Anti-patterns

- Free-text tag values (`Prod`, `production`, `PROD` fragment your reports) — enforce an allowed set.
- Too many mandatory tags — friction leads to bypass; keep it to ~5.
- Tagging only at creation with no drift detection — coverage decays.
- No `owner` tag — you can't safely automate cleanup.
