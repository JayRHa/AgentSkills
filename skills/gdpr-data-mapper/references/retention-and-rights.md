# Retention & Data Subject Rights

## Retention

Every data category needs a **period** and a **trigger**, never "indefinite".

| Pattern | Example |
| --- | --- |
| Event + duration | "Until account closure + 30 days" |
| Legal minimum | "Invoices: 10 years (tax law)" |
| Rolling window | "Server logs: 90 days, then purged" |
| Until withdrawal | "Marketing data: until unsubscribe" |

Checklist:
- [ ] Period defined per category (not per system)
- [ ] Concrete deletion trigger
- [ ] Backups covered (deletion or documented exception with end date)
- [ ] Automated deletion job where possible

## Data Subject Rights (Chapter 3)

For each activity, document how you'd fulfill each right and any blockers.

| Right | Article | What you must be able to do |
| --- | --- | --- |
| Information | 13–14 | Tell people what you collect and why (privacy notice) |
| Access (DSAR) | 15 | Provide a copy of their data + processing details, usually within 1 month |
| Rectification | 16 | Correct inaccurate data |
| Erasure ("right to be forgotten") | 17 | Delete when basis ends, consent withdrawn, etc. (with exceptions) |
| Restriction | 18 | Pause processing while a dispute is resolved |
| Portability | 20 | Export consent/contract-based data in a machine-readable format |
| Objection | 21 | Stop processing based on legitimate interest / direct marketing |
| Automated decisions | 22 | Offer human review of solely-automated decisions with legal effect |

## DSAR readiness questions
- Can you locate **all** copies of a person's data (incl. analytics, CRM, backups, third parties)?
- Can you export it within one month?
- Can you erase it without breaking referential integrity or legal-retention duties?

If the answer to any is "no", that's a gap to record.
