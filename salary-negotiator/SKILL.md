---
name: salary-negotiator
description: Coaches a candidate or employee through compensation negotiation — researching market ranges, anchoring, countering an offer, negotiating the full package (base, bonus, equity, signing, benefits), and scripting the conversation. Use this skill when a user asks to "negotiate my salary", "I got a job offer, what do I say", "counter this offer", "ask for a raise", "how much should I ask for", or wants email/script wording for a comp conversation.
license: MIT
---

# Salary Negotiator

## Overview
This skill helps a user negotiate compensation with confidence and tact — whether it's a new job offer or an internal raise. It covers market research, what's actually negotiable, anchoring, counter-offer math, and word-for-word scripts that stay collaborative rather than adversarial.

**Keywords**: salary negotiation, compensation, job offer, counter offer, raise, equity, RSU, signing bonus, total comp, benefits, anchoring, BATNA, ask for more money.

## When to use vs. not
Use this when a user has (or is about to get) an offer, wants a raise, or needs scripting for a comp conversation. This skill gives strategy and wording, not live market data — always tell the user to verify ranges against current sources (levels.fyi, Glassdoor, Payscale, Levels, local salary surveys) for their role, level, and location near the conversation date.

## Inputs to gather first
1. **The full current offer / current comp** — base, bonus, equity, signing, benefits, not just base.
2. **Role, level, location** (remote vs. on-site changes the market).
3. **The user's target and walk-away** numbers, and their **BATNA** (other offers, staying put).
4. **Leverage**: competing offers, in-demand skills, internal value, how badly they need this job.
5. **Stage**: verbal offer, written offer, or annual review.

## Workflow
1. **Establish the market range.** Have the user pull comparables for their exact role/level/location. Define a defensible range; place the *target* near the top third. See `references/market-research.md`.
2. **Map the full package.** List every negotiable lever — base, annual bonus %, equity/RSUs, signing bonus, start date, vacation, remote, title, review timing. Base isn't the only knob. See `references/levers.md`.
3. **Know your BATNA and walk-away.** The strongest negotiator is willing to walk. Define the alternative and the lowest acceptable total comp before talking.
4. **Never name the first number if you can avoid it.** If asked expectations, deflect to "what's the range for this role?" If forced, anchor with a researched range whose bottom is your real target.
5. **Get the offer in writing**, then express genuine enthusiasm *and* a counter: "I'm excited about this — I was hoping we could get the base closer to $X." Anchor high but defensible.
6. **Counter on the strongest lever first**, with a reason (market data, competing offer, scope). Bundle 2–3 asks so there's room to concede gracefully. See `references/scripts.md`.
7. **Negotiate collaboratively.** Use "we" framing, silence after the ask, and trade — if base won't move, pivot to signing bonus, equity, or an early review.
8. **Get the final deal in writing** before resigning anything. Confirm every component.

## Decision framework
| If… | Then… |
| --- | --- |
| You have a competing offer | Lead with it (honestly) — it's the strongest lever |
| Base is capped by band | Pivot to signing bonus, equity, title, or a 6-month review |
| You're underpaid internally | Use market data + documented impact; request a specific number |
| Offer already meets target | Make one modest ask; don't over-negotiate a great offer |
| They say "this is final" | Test once politely; then decide against your walk-away, not your ego |

## Worked example
See `examples/counter-offer.md` for a full counter-email and the reasoning behind each ask.

## Best Practices
- **Always negotiate** a job offer — most have built-in room, and not asking leaves money on the table.
- **Anchor with research, not feelings.** Tie every number to market data or scope.
- **Negotiate total comp**, not just base.
- **Stay warm and collaborative** — you'll work with these people.
- **Use silence.** After you state a number, stop talking.
- **Get everything in writing** before resigning.

## Common Pitfalls
- **Accepting on the spot** out of excitement or fear.
- **Disclosing your current salary or target first** when you don't have to.
- **Negotiating against yourself** by lowering your ask before they respond.
- **Threatening or ultimatums** ("match this or I walk") unless you mean it.
- **Forgetting non-base levers** (equity, signing, remote, vacation).
- **Burning goodwill** with an aggressive or entitled tone.
