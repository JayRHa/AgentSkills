---
name: gdpr-data-mapper
description: Maps how personal data flows through a system and produces GDPR artifacts — a Record of Processing Activities (RoPA), lawful-basis analysis, retention schedule, and data-subject-rights readiness — for each processing activity. Use this skill when the user asks to "map our data", "create a RoPA / Article 30 record", "do a GDPR data mapping", "figure out our lawful basis", "build a retention schedule", "prepare for a DSAR / data subject request", or assess privacy/personal-data handling. Not legal advice — produces a structured draft for review by counsel/DPO.
license: MIT
---

# GDPR Data Mapper

## Overview

Produce a clear, auditable map of personal-data processing and the core GDPR artifacts that depend on it. Output is a structured draft to be reviewed by a DPO or counsel — **this skill does not give legal advice**.

Keywords: GDPR, data mapping, RoPA, Article 30, record of processing, lawful basis, consent, legitimate interest, retention schedule, data subject rights, DSAR, data minimization, special category data, processor, controller, cross-border transfer, DPIA.

## Workflow

1. **Inventory processing activities.** List each distinct purpose for which personal data is used (e.g. "account management", "marketing emails", "fraud detection"). One activity per purpose.
2. **For each activity, capture the RoPA fields** (see `templates/ropa-template.md`): controller/processor role, purpose, data categories, data subjects, recipients, retention, transfers, and security measures.
3. **Classify the data.** Flag **special category** data (health, biometrics, religion, etc., Art. 9) and children's data — these need stronger justification. Apply data minimization: challenge every field ("why do we hold this?").
4. **Determine the lawful basis** for each activity using the decision guide in `references/lawful-basis-guide.md`. Exactly one of the six bases per purpose; document the reasoning. For legitimate interest, note that a balancing test (LIA) is required.
5. **Set retention.** Define a concrete retention period and trigger per data category (see `references/retention-and-rights.md`). "Indefinite" is not acceptable.
6. **Map data-subject rights readiness.** For each activity, note how access, erasure, rectification, portability, restriction, and objection would be fulfilled — and any blockers (e.g. data in backups, third parties).
7. **Flag transfers and DPIA triggers.** Note any transfers outside the EEA (and the safeguard: adequacy decision, SCCs) and whether the activity likely needs a DPIA (large-scale, special category, systematic monitoring).
8. **Summarize risks and gaps** — missing basis, over-retention, undocumented processors, no DSAR path.

## Decision Aids

| Question | Where |
| --- | --- |
| Which lawful basis applies? | `references/lawful-basis-guide.md` |
| How long can we keep this? | `references/retention-and-rights.md` |
| What goes in the record? | `templates/ropa-template.md` |
| Does this need a DPIA? | Large-scale + (special category OR systematic monitoring OR new tech) → likely yes |

## Worked Example (one activity)

| Field | Value |
| --- | --- |
| Activity | Marketing newsletter |
| Role | Controller |
| Purpose | Send product updates to subscribers |
| Data categories | Name, email, open/click events |
| Data subjects | Newsletter subscribers |
| Lawful basis | **Consent** (Art. 6(1)(a)) — opt-in checkbox, logged |
| Recipients | Email service provider (processor, DPA signed) |
| Retention | Until unsubscribe + 30 days, then deleted |
| Transfers | ESP in US — SCCs in place |
| Rights | Unsubscribe link (objection); export on request (portability) |

## Best Practices

- **One purpose = one activity.** Don't lump unrelated processing together.
- **Minimize first.** The cheapest compliance is data you never collected.
- **Exactly one lawful basis per purpose**, documented — you can't switch later to dodge a request.
- **Concrete retention periods with triggers**, never "as long as needed".
- **Treat backups and third parties** explicitly in rights fulfillment.
- **Keep the RoPA living** — update it when a new tool or purpose appears.

## Common Pitfalls

- Using **consent** when you can't truly offer a free choice (use another basis).
- Treating **legitimate interest** as a catch-all without a balancing test.
- Forgetting **processors** (analytics, email, CRM) in the recipients list.
- **Indefinite retention** or no deletion trigger.
- Missing **special category** flags, which demand an Art. 9 condition on top of the Art. 6 basis.
- No documented path for **erasure/portability**, discovered only when a DSAR arrives.

> This is a drafting aid, not legal advice. Have a DPO or qualified counsel review the output.
