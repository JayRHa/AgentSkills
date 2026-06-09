# Security Audit Report

- **Target:** <repo / service / commit sha>
- **Scope:** <paths / endpoints reviewed>
- **Date:** <YYYY-MM-DD>
- **Auditor:** <name>
- **Standard:** OWASP Top 10 (2021)

## Executive summary

<One or two sentences: overall posture and the single most important thing to fix. e.g. "Three Critical findings allow unauthenticated database access and account takeover; remediate before release.">

| Severity | Count |
|----------|-------|
| Critical | 0 |
| High     | 0 |
| Medium   | 0 |
| Low      | 0 |
| Info     | 0 |

## Findings

> Sorted by severity. Each finding includes all five required fields.

### [SEVERITY] Title — short impact phrase (CWE-XXX)

- **OWASP category:** A0X:2021 — <name>
- **Location:** `path/to/file.ext:line` (add more locations if the same flaw recurs)
- **Vulnerability:** <named class + why this code is vulnerable>
- **Code:**
  ```
  <the offending snippet>
  ```
- **Exploit (PoC):**
  ```
  <exact request / payload / call sequence an attacker uses>
  ```
- **Impact:** <what the attacker gains>
- **Severity rationale:** Impact=<..>, Exploitability=<..>, Exposure=<..>. CVSS: <vector / score if known>
- **Fix:**
  ```
  <minimal, idiomatic, copy-pasteable remediation>
  ```
- **References:** CWE-XXX, <links>

<Repeat the block for each finding.>

## Notes & hardening suggestions

> Items that are NOT exploitable findings but improve posture (missing headers, defense-in-depth, slightly outdated deps without a reachable path). Kept separate so findings stay high-signal.

- <note>

## Coverage

Which OWASP categories were reviewed and the outcome. Proves the audit was systematic.

| # | Category | Reviewed | Outcome |
|---|----------|----------|---------|
| A01 | Broken Access Control | yes/no | Finding / No issue / N/A |
| A02 | Cryptographic Failures | | |
| A03 | Injection | | |
| A04 | Insecure Design | | |
| A05 | Security Misconfiguration | | |
| A06 | Vulnerable Components | | |
| A07 | Identification & Auth Failures | | |
| A08 | Software & Data Integrity Failures | | |
| A09 | Logging & Monitoring Failures | | |
| A10 | SSRF | | |

## Methodology

1. Scoped entry points and trust boundaries.
2. Ran `scripts/grep_audit.sh` for triage.
3. Traced tainted data source -> sink for each candidate.
4. Walked the OWASP Top 10 checklist (`references/owasp-top-10.md`).
5. Confirmed exploitability with a PoC; rated severity (`references/severity-rubric.md`).
6. Wrote root-cause fixes.
