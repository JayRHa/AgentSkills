---
name: meal-plan-builder
description: Builds balanced weekly meal plans with calculated macros, calorie targets, ingredient variety, batch-prep steps, and a consolidated grocery list organized by store aisle. Use this skill when a user asks to "plan my meals", "make a meal plan", "weekly menu", "what should I eat this week", "meal prep plan", "create a grocery list from meals", "plan meals for X calories/macros", or wants help with budgeting, dietary restrictions (vegan, keto, gluten-free, halal, etc.), family meal planning, or reducing food waste.
license: MIT
---

# Meal Plan Builder

## Overview
Produce a complete, realistic weekly meal plan that hits the user's calorie and macro targets, respects their dietary restrictions and budget, maximizes ingredient reuse to cut cost and waste, and ships with an aisle-organized grocery list plus a batch-prep schedule.

Keywords: meal plan, weekly menu, meal prep, macros, calories, grocery list, shopping list, batch cooking, dietary restrictions, vegan, keto, gluten-free, budget meals, leftovers, portion sizes.

This skill is for **planning**, not for medical nutrition therapy. For clinical conditions (diabetes management, eating disorders, renal diets), advise the user to consult a registered dietitian.

## Workflow

Follow these steps in order. Do not skip the intake — a plan built on wrong assumptions is useless.

1. **Intake.** Gather the constraints below. If the user gave only partial info, ask 2-4 focused questions, then proceed with sensible defaults rather than stalling.
   - People & servings (adults/kids, who eats which meals).
   - Calorie target and macro split (or compute it — see step 2).
   - Diet style & restrictions (vegan, vegetarian, pescatarian, keto, paleo, halal, kosher, gluten-free, dairy-free, nut allergy, etc.).
   - Dislikes / must-haves.
   - Budget (per week or per serving) and currency.
   - Cooking time available on weeknights; whether they want to batch-prep on a weekend day.
   - Kitchen equipment (oven, instant pot, blender, etc.) and skill level.
   - Meals per day to plan (breakfast/lunch/dinner/snacks) and number of days.

2. **Set targets.** If the user did not give numbers, estimate calories with Mifflin-St Jeor and an activity factor, then apply a macro split fit to their goal. The full formulas, activity factors, goal adjustments, and split presets are in `references/macro-targets.md`. Always state the assumptions you used.

3. **Pick a strategy for variety + reuse.** Use the "rule of overlapping ingredients": choose 2-3 anchor proteins, 2-3 anchor carbs, and a rotating set of vegetables so one shopping trip feeds the whole week. Repeat breakfasts (1-2 options) to reduce decision load; vary lunches and dinners. See `references/planning-heuristics.md` for the variety/repetition balance, leftover-roll-forward patterns, and batch-prep sequencing.

4. **Draft the grid.** Fill a day-by-meal table. For each meal record: name, the per-serving calories and protein/carbs/fat, and servings made. Aim within ±5% of the daily calorie target and within ±10% of each macro target across the day (intra-day swings are fine).

5. **Verify the numbers.** Total each day and the week. If a day is off-target, adjust portion sizes or swap a side before changing whole meals. You may use `scripts/plan_calc.py` to total macros and flag days outside tolerance from a simple JSON plan file.

6. **Build the batch-prep schedule.** Group tasks by appliance and by "cook once, use 2-3 times" (e.g., roast a tray of vegetables, cook a pot of grains, prep a sauce). Order tasks so the oven/stove is never idle. List what goes in the fridge vs. freezer and food-safety holding times.

7. **Generate the grocery list.** Consolidate every ingredient across all meals, sum quantities, convert to purchasable units (e.g., "3 onions" not "1/2 onion x6"), and group by store section using `references/grocery-aisles.md`. Note pantry staples the user likely already has separately so they don't re-buy.

8. **Deliver.** Output in this order: (a) targets & assumptions, (b) the weekly meal grid with daily totals, (c) batch-prep schedule, (d) grocery list by aisle, (e) swap suggestions and storage notes. Use `templates/meal-plan.md` as the output skeleton.

## Decision Frameworks

**Calorie tolerance.** Daily total within ±5% of target = good. If 5-10% off, tweak portions. If >10% off, restructure a meal.

**Protein floor.** For most adults aim for at least 1.6 g protein per kg bodyweight (higher for muscle gain / fat loss). Never let protein fall short to chase a calorie number — add lean protein and trim fat/carbs instead.

**Cost vs. convenience.** Cheaper plans lean on dried legumes, whole grains, frozen veg, eggs, and cheaper cuts; faster plans lean on canned/frozen, pre-cut produce, and rotisserie shortcuts. Surface the trade-off; don't silently pick.

**Variety dial.** Default: breakfast 1-2 repeating options, lunch 2-3 options (often dinner leftovers), dinner 4-5 distinct meals across the week. Increase variety only if the user explicitly wants it (raises cost and prep).

## Best Practices
- State every assumption (calorie target, servings, what counts as a pantry staple).
- Make leftovers intentional: cook dinner in a double batch to become next-day lunch.
- Keep one "flex meal" slot for eating out or using up odds and ends.
- Round grocery quantities up to real package sizes.
- Respect allergies as hard constraints — never substitute an allergen, and flag cross-contamination risks.
- Default to seasonal/frozen produce for cost and nutrition unless told otherwise.

## Common Pitfalls
- Hitting calories but missing the protein floor.
- Listing fractional, un-buyable quantities (½ a can, ⅓ an onion).
- Over-varied plans that buy 30 ingredients used once each — expensive and wasteful.
- Ignoring weeknight time limits and scheduling 60-minute dinners on workdays.
- Forgetting snacks and drinks in the calorie math.
- Treating a meal plan as medical advice for a clinical condition.

## Bundled Files
- `references/macro-targets.md` — Mifflin-St Jeor formula, activity factors, goal adjustments, macro-split presets, protein guidance.
- `references/planning-heuristics.md` — variety vs. repetition, ingredient-overlap strategy, batch-prep sequencing, food-safety storage times.
- `references/grocery-aisles.md` — canonical aisle ordering and ingredient-to-section mapping for list organization.
- `scripts/plan_calc.py` — totals macros/calories from a JSON plan and flags days outside tolerance.
- `templates/meal-plan.md` — output skeleton for the final deliverable.
- `examples/sample-week.md` — a worked 7-day example with targets, grid, prep schedule, and grocery list.
