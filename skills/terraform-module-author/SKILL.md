---
name: terraform-module-author
description: Authors reusable, production-grade Terraform modules with clean typed variables, well-documented outputs, version pinning, state hygiene, and built-in validation. Use this skill when the user asks to "write a Terraform module", "refactor Terraform into a module", "add variable validation", "structure a Terraform repo", "publish a module to the registry", "review my .tf files", or otherwise create, organize, or harden HCL infrastructure code.
license: MIT
---

# Terraform Module Author

## Overview

This skill encodes the conventions for writing reusable Terraform modules that are safe to share, version, and consume across teams. It covers file layout, typed variables with validation, outputs, provider/version pinning, state hygiene, and documentation.

**Keywords:** terraform, opentofu, hcl, module, variables, outputs, validation, `terraform.tfvars`, `versions.tf`, provider pinning, remote state, registry, `tflint`, `terraform fmt`, `terraform validate`, infrastructure as code, IaC, DevOps.

A "module" here is any directory of `.tf` files meant to be called by another configuration via a `module "x" { source = ... }` block. The same rules apply to the *root* module — the only difference is the root configures providers and backends, while reusable child modules must NOT.

## Workflow

1. **Clarify the boundary.** Decide what the module owns. A good module manages one logical unit (a VPC, an S3 bucket with policy, a Kubernetes namespace). If you cannot name it in one phrase, split it. List required inputs, optional inputs, and what callers need back as outputs.
2. **Lay out the standard files.** Create `main.tf`, `variables.tf`, `outputs.tf`, `versions.tf`, and `README.md`. Keep resource logic in `main.tf` (or split by concern, e.g. `iam.tf`, `network.tf`). Never put variables or outputs inline in `main.tf`. See `references/module-conventions.md`.
3. **Pin versions in `versions.tf`.** Set `required_version` for Terraform/OpenTofu and `required_providers` with a source and a `~>` pessimistic constraint. Reusable child modules declare `required_providers` but do NOT include `provider` blocks or `backend` config — those belong only to the root.
4. **Write typed variables with validation.** Every variable gets an explicit `type`, a `description`, and a `default` only when truly optional. Add `validation` blocks for enums, ranges, regex, and naming rules. Mark secrets `sensitive = true`. See `references/variables-and-validation.md`.
5. **Expose minimal, stable outputs.** Output the IDs/ARNs/endpoints callers need to wire things together. Every output has a `description`. Mark sensitive outputs `sensitive = true`. Avoid leaking the entire resource object unless intentional.
6. **Guard state hygiene.** Use `for_each` over `count` for named, stable resources. Never hardcode backends inside reusable modules. Document any `moved {}` blocks when renaming resources to avoid destroy/recreate. See `references/state-hygiene.md`.
7. **Validate and lint.** Run `terraform fmt -recursive`, `terraform validate`, and `tflint`. Use the bundled `scripts/validate_module.sh` to run the full gate in one command.
8. **Document.** Fill in `README.md` from `templates/README.md.tmpl` — purpose, usage example, and an inputs/outputs table. If `terraform-docs` is available, generate the tables automatically.

## Module Layout (canonical)

```
my-module/
├── main.tf          # resources and locals
├── variables.tf     # all input variables, typed + validated
├── outputs.tf       # all outputs, described
├── versions.tf      # required_version + required_providers (no provider/backend)
├── README.md        # purpose, usage, inputs/outputs tables
├── examples/
│   └── basic/       # a runnable example that calls the module
└── tests/           # optional: terraform test (.tftest.hcl) or terratest
```

## Decision Framework: `count` vs `for_each`

| Situation | Use | Why |
|-----------|-----|-----|
| Toggle a single resource on/off | `count = var.enabled ? 1 : 0` | Simple boolean gate |
| N identical, order-insensitive copies | `for_each` over a set | Stable keys survive list reordering |
| Named/keyed resources (buckets, users) | `for_each` over a map | Renaming/removing one item won't reindex the rest |
| A list that may be reordered | NOT `count` | `count` keys by index; reordering forces destroy/recreate |

Rule of thumb: prefer `for_each` whenever items have a natural identity. Reserve `count` for on/off toggles.

## Variable Validation Cheatsheet

```hcl
variable "environment" {
  type        = string
  description = "Deployment environment."
  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "environment must be one of: dev, staging, prod."
  }
}

variable "instance_count" {
  type        = number
  description = "Number of instances (1-10)."
  default     = 1
  validation {
    condition     = var.instance_count >= 1 && var.instance_count <= 10
    error_message = "instance_count must be between 1 and 10."
  }
}

variable "name" {
  type        = string
  description = "Resource base name (lowercase, hyphen-separated)."
  validation {
    condition     = can(regex("^[a-z][a-z0-9-]{1,30}[a-z0-9]$", var.name))
    error_message = "name must be 3-32 chars, lowercase alphanumeric and hyphens, not starting/ending with a hyphen."
  }
}
```

See `references/variables-and-validation.md` for object types, `optional()` attributes with defaults, cross-variable validation, and `precondition`/`postcondition` checks.

## Worked Example

`examples/s3-bucket-module.md` shows a complete reusable S3 bucket module: typed variables with validation, `for_each` lifecycle rules, sensitive outputs, version pinning, and a calling example. Use it as a reference shape when authoring new modules.

## Best Practices

- **One responsibility per module.** Compose small modules in the root rather than building one mega-module with dozens of feature flags.
- **No providers or backends in child modules.** Declare `required_providers` only. The root passes providers in (implicitly or via `providers = {}`) and owns the backend.
- **Pin everything.** `required_version`, every provider, and any nested `source` (use a `?ref=tag` or registry version). Unpinned modules break silently on upstream changes.
- **Describe every variable and output.** The description is the API contract; `terraform-docs` renders it.
- **Validate at the boundary.** Catch bad input with `validation` blocks rather than letting the provider fail mid-apply with a cryptic error.
- **Prefer `for_each` with stable keys** so adding/removing one item never reshuffles others.
- **Mark secrets `sensitive`** on both variables and outputs to keep them out of plan output and logs.
- **Use `locals` for computed/derived values**, not for things that should be inputs. Tag merging (`merge(var.tags, local.common_tags)`) belongs in locals.
- **Keep examples runnable.** An `examples/basic` that actually `terraform plan`s is your best regression test and documentation.
- **Run the gate before commit:** `scripts/validate_module.sh`.

## Common Pitfalls

- **Backend/provider blocks inside a reusable module.** This makes it un-composable and causes "provider configuration not allowed" or duplicate backend errors. Move them to the root.
- **Using `count` for keyed resources.** Removing the first item in a list re-indexes everything and triggers needless destroy/recreate. Use `for_each`.
- **Untyped variables (`type = any` everywhere).** Loses validation and self-documentation. Type explicitly; use `object({...})` for structured input.
- **Outputting nothing useful.** Callers can't reference IDs/ARNs that aren't exported. Output the wiring points.
- **Renaming resources without `moved {}`.** Terraform sees a delete + create. Add a `moved {}` block to preserve state.
- **`terraform.tfvars` committed with secrets.** Never commit real secrets; pass via env (`TF_VAR_*`), a secrets manager, or `-var-file` excluded from VCS.
- **Mutable default tags overriding caller tags.** Always `merge()` with caller-supplied tags taking precedence.
- **Skipping `terraform fmt`/`validate` in CI.** Drift in formatting and silent config errors accumulate. Gate every PR.