# State Hygiene

Terraform state maps config to real infrastructure. Poor hygiene causes accidental destroy/recreate, lock contention, and leaked secrets.

## Backends live in the ROOT only

Reusable modules must not declare a `backend`. Configure it once in the root:

```hcl
# root backend.tf
terraform {
  backend "s3" {
    bucket         = "my-tf-state"
    key            = "prod/network/terraform.tfstate"
    region         = "us-east-1"
    dynamodb_table = "tf-locks"   # state locking
    encrypt        = true
  }
}
```

Always use a remote backend with **locking** (S3+DynamoDB, GCS, azurerm, or Terraform Cloud) for any shared environment. Local state is fine only for throwaway experiments.

## Stable addressing: `for_each` over `count`

State keys resources by their address. `count` keys by integer index, so reordering a list reshuffles addresses and forces destroy/recreate. `for_each` keys by a stable string.

```hcl
# Fragile: removing "alice" reindexes "bob" -> destroy/recreate
resource "aws_iam_user" "u" {
  count = length(var.usernames)
  name  = var.usernames[count.index]
}

# Stable: each user keyed by name
resource "aws_iam_user" "u" {
  for_each = toset(var.usernames)
  name     = each.value
}
```

## Renaming without destroy: `moved {}`

When you rename a resource or change `count` -> `for_each`, add a `moved` block so Terraform updates state addresses instead of deleting/creating:

```hcl
moved {
  from = aws_iam_user.u[0]
  to   = aws_iam_user.u["alice"]
}

moved {
  from = aws_s3_bucket.old_name
  to   = aws_s3_bucket.this
}
```

`moved` blocks are safe to keep; remove them only after every environment has applied.

## Importing existing resources

Prefer config-driven import (`import {}` blocks, Terraform >= 1.5) over the imperative `terraform import` so it is reviewable and repeatable:

```hcl
import {
  to = aws_s3_bucket.this
  id = "my-existing-bucket"
}
```

Run `terraform plan -generate-config-out=generated.tf` to scaffold the resource, then refine it.

## Lifecycle guards

```hcl
resource "aws_db_instance" "this" {
  # ...
  lifecycle {
    prevent_destroy = true            # block accidental deletion of stateful resources
    ignore_changes  = [tags["LastSeen"]] # don't fight external mutators
  }
}
```

Use `prevent_destroy` on databases, state buckets, and anything holding data.

## Secrets and state

- State stores resource attributes **including secrets in plaintext**. Encrypt the backend at rest and restrict access.
- Never commit `terraform.tfstate` or `.terraform/` to VCS. Add to `.gitignore`:
  ```
  .terraform/
  *.tfstate
  *.tfstate.*
  *.tfvars   # if they may contain secrets
  crash.log
  ```
- Mark sensitive outputs/variables `sensitive = true` to keep them out of CLI output and plan logs.

## Drift and refresh

- `terraform plan` refreshes state and shows drift. Run it in CI on a schedule to detect manual changes.
- Avoid `terraform apply -refresh-only` surprises by keeping infra changes in code, not the console.

## Workspace vs directory separation

For environment separation (dev/staging/prod), prefer **separate state files via separate backend keys/directories** over `terraform workspace` for production systems — workspaces share the same backend config and are easy to mix up. Reserve workspaces for ephemeral parallel copies.
