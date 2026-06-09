# Risk Rating Rubrics

Consistent scoring lets you prioritize mitigation effort objectively. Pick ONE model per engagement and apply it to every threat.

## Model A (default): Likelihood × Impact

Score Likelihood and Impact each on 1–5, multiply for a 1–25 risk score.

### Likelihood (how plausible is exploitation?)

| Score | Label | Guidance |
|:-:|---|---|
| 1 | Rare | Requires deep insider access or implausible conditions. |
| 2 | Unlikely | Skilled attacker, significant effort, multiple preconditions. |
| 3 | Possible | Moderate skill; known technique; some preconditions. |
| 4 | Likely | Common technique, low effort, exposed surface, tooling exists. |
| 5 | Almost certain | Trivial, unauthenticated, publicly exposed, actively exploited. |

Consider: attacker skill required, authentication needed, public exposure, availability of exploits, existing partial controls.

### Impact (how bad is the outcome?)

| Score | Label | Guidance |
|:-:|---|---|
| 1 | Negligible | Minor, no sensitive data, easily reversible. |
| 2 | Minor | Limited data, single user, contained. |
| 3 | Moderate | Notable data exposure or partial outage; recoverable. |
| 4 | Major | Sensitive/PII breach, broad outage, financial loss. |
| 5 | Severe | Full compromise, mass PII/regulated data, safety, existential. |

Consider: confidentiality/integrity/availability damage, number of affected users, regulatory/legal exposure, financial and reputational cost, recoverability.

### Risk score → priority bucket

| Score range | Bucket | Action |
|---|---|---|
| 20–25 | Critical | Fix before release; block ship. |
| 12–19 | High | Fix this iteration; needs sign-off to defer. |
| 6–11 | Medium | Plan and schedule; track. |
| 1–5 | Low | Accept or fix opportunistically; document. |

## Model B: DREAD

Score five dimensions 1–10 (or 1–3 for a coarser scale), average for a 1–10 risk score.

| Dimension | Question |
|---|---|
| **D**amage | How bad if the attack succeeds? |
| **R**eproducibility | How reliably can it be reproduced? |
| **E**xploitability | How much effort/skill to launch? |
| **A**ffected users | What share of users are impacted? |
| **D**iscoverability | How easily can an attacker find it? |

DREAD = (Damage + Reproducibility + Exploitability + Affected + Discoverability) / 5.

Buckets (1–10 scale): 8–10 Critical, 6–7.9 High, 4–5.9 Medium, <4 Low. DREAD is more subjective than Likelihood×Impact; reserve it for deep engagements and have two reviewers score independently to reduce bias.

## Residual risk

After a mitigation is implemented, re-rate the threat. Record both the inherent (pre-mitigation) and residual (post-mitigation) scores so the model shows risk reduction. A mitigation that does not move the score is the wrong control.

## Prioritization tie-breakers

When two threats share a score, rank higher the one that: is reachable without authentication; affects more users/tenants; touches regulated data; has a known public exploit; or is cheap to fix (quick wins clear the board).

## Worked scoring

> Threat: "Unauthenticated SQL injection in the public search endpoint allows full DB read."
> Likelihood = 5 (public, unauthenticated, trivial with tooling). Impact = 5 (full PII DB read). Risk = 25 → Critical → block ship. Mitigation: parameterized queries + WAF. Residual: Likelihood 1 × Impact 5 = 5 → Low.
