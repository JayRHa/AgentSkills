# Blameless Language Guide

Blameless postmortems get the truth. The moment people fear being named as the cause, the timeline gets sanitized and the real conditions stay hidden. Reframe every blame statement into a systems statement.

## Core principle

> Assume every person acted reasonably given the information, tools, time pressure, and incentives they had **at the moment** — not with the hindsight you have now.

If an action looks "wrong", the postmortem question is: *what made that action look reasonable at the time, and what system would have made the better action easier or automatic?*

## Words and phrases to eliminate

| Avoid (blame) | Why it's a problem | Reframe (systems) |
|---------------|--------------------|--------------------|
| "Alice deployed bad code" | Names a person as the cause | "A deploy passed CI but lacked a canary stage that would have caught the regression" |
| "human error" | A label, not an explanation; ends inquiry | "The UI allowed a destructive action without confirmation, making the mistake easy to make" |
| "should have known / should have tested" | Hindsight bias; implies negligence | "The runbook did not cover this scenario, so responders had to improvise" |
| "failed to follow the process" | Blames the person, not the process | "The process required a manual step that is easy to skip and was not enforced by tooling" |
| "someone forgot to..." | Memory is not a control | "The step relied on memory rather than an automated check" |
| "the on-call was slow" | Blames the responder | "The alert routed to a pager that was 40 minutes from acknowledgement; escalation was not configured" |
| "careless / negligent" | Pure judgment | (delete; describe the missing safeguard instead) |

## The reframe move

1. Find the sentence that assigns fault to a person.
2. Ask: *what would have had to be true (in the system) for this outcome to be unlikely regardless of who was at the keyboard?*
3. Write that as the cause.

### Before / after

**Before:** "Bob ignored the alert and the outage got worse."

**After:** "The first alert was one of ~30 low-priority pages that night, so the high-priority signal was not distinguishable. Alert fatigue from noisy thresholds delayed acknowledgement by ~18 minutes."

The after version is both kinder *and* more useful: it produces an action item (fix alert noise / severity tiering) instead of a grudge.

## In the review meeting

- The incident commander states the blameless stance out loud at the start.
- Use "we" and "the system", not "you".
- When someone says "that was my fault", redirect: "Let's find what made that the easy/likely thing to do."
- Thank people who surface mistakes — they are giving the org free safety data.

## Litmus test before publishing

Read each cause and action item. If any could be read as "this happened because person X is bad at their job", rewrite it. Causes should be fixable by changing systems, tooling, or process — not by changing who was on shift.
