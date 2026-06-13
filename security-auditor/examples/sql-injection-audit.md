# Worked Example: Auditing a Flask login endpoint

This shows the full method one finding should follow: triage -> trace -> PoC -> severity -> fix.

## The code under audit

`app/auth.py`
```python
 12  @app.post('/login')
 13  def login():
 14      username = request.form['username']
 15      password = request.form['password']
 16      cur = db.cursor()
 17      cur.execute(
 18          "SELECT id, role FROM users "
 19          "WHERE username = '" + username + "' "
 20          "AND password = '" + password + "'"
 21      )
 22      row = cur.fetchone()
 23      if row:
 24          session['uid'] = row[0]
 25          session['role'] = row[1]
 26          return redirect('/dashboard')
 27      return 'Invalid credentials', 401
```

## Step 1 — Triage
`scripts/grep_audit.sh app/` flags line 17-20 under "SQL string-building":
```
app/auth.py:17: cur.execute("SELECT id, role FROM users WHERE username = '" + username + ...
```
Lead, not proof. Read the code.

## Step 2 — Trace source -> sink
- **Source:** `username`, `password` from `request.form` (fully attacker-controlled, unauthenticated).
- **Sink:** `cur.execute(...)` — a SQL interpreter.
- **Sanitizer:** none. Raw string concatenation. Chain is unbroken.

This is SQL Injection, CWE-89.

## Step 3 — Build a proof-of-concept
Authentication bypass via the password field:
```
POST /login
Content-Type: application/x-www-form-urlencoded

username=admin&password=' OR '1'='1
```
Resulting query:
```sql
SELECT id, role FROM users
WHERE username = 'admin' AND password = '' OR '1'='1'
```
The `OR '1'='1'` makes the WHERE always true; `fetchone()` returns the first row (often the admin). Attacker logs in as admin with no password.

Data exfiltration via UNION (if column count/types align):
```
username=x' UNION SELECT credit_card, cvv FROM payments-- &password=x
```

## Step 4 — Impact & severity
- **Impact:** Authentication bypass + full database read (and write on stacked-query backends). Account takeover of any user including admin.
- **Exploitability:** Trivial — single unauthenticated request, classic payload.
- **Exposure:** Internet-facing login endpoint.
- **Severity: CRITICAL.** `CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H` (9.8).

## Step 5 — Fix
Parameterize the query (let the driver bind values) and stop comparing passwords in SQL — hash and verify them:
```python
from werkzeug.security import check_password_hash

@app.post('/login')
def login():
    username = request.form['username']
    password = request.form['password']
    cur = db.cursor()
    cur.execute(
        "SELECT id, role, password_hash FROM users WHERE username = %s",
        (username,),
    )
    row = cur.fetchone()
    if row and check_password_hash(row[2], password):
        session.clear()                 # rotate session (fixes A07 session fixation)
        session['uid'], session['role'] = row[0], row[1]
        return redirect('/dashboard')
    return 'Invalid credentials', 401   # same message + timing for valid/invalid user
```
Notes: `%s` is a bind placeholder (not Python `%` formatting); the driver escapes it safely. Passwords are now verified against a salted hash, not stored/compared in plaintext.

## Step 6 — Report entry (final form)

> **[CRITICAL] SQL Injection in login endpoint — auth bypass & data theft (CWE-89)**
> - **Location:** `app/auth.py:17-21`
> - **Exploit:** `POST /login` with `password=' OR '1'='1` bypasses authentication and logs in as the first user (admin).
> - **Impact:** Full authentication bypass, account takeover, read/exfiltration of the entire `users`/`payments` tables.
> - **Fix:** Use parameterized queries (`%s` binding) and verify a salted password hash; see patch above.
