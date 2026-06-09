# Secret Storage Backend Reference

Choose the backend that matches your runtime and existing cloud. Prefer dynamic, short-lived credentials and identity federation (OIDC / workload identity) over long-lived static keys.

## Comparison matrix

| Backend | Best for | Rotation support | Dynamic secrets | Cost/Ops | Notes |
|---|---|---|---|---|---|
| `.env` + dotenv | Local dev only | Manual | No | Free | Must be gitignored; never ship to prod |
| HashiCorp Vault | Multi-cloud, high compliance | Built-in + lease TTLs | Yes (DB, cloud, PKI) | High (run cluster) | Gold standard; dynamic DB/cloud creds |
| AWS Secrets Manager | AWS workloads | Native rotation Lambdas | Limited (RDS) | $0.40/secret/mo | Tight IAM + KMS integration |
| AWS SSM Parameter Store | AWS, cheap config+secrets | Manual/automation | No | Free (standard tier) | Use `SecureString` (KMS-backed) |
| GCP Secret Manager | GCP workloads | Manual + versions | No | Per-access + storage | Versioned; IAM-scoped |
| Azure Key Vault | Azure workloads | Built-in for some | No | Per-operation | Keys, secrets, certs in one |
| K8s External Secrets Operator | Kubernetes | Syncs from above | Inherits backend | Operator overhead | Pulls from Vault/cloud into K8s Secrets |
| Sealed Secrets / SOPS | GitOps for K8s | Manual re-encrypt | No | Low | Encrypt secrets so they CAN live in git safely |
| 1Password / Doppler / Infisical | SaaS, dev-friendly | Yes | Some | Subscription | Good DX, CLI + CI integrations |

## Runtime delivery patterns

### Environment variables
Simplest, broadly supported. Risk: leak via `/proc`, child-process inheritance, crash dumps, or logging `env`. Acceptable for most apps when sourced from a secret store at start.

### File mount (tmpfs)
Secret written to an in-memory filesystem and read by the app. Avoids env-var inheritance leaks. Used by Vault Agent, K8s projected volumes, and cloud secret CSI drivers.

### Fetch-at-startup SDK call
App calls the secret store API on boot using its workload identity (no bootstrap secret needed). Cache in memory, refresh on TTL expiry. Best with OIDC/IAM roles.

## KMS envelope encryption

Do not encrypt large payloads directly with the KMS master key. Instead:

1. KMS generates a **data key** (returns plaintext + encrypted form).
2. Encrypt your secret/data locally with the plaintext data key (AES-256-GCM).
3. Discard the plaintext data key; store the **encrypted data key alongside the ciphertext**.
4. To decrypt: send the encrypted data key to KMS, get plaintext data key back, decrypt locally.

Benefits: master key never leaves the HSM, you can rotate the master key without re-encrypting all data, and you minimize KMS API calls.

## OIDC / workload identity (eliminate static cloud keys)

- **GitHub Actions -> AWS:** configure an OIDC identity provider + IAM role; the workflow assumes the role with a short-lived token. No `AWS_ACCESS_KEY_ID` stored.
- **GKE/EKS/AKS -> cloud APIs:** bind the pod's service account to a cloud IAM identity (Workload Identity / IRSA / Azure Workload Identity).
- **Vault:** authenticate workloads via Kubernetes auth, AWS IAM auth, or JWT/OIDC — no shared token in the image.

Prefer these over any stored long-lived credential.

## Anti-patterns

- Plain Kubernetes `Secret` committed to git (base64 != encryption).
- Secrets in Terraform state without encrypting the backend (state holds plaintext).
- Long-lived personal access tokens used as service credentials.
- A single shared key across all services and environments.
