# Worked Example: Transcript → Summary

This example shows messy input and the polished summary produced by the skill.

## Input (raw transcript snippet)

```
[09:02] Maria: ok morning everyone, can you all hear me? cool.
[09:02] Maria: so quick standup. Dev, where are we on the checkout bug?
[09:03] Dev: yeah so the double-charge thing — I found it, it's a retry loop in the
        payment client. I'll have the fix in a PR by tomorrow EOD.
[09:04] Maria: nice. is that the same one finance flagged last week?
[09:04] Dev: yep same one. 3 customers affected, all refunded already.
[09:05] Priya: on my side the new onboarding email is drafted but I'm blocked —
        I need legal to sign off on the disclaimer copy.
[09:06] Maria: ok let's agree we don't ship onboarding until legal approves. I'll
        ping legal today and ask for a turnaround by Thursday.
[09:07] Priya: works. also should we A/B test the subject line? not sure.
[09:07] Maria: let's park that for now. decision: launch with one subject line,
        revisit A/B next sprint.
[09:08] Dev: oh and we're moving the deploy window to Tuesday 2pm instead of Monday,
        everyone good with that? ... ok agreed.
[09:09] Maria: great, that's it. thanks all.
```

## Output (summary produced)

```markdown
# Daily Standup — Summary

> Date: not stated | Attendees: Maria, Dev, Priya

## TLDR
Dev located the checkout double-charge bug (a payment-client retry loop) and will
open a fix PR by tomorrow EOD; all 3 affected customers are already refunded.
Onboarding email launch is gated on legal approval of the disclaimer copy.

## Decisions
- Onboarding email will not ship until legal approves the disclaimer copy.
- Launch onboarding with a single subject line; revisit A/B testing next sprint.
- Move the deploy window to Tuesday 2pm (was Monday).

## Action Items

| # | Action | Owner | Due |
|---|--------|-------|-----|
| 1 | Open a PR fixing the payment-client retry loop (double-charge bug) | Dev | Tomorrow EOD |
| 2 | Ping legal to review the onboarding disclaimer copy | Maria | Requesting turnaround by Thursday |

## Discussion Highlights
- Double-charge bug is the same issue finance flagged last week; 3 customers affected, all already refunded.

## Open Questions / Risks
- Legal sign-off on disclaimer copy is a blocker for the onboarding email launch.
```

## Why this output is correct

- The greeting and "can you hear me?" filler were dropped.
- The "park A/B for now" became a **decision** (revisit next sprint), not an open question, because Maria settled it.
- The deploy-window change is a decision even though it arrived as an offhand "everyone good?" → "agreed".
- Every action item has an owner and a due field; the relative date "tomorrow EOD" was kept verbatim because no absolute meeting date was given.
- The refund fact stayed a discussion highlight (context), not an action (no future work).
