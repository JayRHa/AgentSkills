---
name: trip-planner
description: Builds realistic, day-by-day travel itineraries that balance logistics, budget, pacing, and local highlights, with hour-level day plans, transit links, cost estimates, and contingency buffers. Use this skill when a user asks to "plan a trip", "build an itinerary", "plan X days in <city/country>", "what should I do in <destination>", "make a travel schedule", "plan a road trip / honeymoon / family vacation", or wants help sequencing activities, allocating a travel budget, or pacing days to avoid burnout.
license: MIT
---

# Trip Planner

## Overview
This skill turns a loose travel idea ("5 days in Tokyo, mid budget, love food and temples") into a concrete, day-by-day itinerary that is actually executable on the ground. It optimizes four competing dimensions at once:

- **Logistics** — geographic clustering, transit time, opening hours, reservations, jet lag.
- **Budget** — flights, lodging, food, activities, local transport, and a buffer.
- **Pacing** — anchors per day, rest, and travel-day recovery so the trip is enjoyable, not exhausting.
- **Highlights** — the destination's signature experiences matched to the traveler's stated interests.

Keywords: trip, travel, itinerary, vacation, holiday, road trip, day plan, sightseeing, budget travel, packing, honeymoon, family travel, city break, backpacking.

## When to use vs. not
Use this for planning the *shape* of a trip: which days, which areas, what order, rough costs. This skill does not book anything or guarantee live prices/hours — always tell the user to verify hours, prices, and reservations against official sources near the travel date.

## Inputs to gather first
Before planning, collect (ask only for what's missing — infer sensible defaults for the rest):

1. **Destination(s)** and whether it's single-base or multi-city/road trip.
2. **Dates or duration** (and travel season — drives weather, crowds, prices).
3. **Number of travelers** and group type (solo, couple, family with kids' ages, friends, accessibility needs).
4. **Total budget** and currency, plus what it includes (flights? lodging? just on-the-ground?).
5. **Interests** (food, history, nature, nightlife, art, beaches, shopping, adventure).
6. **Pace preference** (packed / balanced / relaxed) and any energy constraints.
7. **Home origin** (for flight time/cost and jet lag) and **dietary/mobility constraints**.

If the user gives a one-liner, restate your assumptions in one short block and proceed — don't block on a full interview.

## Workflow
Follow these steps in order. Each produces a visible artifact for the user.

1. **Confirm the frame.** Echo destination, dates/duration, party, budget, interests, and pace in 4–6 lines. State assumptions explicitly.
2. **Set the budget envelope.** Use the category split heuristics in `references/budgeting.md` to break the total into Transport / Lodging / Food / Activities / Local transit / Buffer. Flag if the budget is tight, comfortable, or generous for the destination and season.
3. **Choose the base(s).** For single-city, pick a neighborhood to stay in (central, well-connected, matches vibe). For multi-city/road trips, decide the route and how many nights per stop using the "minimum-nights" rule in `references/pacing.md` (avoid 1-night stops unless en route).
4. **Build the highlight pool.** List 8–15 candidate experiences ranked by fit to the stated interests. Tag each with area, approx. duration, cost tier ($/$$/$$$), and best time of day. Note anything that needs advance booking.
5. **Cluster by geography.** Group highlights into 2–4 geographic zones so each day stays in one area and minimizes backtracking. This is the single biggest lever for a good itinerary.
6. **Sequence the days.** Assign zones to days. Apply pacing rules: arrival/departure days are light, one major anchor + one or two minor stops per day, build in a flex/rest block. Put weather-dependent things on flexible days and reservation-locked things on fixed days.
7. **Write each day in detail.** Use `templates/itinerary-day.md`. Include rough times, transit between stops (mode + minutes), a meal plan that fits the zone, and a per-day cost estimate. Add a "rainy day swap" alternative.
8. **Add the connective tissue.** Airport/station transfers, a SIM/eSIM + payment note, opening-hour and reservation callouts, and one or two contingency buffers.
9. **Tally and reconcile.** Sum estimated costs against the envelope from step 2. If over, propose specific trade-downs (lodging tier, fewer paid attractions, free alternatives). Run `scripts/budget_calc.py` to do the math and produce a clean table.
10. **Deliver + caveat.** Present the full itinerary, the budget table, a short packing pointer (`references/packing.md`), and remind the user to verify live hours/prices/bookings.

## Decision frameworks

**Pace dial (anchors per day):**
- Relaxed: 1 anchor + 1 optional, long meals, downtime.
- Balanced: 1 anchor + 2 minor stops.
- Packed: 2 anchors + 2 minor — only sustainable for short trips or high-energy travelers.

**The "is this day realistic?" check:** Sum activity durations + transit + meals. If it exceeds ~10 waking hours or has 3+ cross-city transits, cut something.

**Budget triage when over:** lodging tier → paid attractions → dining tier → trip length. Adjust in that order; protect the signature experiences the trip is *for*.

**Multi-city minimum nights:** 1 night = "touch and go" (only if directly en route); 2 nights = a taste; 3+ = actually experience it. See `references/pacing.md`.

See `references/budgeting.md` for cost splits and regional day-rate ranges, `references/pacing.md` for sequencing and jet-lag rules, and `references/packing.md` for a season/activity-driven packing checklist.

## Worked example
See `examples/tokyo-5day.md` for a complete five-day Tokyo itinerary built from a one-line prompt, including the budget reconciliation.

## Best Practices
- **One zone per day.** Cluster geographically before you sequence by time.
- **Light bookends.** Arrival and departure days carry travel fatigue — plan them at half capacity.
- **Lock the unmovable first.** Timed-entry tickets, restaurant reservations, and day tours anchor the calendar; build everything else around them.
- **Always leave a buffer** — both money (10–15%) and time (a free afternoon or flex block).
- **Match meals to location.** Don't send the traveler across town for lunch; eat where they already are.
- **Name specific places, not categories.** "Sensō-ji at 8am before crowds" beats "visit a temple."
- **Give alternatives.** A rainy-day swap and a budget swap per day make the plan resilient.

## Common Pitfalls
- **Overpacking days** — the #1 mistake; tourists routinely plan 30% more than they can do.
- **Ignoring transit time** between attractions, especially in large or spread-out cities.
- **Forgetting opening days/hours** — many museums close Mondays; markets are morning-only.
- **Treating travel days as full days** — they rarely are.
- **Burying the signature experience** on the last day where weather/delays can kill it.
- **Quoting prices/hours as fact** — they drift; always tag estimates and tell the user to verify.
- **No budget buffer** — unexpected costs (taxis, tips, a splurge meal) always appear.
