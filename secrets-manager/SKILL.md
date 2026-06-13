---
name: secrets-manager
description: Detects, prevents, and remediates leaked credentials and teaches safe secret handling using environment variables, vaults (HashiCorp Vault, AWS/GCP/Azure secret stores), KMS envelope encryption, and rotation. Use this skill when a user mentions hardcoded API keys, passwords, tokens, or .env files in code; asks how to store, inject, or rotate secrets; wants to set up a vault or KMS; needs to scrub a leaked credential from git history; or asks to add pre-commit secret scanning.
license: MIT
---

# Secrets Manager

## Overview

This skill governs the full lifecycle of secrets: keeping them out of source code, storing them in the right backend, injecting them at runtime, rotating them on schedule, and remediating leaks fast and completely. A leaked credential is an active incident — assume it is compromised the moment it touches a public surface.

Keywords: secret, credential, API key, token, password, .env, environment variable, vault, HashiCorp Vault, KMS, envelope encryption, AWS Secrets Manager, GCP Secret Manager, Azure Key Vault, SOPS, sealed-secrets, rotation, key rotation, git-secrets, gitleaks, trufflehog, pre-commit hook, scrub, BFG, git filter-repo, hardcoded credentials, dotenv, OIDC, workload identity, leaked key.

## Workflow

1. **Classify the request** into one of four modes (see Decision Framework):
   - PREVENT — keep new secrets out of code.
   - STORE/INJECT — choose a backend and runtime delivery.
   - ROTATE — establish rotation cadence and automation.
   - REMEDIATE — a secret has already leaked.

2. **If a secret may already be exposed, treat it as REMEDIATE first.** Rotation/revocation precedes cleanup. Removing the secret from git does NOT un-leak it. Follow `references/leak-remediation.md` step by step.

3. **Scan before you advise.** Run `scripts/scan_secrets.py` over the repo (or recommend `gitleaks`/`trufflehog` for git history). Never assume the codebase is clean. Report findings with file, line, and a redacted match — never echo full secret values into logs, chat, or commits.

4. **Pick a storage backend** using the matrix in `references/storage-backends.md`. Match to the runtime (local dev, CI, Kubernetes, serverless, VM) and the org's existing cloud. Prefer short-lived, dynamically-issued credentials and OIDC/workload identity over long-lived static keys wherever possible.

5. **Define injection.** Secrets reach the process via environment variables, mounted files (tmpfs), or a fetch-at-startup SDK call — never baked into images, never committed. Use `templates/dotenv-template.md` for local dev and document `.env` in `.gitignore`.

6. **Establish rotation.** Set a cadence per secret class (see `references/rotation-runbook.md`), automate it where the backend supports it (Vault dynamic secrets, AWS Secrets Manager rotation Lambdas), and verify zero-downtime cutover with overlapping validity windows.

7. **Add guardrails.** Install a pre-commit hook (`scripts/install_precommit.sh`) and CI scanning so the next secret never lands. Verify `.gitignore` covers `.env`, `*.pem`, `*.key`, credential files.

8. **Verify and document.** Confirm no secret remains in working tree or history, rotation is scheduled, and access is least-privilege. Produce a short summary of what changed and what the human must still do (e.g., update the secret in the vault console).

## Decision Framework

| Signal in the request | Mode | First action |
|---|---|---|
| "I have this key in my config / source" already pushed | REMEDIATE | Revoke + rotate immediately, then scrub history |
| "Where should I keep my secrets?" / new app | STORE/INJECT | Backend matrix in `references/storage-backends.md` |
| "How often / how do I rotate?" | ROTATE | `references/rotation-runbook.md` |
| "Stop me committing secrets" | PREVENT | `scripts/install_precommit.sh` + CI scan |
| Unsure / mixed | Scan first | `scripts/scan_secrets.py`, then classify |

### Backend selection quick guide

- **Local dev:** `.env` file (gitignored) loaded by dotenv, OR a developer vault like `direnv` + 1Password CLI / `vault` agent. Never commit `.env`.
- **CI/CD:** native masked secrets (GitHub Actions secrets/OIDC, GitLab CI variables) — prefer OIDC federation to a cloud role over storing static cloud keys.
- **Cloud runtime (AWS/GCP/Azure):** the cloud-native secret store + IAM/workload identity. Fetch at startup; cache in memory only.
- **Kubernetes:** External Secrets Operator or sealed-secrets/SOPS — avoid plain `Secret` objects checked into git (they are only base64, not encrypted).
- **High-compliance / multi-cloud:** HashiCorp Vault with dynamic secrets and short TTLs.

## Worked Examples

See `examples/remediate-leaked-aws-key.md` for an end-to-end leak response: detection, revocation, history rewrite, and prevention.

Inline example — converting a hardcoded secret:

```python
# BEFORE — hardcoded, will be flagged
STRIPE_KEY = "sk_live_PLACEHOLDER_EXAMPLE_KEY"

# AFTER — read from environment, fail loudly if absent
import os
STRIPE_KEY = os.environ["STRIPE_KEY"]  # set via vault/CI, never committed
```

## Best Practices

- **Treat any exposed secret as compromised.** Rotate first; clean up second. Attackers scrape public repos within seconds.
- **Prefer short-lived dynamic credentials** (Vault dynamic secrets, STS, OIDC tokens) over long-lived static keys.
- **Least privilege per secret.** Scope tokens to the minimum API, resource, and TTL. One secret per service per environment.
- **Never log or print secret values.** Redact in logs, error messages, and tracebacks. The scanner output shows partial matches only.
- **Encrypt at rest with KMS envelope encryption** — the data key encrypts the secret, the KMS master key encrypts the data key; rotate the master key independently.
- **Keep `.env`, `*.pem`, `*.key`, `*.p12`, `credentials*` out of git** via `.gitignore` and enforce with a pre-commit hook.
- **Automate rotation** and alert on rotation failures; manual rotation drifts and gets skipped.
- **Audit access.** Enable access logging on the vault/KMS and review who/what read each secret.

## Common Pitfalls

- **Deleting the file but not rewriting history.** The secret still lives in every prior commit and every clone/fork. Use `git filter-repo` or BFG, then force-push, then have collaborators re-clone.
- **Rotating without revoking the old value.** The leaked key keeps working until you revoke it at the provider.
- **Committing Kubernetes `Secret` manifests.** Base64 is encoding, not encryption — anyone can decode it. Use sealed-secrets/SOPS/External Secrets.
- **Storing secrets in CI environment variable definitions in code** (e.g., plaintext in a YAML pipeline). Use the platform's masked secret store.
- **Baking secrets into Docker image layers** via `ENV` or `COPY .env`. They persist in the image history. Inject at runtime instead.
- **Using one shared key everywhere.** A single leak then forces a fleet-wide rotation. Scope per service/environment.
- **Trusting `.gitignore` alone.** It does not untrack already-committed files and does not stop a `git add -f`. Pair it with scanning.
- **Echoing the secret into chat or a summary while "helping."** Redact always.
