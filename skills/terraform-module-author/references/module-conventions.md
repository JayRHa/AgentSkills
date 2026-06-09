# Terraform Module Conventions

## File responsibilities

| File | Contains | Must NOT contain |
|------|----------|------------------|
| `main.tf` | resources, data sources, `locals`, `moved`/`import` blocks | variable or output declarations |
| `variables.tf` | all `variable` blocks | resources |
| `outputs.tf` | all `output` blocks | resources |
| `versions.tf` | `terraform { required_version, required_providers }` | `provider {}`, `backend {}` (in child modules) |
| `README.md` | purpose, usage, inputs/outputs tables | — |

For larger modules, split `main.tf` by concern: `network.tf`, `iam.tf`, `compute.tf`. Keep `variables.tf` and `outputs.tf` single files so the public API is read in one place.

## Root module vs child (reusable) module

- **Root module**: the directory you run `terraform apply` in. It owns the **backend** configuration and the **provider** configurations.
- **Child/reusable module**: called via `module "x" { source = ... }`. It declares `required_providers` (so Terraform knows which providers it needs) but **never** declares a `backend` or concrete `provider` block. Provider configuration flows in from the root.

```hcl
# CHILD module versions.tf — correct
terraform {
  required_version = ">= 1.5.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}
# NO provider "aws" {} block here. NO backend {} here.
```

## Version pinning constraints

| Operator | Meaning | Example | Allows |
|----------|---------|---------|--------|
| `=` | exact | `= 5.31.0` | only 5.31.0 |
| `>=` | minimum | `>= 1.5.0` | 1.5.0 and up |
| `~>` | pessimistic | `~> 5.0` | >= 5.0, < 6.0 |
| `~>` | pessimistic (patch) | `~> 5.31.0` | >= 5.31.0, < 5.32.0 |

- Use `~> MAJOR.0` for providers in reusable modules (allow minor/patch, block breaking majors).
- Use `>= MIN` for `required_version` so callers on newer Terraform aren't blocked.
- Pin **nested module sources** too: `source = "git::https://...//modules/x?ref=v1.4.0"` or `version = "1.4.0"` for registry modules.

## Naming conventions

- Module folder + `name` frontmatter in registry: `terraform-<PROVIDER>-<NAME>` (e.g. `terraform-aws-vpc`).
- Resource local names: describe role, not type — `resource "aws_s3_bucket" "this"` for the single primary resource; `"logs"`, `"data"` when multiple.
- Variables: `snake_case`, no `var_` prefix.
- Booleans: prefix with `enable_`/`create_` (`enable_versioning`, `create_kms_key`).
- Tags: accept a `tags` map; merge with module defaults.

## Tagging pattern

```hcl
locals {
  common_tags = {
    ManagedBy = "terraform"
    Module    = "terraform-aws-example"
  }
  tags = merge(local.common_tags, var.tags) # caller wins
}
```

## Documentation

Keep a README with a usage block and inputs/outputs tables. Generate tables with `terraform-docs`:

```bash
terraform-docs markdown table --output-file README.md --output-mode inject .
```

The `<!-- BEGIN_TF_DOCS -->` / `<!-- END_TF_DOCS -->` markers (in the bundled template) tell `terraform-docs` where to inject.

## Examples and tests

- `examples/<name>/` is a root module that calls your module with realistic inputs and can `terraform plan`.
- Native tests: `tests/*.tftest.hcl` run with `terraform test`. Use `command = plan` for fast assertions, `command = apply` for integration.

```hcl
# tests/defaults.tftest.hcl
run "valid_name_passes" {
  command = plan
  variables { name = "my-bucket" }
}

run "invalid_name_fails" {
  command = plan
  variables { name = "Bad_Name!" }
  expect_failures = [var.name]
}
```
