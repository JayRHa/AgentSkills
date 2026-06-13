---
name: gift-advisor
description: Recommends thoughtful, personalized gift ideas for any recipient and occasion — by profiling interests, relationship, budget, and occasion, then generating ranked, specific suggestions with reasoning, price tiers, and backup options. Use this skill when a user asks "what should I get X", "gift ideas for my mom/partner/coworker", "birthday/anniversary/holiday present", "I don't know what to buy", or wants help choosing a present within a budget.
license: MIT
---

# Gift Advisor

## Overview
This skill generates thoughtful, specific gift recommendations matched to a particular person and occasion — not generic "scarf or gift card" lists. It profiles the recipient, applies gifting principles (thoughtfulness over price, experiences over clutter, match the relationship), and returns ranked ideas with reasoning, price tiers, and safe fallbacks.

**Keywords**: gift ideas, present, birthday gift, anniversary, holiday gift, Christmas, what to buy, gift for him/her, secret santa, housewarming, wedding gift, thoughtful gift.

## When to use vs. not
Use this to brainstorm and narrow gift choices for any recipient/occasion/budget. It can't see live stock or prices — tell the user to confirm availability and current price. For high-value or very personal purchases (jewelry, tech), suggest verifying preferences/sizes/returns.

## Inputs to gather first
1. **Who** — relationship to the user, age, gender if relevant.
2. **Occasion** and how much it "should" signal (a coworker's farewell ≠ a 10th anniversary).
3. **Budget** (and currency).
4. **Interests, hobbies, recent life events**, and things they've mentioned wanting.
5. **Constraints** — allergies, space, dislikes, what they already own, delivery deadline.

## Workflow
1. **Profile the recipient.** Pull out concrete signals: hobbies, current obsessions, pain points (what annoys them daily — solving it is a great gift), aspirations, recent milestones. The more specific the input, the better the gift.
2. **Calibrate to the relationship + occasion.** Match intimacy and price to the bond — a sentimental gift is wonderful from a partner, odd from a new colleague. See `references/gift-principles.md`.
3. **Generate across categories.** Brainstorm widely first: experiences, hobby upgrades, consumables/luxuries they won't buy themselves, sentimental/personalized, practical-but-delightful, and "solve a daily annoyance." See `references/idea-categories.md`.
4. **Rank and justify.** Pick the top 3–5, each with a one-line *why it fits this person*, a price tier, and where it lands on the safe↔bold spectrum.
5. **Add a fallback + a presentation idea.** Always include one low-risk option and a tip on wrapping/timing/a handwritten note (the note often matters more than the object).
6. **Sanity-check.** Within budget? Available in time? Avoids known dislikes/allergies/duplicates? Appropriate for the relationship?

## Decision framework
| Relationship | Lean toward | Avoid |
| --- | --- | --- |
| Partner/spouse | Sentimental, experiences together, something they hinted at | Appliances "for the house," anything that implies criticism |
| Parent | Experiences, quality upgrade of something they use, photos/memories | Generic gift cards if you know them well |
| Friend | Shared interest, inside jokes, hobby gear | Over-expensive (creates obligation) |
| Coworker / Secret Santa | Consumables, desk items, fun & neutral, modest budget | Anything personal, pricey, or inside-only |
| Kids | Age-appropriate, creative/active, parent-approved | Noisy/messy without checking parents |

## Worked example
See `examples/gift-for-dad.md` for a profile-to-ranked-ideas walkthrough.

## Best Practices
- **Thoughtfulness beats price.** A $20 gift that shows you listened beats a generic $200 one.
- **Solve a daily annoyance** or upgrade something they use constantly — always lands.
- **Experiences and consumables** reduce clutter and are remembered longer.
- **Listen for hints** in what they've mentioned wanting.
- **Match the relationship** — calibrate intimacy and price.
- **The note matters.** A handwritten card elevates almost any gift.

## Common Pitfalls
- **Generic defaults** (mug, candle, gift card) when you actually know the person.
- **Gifting your own taste** rather than theirs.
- **Mismatched intimacy** — too personal/expensive for the relationship.
- **Ignoring stated dislikes, allergies, or what they already own.**
- **Practical gifts that read as criticism** (diet books, cleaning gadgets) unless explicitly wanted.
- **Forgetting the deadline** — the perfect gift that arrives late isn't.
