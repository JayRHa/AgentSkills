# Worked Example: A Reusable S3 Bucket Module

A complete, registry-ready `terraform-aws-s3bucket` module showing typed/validated variables, `for_each` lifecycle rules, sensitive-safe outputs, and version pinning — plus how a root module consumes it.

## Module: `versions.tf`

```hcl
terraform {
  required_version = ">= 1.5.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}
# Note: no provider "aws" {} and no backend {} — those belong to the root.
```

## Module: `variables.tf`

```hcl
variable "name" {
  type        = string
  description = "Bucket name (DNS-compatible, 3-63 chars)."
  validation {
    condition     = can(regex("^[a-z0-9][a-z0-9.-]{1,61}[a-z0-9]$", var.name))
    error_message = "name must be 3-63 chars, lowercase alphanumeric, dots and hyphens."
  }
}

variable "environment" {
  type        = string
  description = "Deployment environment."
  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "environment must be one of: dev, staging, prod."
  }
}

variable "enable_versioning" {
  type        = bool
  description = "Enable object versioning."
  default     = true
}

variable "lifecycle_rules" {
  description = "Lifecycle expiration rules keyed by rule id."
  type = map(object({
    prefix          = optional(string, "")
    expiration_days = number
  }))
  default = {}
  validation {
    condition     = alltrue([for r in var.lifecycle_rules : r.expiration_days > 0])
    error_message = "every lifecycle rule's expiration_days must be > 0."
  }
}

variable "tags" {
  type        = map(string)
  description = "Tags merged over module defaults (caller wins)."
  default     = {}
}
```

## Module: `main.tf`

```hcl
locals {
  tags = merge(
    {
      ManagedBy   = "terraform"
      Module      = "terraform-aws-s3bucket"
      Environment = var.environment
    },
    var.tags,
  )
}

resource "aws_s3_bucket" "this" {
  bucket = var.name
  tags   = local.tags

  lifecycle {
    prevent_destroy = true # protect data-bearing buckets
  }
}

resource "aws_s3_bucket_versioning" "this" {
  bucket = aws_s3_bucket.this.id
  versioning_configuration {
    status = var.enable_versioning ? "Enabled" : "Suspended"
  }
}

resource "aws_s3_bucket_public_access_block" "this" {
  bucket                  = aws_s3_bucket.this.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# for_each (not count) so removing one rule never reshuffles the others
resource "aws_s3_bucket_lifecycle_configuration" "this" {
  count  = length(var.lifecycle_rules) > 0 ? 1 : 0
  bucket = aws_s3_bucket.this.id

  dynamic "rule" {
    for_each = var.lifecycle_rules
    content {
      id     = rule.key
      status = "Enabled"
      filter { prefix = rule.value.prefix }
      expiration { days = rule.value.expiration_days }
    }
  }
}
```

## Module: `outputs.tf`

```hcl
output "id" {
  description = "Bucket name/id."
  value       = aws_s3_bucket.this.id
}

output "arn" {
  description = "Bucket ARN, for IAM policies."
  value       = aws_s3_bucket.this.arn
}

output "bucket_domain_name" {
  description = "Regional domain name of the bucket."
  value       = aws_s3_bucket.this.bucket_regional_domain_name
}
```

## Root module that consumes it: `examples/basic/main.tf`

```hcl
terraform {
  required_version = ">= 1.5.0"
  required_providers {
    aws = { source = "hashicorp/aws", version = "~> 5.0" }
  }
}

provider "aws" {
  region = "us-east-1" # provider config lives in the ROOT
}

module "logs_bucket" {
  source = "../../"

  name        = "acme-app-logs-dev"
  environment = "dev"

  lifecycle_rules = {
    expire-old-logs = {
      prefix          = "logs/"
      expiration_days = 30
    }
  }

  tags = { Owner = "platform-team" }
}

output "bucket_arn" {
  value = module.logs_bucket.arn
}
```

## Native test: `tests/validation.tftest.hcl`

```hcl
run "rejects_invalid_environment" {
  command         = plan
  variables {
    name        = "acme-logs"
    environment = "production" # not in allowed set
  }
  expect_failures = [var.environment]
}

run "rejects_zero_expiration" {
  command = plan
  variables {
    name           = "acme-logs"
    environment    = "dev"
    lifecycle_rules = { bad = { expiration_days = 0 } }
  }
  expect_failures = [var.lifecycle_rules]
}
```

## What this demonstrates

- Typed variables, every one with a `description` and `validation`.
- `optional()` attributes with defaults in an `object` map type.
- `for_each`/`dynamic` keyed by stable rule ids — no index churn.
- `prevent_destroy` and a public-access block for safe-by-default storage.
- Provider config kept in the root; the module only declares `required_providers`.
- Outputs limited to the wiring points (`id`, `arn`, domain name).
- Validation enforced by `terraform test` before any apply.
