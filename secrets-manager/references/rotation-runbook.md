# Secret Rotation Runbook

Rotation limits the value of a leaked credential and is required by most compliance frameworks. Automate it; manual rotation drifts and gets skipped.

## Cadence by secret class

| Secret class | Suggested max lifetime | Rotation method |
|---|---|---|
| Dynamic DB / cloud creds (Vault) | minutes-hours (lease TTL) | Automatic on lease expiry |
| Service API keys | 30-90 days | Provider API + secret store update |
| Database passwords | 30-90 days | Automated rotation function |
| Cloud access keys (static) | 90 days (or eliminate via OIDC) | IAM rotate + redeploy |
| TLS certificates | <= 1 year (ACME: 90 days) | ACME auto-renew |
| Signing keys (JWT/OAuth) | 90-180 days, overlap windows | Dual-key publish then retire |
| Encryption master keys (KMS) | 1 year (auto) | KMS automatic rotation |
| On any leak or offboarding | Immediately | Out-of-band emergency rotation |

## Zero-downtime rotation pattern (overlapping validity)

1. **Create** the new secret/version while the old one is still valid.
2. **Distribute** the new value to the secret store (new version, old still readable).
3. **Deploy/refresh** consumers so they pick up the new value (rolling restart or TTL refresh).
4. **Verify** all consumers use the new value (logs/metrics show success on new key).
5. **Revoke** the old value only after confirmation.

Never revoke the old value before consumers have adopted the new one — that causes an outage.

## Automated rotation examples

### AWS Secrets Manager
- Attach a rotation Lambda; configure `RotationRules` (e.g., 30 days).
- For RDS, use the AWS-provided rotation templates (single-user or multi-user strategy).
- Multi-user strategy avoids downtime by alternating between two DB users.

### HashiCorp Vault dynamic secrets
- Configure a database secrets engine; Vault issues per-request credentials with a TTL.
- Apps request creds at startup; Vault revokes them automatically at lease end.
- No rotation logic in the app — the short TTL IS the rotation.

### Certificates (ACME / cert-manager)
- Use cert-manager (Kubernetes) or certbot with auto-renew; renew at ~2/3 of lifetime.

## Verification checklist

- [ ] New secret created and stored in the backend
- [ ] All consumers updated and confirmed working on the new value
- [ ] Old secret revoked at the provider (not just deleted from store)
- [ ] Rotation event logged/audited
- [ ] Next rotation scheduled (automation or calendar)
- [ ] Alert configured for rotation failures
