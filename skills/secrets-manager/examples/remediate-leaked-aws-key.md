# Worked Example: Remediating a Leaked AWS Key

## Scenario

A developer pushed `config/settings.py` containing a live AWS access key to a public GitHub repo three commits ago. CI did not yet have secret scanning.

```python
# config/settings.py  (committed)
AWS_ACCESS_KEY_ID = "AKIAIOSFODNN7EXAMPLE"
AWS_SECRET_ACCESS_KEY = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
```

## Step 1 — Treat as compromised, revoke immediately

Do NOT start with git cleanup. The key was public; assume it is harvested.

```bash
# deactivate then delete the leaked key at the provider
aws iam update-access-key --access-key-id AKIAIOSFODNN7EXAMPLE --status Inactive --user-name ci-deployer
aws iam delete-access-key --access-key-id AKIAIOSFODNN7EXAMPLE --user-name ci-deployer
```

Check for abuse during the exposure window:

```bash
aws cloudtrail lookup-events --lookup-attributes AttributeKey=AccessKeyId,AttributeValue=AKIAIOSFODNN7EXAMPLE
```

## Step 2 — Issue a replacement, store it properly

Better than a new static key: move CI to OIDC federation (no stored key at all). If a key is still required short-term:

```bash
aws iam create-access-key --user-name ci-deployer
# store in the secret backend, NOT in code
aws secretsmanager create-secret --name ci-deployer/aws --secret-string '{"AWS_ACCESS_KEY_ID":"...","AWS_SECRET_ACCESS_KEY":"..."}'
```

Update the app to read from the environment, failing loudly if unset:

```python
import os
AWS_ACCESS_KEY_ID = os.environ["AWS_ACCESS_KEY_ID"]
AWS_SECRET_ACCESS_KEY = os.environ["AWS_SECRET_ACCESS_KEY"]
```

## Step 3 — Scrub git history

```bash
pip install git-filter-repo
printf 'AKIAIOSFODNN7EXAMPLE==>***REMOVED***\nwJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY==>***REMOVED***\n' > replacements.txt
git filter-repo --replace-text replacements.txt
```

## Step 4 — Force-push and re-sync the team

```bash
git push --force --all
git push --force --tags
```

- Tell every collaborator to delete and re-clone (their reflogs still hold the key).
- Because the repo was public, request a cache purge from GitHub support and check for forks.

## Step 5 — Verify clean

```bash
python scripts/scan_secrets.py .
# expected: OK: no likely secrets found.
gitleaks detect --source . --redact
```

## Step 6 — Prevent recurrence

```bash
./scripts/install_precommit.sh .
```

Add to `.gitignore`:

```
.env
*.pem
*.key
config/secrets.*
```

Add CI scanning (e.g., a gitleaks GitHub Action) on every PR and push.

## Timeline recorded

| Event | Time (UTC) |
|---|---|
| Secret pushed | 14:02 |
| Detected | 14:31 |
| Key revoked | 14:36 |
| History scrubbed + force-push | 15:10 |
| Prevention in place | 15:40 |

## Key takeaways

- Revocation happened 5 minutes after detection — before any cleanup.
- The replacement path moved toward OIDC to eliminate the static key entirely.
- History rewrite + team re-clone + cache purge closed the loop; scanning prevents the next one.
