# Local `.env` Template

Use this for LOCAL DEVELOPMENT ONLY. Never commit a real `.env`. Commit a
`.env.example` with placeholder values so teammates know which variables exist.

## .gitignore (must include)

```
.env
.env.*
!.env.example
*.pem
*.key
*.p12
credentials*
```

## .env.example (safe to commit — placeholders only)

```dotenv
# === Database ===
DATABASE_URL=postgres://user:password@localhost:5432/appdb

# === Third-party APIs ===
# Get from the secret store; do NOT paste real values here.
STRIPE_SECRET_KEY=sk_test_replace_me
OPENAI_API_KEY=sk-replace_me

# === App ===
SESSION_SECRET=generate_a_random_32_byte_value
LOG_LEVEL=info
```

## Real `.env` (NEVER committed — gitignored)

Populate from your secret backend, not by hand-copying into chat or tickets:

```bash
# pull from AWS Secrets Manager into a local .env
aws secretsmanager get-secret-value --secret-id myapp/dev \
  --query SecretString --output text > .env
chmod 600 .env
```

## Loading conventions

- Python: `python-dotenv` (`load_dotenv()`), then `os.environ["KEY"]`.
- Node: `dotenv` (`require('dotenv').config()`), then `process.env.KEY`.
- Shell/dev: `direnv` with a gitignored `.envrc` that sources from a vault.

## Rules

- Access each var with a fail-loud lookup (`os.environ["KEY"]`, not `.get` with a silent default) so a missing secret fails at startup, not in production.
- Generate random secrets with `openssl rand -hex 32` — never reuse across environments.
- Rotate the values in the backend on the cadence in `references/rotation-runbook.md`; `.env` is just a local cache.
- When done debugging, `rm .env` if it held production-like values.
