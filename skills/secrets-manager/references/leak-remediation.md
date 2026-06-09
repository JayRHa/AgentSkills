# Leaked Secret Remediation Runbook

A committed/pushed secret is an active incident. Order matters: **revoke before you clean up.** Cleaning git history does not un-leak a secret that was ever public.

## Step 0 — Contain (minutes matter)

Assume the secret is already compromised. Public-repo scrapers find keys in seconds.

## Step 1 — Revoke and rotate at the provider

For the affected credential type, revoke the old value and issue a new one:

- **Cloud keys (AWS/GCP/Azure):** deactivate then delete the access key; create a replacement scoped to least privilege.
- **API keys (Stripe, OpenAI, etc.):** roll the key in the provider dashboard; the old key stops working.
- **Database passwords:** change the password; update consumers via the vault.
- **OAuth client secrets / signing keys:** rotate and re-deploy; invalidate sessions/tokens issued under the old key if it was a signing key.
- **TLS private keys / SSH keys:** reissue the cert / regenerate the keypair; revoke the old (CRL/OCSP) and remove old public keys from `authorized_keys`.

Update the new value in your secret store BEFORE removing the old one from running systems to avoid downtime.

## Step 2 — Scope the blast radius

- Check provider audit/access logs for unauthorized use during the exposure window.
- Identify every place the secret was distributed (CI, other repos, docs, Slack).
- If exposure indicates account compromise, escalate to incident response.

## Step 3 — Remove from git history

Removing the file in a new commit is NOT enough; the secret persists in history.

### Option A — git filter-repo (recommended)

```bash
# install: pip install git-filter-repo
# remove a specific file from all history
git filter-repo --invert-paths --path config/secrets.yml

# or replace a literal secret string everywhere with ***REMOVED***
printf 'sk_live_PLACEHOLDER_EXAMPLE_KEY==>***REMOVED***\n' > replacements.txt
git filter-repo --replace-text replacements.txt
```

### Option B — BFG Repo-Cleaner

```bash
bfg --delete-files secrets.yml
# or
bfg --replace-text replacements.txt
git reflog expire --expire=now --all && git gc --prune=now --aggressive
```

## Step 4 — Force-push and re-sync

```bash
git push --force --all
git push --force --tags
```

- Notify all collaborators to **delete their clones and re-clone** (old history lingers in their copies and reflogs).
- On GitHub/GitLab, old commits may persist in caches/forks — open a support request to purge if the repo was public and the data is sensitive.
- Close any open PRs that contain the secret in their diffs.

## Step 5 — Verify clean

```bash
# scan working tree
python scripts/scan_secrets.py .
# scan full history
gitleaks detect --source . --redact
trufflehog git file://. --only-verified
```

## Step 6 — Prevent recurrence

- Install a pre-commit secret scanner (`scripts/install_precommit.sh`).
- Add CI scanning on every push/PR.
- Move the secret to a proper backend (see `storage-backends.md`).
- Add the file pattern to `.gitignore`.

## Communication rules

- Never paste the full secret value into tickets, chat, or commit messages — redact (show first/last 4 chars max).
- Record the timeline: leaked at, detected at, revoked at, cleaned at.
