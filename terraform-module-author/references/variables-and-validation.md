# Variables, Types, and Validation

## Always specify type + description

```hcl
variable "region" {
  type        = string
  description = "AWS region to deploy into."
}
```

Use `default` ONLY for genuinely optional inputs. A variable with no default is required — that is the clearest contract for mandatory inputs.

## Type system

| Type | Example | Notes |
|------|---------|-------|
| `string` / `number` / `bool` | `"us-east-1"`, `3`, `true` | primitives |
| `list(T)` | `list(string)` | ordered, index-keyed |
| `set(T)` | `set(string)` | unordered, unique — good for `for_each` |
| `map(T)` | `map(string)` | key/value |
| `object({...})` | structured input | per-attribute types |
| `tuple([...])` | fixed-length mixed | rarely needed |
| `any` | escape hatch | avoid — loses validation |

## Object types with optional attributes and defaults

```hcl
variable "lifecycle_rules" {
  description = "S3 lifecycle rules keyed by rule id."
  type = map(object({
    prefix          = optional(string, "")
    enabled         = optional(bool, true)
    expiration_days = number
  }))
  default = {}
}
```

`optional(type, default)` fills missing attributes so callers only specify what they need.

## Validation blocks

A variable may have multiple `validation` blocks; each has a `condition` (must be `true`) and an `error_message`.

```hcl
variable "cidr_block" {
  type        = string
  description = "VPC CIDR."
  validation {
    condition     = can(cidrhost(var.cidr_block, 0))
    error_message = "cidr_block must be a valid CIDR (e.g. 10.0.0.0/16)."
  }
}
```

Useful condition patterns:

| Goal | Condition |
|------|-----------|
| Enum | `contains(["a","b"], var.x)` |
| Range | `var.n >= 1 && var.n <= 10` |
| Regex | `can(regex("^[a-z-]+$", var.x))` |
| Valid CIDR | `can(cidrhost(var.x, 0))` |
| Non-empty list | `length(var.x) > 0` |
| All items match | `alltrue([for s in var.x : can(regex("^p-", s))])` |
| String length | `length(var.x) <= 63` |

### Cross-variable validation (Terraform >= 1.9)

```hcl
variable "max_size" {
  type = number
  validation {
    condition     = var.max_size >= var.min_size
    error_message = "max_size must be >= min_size."
  }
}
```

## Sensitive variables

```hcl
variable "db_password" {
  type        = string
  description = "Database master password."
  sensitive   = true
}
```

Never set a default for a secret. Pass via `TF_VAR_db_password`, a `-var-file` excluded from VCS, or a secrets manager data source.

## Preconditions and postconditions

Validate relationships that span resources/data, not just a single variable, using `lifecycle` checks:

```hcl
resource "aws_instance" "this" {
  # ...
  lifecycle {
    precondition {
      condition     = data.aws_ami.this.architecture == "x86_64"
      error_message = "Selected AMI must be x86_64."
    }
    postcondition {
      condition     = self.public_ip != ""
      error_message = "Instance did not receive a public IP."
    }
  }
}
```

## Outputs

```hcl
output "bucket_arn" {
  description = "ARN of the created bucket."
  value       = aws_s3_bucket.this.arn
}

output "connection_string" {
  description = "Database connection string."
  value       = local.conn_str
  sensitive   = true
}
```

Guidance:
- Output IDs/ARNs/names/endpoints callers need to wire other resources.
- Add `depends_on` to an output only when a consumer must wait for a side-effecting resource.
- Don't output entire resource objects unless intentional — it bloats the API and may leak data.
