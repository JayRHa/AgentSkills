# Worked Example: Reviewing a Login Handler Change

## Input diff

```diff
diff --git a/app/auth.py b/app/auth.py
index 1a2b3c4..5d6e7f8 100644
--- a/app/auth.py
+++ b/app/auth.py
@@ -10,12 +10,20 @@ import sqlite3
-def login(request):
-    user = get_user(request.form["username"])
-    if user and user.password == request.form["password"]:
-        return make_session(user)
-    return error("bad creds")
+def login(request):
+    username = request.form["username"]
+    password = request.form["password"]
+    db = sqlite3.connect("app.db")
+    row = db.execute(
+        "SELECT id, pwhash FROM users WHERE name = '" + username + "'"
+    ).fetchone()
+    if row and row[1] == hashlib.md5(password.encode()).hexdigest():
+        log.info("login ok user=%s pw=%s", username, password)
+        return make_session(row[0])
+    return error("bad creds")
```

## Produced review

# Code Review: Rework login() to query DB directly

**Scope:** main...feat/login | 1 file, +12/-5
**Reviewed:** 2026-06-08

## Verdict

> **Block**

**Summary:** 2 Critical, 1 High, 1 Medium, 1 Low. The new login path introduces a SQL injection and weak password hashing, and leaks the plaintext password into logs. Must not merge.

---

## Findings

### Critical

**[Critical] Security — `app/auth.py:16`**
What: Username is concatenated directly into the SQL string.
Why it matters: `username = "' OR '1'='1' --"` returns the first user and bypasses auth; `'; DROP TABLE users; --` is possible depending on driver. Classic SQL injection (OWASP A03).
Fix:
```diff
-        "SELECT id, pwhash FROM users WHERE name = '" + username + "'"
+        "SELECT id, pwhash FROM users WHERE name = ?", (username,)
```

**[Critical] Security — `app/auth.py:18`**
What: Password hashed with MD5.
Why it matters: MD5 is fast and broken; offline cracking of a leaked DB is trivial (OWASP A02). Existing hashes must be migrated.
Fix: Use a password KDF, e.g. `bcrypt.checkpw(password.encode(), row[1])`, and re-hash on the next successful login during migration.

### High

**[High] Security — `app/auth.py:19`**
What: The plaintext password is written to the info log.
Why it matters: Credentials end up in log aggregation/retention; anyone with log access can impersonate users (OWASP A09).
Fix:
```diff
-        log.info("login ok user=%s pw=%s", username, password)
+        log.info("login ok user=%s", username)
```

### Medium

**[Medium] Correctness — `app/auth.py:13`**
What: New `sqlite3.connect` is opened on every request and never closed.
Why it matters: Connection/file-handle leak under load; resources held on the error path too.
Fix: Use a context manager or a shared connection pool: `with sqlite3.connect("app.db") as db:`.

### Low

**[Low] Security — `app/auth.py:18`** — Hash comparison uses `==`, which is not constant-time. Once bcrypt is adopted this is moot (its compare is constant-time); otherwise use `hmac.compare_digest`.

---

## What's good

- Splitting `username`/`password` into locals reads more clearly than indexing the form inline.

## Open questions

- Is there an existing `users.pwhash` format? The fix assumes a migration path from MD5 to bcrypt; confirm before merging.

---

## Why this review is structured this way

- Verdict first (**Block**) so the author knows the stakes before reading details.
- Two Critical items are genuinely merge-blocking and each has a concrete, minimal fix.
- The constant-time comparison is correctly downgraded to **Low** because the recommended bcrypt fix already resolves it — no nit-inflation.
- One positive note keeps the review balanced; one open question flags an assumption rather than guessing silently.
