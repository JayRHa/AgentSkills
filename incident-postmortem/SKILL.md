---
name: incident-postmortem
description: Facilitates blameless incident postmortems by reconstructing a precise timeline, identifying root cause and contributing factors, and producing tracked, owned action items. Use this skill when an incident, outage, SEV, or production failure has been resolved and someone needs to "write the postmortem", "do a retro on the outage", "run a blameless RCA", "fill out the incident report", "find the root cause", or "track follow-up action items" after a service disruption.
license: MIT
---

# Incident Postmortem

## Overview

Keywords: postmortem, post-mortem, RCA, root cause analysis, blameless, incident review, outage retro, SEV1, SEV2, contributing factors, action items, five whys, timeline, MTTR, COE, incident report, learning review.

This skill turns a resolved incident into a durable learning artifact. It enforces a **blameless** stance (focus on systems and conditions, never individuals), drives toward **systemic root causes** (not just the proximate trigger), and converts findings into **specific, owned, dated action items** with verification. The output is a single postmortem document plus a list of trackable follow-ups.

A good postmortem answers five questions: What happened? What was the impact? Why did it happen? How was it detected and resolved? How do we prevent recurrence (and reduce time-to-detect/time-to-resolve next time)?

Use `templates/postmortem.md` as the document skeleton, `references/root-cause-techniques.md` for the analysis methods, `references/blameless-language.md` to rewrite blame into systems language, and `scripts/timeline_builder.py` to assemble a clean timeline and compute incident metrics.

## Workflow

1. **Gather the raw record.** Collect the incident channel/war-room transcript, alert timestamps, deploy and config-change logs, dashboards/graphs, the first customer report, and the resolution moment. Note the SEV/severity level and the systems affected. Do not start writing prose yet — collect facts.

2. **Build the timeline.** Convert every relevant event into a `timestamp | actor/system | event` row. Use UTC and ISO-8601. Run `scripts/timeline_builder.py` to sort events, normalize timestamps, and auto-derive the key metrics (time-to-detect, time-to-mitigate, time-to-resolve, total duration). The timeline is the spine of the document — get it right before reasoning about causes.

3. **Establish impact.** Quantify in user/business terms: affected users or %, requests failed, revenue/SLA/error-budget burned, duration of degradation. Vague impact ("some users affected") undermines prioritization — push for numbers or explicit estimates with their basis.

4. **Find root cause and contributing factors.** Distinguish the **trigger** (what kicked it off) from the **root cause** (the systemic condition that allowed a trigger to cause an outage). Apply the techniques in `references/root-cause-techniques.md` — Five Whys to reach systemic depth, then a contributing-factors sweep (detection gaps, response friction, latent risks). Most real incidents have **multiple** contributing factors; resist the single-cause trap.

5. **Analyze detection and response.** Separately critique: How long until *anyone* knew? Was it auto-detected or customer-reported? What slowed mitigation? What worked well (capture this — postmortems are not only about failures)?

6. **Write action items.** For each root cause and significant contributing factor, write at least one action item. Every action item MUST have an owner (a person), a due date, a priority, and a type (prevent / detect-faster / mitigate-faster / process). Use the checklist in `references/action-item-checklist.md`. Convert "be more careful" into concrete engineering or process changes.

7. **Apply blameless language.** Review the whole document against `references/blameless-language.md`. Replace names-as-causes ("Alice deployed bad code") with system framing ("a deploy passed CI but lacked a canary stage that would have caught the regression"). Remove "should have", "failed to", "human error" as terminal explanations — each is a prompt for a deeper Why.

8. **Review and circulate.** Hold a blameless review meeting. Confirm the timeline with participants, validate action-item owners agreed, and assign a tracking mechanism (ticket per action item). Mark the postmortem state: Draft → In Review → Final.

## Trigger vs. Root Cause (worked distinction)

- **Symptom:** API 500 error rate spiked to 40%.
- **Trigger:** A deploy at 14:02 UTC shipped a query missing an index hint.
- **Proximate cause:** The unindexed query caused DB CPU saturation under production load.
- **Root cause(s) (systemic):** (a) CI ran no representative-load query analysis, so the regression was invisible pre-prod; (b) there was no automatic deploy rollback on error-rate breach.
- **Contributing factors:** alerting fired 8 minutes late because the threshold was tuned for a previous traffic baseline; the on-call runbook had no DB-saturation playbook.

Note how the root causes point at *missing safeguards*, not at the engineer who wrote the query. That is the blameless reframe in action.

## Severity quick reference

| SEV | Meaning | Postmortem required? | Review timing |
|-----|---------|----------------------|---------------|
| SEV1 | Full/critical outage, major data loss, security breach | Always | Within 3 business days |
| SEV2 | Major feature down, significant degradation | Always | Within 5 business days |
| SEV3 | Minor degradation, workaround exists | Recommended | Optional / lightweight |
| SEV4 | Low impact, near-miss | Optional (capture near-misses!) | Lightweight |

## Best Practices

- **Blameless by construction.** Assume everyone acted reasonably given the information, incentives, and tools they had at the time. The question is never "who?", always "what conditions made this outcome likely?".
- **Timeline first, narrative second.** Reasoning about causes before the facts are pinned leads to confabulation. Lock the timeline, then interpret.
- **Drive to systemic depth.** Stop the Five Whys only when the answer is a fixable property of a system or process, not a person's intent.
- **Quantify impact and timing.** "Detected in 8 min, mitigated in 22 min, resolved in 51 min" is actionable; "took a while" is not. Use the computed metrics from the script.
- **Multiple contributing factors are the norm.** Use the contributing-factors sweep so you don't stop at the first plausible cause.
- **Action items must be SMART and owned.** No action item without a named owner and a date. Track each as a real ticket; an untracked action item is a wish.
- **Capture what went well.** Reinforce the detection, tooling, and decisions that helped — so they survive the next reorg.
- **Record near-misses.** Incidents that almost happened are free lessons; give them a lightweight postmortem.

## Common Pitfalls

- **Single-root-cause tunnel vision.** Declaring the trigger as "the" cause and stopping. Real incidents are usually a chain plus latent conditions — do the full sweep.
- **Blame disguised as analysis.** "Insufficient testing by the team" or "human error" are blame, not root causes. Ask why the system allowed the error to reach production.
- **Action items that aren't actionable.** "Be more careful", "improve communication", "add more monitoring" (which monitoring? alerting on what threshold?). Make them concrete, owned, and dated.
- **No owner / no date / no tracking.** Action items decay into nothing. Each needs one accountable person and a ticket.
- **Skipping detection/response analysis.** Even with a fixed root cause, slow detection or messy response are independent improvement areas — analyze them separately.
- **Hindsight bias.** "It was obvious the deploy would break things." It was not obvious at the time; reconstruct the information available *then*, not now.
- **Letting the document languish in Draft.** A postmortem nobody reviews changes nothing. Schedule the blameless review and close it to Final.