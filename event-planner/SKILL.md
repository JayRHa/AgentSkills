---
name: event-planner
description: Plans events end-to-end — birthdays, weddings, dinner parties, offsites, conferences, fundraisers — with a budget breakdown, guest and venue logistics, a backward-planned timeline, vendor checklist, run-of-show, and contingency plans. Use this skill when a user asks to "help me plan a party / wedding / event", "organize an offsite or conference", "throw a dinner for X people", "make an event timeline / checklist", or wants a budget and run-of-show for a gathering.
license: MIT
---

# Event Planner

## Overview
This skill plans an event from concept to run-of-show: it sets the budget envelope, sizes the guest list and venue, builds a backward-planned timeline from the event date, assembles the vendor/task checklist, writes the day-of run-of-show, and bakes in contingencies (weather, no-shows, vendor failure).

**Keywords**: event planning, party, wedding, birthday, dinner party, offsite, conference, fundraiser, guest list, venue, catering, run of show, event timeline, vendor checklist, RSVP.

## When to use vs. not
Use this to plan and coordinate the *shape and logistics* of an event. It doesn't book vendors or guarantee live prices/availability — tell the user to confirm quotes, capacity, and contracts directly. For large/high-risk events (permits, alcohol licensing, crowd safety), flag that professional/licensed help and local regulations apply.

## Inputs to gather first
1. **Event type, purpose, and vibe** (formal/casual, the feeling you want).
2. **Date(s), or flexibility**, and **guest count** (and who).
3. **Total budget** and what it must cover.
4. **Location/region** (indoor/outdoor, home/venue) and any constraints.
5. **Must-haves** (specific food, accessibility, kids, dietary needs) and known risks (weather, travel).

## Workflow
1. **Lock the frame.** Confirm type, date, headcount, budget, and vibe in a few lines. These four — date, headcount, budget, venue — constrain everything else and should be decided first.
2. **Set the budget envelope.** Split the total across the big rocks (venue, food & drink, and for weddings/large events the catering+venue often eat 50%+). Reserve a **10–15% contingency**. See `references/budget-and-vendors.md`.
3. **Size venue to guest list.** Confirm capacity, layout, parking/transit, restrooms, A/V, and whether catering is in-house or external. Build a **backup venue/plan** for outdoor events.
4. **Build the guest + invite plan.** Headcount → invites with RSVP deadline → track responses → assume some no-show rate (and over-invite if a target headcount matters). Capture dietary/accessibility needs at RSVP.
5. **Backward-plan the timeline.** Work back from the event date to today with milestones (book venue → send invites → finalize menu → confirm vendors → final headcount → day-of). See `references/timeline.md`.
6. **Assemble the vendor/task checklist.** Catering, drinks, cake, décor, A/V, photography, music/entertainment, rentals, transport. For each: quote, deposit, confirmation date, point of contact.
7. **Write the run-of-show.** A minute-by-minute day-of schedule: setup, guest arrival, key moments (toasts, cake, speeches), meals, teardown — with an owner per block.
8. **Plan contingencies.** Weather backup, vendor no-show plan, extra food buffer, a day-of point person, and an emergency kit. Confirm everything 48–72 h before.

## Decision framework
| Event | Biggest budget lines | Lead time |
| --- | --- | --- |
| Dinner party (≤12) | Food, drinks | 1–3 weeks |
| Birthday (20–50) | Venue/space, food, cake, entertainment | 3–6 weeks |
| Wedding | Venue + catering (often 50%+), photography | 6–12 months |
| Corporate offsite | Venue, travel, catering, facilitation | 1–3 months |
| Conference / fundraiser | Venue, A/V, catering, speakers/permits | 3–9 months |

## Worked example
See `examples/30th-birthday.md` for a full plan: budget, timeline, run-of-show, and contingencies for a 40-person birthday.

## Best Practices
- **Decide date, headcount, budget, venue first** — everything else flows from them.
- **Backward-plan** from the event date so nothing is left to the last week.
- **Always keep a 10–15% contingency** and a weather/Plan-B.
- **Confirm vendors 48–72 h out** and reconfirm headcount.
- **Assign a day-of point person** (not the host) so the host can enjoy it.
- **Capture dietary/accessibility needs** at RSVP, not on the day.

## Common Pitfalls
- **Underbudgeting** — taxes, tips, service fees, and rentals add up fast.
- **No contingency** for weather, no-shows, or a vendor cancelling.
- **Inviting to capacity** with no no-show buffer (or over-inviting and overflowing).
- **Leaving setup/teardown unplanned** — they always take longer than expected.
- **The host running the event** instead of delegating day-of.
- **Forgetting logistics:** parking, restrooms, power, accessibility, timing of food.
