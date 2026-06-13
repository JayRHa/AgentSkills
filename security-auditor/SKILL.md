---
name: security-auditor
description: Audits source code against the OWASP Top 10 (2021) and produces concrete, exploitable findings with proof-of-concept, severity ratings, and copy-pasteable fixes. Use this skill when the user asks to "do a security review", "audit this code for vulnerabilities", "check for OWASP Top 10 issues", "find security bugs", "is this code safe", "review for injection/XSS/SSRF/auth flaws", or before shipping security-sensitive code.
license: MIT
---

# Security Auditor

## Overview

This skill performs a rigorous, evidence-based security audit of a codebase against the **OWASP Top 10 (2021)**. Every finding must be **concrete and exploitable**, not a vague "consider validating input." A finding is only worth reporting if you can name the vulnerable file and line, describe how an attacker triggers it, rate its severity, and supply a working fix.

Keywords: security audit, OWASP Top 10, SQL injection, XSS, SSRF, IDOR, broken access control, authentication, secrets, cryptography, deserialization, command injection, path traversal, CSRF, vulnerability, CWE, CVSS, penetration test, threat model, secure code review.

The deliverable is a **prioritized findings report** (use `templates/finding-report.md`) where each item follows: *vulnerability → location → exploit → impact → fix*.

## Workflow

1. **Scope the audit.** Identify language(s), framework(s), entry points (HTTP routes, message handlers, CLI args, file uploads), trust boundaries, and where untrusted input enters. Note authn/authz mechanism and the data store(s).
2. **Run the grep triage.** Execute `scripts/grep_audit.sh <path>` to surface high-signal patterns (raw SQL string building, `eval`, `pickle.loads`, `dangerouslySetInnerHTML`, hardcoded secrets, weak crypto, disabled TLS verification). Triage is a *lead generator*, not proof — every hit must be manually confirmed.
3. **Trace tainted data.** For each candidate, follow untrusted input from source (request param, header, body, file) to sink (DB query, shell, file path, HTML, deserializer, redirect). A vulnerability exists only when a source reaches a dangerous sink **without adequate sanitization for that sink**.
4. **Walk the OWASP checklist.** Go through `references/owasp-top-10.md` category by category. For each, decide: Not Applicable / No Issue Found / Finding. Do not skip categories — absence of evidence is itself worth noting.
5. **Confirm exploitability.** For each finding write a concrete proof-of-concept: the exact request, payload, or call sequence. If you cannot construct a PoC, downgrade to "potential" and say why.
6. **Rate severity.** Use the CVSS-lite rubric in `references/severity-rubric.md` (Critical / High / Medium / Low / Info) based on impact × exploitability × exposure.
7. **Write the fix.** Provide minimal, idiomatic, copy-pasteable remediation — parameterized query, output encoding, allowlist, framework auth guard. Prefer fixing the root cause, not the symptom.
8. **Assemble the report.** Sort findings by severity. Use `templates/finding-report.md`. Include a one-line executive summary and a coverage table showing which OWASP categories you reviewed.

## What counts as a real finding

A finding MUST include all five:

| Field | Requirement |
|-------|-------------|
| **Vulnerability** | Named class + CWE id (e.g. SQL Injection, CWE-89) |
| **Location** | `path/to/file.ext:line` and the offending code snippet |
| **Exploit** | Concrete payload/request showing attacker control reaches the sink |
| **Impact** | What an attacker gains (data read/write, RCE, account takeover) |
| **Fix** | Specific code change, not generic advice |

If you cannot fill all five, it is a *note* or a *hardening suggestion*, not a finding — label it as such so you do not inflate the report with noise.

## The OWASP Top 10 (2021) at a glance

| # | Category | The question to ask |
|---|----------|---------------------|
| A01 | Broken Access Control | Can a user act on data/functions they shouldn't? (IDOR, missing authz, path traversal) |
| A02 | Cryptographic Failures | Is sensitive data protected at rest/in transit? (weak hash, plaintext, hardcoded keys) |
| A03 | Injection | Does untrusted input reach an interpreter? (SQL, NoSQL, OS command, LDAP, XSS) |
| A04 | Insecure Design | Is there a missing security control by design? (no rate limit, no MFA on sensitive flow) |
| A05 | Security Misconfiguration | Defaults, verbose errors, open CORS, debug mode on |
| A06 | Vulnerable Components | Outdated/known-CVE dependencies |
| A07 | Identification & Auth Failures | Weak session mgmt, credential stuffing, weak passwords, JWT flaws |
| A08 | Software & Data Integrity Failures | Insecure deserialization, unsigned updates, untrusted CI/CD |
| A09 | Logging & Monitoring Failures | No audit log on auth events, logging secrets |
| A10 | SSRF | Server fetches an attacker-controlled URL |

Full detail, patterns, and language-specific sinks are in `references/owasp-top-10.md`.

## Worked example

See `examples/sql-injection-audit.md` for a complete source-to-sink trace, PoC, severity rating, and fix on a vulnerable Flask endpoint. Use it as the model for how every finding should read.

## Tainted-data tracing (the core technique)

```
SOURCE (untrusted)            SINK (dangerous)              SANITIZER (breaks the chain)
request.args / .form    -->   cursor.execute(f"...")  -->   parameterized query (?)
request.json            -->   subprocess(shell=True)  -->   arg list + shlex, no shell
request.headers         -->   open(path)              -->   resolve + allowlist base dir
user content            -->   render as raw HTML      -->   context-aware output encoding
request param URL       -->   requests.get(url)       -->   allowlist host + block internal IPs
```

A sink without a reaching source is dead code, not a vuln. A source reaching a sink **with** a correct sanitizer for that sink is safe. Report only source→sink with no/wrong sanitizer.

## Best Practices

- **Confirm, don't speculate.** Grep finds candidates; you must read the surrounding code to confirm the input is actually attacker-controlled and unsanitized.
- **Match the sanitizer to the sink.** HTML-escaping does nothing for SQL; `quote()` for shell differs from SQL escaping. Wrong-context encoding is a common false sense of safety.
- **Prefer framework-native fixes.** Use the ORM's parameter binding, the template engine's auto-escaping, the framework's auth decorator — don't hand-roll.
- **Rank by exploitability, not by category.** A "Medium" category with a trivial unauthenticated PoC outranks a "High" category needing admin access.
- **Show the PoC.** A finding with a concrete curl command is actionable; "input not validated" is ignorable.
- **Note what you checked and found clean** — it proves coverage and builds trust in the report.
- **Cite CWE and CVSS** so findings map to standard tracking systems.

## Common Pitfalls

- **False positives from grep alone.** `eval` on a hardcoded constant is not a vuln. Always read the data flow.
- **Stopping at the first sink type.** One endpoint can have injection *and* broken access control. Audit each independently.
- **Trusting client-side validation.** JS validation is not a security control; the server is the trust boundary.
- **Missing second-order injection.** Data stored now and concatenated into a query later is still injection.
- **Ignoring authz when authn passes.** Logged-in ≠ authorized. IDOR/BOLA is the #1 real-world web vuln — always test object ownership.
- **Reporting dependency CVEs without reachability.** Note them, but rate by whether the vulnerable code path is actually invoked.
- **Logging secrets in the "fix".** Don't recommend adding logging that captures passwords/tokens.
- **Generic advice.** "Sanitize input" is not a fix. Show the exact parameterized query or encoder call.
