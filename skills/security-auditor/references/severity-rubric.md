# Severity Rubric (CVSS-lite)

Rate every finding. Severity = function of **Impact**, **Exploitability**, and **Exposure**. When in doubt, rate by the easiest realistic attack.

## Levels

| Severity | Meaning | Typical examples |
|----------|---------|------------------|
| **Critical** | Trivial to exploit, severe impact, often unauthenticated. Fix now. | Unauthenticated RCE, SQLi dumping all data, auth bypass, SSRF to cloud metadata creds, insecure deserialization of request body |
| **High** | Serious impact, exploitable with low privilege or moderate effort. | Authenticated SQLi, stored XSS, IDOR exposing other users' PII, hardcoded prod secret, JWT signature not verified |
| **Medium** | Real but constrained — needs privilege, user interaction, or limited impact. | Reflected XSS needing a click, CSRF on a non-critical action, weak password hashing (bcrypt-able offline), verbose errors leaking stack traces |
| **Low** | Minor / hard to exploit / low impact. | Missing security header, missing rate limit on low-value endpoint, autocomplete on password field |
| **Info** | Hardening / best practice, not an exploitable flaw. | Dependency slightly outdated but not reachable, defense-in-depth suggestions |

## Scoring dimensions

**Impact** — what does success grant?
- Critical: full system/RCE, all-user data, account takeover, financial loss
- High: another user's sensitive data, write/modify, privilege escalation
- Medium: limited data, single-user impact with interaction
- Low: information disclosure of non-sensitive data

**Exploitability** — how hard?
- Trivial: single crafted request, no auth, no special tools
- Easy: needs a valid low-priv account or a known payload
- Moderate: needs user interaction (clicking a link) or chaining
- Hard: needs admin, race condition, or significant effort

**Exposure** — who can reach it?
- Internet-facing unauthenticated > authenticated > internal-only > local-only

## Combining

```
Critical = (Critical impact) AND (Trivial/Easy exploit) AND (reachable)
High     = High impact with Easy/Moderate exploit, OR Critical impact gated behind low-priv auth
Medium   = Medium impact, OR High impact needing user interaction / hard exploit
Low      = Low impact OR very hard to exploit
Info     = no demonstrable exploit
```

## CVSS hint
If the team uses CVSS 3.1, map: Critical 9.0-10.0, High 7.0-8.9, Medium 4.0-6.9, Low 0.1-3.9. State the vector when you can, e.g. `CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H` for unauth RCE.

## Rule of thumb
An unauthenticated, single-request exploit is **at least High** regardless of category. Authorization (logged-in ≠ authorized) flaws that expose other users' data are **High** even though they feel mundane — they are the most common real breach.
