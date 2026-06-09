---
name: threat-modeler
license: MIT
description: Runs structured STRIDE threat modeling by decomposing a system into a data flow diagram, enumerating threats per element (Spoofing, Tampering, Repudiation, Information disclosure, Denial of service, Elevation of privilege), and producing prioritized, actionable mitigations with risk ratings. Use this skill when the user asks to "threat model", "do a STRIDE analysis", "find security threats", "assess attack surface", "build a data flow diagram for security", "review the security design", or wants a risk-ranked list of threats and countermeasures for a feature, API, service, or architecture.
---

# Threat Modeler (STRIDE)

## Overview

Keywords: STRIDE, threat model, threat modeling, data flow diagram, DFD, trust boundary, attack surface, spoofing, tampering, repudiation, information disclosure, denial of service, elevation of privilege, DREAD, risk rating, mitigation, countermeasure, security review, attacker, asset.

This skill drives a rigorous, repeatable threat-modeling session using the **STRIDE** methodology popularized by Microsoft's Security Development Lifecycle. It turns an architecture description into:

1. A **data flow diagram (DFD)** with trust boundaries.
2. A **per-element threat enumeration** mapped to the six STRIDE categories.
3. A **prioritized mitigation plan** with risk ratings and concrete countermeasures.

The output is a single threat model document. Threat modeling answers four questions (the Shostack frame): *What are we building? What can go wrong? What are we going to do about it? Did we do a good enough job?*

Bundled resources:
- `references/stride-catalog.md` — STRIDE definitions, the element-to-threat applicability matrix, attacker archetypes, and a large catalog of concrete threats and standard mitigations per category.
- `references/risk-rating.md` — DREAD and Likelihood×Impact rating rubrics with scoring tables and prioritization guidance.
- `scripts/threat_report.py` — stdlib-only Python tool that ingests a YAML/JSON threat list and emits a sorted Markdown risk register plus summary stats.
- `templates/threat-model.md` — the fill-in document the skill produces.
- `examples/url-shortener.md` — a complete worked example (input architecture → DFD → threats → mitigations).

## Workflow

Follow these steps in order. Do not skip decomposition — most missed threats come from a sloppy DFD.

### 1. Scope and gather context
Establish what is in and out of scope. Capture:
- **Assets**: what an attacker wants (credentials, PII, money, availability, integrity of records).
- **System purpose** and the primary user journeys.
- **Tech stack**, deployment model, and external dependencies (third-party APIs, SaaS, queues, databases).
- **Existing controls** already in place (auth, TLS, WAF, RBAC).

If the user has not provided architecture detail, ask targeted questions: entry points, who the users/roles are, where data is stored, what crosses a network or process boundary, and what the worst-case outcome is.

### 2. Build the data flow diagram (DFD)
Identify the four DFD element types and lay out how data moves:

| Element | Symbol | Examples |
|---|---|---|
| **External entity** | square | end user, third-party API, browser, mobile app |
| **Process** | circle | web server, API service, lambda, worker |
| **Data store** | parallel lines | database, S3 bucket, cache, file system, secrets vault |
| **Data flow** | arrow | HTTP request, SQL query, message on a queue |
| **Trust boundary** | dashed line | network edge, process/container boundary, privilege change, tenant separation |

Render the DFD as a Mermaid `flowchart` (use subgraphs for trust boundaries) so it is viewable inline. Number every element (E1, P1, DS1, DF1...) — threats reference these IDs.

Trust boundaries are where threats concentrate. Draw a boundary wherever data crosses between principals at different trust levels (Internet→DMZ, app→DB, user-space→kernel, tenant A→tenant B).

### 3. Enumerate threats per element
Walk each element and apply the STRIDE-per-element matrix from `references/stride-catalog.md`:

| Element type | S | T | R | I | D | E |
|---|:-:|:-:|:-:|:-:|:-:|:-:|
| External entity | ✓ | | ✓ | | | |
| Process | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Data store | | ✓ | ✓* | ✓ | ✓ | |
| Data flow | | ✓ | | ✓ | ✓ | |

(* Data stores have repudiation relevance when they are logs/audit trails.)

For each applicable cell, ask the guiding question and write at least one concrete, system-specific threat — not a generic phrase. A good threat names the **threat agent**, the **element/asset**, the **action**, and the **impact**. Pull patterns from the catalog but specialize them to this system. Give each threat a stable ID (T-01, T-02...).

STRIDE prompts:
- **Spoofing** — Can an attacker pretend to be another user, service, or machine? (auth, identity)
- **Tampering** — Can data be modified in transit, at rest, or in memory? (integrity)
- **Repudiation** — Can someone deny an action with no proof? (logging, audit)
- **Information disclosure** — Can data leak to unauthorized parties? (confidentiality)
- **Denial of service** — Can the system be made unavailable or exhausted? (availability)
- **Elevation of privilege** — Can an attacker gain capabilities they should not have? (authorization)

### 4. Rate and prioritize
Score each threat using a rubric from `references/risk-rating.md`. Default to **Likelihood × Impact** (each 1–5) yielding a 1–25 risk score; use DREAD if the user prefers it. Sort descending. Bucket into Critical / High / Medium / Low. The top of the list is where mitigation effort goes first.

### 5. Define mitigations
For each non-trivial threat, choose a response and a concrete control:
- **Mitigate** — add a countermeasure (preferred). Map to a standard control from the catalog (e.g., MFA, parameterized queries, mTLS, rate limiting, RBAC checks, audit logging, encryption at rest).
- **Eliminate** — remove the feature/data that creates the risk.
- **Transfer** — shift to a third party (managed service, insurance) — note residual responsibility.
- **Accept** — document a conscious, signed-off acceptance of residual risk.

Each mitigation should be specific, testable, and assigned a status (Proposed / Planned / Implemented).

### 6. Assemble and validate
Fill in `templates/threat-model.md`. Then run the "Did we do a good enough job?" check: every DFD element covered, every trust boundary has authn/authz, high-risk threats all mitigated, and the model lists assumptions and out-of-scope items. Optionally feed the threat list to `scripts/threat_report.py` to generate the sorted risk register.

## Decision framework: how deep to go

- **Lightweight (single feature / PR):** quick DFD sketch, STRIDE only on new/changed elements and any new trust boundary. 30–60 min.
- **Standard (a service or API):** full DFD, STRIDE-per-element across all components, Likelihood×Impact rating. Half a day.
- **Deep (regulated / high-value / new product):** add abuse cases, attacker personas, DREAD scoring, and a verification plan (pen test scope, security tests).

## Worked mini-example

System: a public API that accepts a webhook and writes to a database.

- DFD: `E1 Caller → (DF1 HTTPS POST) → P1 Webhook Service → (DF2 SQL) → DS1 Postgres`. Trust boundary between E1 and P1 (Internet edge).
- Threat (T-01, Spoofing on DF1/P1): "An attacker forges webhook calls because the endpoint does not verify the sender → injected fraudulent records." Likelihood 4 × Impact 4 = 16 (High). Mitigation: verify HMAC signature with shared secret + timestamp anti-replay (Implemented).
- Threat (T-02, Tampering on DF2): "SQL injection via unvalidated payload field → arbitrary data read/write." L3×I5=15 (High). Mitigation: parameterized queries + input schema validation.
- Threat (T-03, DoS on P1): "Unbounded webhook volume exhausts DB connections." L4×I3=12 (Medium). Mitigation: rate limiting + queue + connection pool cap.

See `examples/url-shortener.md` for the full-length example.

## Best Practices

- **Specialize every threat.** "Tampering with the database" is useless; "an attacker with read-only DB creds escalates via a stored procedure to modify the `orders` table" is actionable.
- **Threat model early and iteratively.** Do it at design time and revisit when the architecture changes. It is cheapest before code exists.
- **Focus on trust boundaries.** Most real threats live where data crosses a boundary — prioritize those elements.
- **Cover the whole DFD.** Apply the per-element matrix mechanically so nothing is skipped; absence of a threat should be a deliberate, recorded decision.
- **Tie mitigations to known controls.** Reference OWASP ASVS / Top 10 and standard patterns rather than inventing bespoke defenses.
- **Record assumptions and out-of-scope items explicitly.** Unstated assumptions are how threats slip through.
- **Make it a living artifact.** Track mitigation status and re-rate residual risk after controls land.

## Common Pitfalls

- **DFD too coarse.** One giant "the app" process hides the boundaries where threats occur. Decompose to the level of distinct processes and stores.
- **Generic threats.** Copy-pasting the STRIDE list without specializing yields a checklist, not a threat model.
- **Skipping repudiation and DoS.** Teams over-index on injection/auth and forget audit logging and availability.
- **Rating without a rubric.** Gut-feel severity is inconsistent; use the tables in `references/risk-rating.md`.
- **Listing threats with no owner or status.** A threat model that does not drive tracked work is shelf-ware.
- **Confusing mitigations with wishes.** "Be more secure" is not a control; name the mechanism (HMAC, RBAC, TLS 1.3, rate limit) and how it is verified.
- **Treating the model as one-and-done.** Architecture drifts; an unmaintained model gives false confidence.
